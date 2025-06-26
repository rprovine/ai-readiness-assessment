from sqlalchemy import create_engine, Column, Integer, String, Float, Date, DateTime, JSON, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

# Database URL - using SQLite for development
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./hawaii_tourism.db")

# Create engine
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {})

# Create sessionmaker
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Database Models
class VisitorArrivalDB(Base):
    __tablename__ = "visitor_arrivals"
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, index=True)
    island = Column(String, index=True)
    origin_state = Column(String, nullable=True)
    arrival_count = Column(Integer)
    arrival_type = Column(String)  # air, cruise
    created_at = Column(DateTime, default=datetime.utcnow)

class HotelOccupancyDB(Base):
    __tablename__ = "hotel_occupancy"
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, index=True)
    island = Column(String, index=True)
    occupancy_rate = Column(Float)  # percentage
    adr = Column(Float)  # Average Daily Rate
    revpar = Column(Float, nullable=True)  # Revenue per Available Room
    created_at = Column(DateTime, default=datetime.utcnow)

class EconomicIndicatorDB(Base):
    __tablename__ = "economic_indicators"
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, index=True)
    unemployment_rate = Column(Float)
    visitor_spending_millions = Column(Float)
    gdp_growth_rate = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class BusinessLeadDB(Base):
    __tablename__ = "business_leads"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    business_name = Column(String, nullable=True)
    business_type = Column(String)
    island = Column(String)
    contact_name = Column(String)
    phone = Column(String, nullable=True)
    interest_areas = Column(JSON)
    source = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_contacted = Column(DateTime, nullable=True)

class TourismForecastDB(Base):
    __tablename__ = "tourism_forecasts"
    
    id = Column(Integer, primary_key=True, index=True)
    forecast_date = Column(Date)
    target_date = Column(Date)
    island = Column(String)
    predicted_arrivals = Column(Integer)
    confidence_lower = Column(Integer)
    confidence_upper = Column(Integer)
    model_name = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

class AnalyticsCacheDB(Base):
    __tablename__ = "analytics_cache"
    
    id = Column(Integer, primary_key=True, index=True)
    query_hash = Column(String, unique=True, index=True)
    results = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)

# Create all tables
Base.metadata.create_all(bind=engine)