from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from datetime import datetime, date, timedelta
from typing import List, Dict, Optional

from config.database import get_db, VisitorArrivalDB, HotelOccupancyDB
from models.data_models import DashboardMetrics, Island

router = APIRouter()

@router.get("/metrics", response_model=DashboardMetrics)
async def get_dashboard_metrics(db: Session = Depends(get_db)):
    """Get current dashboard metrics"""
    try:
        today = date.today()
        current_month_start = date(today.year, today.month, 1)
        previous_month_start = (current_month_start - timedelta(days=1)).replace(day=1)
        previous_month_end = current_month_start - timedelta(days=1)
        year_start = date(today.year, 1, 1)
        last_year_month = current_month_start.replace(year=today.year - 1)
        
        current_month_arrivals = db.query(func.sum(VisitorArrivalDB.arrival_count)).filter(
            VisitorArrivalDB.date >= current_month_start
        ).scalar() or 0
        
        previous_month_arrivals = db.query(func.sum(VisitorArrivalDB.arrival_count)).filter(
            VisitorArrivalDB.date >= previous_month_start,
            VisitorArrivalDB.date <= previous_month_end
        ).scalar() or 0
        
        last_year_month_arrivals = db.query(func.sum(VisitorArrivalDB.arrival_count)).filter(
            VisitorArrivalDB.date >= last_year_month,
            VisitorArrivalDB.date < last_year_month.replace(month=last_year_month.month % 12 + 1)
        ).scalar() or 0
        
        yoy_growth_rate = ((current_month_arrivals - last_year_month_arrivals) / last_year_month_arrivals * 100) if last_year_month_arrivals > 0 else 0
        
        ytd_arrivals = db.query(func.sum(VisitorArrivalDB.arrival_count)).filter(
            VisitorArrivalDB.date >= year_start
        ).scalar() or 0
        
        top_states = db.query(
            VisitorArrivalDB.origin_state,
            func.sum(VisitorArrivalDB.arrival_count).label('total')
        ).filter(
            VisitorArrivalDB.date >= current_month_start,
            VisitorArrivalDB.origin_state.isnot(None)
        ).group_by(VisitorArrivalDB.origin_state).order_by(desc('total')).limit(5).all()
        
        top_origin_states = [{"state": state, "arrivals": total} for state, total in top_states]
        
        occupancy_data = db.query(
            HotelOccupancyDB.island,
            func.avg(HotelOccupancyDB.occupancy_rate).label('avg_occupancy')
        ).filter(
            HotelOccupancyDB.date >= current_month_start
        ).group_by(HotelOccupancyDB.island).all()
        
        occupancy_by_island = {island: round(avg_occ, 1) for island, avg_occ in occupancy_data}
        
        return DashboardMetrics(
            current_month_arrivals=int(current_month_arrivals),
            previous_month_arrivals=int(previous_month_arrivals),
            yoy_growth_rate=round(yoy_growth_rate, 1),
            ytd_arrivals=int(ytd_arrivals),
            top_origin_states=top_origin_states,
            occupancy_by_island=occupancy_by_island
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/visitor-trends")
async def get_visitor_trends(
    days: int = 30,
    island: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get visitor arrival trends"""
    try:
        end_date = date.today()
        start_date = end_date - timedelta(days=days)
        
        query = db.query(
            VisitorArrivalDB.date,
            func.sum(VisitorArrivalDB.arrival_count).label('total_arrivals')
        ).filter(
            VisitorArrivalDB.date >= start_date,
            VisitorArrivalDB.date <= end_date
        )
        
        if island:
            query = query.filter(VisitorArrivalDB.island == island)
        
        trends = query.group_by(VisitorArrivalDB.date).order_by(VisitorArrivalDB.date).all()
        
        return {
            "dates": [trend.date.isoformat() for trend in trends],
            "arrivals": [trend.total_arrivals for trend in trends],
            "period": f"{days} days",
            "island": island or "All Islands"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/occupancy-trends")
async def get_occupancy_trends(
    days: int = 30,
    island: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get hotel occupancy trends"""
    try:
        end_date = date.today()
        start_date = end_date - timedelta(days=days)
        
        query = db.query(
            HotelOccupancyDB.date,
            func.avg(HotelOccupancyDB.occupancy_rate).label('avg_occupancy'),
            func.avg(HotelOccupancyDB.adr).label('avg_adr')
        ).filter(
            HotelOccupancyDB.date >= start_date,
            HotelOccupancyDB.date <= end_date
        )
        
        if island:
            query = query.filter(HotelOccupancyDB.island == island)
        
        trends = query.group_by(HotelOccupancyDB.date).order_by(HotelOccupancyDB.date).all()
        
        return {
            "dates": [trend.date.isoformat() for trend in trends],
            "occupancy_rates": [round(trend.avg_occupancy, 1) for trend in trends],
            "adr_values": [round(trend.avg_adr, 2) for trend in trends],
            "period": f"{days} days",
            "island": island or "All Islands"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/island-comparison")
async def get_island_comparison(db: Session = Depends(get_db)):
    """Get comparison metrics across all islands"""
    try:
        today = date.today()
        month_start = date(today.year, today.month, 1)
        
        island_data = []
        
        for island in Island:
            arrivals = db.query(func.sum(VisitorArrivalDB.arrival_count)).filter(
                VisitorArrivalDB.date >= month_start,
                VisitorArrivalDB.island == island.value
            ).scalar() or 0
            
            occupancy = db.query(func.avg(HotelOccupancyDB.occupancy_rate)).filter(
                HotelOccupancyDB.date >= month_start,
                HotelOccupancyDB.island == island.value
            ).scalar() or 0
            
            adr = db.query(func.avg(HotelOccupancyDB.adr)).filter(
                HotelOccupancyDB.date >= month_start,
                HotelOccupancyDB.island == island.value
            ).scalar() or 0
            
            island_data.append({
                "island": island.value,
                "arrivals": int(arrivals),
                "occupancy_rate": round(occupancy, 1),
                "average_daily_rate": round(adr, 2)
            })
        
        return {"islands": island_data, "month": today.strftime("%B %Y")}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))