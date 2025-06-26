import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, date, timedelta
from typing import List, Dict, Optional
import json
from sqlalchemy.orm import Session

from config.database import get_db, VisitorArrivalDB, HotelOccupancyDB, EconomicIndicatorDB
from models.data_models import Island

class DataCollector:
    def __init__(self):
        self.hta_base_url = "https://www.hawaiitourismauthority.org"
        self.dbedt_base_url = "http://dbedt.hawaii.gov"
        
    async def collect_all_data(self):
        """Main method to collect all tourism data"""
        results = {
            "visitor_arrivals": await self.collect_visitor_arrivals(),
            "hotel_occupancy": await self.collect_hotel_occupancy(),
            "economic_indicators": await self.collect_economic_indicators(),
            "timestamp": datetime.utcnow()
        }
        
        await self.save_to_database(results)
        return results
    
    async def collect_visitor_arrivals(self) -> List[Dict]:
        """Collect visitor arrival data from HTA"""
        try:
            arrivals_data = []
            
            mock_data = self.generate_mock_visitor_data()
            arrivals_data.extend(mock_data)
            
            return arrivals_data
        except Exception as e:
            print(f"Error collecting visitor arrivals: {e}")
            return []
    
    async def collect_hotel_occupancy(self) -> List[Dict]:
        """Collect hotel occupancy data"""
        try:
            occupancy_data = []
            
            mock_data = self.generate_mock_occupancy_data()
            occupancy_data.extend(mock_data)
            
            return occupancy_data
        except Exception as e:
            print(f"Error collecting hotel occupancy: {e}")
            return []
    
    async def collect_economic_indicators(self) -> List[Dict]:
        """Collect economic indicators"""
        try:
            economic_data = []
            
            mock_data = self.generate_mock_economic_data()
            economic_data.extend(mock_data)
            
            return economic_data
        except Exception as e:
            print(f"Error collecting economic indicators: {e}")
            return []
    
    async def save_to_database(self, data: Dict):
        """Save collected data to database"""
        db = next(get_db())
        
        try:
            for arrival in data.get("visitor_arrivals", []):
                db_arrival = VisitorArrivalDB(**arrival)
                db.add(db_arrival)
            
            for occupancy in data.get("hotel_occupancy", []):
                db_occupancy = HotelOccupancyDB(**occupancy)
                db.add(db_occupancy)
            
            for indicator in data.get("economic_indicators", []):
                db_indicator = EconomicIndicatorDB(**indicator)
                db.add(db_indicator)
            
            db.commit()
        except Exception as e:
            db.rollback()
            print(f"Error saving to database: {e}")
        finally:
            db.close()
    
    def generate_mock_visitor_data(self) -> List[Dict]:
        """Generate realistic mock visitor arrival data"""
        data = []
        islands = [island.value for island in Island]
        states = ["California", "Texas", "Washington", "Oregon", "New York", "Florida", "Arizona", "Colorado"]
        
        base_date = date.today() - timedelta(days=365)
        
        for i in range(365):
            current_date = base_date + timedelta(days=i)
            
            for island in islands:
                for state in states[:5]:
                    base_arrivals = {
                        "Oahu": 5000,
                        "Maui": 3000,
                        "Kauai": 2000,
                        "Hawaii": 2500,
                        "Molokai": 200,
                        "Lanai": 150
                    }
                    
                    seasonal_factor = 1.0
                    if current_date.month in [12, 1, 2]:
                        seasonal_factor = 1.3
                    elif current_date.month in [6, 7, 8]:
                        seasonal_factor = 1.2
                    
                    state_factor = {
                        "California": 1.5,
                        "Texas": 0.8,
                        "Washington": 1.0,
                        "Oregon": 0.9,
                        "New York": 0.7
                    }
                    
                    arrivals = int(
                        base_arrivals.get(island, 1000) * 
                        seasonal_factor * 
                        state_factor.get(state, 1.0) * 
                        (0.9 + 0.2 * (i % 7) / 7)
                    )
                    
                    data.append({
                        "date": current_date,
                        "island": island,
                        "origin_state": state,
                        "arrival_count": arrivals,
                        "arrival_type": "air"
                    })
        
        return data
    
    def generate_mock_occupancy_data(self) -> List[Dict]:
        """Generate realistic mock hotel occupancy data"""
        data = []
        islands = [island.value for island in Island]
        
        base_date = date.today() - timedelta(days=365)
        
        for i in range(365):
            current_date = base_date + timedelta(days=i)
            
            for island in islands:
                base_occupancy = {
                    "Oahu": 0.80,
                    "Maui": 0.75,
                    "Kauai": 0.70,
                    "Hawaii": 0.72,
                    "Molokai": 0.60,
                    "Lanai": 0.65
                }
                
                base_adr = {
                    "Oahu": 250,
                    "Maui": 350,
                    "Kauai": 300,
                    "Hawaii": 275,
                    "Molokai": 150,
                    "Lanai": 450
                }
                
                seasonal_factor = 1.0
                if current_date.month in [12, 1, 2]:
                    seasonal_factor = 1.15
                elif current_date.month in [6, 7, 8]:
                    seasonal_factor = 1.10
                
                weekend_factor = 1.1 if current_date.weekday() >= 5 else 1.0
                
                occupancy_rate = min(
                    base_occupancy.get(island, 0.70) * seasonal_factor * weekend_factor * (0.95 + 0.1 * (i % 30) / 30),
                    0.95
                )
                
                adr = base_adr.get(island, 200) * seasonal_factor * weekend_factor
                revpar = occupancy_rate * adr
                
                data.append({
                    "date": current_date,
                    "island": island,
                    "occupancy_rate": round(occupancy_rate * 100, 1),
                    "adr": round(adr, 2),
                    "revpar": round(revpar, 2)
                })
        
        return data
    
    def generate_mock_economic_data(self) -> List[Dict]:
        """Generate realistic mock economic data"""
        data = []
        
        base_date = date.today() - timedelta(days=365)
        
        for i in range(0, 365, 30):
            current_date = base_date + timedelta(days=i)
            
            base_unemployment = 2.8
            seasonal_variation = 0.3 * ((i % 180) / 180)
            unemployment_rate = base_unemployment + seasonal_variation
            
            base_spending = 1500
            seasonal_factor = 1.2 if current_date.month in [12, 1, 2, 6, 7, 8] else 1.0
            visitor_spending = base_spending * seasonal_factor * (0.95 + 0.1 * (i % 90) / 90)
            
            gdp_growth = 2.5 + 0.5 * ((i % 120) / 120)
            
            data.append({
                "date": current_date,
                "unemployment_rate": round(unemployment_rate, 1),
                "visitor_spending_millions": round(visitor_spending, 1),
                "gdp_growth_rate": round(gdp_growth, 1)
            })
        
        return data
    
    async def fetch_real_hta_data(self):
        """Fetch real data from Hawaii Tourism Authority when available"""
        pass
    
    async def fetch_tsa_checkpoint_data(self):
        """Fetch TSA checkpoint data for Hawaii airports"""
        pass
    
    async def fetch_google_trends_data(self):
        """Fetch Google Trends data for Hawaii tourism searches"""
        pass