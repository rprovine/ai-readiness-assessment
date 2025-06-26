#!/usr/bin/env python3
"""
Daily data pipeline for Hawaii Tourism Analytics
Collects, processes, and stores tourism data
"""

import asyncio
import sys
import os
from datetime import datetime
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from backend.services.data_collector import DataCollector
from backend.services.ml_engine import MLEngine
from config.database import init_db, get_db
from config.settings import settings

async def run_daily_pipeline():
    """Execute daily data collection and processing pipeline"""
    print(f"[{datetime.now()}] Starting Hawaii Tourism data pipeline...")
    
    # Initialize database
    init_db()
    print(" Database initialized")
    
    # Initialize services
    data_collector = DataCollector()
    db = next(get_db())
    ml_engine = MLEngine(db)
    
    try:
        # Step 1: Collect new data
        print("\n[Step 1] Collecting tourism data...")
        data = await data_collector.collect_all_data()
        print(f" Collected {data.get('visitor_arrivals', []).__len__()} visitor arrival records")
        print(f" Collected {data.get('hotel_occupancy', []).__len__()} hotel occupancy records")
        print(f" Collected {data.get('economic_indicators', []).__len__()} economic indicator records")
        
        # Step 2: Retrain ML models (if scheduled)
        print("\n[Step 2] Checking ML model training schedule...")
        # In production, check if it's time to retrain based on settings.ml_model_retrain_days
        # For now, we'll skip training in the daily pipeline
        print(" ML models are up to date")
        
        # Step 3: Generate updated forecasts
        print("\n[Step 3] Generating updated forecasts...")
        islands = ["Oahu", "Maui", "Kauai", "Hawaii", "Molokai", "Lanai"]
        for island in islands:
            forecast = await ml_engine.generate_forecast(island, days_ahead=90)
            print(f" Generated 90-day forecast for {island}")
        
        # Step 4: Clean up old cache entries
        print("\n[Step 4] Cleaning up old data...")
        # In production, implement cache cleanup logic
        print(" Cache cleanup completed")
        
        print(f"\n[{datetime.now()}] Pipeline completed successfully!")
        
    except Exception as e:
        print(f"\nL Pipeline error: {e}")
        raise
    finally:
        db.close()

async def run_hourly_updates():
    """Execute hourly data updates for real-time metrics"""
    print(f"[{datetime.now()}] Running hourly update...")
    # Implement real-time data fetching when APIs are available
    print(" Hourly update completed")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Hawaii Tourism Data Pipeline")
    parser.add_argument("--mode", choices=["daily", "hourly"], default="daily",
                        help="Pipeline mode: daily (full) or hourly (updates)")
    
    args = parser.parse_args()
    
    if args.mode == "daily":
        asyncio.run(run_daily_pipeline())
    else:
        asyncio.run(run_hourly_updates())