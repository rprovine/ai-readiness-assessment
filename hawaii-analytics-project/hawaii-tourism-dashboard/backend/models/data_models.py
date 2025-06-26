from pydantic import BaseModel, Field
from datetime import datetime, date
from typing import Optional, List, Dict, Any
from enum import Enum

class Island(str, Enum):
    OAHU = "Oahu"
    MAUI = "Maui"
    KAUAI = "Kauai"
    BIG_ISLAND = "Hawaii"
    MOLOKAI = "Molokai"
    LANAI = "Lanai"

class BusinessType(str, Enum):
    HOTEL = "hotel"
    RESTAURANT = "restaurant"
    TOUR_OPERATOR = "tour_operator"
    RETAIL = "retail"
    TRANSPORTATION = "transportation"
    OTHER = "other"

class VisitorArrival(BaseModel):
    date: date
    island: Island
    origin_state: Optional[str] = None
    origin_country: str = "USA"
    arrival_count: int
    arrival_type: str = "air"
    
class HotelOccupancy(BaseModel):
    date: date
    island: Island
    occupancy_rate: float = Field(ge=0, le=100)
    adr: float = Field(ge=0, description="Average Daily Rate")
    revpar: Optional[float] = Field(None, description="Revenue Per Available Room")
    
class EconomicIndicator(BaseModel):
    date: date
    unemployment_rate: float
    visitor_spending_millions: float
    gdp_growth_rate: Optional[float] = None
    
class TourismForecast(BaseModel):
    model_config = {"protected_namespaces": ()}
    
    forecast_date: date
    target_date: date
    island: Island
    predicted_arrivals: int
    confidence_lower: int
    confidence_upper: int
    model_name: str = "prophet"
    
class BusinessLead(BaseModel):
    email: str
    business_name: Optional[str] = None
    business_type: BusinessType
    island: Island
    contact_name: str
    phone: Optional[str] = None
    interest_areas: List[str] = []
    source: str = "dashboard"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
class DashboardMetrics(BaseModel):
    current_month_arrivals: int
    previous_month_arrivals: int
    yoy_growth_rate: float
    ytd_arrivals: int
    top_origin_states: List[Dict[str, Any]]
    occupancy_by_island: Dict[str, float]
    
class AnalyticsRequest(BaseModel):
    start_date: date
    end_date: date
    islands: List[Island] = []
    metrics: List[str] = ["arrivals", "occupancy", "spending"]
    group_by: str = "month"
    
class PremiumReportRequest(BaseModel):
    email: str
    business_name: str
    business_type: BusinessType
    island: Island
    report_type: str = "comprehensive"
    custom_parameters: Optional[Dict[str, Any]] = None