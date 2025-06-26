from sqlalchemy import create_engine, Column, Integer, String, Float, Date, DateTime, Boolean, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime

from config.settings import settings

Base = declarative_base()

class VisitorArrivalDB(Base):
    __tablename__ = "visitor_arrivals"
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False, index=True)
    island = Column(String, nullable=False, index=True)
    origin_state = Column(String)
    origin_country = Column(String, default="USA")
    arrival_count = Column(Integer, nullable=False)
    arrival_type = Column(String, default="air")
    created_at = Column(DateTime, default=datetime.utcnow)
    
class HotelOccupancyDB(Base):
    __tablename__ = "hotel_occupancy"
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False, index=True)
    island = Column(String, nullable=False, index=True)
    occupancy_rate = Column(Float, nullable=False)
    adr = Column(Float, nullable=False)
    revpar = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    
class EconomicIndicatorDB(Base):
    __tablename__ = "economic_indicators"
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False, index=True)
    unemployment_rate = Column(Float)
    visitor_spending_millions = Column(Float)
    gdp_growth_rate = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    
class BusinessLeadDB(Base):
    __tablename__ = "business_leads"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, nullable=False, index=True)
    business_name = Column(String)
    business_type = Column(String)
    island = Column(String)
    contact_name = Column(String, nullable=False)
    phone = Column(String)
    interest_areas = Column(JSON)
    source = Column(String, default="dashboard")
    created_at = Column(DateTime, default=datetime.utcnow)
    last_contacted = Column(DateTime)
    is_premium = Column(Boolean, default=False)
    
class AnalyticsCacheDB(Base):
    __tablename__ = "analytics_cache"
    
    id = Column(Integer, primary_key=True, index=True)
    query_hash = Column(String, nullable=False, index=True)
    results = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)
    
class TourismForecastDB(Base):
    __tablename__ = "tourism_forecasts"
    
    id = Column(Integer, primary_key=True, index=True)
    forecast_date = Column(Date, nullable=False)
    target_date = Column(Date, nullable=False, index=True)
    island = Column(String, nullable=False, index=True)
    predicted_arrivals = Column(Integer)
    confidence_lower = Column(Integer)
    confidence_upper = Column(Integer)
    model_name = Column(String, default="prophet")
    created_at = Column(DateTime, default=datetime.utcnow)

engine = create_engine(settings.database_url, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    Base.metadata.create_all(bind=engine)