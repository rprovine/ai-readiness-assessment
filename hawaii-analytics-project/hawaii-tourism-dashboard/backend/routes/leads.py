from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Dict

from config.database import get_db, BusinessLeadDB
from models.data_models import BusinessLead, PremiumReportRequest
from utils.email_sender import EmailSender

router = APIRouter()

@router.post("/capture")
async def capture_lead(
    lead: BusinessLead,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Capture a new business lead"""
    try:
        existing_lead = db.query(BusinessLeadDB).filter(
            BusinessLeadDB.email == lead.email
        ).first()
        
        if existing_lead:
            existing_lead.last_contacted = datetime.utcnow()
            existing_lead.interest_areas = list(set(existing_lead.interest_areas + lead.interest_areas))
        else:
            db_lead = BusinessLeadDB(
                email=lead.email,
                business_name=lead.business_name,
                business_type=lead.business_type.value,
                island=lead.island.value,
                contact_name=lead.contact_name,
                phone=lead.phone,
                interest_areas=lead.interest_areas,
                source=lead.source
            )
            db.add(db_lead)
        
        db.commit()
        
        email_sender = EmailSender()
        background_tasks.add_task(
            email_sender.send_welcome_email,
            lead.email,
            lead.contact_name,
            lead.business_type.value,
            lead.island.value
        )
        
        return {
            "status": "success",
            "message": "Thank you for your interest! Check your email for Hawaii tourism insights."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/request-report")
async def request_premium_report(
    request: PremiumReportRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Request a premium custom report"""
    try:
        lead = BusinessLead(
            email=request.email,
            business_name=request.business_name,
            business_type=request.business_type,
            island=request.island,
            contact_name=request.business_name,
            interest_areas=["premium_report", request.report_type]
        )
        
        await capture_lead(lead, background_tasks, db)
        
        email_sender = EmailSender()
        background_tasks.add_task(
            email_sender.send_report_request_confirmation,
            request.email,
            request.business_name,
            request.report_type
        )
        
        return {
            "status": "success",
            "message": "Your custom report request has been received. We'll email you within 24 hours."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/download-sample-report")
async def download_sample_report():
    """Provide a sample report to capture leads"""
    return {
        "download_url": "/api/leads/sample-report.pdf",
        "message": "Please provide your contact information to download the Hawaii Tourism Insights Report"
    }

@router.post("/newsletter-signup")
async def newsletter_signup(
    email: str,
    name: str,
    business_type: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Sign up for weekly Hawaii tourism newsletter"""
    try:
        lead = BusinessLead(
            email=email,
            contact_name=name,
            business_type=business_type,
            island="Oahu",
            interest_areas=["newsletter"]
        )
        
        await capture_lead(lead, background_tasks, db)
        
        return {
            "status": "success",
            "message": "You're subscribed to our weekly Hawaii Tourism Intelligence newsletter!"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/consultation-request")
async def request_consultation(
    lead_data: Dict,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Request a consultation based on tourism data insights"""
    try:
        lead = BusinessLead(
            email=lead_data["email"],
            business_name=lead_data.get("business_name"),
            business_type=lead_data["business_type"],
            island=lead_data["island"],
            contact_name=lead_data["contact_name"],
            phone=lead_data.get("phone"),
            interest_areas=["consultation", lead_data.get("consultation_topic", "general")]
        )
        
        await capture_lead(lead, background_tasks, db)
        
        email_sender = EmailSender()
        background_tasks.add_task(
            email_sender.send_consultation_booking,
            lead.email,
            lead.contact_name,
            lead_data.get("preferred_time")
        )
        
        return {
            "status": "success",
            "message": "Consultation request received! We'll contact you within 1 business day to schedule."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))