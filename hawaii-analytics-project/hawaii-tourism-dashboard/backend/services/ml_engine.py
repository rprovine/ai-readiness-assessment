import pandas as pd
import numpy as np
from datetime import datetime, date, timedelta
from typing import List, Dict, Tuple, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
import joblib
from prophet import Prophet
# from statsmodels.tsa.arima.model import ARIMA  # Temporarily disabled due to scipy conflict
import warnings
warnings.filterwarnings('ignore')

from config.database import VisitorArrivalDB, TourismForecastDB

class MLEngine:
    def __init__(self, db: Session):
        self.db = db
        self.models = {}
        
    async def train_all_models(self):
        """Train models for all islands"""
        islands = ["Oahu", "Maui", "Kauai", "Hawaii", "Molokai", "Lanai"]
        
        for island in islands:
            print(f"Training model for {island}...")
            await self.train_prophet_model(island)
            # await self.train_arima_model(island)  # Temporarily disabled
    
    async def train_prophet_model(self, island: str):
        """Train Prophet model for visitor arrivals forecasting"""
        try:
            historical_data = self.db.query(
                VisitorArrivalDB.date,
                func.sum(VisitorArrivalDB.arrival_count).label('y')
            ).filter(
                VisitorArrivalDB.island == island
            ).group_by(VisitorArrivalDB.date).all()
            
            if not historical_data:
                return None
            
            df = pd.DataFrame(historical_data)
            df.columns = ['ds', 'y']
            df['ds'] = pd.to_datetime(df['ds'])
            
            model = Prophet(
                yearly_seasonality=True,
                weekly_seasonality=True,
                daily_seasonality=False,
                seasonality_mode='multiplicative',
                changepoint_prior_scale=0.05
            )
            
            model.add_country_holidays(country_name='US')
            
            model.fit(df)
            
            self.models[f"prophet_{island}"] = model
            
            joblib.dump(model, f"data/models/prophet_{island}.pkl")
            
            return model
        except Exception as e:
            print(f"Error training Prophet model for {island}: {e}")
            return None
    
    async def train_arima_model(self, island: str):
        """Train ARIMA model as alternative forecasting method"""
        # Temporarily disabled due to scipy/statsmodels conflict
        return None
    
    async def generate_forecast(self, island: str, days_ahead: int = 90) -> List[Dict]:
        """Generate visitor arrival forecast for specified island"""
        try:
            model_key = f"prophet_{island}"
            
            if model_key not in self.models:
                try:
                    self.models[model_key] = joblib.load(f"data/models/{model_key}.pkl")
                except:
                    await self.train_prophet_model(island)
            
            if model_key not in self.models:
                return self.generate_baseline_forecast(island, days_ahead)
            
            model = self.models[model_key]
            
            future = model.make_future_dataframe(periods=days_ahead)
            forecast = model.predict(future)
            
            forecast_data = []
            today = date.today()
            
            for i in range(days_ahead):
                forecast_date = today + timedelta(days=i)
                idx = len(forecast) - days_ahead + i
                
                if idx < len(forecast):
                    predicted = max(0, int(forecast.iloc[idx]['yhat']))
                    lower = max(0, int(forecast.iloc[idx]['yhat_lower']))
                    upper = max(0, int(forecast.iloc[idx]['yhat_upper']))
                else:
                    predicted = 5000
                    lower = 4500
                    upper = 5500
                
                forecast_data.append({
                    "date": forecast_date,
                    "predicted_arrivals": predicted,
                    "confidence_lower": lower,
                    "confidence_upper": upper,
                    "island": island
                })
                
                db_forecast = TourismForecastDB(
                    forecast_date=today,
                    target_date=forecast_date,
                    island=island,
                    predicted_arrivals=predicted,
                    confidence_lower=lower,
                    confidence_upper=upper,
                    model_name="prophet"
                )
                self.db.add(db_forecast)
            
            self.db.commit()
            
            return forecast_data
        except Exception as e:
            print(f"Error generating forecast: {e}")
            return self.generate_baseline_forecast(island, days_ahead)
    
    def generate_baseline_forecast(self, island: str, days_ahead: int) -> List[Dict]:
        """Generate simple baseline forecast when models aren't available"""
        recent_data = self.db.query(
            func.avg(VisitorArrivalDB.arrival_count).label('avg_arrivals')
        ).filter(
            VisitorArrivalDB.island == island,
            VisitorArrivalDB.date >= date.today() - timedelta(days=30)
        ).scalar() or 5000
        
        forecast_data = []
        today = date.today()
        
        for i in range(days_ahead):
            forecast_date = today + timedelta(days=i)
            
            seasonal_factor = 1.0
            if forecast_date.month in [12, 1, 2]:
                seasonal_factor = 1.2
            elif forecast_date.month in [6, 7, 8]:
                seasonal_factor = 1.1
            
            weekend_factor = 1.1 if forecast_date.weekday() >= 5 else 1.0
            
            predicted = int(recent_data * seasonal_factor * weekend_factor * (0.95 + 0.1 * np.random.random()))
            
            forecast_data.append({
                "date": forecast_date,
                "predicted_arrivals": predicted,
                "confidence_lower": int(predicted * 0.85),
                "confidence_upper": int(predicted * 1.15),
                "island": island
            })
        
        return forecast_data
    
    async def calculate_business_impact(self, island: str, business_type: str) -> Dict:
        """Calculate predicted business impact based on tourism forecasts"""
        forecast = await self.generate_forecast(island, 30)
        
        if not forecast:
            return {"error": "Unable to generate forecast"}
        
        total_predicted_visitors = sum(f["predicted_arrivals"] for f in forecast)
        
        impact_factors = {
            "hotel": {"visitor_ratio": 0.4, "avg_spend": 250},
            "restaurant": {"visitor_ratio": 0.7, "avg_spend": 50},
            "tour_operator": {"visitor_ratio": 0.3, "avg_spend": 150},
            "retail": {"visitor_ratio": 0.5, "avg_spend": 80},
            "transportation": {"visitor_ratio": 0.6, "avg_spend": 40}
        }
        
        factor = impact_factors.get(business_type, {"visitor_ratio": 0.5, "avg_spend": 100})
        
        estimated_customers = int(total_predicted_visitors * factor["visitor_ratio"])
        estimated_revenue = estimated_customers * factor["avg_spend"]
        
        return {
            "period": "Next 30 days",
            "island": island,
            "business_type": business_type,
            "predicted_visitors": total_predicted_visitors,
            "estimated_customers": estimated_customers,
            "estimated_revenue": estimated_revenue,
            "confidence": "Medium",
            "recommendations": self.generate_recommendations(business_type, forecast)
        }
    
    def generate_recommendations(self, business_type: str, forecast: List[Dict]) -> List[str]:
        """Generate business recommendations based on forecast"""
        recommendations = []
        
        peak_days = sorted(forecast, key=lambda x: x["predicted_arrivals"], reverse=True)[:5]
        peak_dates = [d["date"].strftime("%B %d") for d in peak_days]
        
        recommendations.append(f"Peak visitor days expected: {', '.join(peak_dates)}")
        
        if business_type == "hotel":
            recommendations.append("Consider dynamic pricing for peak periods")
            recommendations.append("Ensure adequate staffing for high-occupancy dates")
        elif business_type == "restaurant":
            recommendations.append("Stock up on inventory for peak days")
            recommendations.append("Consider extended hours during high-traffic periods")
        elif business_type == "tour_operator":
            recommendations.append("Add extra tour slots for peak days")
            recommendations.append("Hire seasonal guides if needed")
        
        avg_arrivals = sum(f["predicted_arrivals"] for f in forecast) / len(forecast)
        if avg_arrivals > 10000:
            recommendations.append("High visitor volume expected - prepare marketing campaigns")
        
        return recommendations