from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    # App settings
    app_name: str = "Hawaii Tourism Analytics"
    app_version: str = "1.0.0"
    
    # Database
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./hawaii_tourism.db")
    
    # Email settings
    email_smtp_host: str = os.getenv("EMAIL_SMTP_HOST", "")
    email_smtp_port: int = int(os.getenv("EMAIL_SMTP_PORT", "587"))
    email_username: str = os.getenv("EMAIL_USERNAME", "")
    email_password: str = os.getenv("EMAIL_PASSWORD", "")
    email_from: str = os.getenv("EMAIL_FROM", "noreply@hawaiitourismanalytics.com")
    
    # API Keys (for future integrations)
    google_api_key: str = os.getenv("GOOGLE_API_KEY", "")
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    
    # Security
    secret_key: str = os.getenv("SECRET_KEY", "hawaii-tourism-secret-key-change-in-production")
    
    class Config:
        env_file = ".env"
        extra = "allow"

# Create settings instance
settings = Settings()