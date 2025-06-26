import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date, timedelta
import requests
from typing import Dict, List

st.set_page_config(
    page_title="Hawaii Tourism Analytics Dashboard",
    page_icon="🌺",
    layout="wide",
    initial_sidebar_state="expanded"
)

API_BASE_URL = "http://localhost:8000/api"

def fetch_dashboard_metrics():
    """Fetch main dashboard metrics from API"""
    try:
        response = requests.get(f"{API_BASE_URL}/dashboard/metrics")
        return response.json()
    except:
        return None

def fetch_visitor_trends(days: int, island: str = None):
    """Fetch visitor trend data"""
    params = {"days": days}
    if island:
        params["island"] = island
    try:
        response = requests.get(f"{API_BASE_URL}/dashboard/visitor-trends", params=params)
        return response.json()
    except:
        return None

def fetch_occupancy_trends(days: int, island: str = None):
    """Fetch occupancy trend data"""
    params = {"days": days}
    if island:
        params["island"] = island
    try:
        response = requests.get(f"{API_BASE_URL}/dashboard/occupancy-trends", params=params)
        return response.json()
    except:
        return None

def main():
    st.title("🌺 Hawaii Tourism Analytics Dashboard")
    st.markdown("### Real-time insights for Hawaii businesses")
    
    with st.sidebar:
        st.image("https://via.placeholder.com/300x100/0066CC/FFFFFF?text=Kointyme+Hawaii", use_column_width=True)
        st.markdown("---")
        
        st.markdown("### 📊 Dashboard Controls")
        selected_island = st.selectbox(
            "Select Island",
            ["All Islands", "Oahu", "Maui", "Kauai", "Hawaii", "Molokai", "Lanai"]
        )
        
        time_range = st.selectbox(
            "Time Range",
            ["Last 30 Days", "Last 90 Days", "Last 6 Months", "Last Year"]
        )
        
        days_map = {
            "Last 30 Days": 30,
            "Last 90 Days": 90,
            "Last 6 Months": 180,
            "Last Year": 365
        }
        selected_days = days_map[time_range]
        
        st.markdown("---")
        st.markdown("### 💡 Get Premium Insights")
        
        with st.form("lead_capture"):
            st.markdown("**Unlock full analytics & forecasts**")
            email = st.text_input("Email Address")
            business_name = st.text_input("Business Name")
            business_type = st.selectbox(
                "Business Type",
                ["Hotel", "Restaurant", "Tour Operator", "Retail", "Transportation", "Other"]
            )
            
            if st.form_submit_button("Get Premium Access", type="primary"):
                if email and business_name:
                    st.success("🎉 Check your email for premium access details!")
                    st.balloons()
    
    metrics = fetch_dashboard_metrics()
    
    if metrics:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Current Month Arrivals",
                f"{metrics['current_month_arrivals']:,}",
                f"{((metrics['current_month_arrivals'] - metrics['previous_month_arrivals']) / metrics['previous_month_arrivals'] * 100):.1f}%"
            )
        
        with col2:
            st.metric(
                "YoY Growth",
                f"{metrics['yoy_growth_rate']:.1f}%",
                "vs same month last year"
            )
        
        with col3:
            st.metric(
                "YTD Arrivals",
                f"{metrics['ytd_arrivals']:,}"
            )
        
        with col4:
            avg_occupancy = sum(metrics['occupancy_by_island'].values()) / len(metrics['occupancy_by_island'])
            st.metric(
                "Avg Occupancy",
                f"{avg_occupancy:.1f}%"
            )
    
    tab1, tab2, tab3, tab4 = st.tabs(["📈 Visitor Trends", "🏨 Hotel Analytics", "🌍 Origin Analysis", "🔮 Forecasts"])
    
    with tab1:
        st.markdown("### Visitor Arrival Trends")
        
        island_filter = None if selected_island == "All Islands" else selected_island
        visitor_data = fetch_visitor_trends(selected_days, island_filter)
        
        if visitor_data:
            fig = px.line(
                x=visitor_data['dates'],
                y=visitor_data['arrivals'],
                title=f"Daily Visitor Arrivals - {visitor_data['island']}",
                labels={'x': 'Date', 'y': 'Arrivals'}
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
            
            col1, col2 = st.columns(2)
            
            with col1:
                if metrics and metrics['top_origin_states']:
                    st.markdown("### Top Origin States")
                    origin_df = pd.DataFrame(metrics['top_origin_states'])
                    fig_pie = px.pie(
                        origin_df,
                        values='arrivals',
                        names='state',
                        title="Visitor Origins This Month"
                    )
                    st.plotly_chart(fig_pie, use_container_width=True)
            
            with col2:
                st.markdown("### 🔒 Premium Features")
                st.info("""
                **Unlock Advanced Analytics:**
                - Detailed origin market analysis
                - Seasonal pattern predictions
                - Custom date range reports
                - API access for your systems
                - Weekly email insights
                
                👉 Fill out the form in the sidebar to get started!
                """)
    
    with tab2:
        st.markdown("### Hotel Performance Analytics")
        
        occupancy_data = fetch_occupancy_trends(selected_days, island_filter)
        
        if occupancy_data:
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=occupancy_data['dates'],
                y=occupancy_data['occupancy_rates'],
                name='Occupancy %',
                yaxis='y'
            ))
            fig.add_trace(go.Scatter(
                x=occupancy_data['dates'],
                y=occupancy_data['adr_values'],
                name='ADR ($)',
                yaxis='y2'
            ))
            
            fig.update_xaxes(title_text="Date")
            fig.update_yaxes(title_text="Occupancy %", secondary_y=False)
            fig.update_yaxes(title_text="ADR ($)", secondary_y=True)
            fig.update_layout(
                title=f"Hotel Performance - {occupancy_data['island']}",
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        if metrics and metrics['occupancy_by_island']:
            st.markdown("### Occupancy by Island")
            island_df = pd.DataFrame(
                [(k, v) for k, v in metrics['occupancy_by_island'].items()],
                columns=['Island', 'Occupancy %']
            )
            
            fig_bar = px.bar(
                island_df,
                x='Island',
                y='Occupancy %',
                color='Occupancy %',
                color_continuous_scale='Blues',
                title="Current Month Average Occupancy"
            )
            st.plotly_chart(fig_bar, use_container_width=True)
    
    with tab3:
        st.markdown("### Visitor Origin Analysis")
        st.info("🔒 Premium feature: Detailed origin market analysis with demographic insights")
        
        sample_origins = pd.DataFrame({
            'State': ['California', 'Texas', 'Washington', 'Oregon', 'New York'],
            'Visitors': [45000, 28000, 22000, 18000, 15000]
        })
        
        fig = px.bar(
            sample_origins,
            x='State',
            y='Visitors',
            title="Top Visitor Origins (Sample Data)"
        )
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("""
        **Get Full Access to:**
        - Complete origin market breakdown
        - Spending patterns by origin
        - Length of stay analysis
        - Seasonal variations by market
        - Custom reports for your business
        """)
    
    with tab4:
        st.markdown("### 🔮 Tourism Forecasting")
        st.warning("⚡ Premium Feature - See what's coming for your business")
        
        sample_forecast = pd.DataFrame({
            'Date': pd.date_range(start=date.today(), periods=90, freq='D'),
            'Predicted': [50000 + i * 100 + (i % 7) * 1000 for i in range(90)],
            'Upper': [52000 + i * 100 + (i % 7) * 1000 for i in range(90)],
            'Lower': [48000 + i * 100 + (i % 7) * 1000 for i in range(90)]
        })
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=sample_forecast['Date'],
            y=sample_forecast['Predicted'],
            name='Forecast',
            line=dict(color='blue')
        ))
        fig.add_trace(go.Scatter(
            x=sample_forecast['Date'],
            y=sample_forecast['Upper'],
            fill=None,
            mode='lines',
            line_color='rgba(0,0,0,0)',
            showlegend=False
        ))
        fig.add_trace(go.Scatter(
            x=sample_forecast['Date'],
            y=sample_forecast['Lower'],
            fill='tonexty',
            mode='lines',
            line_color='rgba(0,0,0,0)',
            name='Confidence Interval'
        ))
        
        fig.update_layout(
            title="90-Day Visitor Arrival Forecast (Sample)",
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("**🎯 Predictive Models**")
            st.markdown("- ARIMA & Prophet models")
            st.markdown("- 95% confidence intervals")
            st.markdown("- Seasonal adjustments")
        
        with col2:
            st.markdown("**📊 Business Impact**")
            st.markdown("- Revenue projections")
            st.markdown("- Staffing recommendations")
            st.markdown("- Inventory planning")
        
        with col3:
            st.markdown("**📧 Custom Reports**")
            st.markdown("- Weekly forecasts")
            st.markdown("- Market alerts")
            st.markdown("- Competitor insights")
    
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: #666;'>
        <p>Powered by Kointyme AI Consulting | Real-time Hawaii Tourism Data</p>
        <p>Questions? Contact us at insights@kointyme-hawaii-tourism.com</p>
        </div>
        """,
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()