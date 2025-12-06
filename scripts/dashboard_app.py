"""
Executive Sales Monitoring Dashboard
A complete example of a leadership dashboard using Streamlit

Run with: streamlit run dashboard_app.py
"""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta
import sys

# Import our modules
from snowflake_connection import SnowflakeConnection
from snowflake_analytics import SnowflakeAnalytics


# Page configuration
st.set_page_config(
    page_title="Sales Monitoring Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #1f77b4;
    }
    .stMetric {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 5px;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def get_snowflake_connection():
    """Initialize Snowflake connection (cached)"""
    try:
        sf = SnowflakeConnection()
        return sf
    except Exception as e:
        st.error(f"Connection failed: {str(e)}")
        st.info("Please set your Snowflake credentials as environment variables")
        return None


@st.cache_data(ttl=300)  # Cache for 5 minutes
def load_kpi_data(_analytics, days):
    """Load KPI data with caching"""
    return _analytics.get_kpi_comparison(current_days=days)


@st.cache_data(ttl=300)
def load_trend_data(_analytics, metric, period, days):
    """Load trend data with caching"""
    return _analytics.get_time_series(metric=metric, period=period, lookback_days=days)


@st.cache_data(ttl=600)  # Cache for 10 minutes
def load_segment_data(_analytics):
    """Load customer segment data with caching"""
    return _analytics.get_customer_segments()


@st.cache_data(ttl=600)
def load_regional_data(_analytics):
    """Load regional performance data with caching"""
    return _analytics.get_regional_performance()


def format_number(num):
    """Format large numbers for display"""
    if num >= 1_000_000:
        return f"${num/1_000_000:.2f}M"
    elif num >= 1_000:
        return f"${num/1_000:.1f}K"
    else:
        return f"${num:.2f}"


def format_percent(num):
    """Format percentage with color"""
    if num > 0:
        return f"+{num:.1f}%"
    else:
        return f"{num:.1f}%"


def main():
    """Main dashboard application"""
    
    # Title and description
    st.title("📊 Executive Sales Monitoring Dashboard")
    st.markdown("Real-time monitoring and analytics for leadership decision-making")
    st.markdown("---")
    
    # Initialize connection
    sf_conn = get_snowflake_connection()
    
    if sf_conn is None:
        st.stop()
    
    # Initialize analytics
    analytics = SnowflakeAnalytics(sf_conn)
    
    # Sidebar filters
    st.sidebar.header("⚙️ Dashboard Controls")
    
    # Date range selector
    lookback_days = st.sidebar.selectbox(
        "Time Period",
        options=[7, 14, 30, 60, 90],
        index=2,
        format_func=lambda x: f"Last {x} days"
    )
    
    # Metric selector for trends
    metric_choice = st.sidebar.selectbox(
        "Primary Metric",
        options=['revenue', 'orders', 'customers', 'aov'],
        format_func=lambda x: x.upper().replace('_', ' ')
    )
    
    # Period granularity
    period_choice = st.sidebar.selectbox(
        "Trend Granularity",
        options=['day', 'week', 'month'],
        format_func=lambda x: x.title()
    )
    
    # Refresh button
    if st.sidebar.button("🔄 Refresh Data"):
        st.cache_data.clear()
        st.rerun()
    
    st.sidebar.markdown("---")
    st.sidebar.info("💡 **Tip**: Data is cached for 5 minutes for performance")
    
    # ========================================
    # KPI CARDS SECTION
    # ========================================
    st.header("Key Performance Indicators")
    
    try:
        # Load KPI comparison data
        kpi_data = load_kpi_data(analytics, lookback_days)
        
        if not kpi_data.empty:
            row = kpi_data.iloc[0]
            
            # Display metrics in columns
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    label="💰 Total Revenue",
                    value=format_number(row['CURRENT_REVENUE']),
                    delta=format_percent(row['REVENUE_CHANGE_PCT']),
                    delta_color="normal"
                )
            
            with col2:
                st.metric(
                    label="📦 Total Orders",
                    value=f"{int(row['CURRENT_ORDERS']):,}",
                    delta=format_percent(row['ORDERS_CHANGE_PCT']),
                    delta_color="normal"
                )
            
            with col3:
                st.metric(
                    label="👥 Active Customers",
                    value=f"{int(row['CURRENT_CUSTOMERS']):,}",
                    delta=format_percent(row['CUSTOMERS_CHANGE_PCT']),
                    delta_color="normal"
                )
            
            with col4:
                st.metric(
                    label="🎯 Avg Order Value",
                    value=f"${row['CURRENT_AOV']:,.2f}",
                    delta=format_percent(row['AOV_CHANGE_PCT']),
                    delta_color="normal"
                )
        
    except Exception as e:
        st.error(f"Error loading KPIs: {str(e)}")
    
    st.markdown("---")
    
    # ========================================
    # TREND ANALYSIS SECTION
    # ========================================
    st.header(f"📈 {metric_choice.upper()} Trend Analysis")
    
    try:
        trend_data = load_trend_data(analytics, metric_choice, period_choice, lookback_days)
        
        if not trend_data.empty:
            # Create interactive line chart
            fig_trend = go.Figure()
            
            fig_trend.add_trace(go.Scatter(
                x=trend_data['PERIOD_DATE'],
                y=trend_data['METRIC_VALUE'],
                mode='lines+markers',
                name=metric_choice.title(),
                line=dict(color='#1f77b4', width=3),
                marker=dict(size=8),
                hovertemplate='<b>%{x}</b><br>Value: %{y:,.2f}<extra></extra>'
            ))
            
            fig_trend.update_layout(
                title=f"{metric_choice.title()} Over Time",
                xaxis_title="Date",
                yaxis_title=metric_choice.title(),
                hovermode='x unified',
                height=400,
                showlegend=True,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
            )
            
            st.plotly_chart(fig_trend, use_container_width=True)
            
            # Show statistics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.info(f"**Average**: {trend_data['METRIC_VALUE'].mean():,.2f}")
            with col2:
                st.info(f"**Maximum**: {trend_data['METRIC_VALUE'].max():,.2f}")
            with col3:
                st.info(f"**Minimum**: {trend_data['METRIC_VALUE'].min():,.2f}")
        
    except Exception as e:
        st.error(f"Error loading trend data: {str(e)}")
    
    st.markdown("---")
    
    # ========================================
    # CUSTOMER INSIGHTS SECTION
    # ========================================
    st.header("👥 Customer Insights")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Customer Segmentation")
        try:
            segment_data = load_segment_data(analytics)
            
            if not segment_data.empty:
                # Pie chart for customer distribution
                fig_pie = px.pie(
                    segment_data,
                    values='CUSTOMER_COUNT',
                    names='SEGMENT',
                    title='Customers by Segment',
                    color_discrete_sequence=px.colors.qualitative.Set3
                )
                fig_pie.update_traces(textposition='inside', textinfo='percent+label')
                st.plotly_chart(fig_pie, use_container_width=True)
                
                # Show segment table
                st.dataframe(
                    segment_data[['SEGMENT', 'CUSTOMER_COUNT', 'AVG_LIFETIME_VALUE']].style.format({
                        'CUSTOMER_COUNT': '{:,.0f}',
                        'AVG_LIFETIME_VALUE': '${:,.2f}'
                    }),
                    hide_index=True,
                    use_container_width=True
                )
        
        except Exception as e:
            st.error(f"Error loading segment data: {str(e)}")
    
    with col2:
        st.subheader("Revenue by Segment")
        try:
            if not segment_data.empty:
                # Bar chart for revenue
                fig_bar = px.bar(
                    segment_data,
                    x='SEGMENT',
                    y='TOTAL_SEGMENT_VALUE',
                    title='Total Revenue by Customer Segment',
                    color='TOTAL_SEGMENT_VALUE',
                    color_continuous_scale='Blues'
                )
                fig_bar.update_layout(showlegend=False, height=400)
                st.plotly_chart(fig_bar, use_container_width=True)
                
                # Key insight
                top_segment = segment_data.loc[segment_data['TOTAL_SEGMENT_VALUE'].idxmax()]
                st.success(f"""
                **Top Segment**: {top_segment['SEGMENT']}  
                **Revenue**: {format_number(top_segment['TOTAL_SEGMENT_VALUE'])}  
                **Customers**: {int(top_segment['CUSTOMER_COUNT']):,}
                """)
        
        except Exception as e:
            st.error(f"Error loading revenue data: {str(e)}")
    
    st.markdown("---")
    
    # ========================================
    # REGIONAL PERFORMANCE SECTION
    # ========================================
    st.header("🌍 Regional Performance")
    
    try:
        regional_data = load_regional_data(analytics)
        
        if not regional_data.empty:
            # Group by region
            region_summary = regional_data.groupby('REGION').agg({
                'ORDER_COUNT': 'sum',
                'TOTAL_REVENUE': 'sum',
                'UNIQUE_CUSTOMERS': 'sum'
            }).reset_index()
            
            # Create visualizations
            col1, col2 = st.columns(2)
            
            with col1:
                fig_region = px.bar(
                    region_summary,
                    x='REGION',
                    y='TOTAL_REVENUE',
                    title='Revenue by Region',
                    color='TOTAL_REVENUE',
                    color_continuous_scale='Viridis'
                )
                st.plotly_chart(fig_region, use_container_width=True)
            
            with col2:
                fig_orders = px.bar(
                    region_summary,
                    x='REGION',
                    y='ORDER_COUNT',
                    title='Orders by Region',
                    color='ORDER_COUNT',
                    color_continuous_scale='Cividis'
                )
                st.plotly_chart(fig_orders, use_container_width=True)
            
            # Detailed table by nation
            st.subheader("Detailed Performance by Nation")
            st.dataframe(
                regional_data.sort_values('TOTAL_REVENUE', ascending=False).style.format({
                    'ORDER_COUNT': '{:,.0f}',
                    'TOTAL_REVENUE': '${:,.2f}',
                    'AVG_ORDER_VALUE': '${:,.2f}',
                    'UNIQUE_CUSTOMERS': '{:,.0f}'
                }),
                hide_index=True,
                use_container_width=True
            )
    
    except Exception as e:
        st.error(f"Error loading regional data: {str(e)}")
    
    st.markdown("---")
    
    # ========================================
    # ANOMALY DETECTION SECTION
    # ========================================
    with st.expander("🚨 Anomaly Detection", expanded=False):
        st.subheader("Recent Anomalies and Alerts")
        
        try:
            anomalies = analytics.detect_anomalies(metric='orders', lookback_days=lookback_days)
            
            if not anomalies.empty:
                # Filter for anomalies only
                alerts = anomalies[anomalies['STATUS'].isin(['ANOMALY', 'WARNING'])]
                
                if not alerts.empty:
                    st.warning(f"⚠️ Found {len(alerts)} anomalies in the last {lookback_days} days")
                    
                    # Display anomalies
                    st.dataframe(
                        alerts[['METRIC_DATE', 'METRIC_VALUE', 'Z_SCORE', 'STATUS', 'DIRECTION']].style.format({
                            'METRIC_VALUE': '{:,.0f}',
                            'Z_SCORE': '{:.2f}'
                        }),
                        hide_index=True,
                        use_container_width=True
                    )
                    
                    # Visualization
                    fig_anomaly = go.Figure()
                    
                    # Normal data
                    normal = anomalies[anomalies['STATUS'] == 'NORMAL']
                    fig_anomaly.add_trace(go.Scatter(
                        x=normal['METRIC_DATE'],
                        y=normal['METRIC_VALUE'],
                        mode='markers',
                        name='Normal',
                        marker=dict(color='green', size=6)
                    ))
                    
                    # Anomalies
                    if not alerts.empty:
                        fig_anomaly.add_trace(go.Scatter(
                            x=alerts['METRIC_DATE'],
                            y=alerts['METRIC_VALUE'],
                            mode='markers',
                            name='Anomaly',
                            marker=dict(color='red', size=12, symbol='x')
                        ))
                    
                    fig_anomaly.update_layout(
                        title='Anomaly Detection Over Time',
                        xaxis_title='Date',
                        yaxis_title='Metric Value',
                        height=400
                    )
                    
                    st.plotly_chart(fig_anomaly, use_container_width=True)
                else:
                    st.success("✅ No anomalies detected - all metrics are within normal ranges")
        
        except Exception as e:
            st.error(f"Error in anomaly detection: {str(e)}")
    
    # Footer
    st.markdown("---")
    st.caption(f"""
    Dashboard last refreshed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
    Data source: Snowflake TPCH Sample Database  
    Showing data for last {lookback_days} days
    """)


if __name__ == "__main__":
    main()
