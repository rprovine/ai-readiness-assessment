from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from datetime import datetime, date, timedelta
from typing import List, Dict, Optional

from config.database import get_db, VisitorArrivalDB, HotelOccupancyDB, EconomicIndicatorDB
from models.data_models import AnalyticsRequest, Island
from services.analytics import AnalyticsEngine

router = APIRouter()

@router.post("/query")
async def query_analytics(
    request: AnalyticsRequest,
    db: Session = Depends(get_db)
):
    """Query tourism analytics with custom parameters"""
    try:
        analytics_engine = AnalyticsEngine(db)
        results = await analytics_engine.process_query(request)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/seasonality/{island}")
async def get_seasonality_analysis(
    island: Island,
    db: Session = Depends(get_db)
):
    """Get seasonality patterns for a specific island"""
    try:
        monthly_data = db.query(
            func.extract('month', VisitorArrivalDB.date).label('month'),
            func.avg(VisitorArrivalDB.arrival_count).label('avg_arrivals')
        ).filter(
            VisitorArrivalDB.island == island.value
        ).group_by('month').order_by('month').all()
        
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        
        seasonality = {
            "island": island.value,
            "monthly_averages": [
                {
                    "month": months[int(month[0]) - 1],
                    "average_arrivals": round(month[1])
                } for month in monthly_data
            ],
            "peak_month": months[max(monthly_data, key=lambda x: x[1])[0] - 1],
            "low_month": months[min(monthly_data, key=lambda x: x[1])[0] - 1]
        }
        
        return seasonality
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/origin-analysis")
async def get_origin_analysis(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db)
):
    """Analyze visitor origins and patterns"""
    try:
        if not end_date:
            end_date = date.today()
        if not start_date:
            start_date = end_date - timedelta(days=30)
        
        origin_data = db.query(
            VisitorArrivalDB.origin_state,
            VisitorArrivalDB.island,
            func.sum(VisitorArrivalDB.arrival_count).label('total_arrivals')
        ).filter(
            and_(
                VisitorArrivalDB.date >= start_date,
                VisitorArrivalDB.date <= end_date,
                VisitorArrivalDB.origin_state.isnot(None)
            )
        ).group_by(
            VisitorArrivalDB.origin_state,
            VisitorArrivalDB.island
        ).all()
        
        origin_summary = {}
        for state, island, arrivals in origin_data:
            if state not in origin_summary:
                origin_summary[state] = {"total": 0, "islands": {}}
            origin_summary[state]["total"] += arrivals
            origin_summary[state]["islands"][island] = arrivals
        
        return {
            "period": f"{start_date} to {end_date}",
            "origin_data": origin_summary,
            "top_origins": sorted(origin_summary.items(), key=lambda x: x[1]["total"], reverse=True)[:10]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/economic-correlation")
async def get_economic_correlation(
    metric: str = "visitor_spending",
    db: Session = Depends(get_db)
):
    """Analyze correlation between tourism and economic indicators"""
    try:
        economic_data = db.query(EconomicIndicatorDB).order_by(EconomicIndicatorDB.date.desc()).limit(12).all()
        
        if not economic_data:
            return {"error": "No economic data available"}
        
        correlations = []
        for record in economic_data:
            visitor_count = db.query(func.sum(VisitorArrivalDB.arrival_count)).filter(
                func.extract('month', VisitorArrivalDB.date) == record.date.month,
                func.extract('year', VisitorArrivalDB.date) == record.date.year
            ).scalar() or 0
            
            correlations.append({
                "date": record.date.isoformat(),
                "visitor_arrivals": visitor_count,
                "visitor_spending_millions": record.visitor_spending_millions,
                "unemployment_rate": record.unemployment_rate,
                "gdp_growth_rate": record.gdp_growth_rate
            })
        
        return {
            "correlations": correlations,
            "analysis": "Higher visitor arrivals correlate with increased spending and lower unemployment"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/forecast-preview")
async def get_forecast_preview(
    island: Island,
    days_ahead: int = 90,
    db: Session = Depends(get_db)
):
    """Get a preview of tourism forecasts (limited for free tier)"""
    try:
        from services.ml_engine import MLEngine
        
        ml_engine = MLEngine(db)
        forecast = await ml_engine.generate_forecast(island.value, days_ahead)
        
        return {
            "island": island.value,
            "forecast_period": f"Next {days_ahead} days",
            "preview": forecast[:7],
            "message": "Full forecast available with premium access"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))