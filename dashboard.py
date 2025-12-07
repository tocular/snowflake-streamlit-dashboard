"""
Snowflake Analytics Dashboard
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
from dateutil.relativedelta import relativedelta

# Page Configuration
st.set_page_config(
    page_title="Snowflake Dashboard",
    page_icon="❄️",
    layout="wide",
)

# Load Data Function with caching
@st.cache_data(ttl=3600)
def load_data():
    """Load revenue trend data"""
    try:
        df = pd.read_csv('tables/revenue_trend.csv')
        df['month'] = pd.to_datetime(df['month'])
        return df, None
    except Exception as e:
        return None, str(e)

@st.cache_data(ttl=3600)
def load_product_data():
    """Load product revenue by country data"""
    try:
        # Try compressed version first (for deployment)
        try:
            df = pd.read_csv('tables/product_revenue_by_country.csv.gz', compression='gzip')
        except FileNotFoundError:
            # Fallback to uncompressed (for local development)
            df = pd.read_csv('tables/product_revenue_by_country.csv')
        df['month'] = pd.to_datetime(df['month'])
        return df, None
    except Exception as e:
        return None, str(e)

@st.cache_data(ttl=3600)
def load_geographic_anomaly_data():
    """Load geographic anomaly detection data"""
    try:
        df = pd.read_csv('tables/geographic_anomalies.csv')
        df['month'] = pd.to_datetime(df['month'])
        return df, None
    except Exception as e:
        return None, str(e)

def filter_data_by_timerange(df, timerange):
    """Filter dataframe based on selected time range"""
    if df is None or len(df) == 0:
        return df

    latest_date = df['month'].max()

    if timerange == "All":
        return df
    elif timerange == "1M":
        start_date = latest_date - relativedelta(months=1)
    elif timerange == "3M":
        start_date = latest_date - relativedelta(months=3)
    elif timerange == "6M":
        start_date = latest_date - relativedelta(months=6)
    elif timerange == "1Y":
        start_date = latest_date - relativedelta(years=1)
    elif timerange == "2Y":
        start_date = latest_date - relativedelta(years=2)
    else:
        return df

    return df[df['month'] >= start_date]

def format_currency(value):
    """Format large numbers as currency with B/M suffix"""
    if value >= 1e9:
        return f"${value/1e9:.2f}B"
    elif value >= 1e6:
        return f"${value/1e6:.1f}M"
    else:
        return f"${value:,.0f}"

def build_anomaly_hover_text(row):
    """Build hover text for a single anomaly data row."""
    text = (
        f"<b>{row['country']}</b><br>"
        f"Anomaly Score: {row['anomaly_score']:.1f}/100<br>"
        f"Severity: {row['anomaly_severity']}<br>"
        f"<br>"
        f"Revenue: ${row['total_revenue']:,.0f}<br>"
        f"Revenue Z-Score: {row['revenue_zscore']:.2f}<br>"
        f"Orders: {row['order_count']:,}<br>"
        f"Customers: {row['unique_customers']:,}<br>"
    )
    if pd.notna(row['revenue_mom_change']):
        text += f"MoM Revenue Change: {row['revenue_mom_change']:.1f}%<br>"
    text += f"<br><b>Anomalies:</b> {row['anomaly_types']}"
    return text


def create_geographic_anomaly_map(df, selected_month):
    """Create choropleth map showing geographic anomalies for a given month."""

    # Filter to selected month
    map_data = df[df['month'] == selected_month].copy()

    if len(map_data) == 0:
        return None

    map_data['hover_text'] = map_data.apply(build_anomaly_hover_text, axis=1)

    # Create choropleth map
    fig = go.Figure(data=go.Choropleth(
        locations=map_data['country_code'],
        z=map_data['anomaly_score'],
        text=map_data['hover_text'],
        hovertemplate='%{text}<extra></extra>',
        colorscale=[
            [0.0, '#2E86AB'],    # Dark blue (normal)
            [0.2, '#A6D1E6'],    # Light blue
            [0.4, '#FFD93D'],    # Yellow (minor)
            [0.6, '#FF8C42'],    # Orange (moderate)
            [1.0, '#D62828']     # Red (severe)
        ],
        zmin=0,
        zmax=100,
        marker_line_color='white',
        marker_line_width=0.5,
        colorbar=dict(
            title=dict(text="Anomaly Score", font=dict(size=11)),
            thickness=12,
            len=0.9,
            orientation='v',
            x=1.0,
            xanchor='left',
            y=0.5,
            yanchor='middle',
            tickvals=[12.5, 37.5, 62.5, 87.5],
            ticktext=['Normal', 'Minor', 'Moderate', 'Severe'],
            tickfont=dict(size=10)
        )
    ))

    # Update layout - compact design with fixed aspect ratio
    fig.update_layout(
        title={
            'text': f'Geographic Anomaly Detection<br><span style="font-size: 14px; color: #888;">{selected_month.strftime("%B %Y")}</span>',
            'font': {'size': 20}
        },
        geo=dict(
            projection_type='natural earth',
            showland=True,
            landcolor='#1a1a1a',
            showocean=True,
            oceancolor='#0a0a0a',
            showcountries=True,
            countrycolor='#333',
            showlakes=False,
            showframe=False,
            bgcolor='rgba(0,0,0,0)',
            # Crop to focus on data regions (eliminates polar negative space)
            lataxis=dict(range=[-50, 70]),
            lonaxis=dict(range=[-125, 155]),
            # Push map down to create space below title
            domain=dict(x=[0, 1], y=[0, 0.92])
        ),
        height=420,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=0, r=40, t=70, b=0),
        # Lock the aspect ratio so it renders identically everywhere
        autosize=False
    )

    return fig

def main():
    # Header
    st.title("❄️ Snowflake Dashboard")
    st.caption("Dashboard charting data from Snowflake's sample TPC-H dataset. The database simulates an industrials firm with a global customer base in the 1990s")

    # ========================================
    # NAVIGATION SIDEBAR
    # ========================================

    # Custom CSS for sidebar styling
    st.markdown("""
        <style>
        /* Sidebar background and border */
        [data-testid="stSidebar"] {
            background-color: #0e1117;
            border-right: 1px solid #262730;
        }
        [data-testid="stSidebar"] > div:first-child {
            background-color: #0e1117;
        }
        /* Navigation link styling */
        .nav-link, .nav-link:visited, .nav-link:active {
            display: block;
            padding: 12px 16px;
            margin: 8px 0;
            background-color: transparent;
            border: 1px solid #262730;
            border-radius: 8px;
            color: #ffffff !important;
            text-decoration: none !important;
            font-size: 14px;
            transition: all 0.3s ease;
        }
        .nav-link:hover {
            border-color: #1f77b4;
            background-color: #1a1d24;
            color: #ffffff !important;
            text-decoration: none !important;
        }
        </style>
    """, unsafe_allow_html=True)

    # Sidebar navigation
    with st.sidebar:
        st.markdown("# ❄️  Navigation")
        st.markdown("""
            <a class="nav-link" href="#geographic-anomaly-detection">Geographic Anomalies</a>
            <a class="nav-link" href="#product-revenue">Product Revenue</a>
            <a class="nav-link" href="#monthly-revenue-time-series">Revenue Trends</a>
            <a class="nav-link" href="#raw-data">Raw Data</a>
        """, unsafe_allow_html=True)

    # ========================================
    # GEOGRAPHIC ANOMALY DETECTION
    # ========================================

    # First chart: Geographic Anomaly Detection
    st.subheader("Geographic Anomaly Detection")
    st.caption("Flagging unusual patterns in country-level performance")
    st.markdown("<br>", unsafe_allow_html=True)

    # Load anomaly data
    with st.spinner("Loading geographic anomaly data..."):
        anomaly_data, anomaly_error = load_geographic_anomaly_data()

    if anomaly_error:
        st.error(f"Error loading anomaly data: {anomaly_error}")
        st.info("Please run the dashboard.ipynb notebook to generate the anomaly detection data.")
    else:
        # Layout: 1:3 ratio like existing charts
        anomaly_cols = st.columns([1, 3], vertical_alignment="top")

        # Prepare month data for slider
        available_months = sorted(anomaly_data['month'].unique())
        month_labels = [m.strftime("%B %Y") for m in available_months]

        # Initialize session state for slider if not exists
        if 'anomaly_month_index' not in st.session_state:
            st.session_state.anomaly_month_index = len(available_months) - 1  # Default to latest month

        selected_anomaly_month = available_months[st.session_state.anomaly_month_index]
        month_data = anomaly_data[anomaly_data['month'] == selected_anomaly_month]

        with anomaly_cols[0]:
            # Anomaly Summary container
            with st.container(border=True, height=350):
                st.markdown("**Anomaly Summary**")

                # Count anomalies by severity
                severe_count = len(month_data[month_data['anomaly_severity'] == 'Severe'])
                moderate_count = len(month_data[month_data['anomaly_severity'] == 'Moderate'])
                minor_count = len(month_data[month_data['anomaly_severity'] == 'Minor'])

                st.metric("Severe Anomalies", severe_count)
                st.metric("Moderate Anomalies", moderate_count)
                st.metric("Minor Anomalies", minor_count)

            # Top Anomaly container
            with st.container(border=True, height=174):
                st.markdown("**Top Anomaly**")
                if len(month_data) > 0:
                    top_anomaly = month_data.nlargest(1, 'anomaly_score').iloc[0]
                    st.markdown(f"**{top_anomaly['country']}**")
                    st.caption(f"Score: {top_anomaly['anomaly_score']:.1f}/100")

        with anomaly_cols[1]:
            with st.container(border=True, height=540):
                # Create and display the map
                fig_map = create_geographic_anomaly_map(
                    anomaly_data,
                    selected_month=selected_anomaly_month
                )

                if fig_map is not None:
                    st.plotly_chart(fig_map, width='stretch', config={'displayModeBar': False})
                else:
                    st.info("No data available for the selected month.")

                # Month slider below the map
                selected_month_label = st.select_slider(
                    "Select Month",
                    options=month_labels,
                    value=month_labels[st.session_state.anomaly_month_index],
                    key="anomaly_month_slider"
                )

                # Get the index from the selected label
                selected_index = month_labels.index(selected_month_label)

                # Update session state if slider changed
                if selected_index != st.session_state.anomaly_month_index:
                    st.session_state.anomaly_month_index = selected_index
                    st.rerun()

    # Add line break between charts
    st.markdown("<br>", unsafe_allow_html=True)
    
    # ========================================
    # PRODUCT REVENUE BY COUNTRY
    # ========================================

    # Second chart: Product Revenue by Country
    st.subheader("Product revenue")
    st.caption("Compare sales by product type in each country")
    st.markdown("<br>", unsafe_allow_html=True)

    # Load product data
    with st.spinner("Loading product revenue data..."):
        product_data, product_error = load_product_data()

    if product_error:
        st.error(f"Error loading product data: {product_error}")
        st.info("Please run the dashboard.ipynb notebook to generate the product revenue data.")
    else:
        # Main layout for product chart
        prod_cols = st.columns([1, 3], vertical_alignment="top")

        with prod_cols[0]:
            # Country selector
            with st.container(border=True, height=178):
                st.markdown("**Country Selection**")

                # Get list of countries
                countries = sorted(product_data['country'].unique())
                # Move 'World' to the front if it exists
                if 'World' in countries:
                    countries.remove('World')
                    countries.insert(0, 'World')

                selected_country = st.selectbox(
                    "Select country",
                    options=countries,
                    index=0,
                    label_visibility="collapsed"
                )

            # Product type selector
            with st.container(border=True, height=406):
                st.markdown("**Product Types**")

                # Get unique product types
                product_types = sorted(product_data['product_type'].unique())

                # Initialize session state for product selection
                if 'selected_products' not in st.session_state:
                    st.session_state.selected_products = product_types

                # Select all / deselect all buttons
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Select All", width='stretch'):
                        st.session_state.selected_products = product_types
                        st.rerun()
                with col2:
                    if st.button("Clear All", width='stretch'):
                        st.session_state.selected_products = []
                        st.rerun()

                # Product checkboxes
                selected_products = []
                for product in product_types:
                    if st.checkbox(
                        product,
                        value=product in st.session_state.selected_products,
                        key=f"product_{product}"
                    ):
                        selected_products.append(product)

                # Update session state
                st.session_state.selected_products = selected_products
                                
                # Normalization option
                normalize_revenue = st.radio(
                    "Display mode",
                    options=["Absolute Revenue", "Revenue Share (%)"],
                    index=0,
                    horizontal=True
                )

               

        with prod_cols[1]:
            with st.container(border=True, height=600):
                if selected_products and selected_country:
                    # Filter data for selected country and products
                    filtered_product_data = product_data[
                        (product_data['country'] == selected_country) &
                        (product_data['product_type'].isin(selected_products))
                    ]

                    # Aggregate by month and product type
                    agg_data = filtered_product_data.groupby(['month', 'product_type'])['revenue'].sum().reset_index()

                    if len(agg_data) > 0:
                        # Normalize if revenue share is selected
                        if normalize_revenue == "Revenue Share (%)":
                            # Calculate total revenue per month
                            monthly_totals = agg_data.groupby('month')['revenue'].sum().reset_index()
                            monthly_totals.columns = ['month', 'total_revenue']

                            # Merge and calculate percentage
                            agg_data = agg_data.merge(monthly_totals, on='month')
                            agg_data['revenue_pct'] = (agg_data['revenue'] / agg_data['total_revenue']) * 100
                            value_col = 'revenue_pct'
                            y_axis_title = 'Revenue Share (%)'
                            y_tickformat = '.1f'
                            hover_format = '%{fullData.name}: %{y:.1f}%<extra></extra>'
                        else:
                            value_col = 'revenue'
                            y_axis_title = 'Revenue ($)'
                            y_tickformat = '$,.0f'
                            hover_format = '%{fullData.name}: $%{y:,.0f}<extra></extra>'

                        # Create stacked area chart
                        fig_products = go.Figure()

                        # Add a trace for each product type
                        for product in sorted(selected_products):
                            product_subset = agg_data[agg_data['product_type'] == product]

                            fig_products.add_trace(go.Scatter(
                                x=product_subset['month'],
                                y=product_subset[value_col],
                                mode='lines',
                                name=product,
                                stackgroup='one',
                                hovertemplate='<b>%{x|%b %Y}</b><br>' + hover_format
                            ))

                        # Update layout
                        fig_products.update_layout(
                            title={
                                'text': f'Product Revenue Distribution<br><span style="font-size: 14px; color: #888;">{selected_country}</span>',
                                'font': {'size': 20}
                            },
                            xaxis=dict(
                                title='',
                                showgrid=True,
                                gridwidth=0.5
                            ),
                            yaxis=dict(
                                title=y_axis_title,
                                showgrid=True,
                                gridwidth=0.5,
                                tickformat=y_tickformat,
                                zeroline=False
                            ),
                            hovermode='x unified',
                            height=550,
                            plot_bgcolor='rgba(0,0,0,0)',
                            paper_bgcolor='rgba(0,0,0,0)',
                            margin=dict(l=60, r=40, t=50, b=60),
                            legend=dict(
                                orientation="h",
                                yanchor="bottom",
                                y=-0.2,
                                xanchor="center",
                                x=0.5
                            )
                        )

                        st.plotly_chart(fig_products, width='stretch')
                    else:
                        st.info("No data available for the selected country and products.")
                else:
                    st.info("Please select at least one product type to display the chart.")

    # Add line break between charts
    st.markdown("<br>", unsafe_allow_html=True)
    
    # ========================================
    # MONTHLY REVENUE TS SECTION
    # ========================================

    # Third chart: Monthly Revenue Time Series
    st.subheader("Monthly Revenue Time Series")
    st.caption("Revenue with three-month moving average")
    st.markdown("<br>", unsafe_allow_html=True)

    # Load data
    with st.spinner("Loading revenue trend data..."):
        data, error = load_data()

    if error:
        st.error(f"Error loading data: {error}")
        st.info("Please run the dashboard.ipynb notebook first to generate the data files.")
    else:
        # Use session state to track selected range
        if 'selected_range' not in st.session_state:
            st.session_state.selected_range = "All"

        # Filter data based on selection (before columns so it's available everywhere)
        filtered_data = filter_data_by_timerange(data, st.session_state.selected_range)

        # Main layout: 1:3 ratio (inspired by stockpeers)
        cols = st.columns([1, 3], vertical_alignment="top")

        # Left column: Controls and metrics
        with cols[0]:
            # Time range selector (separate container)
            with st.container(border=True, height=178):
                # Time range selector (pill-style buttons)
                time_ranges = {
                    "1 Month": "1M",
                    "3 Months": "3M",
                    "6 Months": "6M",
                    "1 Year": "1Y",
                    "2 Years": "2Y",
                    "All Time": "All"
                }

                # Create pills for time range selection
                st.markdown("**Time Range**")
                selected_label = st.pills(
                    "",
                    options=list(time_ranges.keys()),
                    default="All Time",
                    label_visibility="collapsed"
                )

                # Update session state based on selection
                if selected_label:
                    new_range = time_ranges[selected_label]
                    if st.session_state.selected_range != new_range:
                        st.session_state.selected_range = new_range
                        st.rerun()

            # Key metrics and period (separate container with remaining height)
            with st.container(border=True, height=406):
                # Calculate metrics
                if filtered_data is not None and len(filtered_data) > 0:
                    total_revenue = filtered_data['revenue'].sum()
                    total_orders = filtered_data['order_count'].sum()
                    avg_revenue = filtered_data['revenue'].mean()

                    # Calculate average MoM growth over the selected period
                    avg_mom_growth = filtered_data['mom_growth_pct'].mean()
                    has_mom_data = filtered_data['mom_growth_pct'].notna().any()

                    st.markdown("**Key Metrics**")

                    # Metric cards
                    st.metric(
                        label="Total Revenue",
                        value=format_currency(total_revenue),
                        delta=f"{avg_mom_growth:.1f}% Avg MoM" if has_mom_data else None
                    )

                    st.metric(
                        label="Total Orders",
                        value=f"{total_orders:,}"
                    )

                    st.metric(
                        label="Avg Monthly Revenue",
                        value=format_currency(avg_revenue)
                    )

                    # Date range info
                    st.markdown("**Period**")
                    st.markdown(f"{filtered_data['month'].min().strftime('%b %Y')} - {filtered_data['month'].max().strftime('%b %Y')}")

        # Right column: Main chart
        with cols[1]:
            with st.container(border=True, height=600):
                if filtered_data is not None and len(filtered_data) > 0:
                    # Create revenue trend chart
                    fig = go.Figure()

                    # Add revenue line (primary line in red, inspired by stockpeers)
                    fig.add_trace(go.Scatter(
                        x=filtered_data['month'],
                        y=filtered_data['revenue'],
                        mode='lines+markers',
                        name='Monthly Revenue',
                        line=dict(color='red', width=3),
                        marker=dict(size=6, color='red'),
                        hovertemplate='<b>%{x|%b %Y}</b><br>Revenue: $%{y:,.0f}<extra></extra>'
                    ))

                    # Add 3-month moving average starting from month 3
                    fig.add_trace(go.Scatter(
                        x=filtered_data['month'].iloc[2:],
                        y=filtered_data['revenue_ma3'].iloc[2:],
                        mode='lines',
                        name='3-Month Moving Avg',
                        line=dict(color='cyan', width=2, dash='dot'),
                        hovertemplate='<b>%{x|%b %Y}</b><br>MA3: $%{y:,.0f}<extra></extra>'
                    ))

                    # Update layout with transparent theme
                    fig.update_layout(
                        title={
                            'text': 'Monthly Revenue Trend',
                            'font': {'size': 20}
                        },
                        xaxis=dict(
                            title='',
                            showgrid=True,
                            gridwidth=0.5
                        ),
                        yaxis=dict(
                            title='Revenue ($)',
                            showgrid=True,
                            gridwidth=0.5,
                            tickformat='$,.0f',
                            zeroline=False
                        ),
                        hovermode='x unified',
                        height=550,
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        margin=dict(l=60, r=40, t=50, b=60),
                        legend=dict(
                            orientation="h",
                            yanchor="bottom",
                            y=-0.2,
                            xanchor="center",
                            x=0.5
                        )
                    )

                    # Display chart with full width
                    st.plotly_chart(fig, width='stretch')
                else:
                    st.info("No data available for the selected time range.")
    
    # line break between sections
    st.markdown("<br>", unsafe_allow_html=True)

    # ========================================
    # RAW DATA SECTION
    # ========================================
    st.subheader("Raw Data")
    st.caption("View the underlying datasets used to create the visualizations above")

    # Create tabs for each dataset
    tab1, tab2, tab3 = st.tabs(["Geographic Anomalies", "Product Revenue", "Monthly Revenue Trend"])

    with tab1:
        if anomaly_data is not None:
            st.caption(f"Geographic anomaly detection data ({len(anomaly_data):,} rows)")

            # Select relevant columns to display
            display_cols = [
                'month', 'country', 'region', 'anomaly_score', 'anomaly_severity',
                'total_revenue', 'order_count', 'unique_customers', 'avg_order_value',
                'revenue_zscore', 'orders_zscore', 'revenue_mom_change', 'anomaly_types'
            ]

            # Filter to only include columns that exist
            available_cols = [col for col in display_cols if col in anomaly_data.columns]

            # Display dataframe with formatting
            st.dataframe(
                anomaly_data[available_cols].sort_values(['month', 'country'], ascending=[False, True]),
                width='stretch',
                hide_index=True
            )
        else:
            st.info("No geographic anomaly data available")

    with tab2:
        if product_data is not None:
            st.caption(f"Product revenue by country data - Aggregated Summary (original data: {len(product_data):,} rows)")

            # Aggregate by month, country, and product_type to reduce size
            product_summary = product_data.groupby(['month', 'country', 'product_type'], as_index=False).agg({
                'revenue': 'sum'
            })

            st.caption(f"Showing aggregated data: {len(product_summary):,} rows")

            # Select relevant columns to display
            display_cols = [
                'month', 'country', 'product_type', 'revenue'
            ]

            # Filter to only include columns that exist
            available_cols = [col for col in display_cols if col in product_summary.columns]

            # Display dataframe
            st.dataframe(
                product_summary[available_cols].sort_values(['month', 'country', 'product_type'], ascending=[False, True, True]),
                width='stretch',
                hide_index=True
            )
        else:
            st.info("No product revenue data available")

    with tab3:
        if data is not None:
            st.caption(f"Monthly revenue trend data ({len(data):,} rows)")

            # Select relevant columns to display
            display_cols = [
                'month', 'revenue', 'order_count', 'unique_customers',
                'revenue_ma3', 'mom_growth_pct'
            ]

            # Filter to only include columns that exist
            available_cols = [col for col in display_cols if col in data.columns]

            # Display dataframe
            st.dataframe(
                data[available_cols].sort_values('month', ascending=False),
                width='stretch',
                hide_index=True
            )
        else:
            st.info("No monthly revenue data available")

if __name__ == "__main__":
    main()
