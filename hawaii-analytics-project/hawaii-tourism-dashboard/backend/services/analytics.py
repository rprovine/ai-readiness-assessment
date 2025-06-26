import pandas as pd
import numpy as np
from datetime import datetime, date, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, extract
import hashlib
import json

from config.database import VisitorArrivalDB, HotelOccupancyDB, EconomicIndicatorDB, AnalyticsCacheDB
from models.data_models import AnalyticsRequest

class AnalyticsEngine:
    def __init__(self, db: Session):
        self.db = db
        
    async def process_query(self, request: AnalyticsRequest) -> Dict[str, Any]:
        """Process analytics query with caching"""
        cache_key = self.generate_cache_key(request)
        
        cached_result = self.get_cached_result(cache_key)
        if cached_result:
            return cached_result
        
        results = {
            "request": request.dict(),
            "generated_at": datetime.utcnow().isoformat(),
            "data": {}
        }
        
        if "arrivals" in request.metrics:
            results["data"]["arrivals"] = await self.analyze_arrivals(request)
        
        if "occupancy" in request.metrics:
            results["data"]["occupancy"] = await self.analyze_occupancy(request)
        
        if "spending" in request.metrics:
            results["data"]["spending"] = await self.analyze_spending(request)
        
        results["insights"] = await self.generate_insights(results["data"])
        
        self.cache_result(cache_key, results)
        
        return results
    
    async def analyze_arrivals(self, request: AnalyticsRequest) -> Dict:
        """Analyze visitor arrival patterns"""
        query = self.db.query(
            VisitorArrivalDB.date,
            VisitorArrivalDB.island,
            func.sum(VisitorArrivalDB.arrival_count).label('total_arrivals')
        ).filter(
            and_(
                VisitorArrivalDB.date >= request.start_date,
                VisitorArrivalDB.date <= request.end_date
            )
        )
        
        if request.islands:
            query = query.filter(VisitorArrivalDB.island.in_([i.value for i in request.islands]))
        
        if request.group_by == "month":
            query = query.group_by(
                extract('year', VisitorArrivalDB.date),
                extract('month', VisitorArrivalDB.date),
                VisitorArrivalDB.island
            )
        else:
            query = query.group_by(VisitorArrivalDB.date, VisitorArrivalDB.island)
        
        results = query.all()
        
        arrival_data = []
        for row in results:
            arrival_data.append({
                "date": row.date.isoformat() if hasattr(row.date, 'isoformat') else str(row.date),
                "island": row.island,
                "arrivals": row.total_arrivals
            })
        
        origin_analysis = self.db.query(
            VisitorArrivalDB.origin_state,
            func.sum(VisitorArrivalDB.arrival_count).label('total')
        ).filter(
            and_(
                VisitorArrivalDB.date >= request.start_date,
                VisitorArrivalDB.date <= request.end_date,
                VisitorArrivalDB.origin_state.isnot(None)
            )
        ).group_by(VisitorArrivalDB.origin_state).order_by(func.sum(VisitorArrivalDB.arrival_count).desc()).limit(10).all()
        
        return {
            "time_series": arrival_data,
            "total_arrivals": sum(row.total_arrivals for row in results),
            "top_origins": [{"state": state, "arrivals": total} for state, total in origin_analysis],
            "average_daily_arrivals": sum(row.total_arrivals for row in results) / max(1, len(results))
        }
    
    async def analyze_occupancy(self, request: AnalyticsRequest) -> Dict:
        """Analyze hotel occupancy patterns"""
        query = self.db.query(
            HotelOccupancyDB.date,
            HotelOccupancyDB.island,
            func.avg(HotelOccupancyDB.occupancy_rate).label('avg_occupancy'),
            func.avg(HotelOccupancyDB.adr).label('avg_adr'),
            func.avg(HotelOccupancyDB.revpar).label('avg_revpar')
        ).filter(
            and_(
                HotelOccupancyDB.date >= request.start_date,
                HotelOccupancyDB.date <= request.end_date
            )
        )
        
        if request.islands:
            query = query.filter(HotelOccupancyDB.island.in_([i.value for i in request.islands]))
        
        query = query.group_by(HotelOccupancyDB.date, HotelOccupancyDB.island)
        
        results = query.all()
        
        occupancy_data = []
        for row in results:
            occupancy_data.append({
                "date": row.date.isoformat(),
                "island": row.island,
                "occupancy_rate": round(row.avg_occupancy, 1),
                "adr": round(row.avg_adr, 2),
                "revpar": round(row.avg_revpar, 2) if row.avg_revpar else None
            })
        
        overall_stats = self.db.query(
            func.avg(HotelOccupancyDB.occupancy_rate).label('avg_occupancy'),
            func.avg(HotelOccupancyDB.adr).label('avg_adr'),
            func.max(HotelOccupancyDB.occupancy_rate).label('peak_occupancy'),
            func.min(HotelOccupancyDB.occupancy_rate).label('low_occupancy')
        ).filter(
            and_(
                HotelOccupancyDB.date >= request.start_date,
                HotelOccupancyDB.date <= request.end_date
            )
        ).first()
        
        return {
            "time_series": occupancy_data,
            "average_occupancy": round(overall_stats.avg_occupancy, 1) if overall_stats.avg_occupancy else 0,
            "average_adr": round(overall_stats.avg_adr, 2) if overall_stats.avg_adr else 0,
            "peak_occupancy": round(overall_stats.peak_occupancy, 1) if overall_stats.peak_occupancy else 0,
            "low_occupancy": round(overall_stats.low_occupancy, 1) if overall_stats.low_occupancy else 0
        }
    
    async def analyze_spending(self, request: AnalyticsRequest) -> Dict:
        """Analyze visitor spending patterns"""
        spending_data = self.db.query(
            EconomicIndicatorDB.date,
            EconomicIndicatorDB.visitor_spending_millions
        ).filter(
            and_(
                EconomicIndicatorDB.date >= request.start_date,
                EconomicIndicatorDB.date <= request.end_date
            )
        ).order_by(EconomicIndicatorDB.date).all()
        
        if not spending_data:
            return {"error": "No spending data available for this period"}
        
        spending_series = [
            {
                "date": record.date.isoformat(),
                "spending_millions": record.visitor_spending_millions
            }
            for record in spending_data
        ]
        
        total_spending = sum(record.visitor_spending_millions for record in spending_data)
        avg_monthly_spending = total_spending / max(1, len(spending_data))
        
        return {
            "time_series": spending_series,
            "total_spending_millions": round(total_spending, 1),
            "average_monthly_spending_millions": round(avg_monthly_spending, 1),
            "spending_trend": "increasing" if len(spending_data) > 1 and spending_data[-1].visitor_spending_millions > spending_data[0].visitor_spending_millions else "stable"
        }
    
    async def generate_insights(self, data: Dict) -> List[str]:
        """Generate actionable insights from analytics data"""
        insights = []
        
        if "arrivals" in data and data["arrivals"].get("top_origins"):
            top_origin = data["arrivals"]["top_origins"][0]
            insights.append(f"Visitors from {top_origin['state']} represent your largest market with {top_origin['arrivals']:,} arrivals")
        
        if "occupancy" in data:
            avg_occ = data["occupancy"].get("average_occupancy", 0)
            if avg_occ > 80:
                insights.append(f"High occupancy rate of {avg_occ}% indicates strong demand - consider premium pricing strategies")
            elif avg_occ < 60:
                insights.append(f"Occupancy at {avg_occ}% suggests opportunity for targeted marketing campaigns")
        
        if "spending" in data and "arrivals" in data:
            total_spending = data["spending"].get("total_spending_millions", 0)
            total_arrivals = data["arrivals"].get("total_arrivals", 1)
            spend_per_visitor = (total_spending * 1_000_000) / total_arrivals if total_arrivals > 0 else 0
            
            if spend_per_visitor > 0:
                insights.append(f"Average visitor spending is ${spend_per_visitor:.0f} - focus on high-value visitor segments")
        
        if "arrivals" in data:
            avg_daily = data["arrivals"].get("average_daily_arrivals", 0)
            insights.append(f"Average {int(avg_daily):,} daily arrivals provides baseline for capacity planning")
        
        return insights
    
    def generate_cache_key(self, request: AnalyticsRequest) -> str:
        """Generate unique cache key for request"""
        request_str = json.dumps(request.dict(), sort_keys=True, default=str)
        return hashlib.md5(request_str.encode()).hexdigest()
    
    def get_cached_result(self, cache_key: str) -> Optional[Dict]:
        """Retrieve cached result if available and not expired"""
        cached = self.db.query(AnalyticsCacheDB).filter(
            AnalyticsCacheDB.query_hash == cache_key,
            AnalyticsCacheDB.expires_at > datetime.utcnow()
        ).first()
        
        if cached:
            return cached.results
        return None
    
    def cache_result(self, cache_key: str, results: Dict):
        """Cache analytics results"""
        try:
            cache_entry = AnalyticsCacheDB(
                query_hash=cache_key,
                results=results,
                expires_at=datetime.utcnow() + timedelta(hours=1)
            )
            self.db.add(cache_entry)
            self.db.commit()
        except Exception as e:
            print(f"Error caching results: {e}")
            self.db.rollback()