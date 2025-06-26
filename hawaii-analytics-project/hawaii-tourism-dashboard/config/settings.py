from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    app_name: str = "Hawaii Tourism Analytics"
    app_version: str = "1.0.0"
    
    database_url: str = "sqlite:///./hawaii_tourism.db"
    
    hta_base_url: str = "https://www.hawaiitourismauthority.org"
    
    email_smtp_host: Optional[str] = None
    email_smtp_port: int = 587
    email_username: Optional[str] = None
    email_password: Optional[str] = None
    email_from: str = "insights@kointyme-hawaii-tourism.com"
    
    secret_key: str = "your-secret-key-here"
    
    redis_url: Optional[str] = None
    
    data_refresh_interval_hours: int = 24
    
    free_tier_limit_days: int = 30
    premium_tier_limit_days: int = 365
    
    ml_model_retrain_days: int = 7
    
    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()