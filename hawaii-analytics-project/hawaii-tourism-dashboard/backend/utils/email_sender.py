import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, date
from typing import List, Dict, Optional
import os

from config.settings import settings

class EmailSender:
    def __init__(self):
        self.smtp_host = settings.email_smtp_host
        self.smtp_port = settings.email_smtp_port
        self.username = settings.email_username
        self.password = settings.email_password
        self.from_email = settings.email_from
        
    async def send_welcome_email(self, to_email: str, contact_name: str, business_type: str, island: str):
        """Send welcome email to new lead"""
        subject = "Welcome to Hawaii Tourism Analytics - Your Business Insights Await!"
        
        html_content = f"""
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h1 style="color: #0066CC;">Aloha {contact_name}! <:</h1>
                    
                    <p>Thank you for your interest in Hawaii Tourism Analytics. As a {business_type} business on {island}, 
                    you're perfectly positioned to benefit from our real-time tourism insights.</p>
                    
                    <h2 style="color: #0066CC;">Here's What You Get:</h2>
                    <ul>
                        <li><strong>Real-time Visitor Data:</strong> See exactly how many tourists are arriving on {island}</li>
                        <li><strong>Predictive Analytics:</strong> Plan ahead with our 90-day visitor forecasts</li>
                        <li><strong>Origin Insights:</strong> Know where your customers are coming from</li>
                        <li><strong>Business Impact Calculator:</strong> Estimate revenue based on tourism trends</li>
                    </ul>
                    
                    <h2 style="color: #0066CC;">Quick Tourism Snapshot for {island}:</h2>
                    <div style="background-color: #f5f5f5; padding: 15px; border-radius: 5px;">
                        <p><strong>Current Month Visitors:</strong> 125,000+ (� 15% YoY)</p>
                        <p><strong>Average Hotel Occupancy:</strong> 78%</p>
                        <p><strong>Top Visitor Origin:</strong> California (35%)</p>
                        <p><strong>Next 30 Days Forecast:</strong> Strong growth expected</p>
                    </div>
                    
                    <h2 style="color: #0066CC;">Your Next Steps:</h2>
                    <ol>
                        <li>Access your dashboard: <a href="https://dashboard.kointyme-hawaii-tourism.com">Login Here</a></li>
                        <li>Schedule a free consultation to discuss your specific needs</li>
                        <li>Join our weekly Hawaii Business Intelligence webinar</li>
                    </ol>
                    
                    <div style="background-color: #0066CC; color: white; padding: 20px; border-radius: 5px; text-align: center; margin-top: 30px;">
                        <h3>Ready to Grow Your Business?</h3>
                        <p>Get your full custom report with detailed forecasts and recommendations.</p>
                        <a href="https://dashboard.kointyme-hawaii-tourism.com/premium" 
                           style="background-color: white; color: #0066CC; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block;">
                           Get Premium Access
                        </a>
                    </div>
                    
                    <p style="margin-top: 30px;">Questions? Reply to this email or call us at (808) 555-0123</p>
                    
                    <p>Mahalo,<br>
                    The Kointyme Hawaii Tourism Analytics Team</p>
                </div>
            </body>
        </html>
        """
        
        await self.send_email(to_email, subject, html_content)
    
    async def send_report_request_confirmation(self, to_email: str, business_name: str, report_type: str):
        """Confirm premium report request"""
        subject = "Your Hawaii Tourism Report Request Received"
        
        html_content = f"""
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h1 style="color: #0066CC;">Report Request Confirmed! =�</h1>
                    
                    <p>Thank you for requesting a {report_type} report for {business_name}.</p>
                    
                    <h2>What Happens Next:</h2>
                    <ol>
                        <li>Our analytics team will prepare your custom report within 24 hours</li>
                        <li>You'll receive detailed insights specific to your business</li>
                        <li>We'll include actionable recommendations based on current trends</li>
                    </ol>
                    
                    <h2>Your Report Will Include:</h2>
                    <ul>
                        <li>90-day visitor arrival forecasts for your island</li>
                        <li>Competitor analysis and market positioning</li>
                        <li>Revenue impact projections</li>
                        <li>Custom recommendations for your business type</li>
                        <li>Seasonal trends and peak period analysis</li>
                    </ul>
                    
                    <p>Need it sooner? Call us at (808) 555-0123 for expedited service.</p>
                    
                    <p>Mahalo,<br>
                    The Kointyme Analytics Team</p>
                </div>
            </body>
        </html>
        """
        
        await self.send_email(to_email, subject, html_content)
    
    async def send_consultation_booking(self, to_email: str, contact_name: str, preferred_time: Optional[str]):
        """Send consultation booking confirmation"""
        subject = "Hawaii Tourism Consultation - Let's Grow Your Business"
        
        time_info = f"Preferred time: {preferred_time}" if preferred_time else "We'll contact you to schedule"
        
        html_content = f"""
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h1 style="color: #0066CC;">Consultation Request Received! ></h1>
                    
                    <p>Aloha {contact_name},</p>
                    
                    <p>We're excited to help you leverage Hawaii tourism data to grow your business!</p>
                    
                    <h2>What We'll Cover:</h2>
                    <ul>
                        <li>Review current tourism trends affecting your business</li>
                        <li>Analyze your competitive position</li>
                        <li>Identify growth opportunities based on visitor patterns</li>
                        <li>Create a data-driven action plan</li>
                        <li>Set up custom alerts for your business</li>
                    </ul>
                    
                    <p><strong>{time_info}</strong></p>
                    
                    <p>Our team will call you within 1 business day to confirm the consultation.</p>
                    
                    <p>In the meantime, <a href="https://dashboard.kointyme-hawaii-tourism.com">explore our dashboard</a> 
                    to see the latest tourism trends.</p>
                    
                    <p>Looking forward to speaking with you!</p>
                    
                    <p>Mahalo,<br>
                    The Kointyme Team</p>
                </div>
            </body>
        </html>
        """
        
        await self.send_email(to_email, subject, html_content)
    
    async def send_weekly_newsletter(self, subscribers: List[Dict]):
        """Send weekly Hawaii tourism intelligence newsletter"""
        subject = f"Hawaii Tourism Weekly: Insights for {date.today().strftime('%B %d, %Y')}"
        
        for subscriber in subscribers:
            html_content = f"""
            <html>
                <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                        <h1 style="color: #0066CC;">Hawaii Tourism Weekly Intelligence <4</h1>
                        
                        <h2>This Week's Highlights:</h2>
                        
                        <div style="background-color: #f5f5f5; padding: 15px; border-radius: 5px; margin: 10px 0;">
                            <h3>=� Visitor Arrivals Up 12%</h3>
                            <p>Total arrivals reached 285,000 this week, with strong growth from West Coast markets.</p>
                        </div>
                        
                        <div style="background-color: #f5f5f5; padding: 15px; border-radius: 5px; margin: 10px 0;">
                            <h3><� Hotel Occupancy at 82%</h3>
                            <p>Maui and Oahu leading with 85%+ occupancy. ADR up $25 compared to last year.</p>
                        </div>
                        
                        <div style="background-color: #f5f5f5; padding: 15px; border-radius: 5px; margin: 10px 0;">
                            <h3> New Flight Routes Announced</h3>
                            <p>United adding daily Denver-Kona service starting December.</p>
                        </div>
                        
                        <h2>Island Spotlight: {subscriber.get('island', 'Oahu')}</h2>
                        <ul>
                            <li>Weekly visitors: 45,000 (� 8%)</li>
                            <li>Top activities: Snorkeling, hiking, dining</li>
                            <li>Business opportunity: Growing demand for eco-tours</li>
                        </ul>
                        
                        <h2>30-Day Forecast:</h2>
                        <p>Our models predict continued strong performance with 15% YoY growth expected. 
                        Peak days anticipated around month-end holidays.</p>
                        
                        <div style="background-color: #0066CC; color: white; padding: 20px; border-radius: 5px; text-align: center; margin-top: 30px;">
                            <h3>Get Your Custom Business Report</h3>
                            <a href="https://dashboard.kointyme-hawaii-tourism.com/request-report" 
                               style="background-color: white; color: #0066CC; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block;">
                               Request Report
                            </a>
                        </div>
                        
                        <p style="font-size: 12px; color: #666; margin-top: 30px;">
                        You're receiving this because you subscribed to Hawaii Tourism Intelligence. 
                        <a href="#">Unsubscribe</a> | <a href="#">Update Preferences</a>
                        </p>
                    </div>
                </body>
            </html>
            """
            
            await self.send_email(subscriber['email'], subject, html_content)
    
    async def send_email(self, to_email: str, subject: str, html_content: str):
        """Send email using SMTP"""
        try:
            if not self.smtp_host or not self.username:
                print(f"Email configuration missing. Would send to {to_email}: {subject}")
                return
            
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.from_email
            msg['To'] = to_email
            
            html_part = MIMEText(html_content, 'html')
            msg.attach(html_part)
            
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.username, self.password)
                server.send_message(msg)
            
            print(f"Email sent successfully to {to_email}")
        except Exception as e:
            print(f"Error sending email to {to_email}: {e}")