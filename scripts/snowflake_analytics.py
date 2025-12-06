"""
Snowflake Analytics Class
Reusable methods for building monitoring and analytical products
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta


class SnowflakeAnalytics:
    """
    Analytics methods for creating monitoring and analytical products
    Designed for leadership dashboards and business intelligence
    """
    
    def __init__(self, snowflake_connection):
        """
        Initialize with a SnowflakeConnection object
        
        Args:
            snowflake_connection: SnowflakeConnection instance
        """
        self.sf = snowflake_connection
    
    # ============================================
    # KPI & SUMMARY METRICS
    # ============================================
    
    def get_kpi_summary(self, start_date=None, end_date=None):
        """
        Get key performance indicators for a date range
        Perfect for executive dashboard summary cards
        
        Returns metrics like total revenue, orders, customers, etc.
        """
        if not start_date:
            start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        if not end_date:
            end_date = datetime.now().strftime('%Y-%m-%d')
        
        query = f"""
        SELECT 
            COUNT(DISTINCT O_CUSTKEY) as unique_customers,
            COUNT(*) as total_orders,
            SUM(O_TOTALPRICE) as total_revenue,
            AVG(O_TOTALPRICE) as avg_order_value,
            MIN(O_ORDERDATE) as first_order_date,
            MAX(O_ORDERDATE) as last_order_date,
            COUNT(DISTINCT O_ORDERDATE) as active_days,
            SUM(O_TOTALPRICE) / COUNT(DISTINCT O_ORDERDATE) as revenue_per_day
        FROM SNOWFLAKE_SAMPLE_DATA.TPCH_SF1.ORDERS
        WHERE O_ORDERDATE BETWEEN '{start_date}' AND '{end_date}'
        """
        return self.sf.execute_query(query)
    
    def get_kpi_comparison(self, current_days=30, comparison_days=30):
        """
        Compare current period KPIs to previous period
        Essential for showing trends and changes
        
        Returns current vs previous metrics with % change
        """
        query = f"""
        WITH current_period AS (
            SELECT 
                COUNT(*) as orders,
                SUM(O_TOTALPRICE) as revenue,
                COUNT(DISTINCT O_CUSTKEY) as customers,
                AVG(O_TOTALPRICE) as avg_order_value
            FROM SNOWFLAKE_SAMPLE_DATA.TPCH_SF1.ORDERS
            WHERE O_ORDERDATE >= DATEADD(day, -{current_days}, CURRENT_DATE())
        ),
        previous_period AS (
            SELECT 
                COUNT(*) as orders,
                SUM(O_TOTALPRICE) as revenue,
                COUNT(DISTINCT O_CUSTKEY) as customers,
                AVG(O_TOTALPRICE) as avg_order_value
            FROM SNOWFLAKE_SAMPLE_DATA.TPCH_SF1.ORDERS
            WHERE O_ORDERDATE >= DATEADD(day, -{current_days + comparison_days}, CURRENT_DATE())
                AND O_ORDERDATE < DATEADD(day, -{current_days}, CURRENT_DATE())
        )
        SELECT 
            c.orders as current_orders,
            p.orders as previous_orders,
            ((c.orders - p.orders) * 100.0 / p.orders) as orders_change_pct,
            c.revenue as current_revenue,
            p.revenue as previous_revenue,
            ((c.revenue - p.revenue) * 100.0 / p.revenue) as revenue_change_pct,
            c.customers as current_customers,
            p.customers as previous_customers,
            ((c.customers - p.customers) * 100.0 / p.customers) as customers_change_pct,
            c.avg_order_value as current_aov,
            p.avg_order_value as previous_aov,
            ((c.avg_order_value - p.avg_order_value) * 100.0 / p.avg_order_value) as aov_change_pct
        FROM current_period c
        CROSS JOIN previous_period p
        """
        return self.sf.execute_query(query)
    
    # ============================================
    # TREND ANALYSIS
    # ============================================
    
    def get_time_series(self, metric='revenue', period='day', lookback_days=90):
        """
        Get time series data for trend analysis
        
        Args:
            metric: 'revenue', 'orders', 'customers', or 'aov'
            period: 'day', 'week', 'month', 'quarter'
            lookback_days: how far back to look
        """
        metric_map = {
            'revenue': 'SUM(O_TOTALPRICE)',
            'orders': 'COUNT(*)',
            'customers': 'COUNT(DISTINCT O_CUSTKEY)',
            'aov': 'AVG(O_TOTALPRICE)'
        }
        
        metric_sql = metric_map.get(metric, 'SUM(O_TOTALPRICE)')
        
        query = f"""
        SELECT 
            DATE_TRUNC('{period}', O_ORDERDATE) as period_date,
            {metric_sql} as metric_value,
            COUNT(*) as order_count,
            COUNT(DISTINCT O_CUSTKEY) as customer_count
        FROM SNOWFLAKE_SAMPLE_DATA.TPCH_SF1.ORDERS
        WHERE O_ORDERDATE >= DATEADD(day, -{lookback_days}, CURRENT_DATE())
        GROUP BY DATE_TRUNC('{period}', O_ORDERDATE)
        ORDER BY period_date
        """
        return self.sf.execute_query(query)
    
    def get_moving_averages(self, window_days=7, lookback_days=90):
        """
        Calculate moving averages for smoothed trends
        Great for identifying patterns without daily noise
        """
        query = f"""
        WITH daily_metrics AS (
            SELECT 
                DATE_TRUNC('day', O_ORDERDATE) as order_date,
                COUNT(*) as orders,
                SUM(O_TOTALPRICE) as revenue,
                COUNT(DISTINCT O_CUSTKEY) as customers
            FROM SNOWFLAKE_SAMPLE_DATA.TPCH_SF1.ORDERS
            WHERE O_ORDERDATE >= DATEADD(day, -{lookback_days}, CURRENT_DATE())
            GROUP BY DATE_TRUNC('day', O_ORDERDATE)
        )
        SELECT 
            order_date,
            orders,
            revenue,
            customers,
            AVG(orders) OVER (
                ORDER BY order_date 
                ROWS BETWEEN {window_days-1} PRECEDING AND CURRENT ROW
            ) as orders_ma,
            AVG(revenue) OVER (
                ORDER BY order_date 
                ROWS BETWEEN {window_days-1} PRECEDING AND CURRENT ROW
            ) as revenue_ma,
            AVG(customers) OVER (
                ORDER BY order_date 
                ROWS BETWEEN {window_days-1} PRECEDING AND CURRENT ROW
            ) as customers_ma
        FROM daily_metrics
        ORDER BY order_date
        """
        return self.sf.execute_query(query)
    
    # ============================================
    # CUSTOMER ANALYTICS
    # ============================================
    
    def get_customer_segments(self):
        """
        Segment customers by value and behavior
        Critical for targeted strategies and resource allocation
        """
        query = """
        WITH customer_metrics AS (
            SELECT 
                O_CUSTKEY,
                COUNT(*) as order_count,
                SUM(O_TOTALPRICE) as lifetime_value,
                AVG(O_TOTALPRICE) as avg_order_value,
                MAX(O_ORDERDATE) as last_order_date,
                MIN(O_ORDERDATE) as first_order_date,
                DATEDIFF(day, MIN(O_ORDERDATE), MAX(O_ORDERDATE)) as customer_tenure_days
            FROM SNOWFLAKE_SAMPLE_DATA.TPCH_SF1.ORDERS
            GROUP BY O_CUSTKEY
        ),
        percentiles AS (
            SELECT 
                PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY lifetime_value) as p75_value,
                PERCENTILE_CONT(0.50) WITHIN GROUP (ORDER BY lifetime_value) as p50_value,
                PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY lifetime_value) as p25_value
            FROM customer_metrics
        )
        SELECT 
            CASE 
                WHEN cm.lifetime_value >= p.p75_value THEN 'VIP'
                WHEN cm.lifetime_value >= p.p50_value THEN 'High Value'
                WHEN cm.lifetime_value >= p.p25_value THEN 'Medium Value'
                ELSE 'Low Value'
            END as segment,
            COUNT(*) as customer_count,
            AVG(cm.lifetime_value) as avg_lifetime_value,
            AVG(cm.order_count) as avg_order_count,
            AVG(cm.avg_order_value) as avg_order_value,
            AVG(cm.customer_tenure_days) as avg_tenure_days,
            SUM(cm.lifetime_value) as total_segment_value
        FROM customer_metrics cm
        CROSS JOIN percentiles p
        GROUP BY segment
        ORDER BY avg_lifetime_value DESC
        """
        return self.sf.execute_query(query)
    
    def get_customer_cohorts(self, cohort_period='month'):
        """
        Analyze customer retention by cohort
        Shows how well you're retaining customers over time
        """
        query = f"""
        WITH first_order AS (
            SELECT 
                O_CUSTKEY,
                DATE_TRUNC('{cohort_period}', MIN(O_ORDERDATE)) as cohort_date
            FROM SNOWFLAKE_SAMPLE_DATA.TPCH_SF1.ORDERS
            GROUP BY O_CUSTKEY
        ),
        customer_orders AS (
            SELECT 
                o.O_CUSTKEY,
                f.cohort_date,
                DATE_TRUNC('{cohort_period}', o.O_ORDERDATE) as order_period,
                DATEDIFF({cohort_period}, f.cohort_date, o.O_ORDERDATE) as periods_since_first
            FROM SNOWFLAKE_SAMPLE_DATA.TPCH_SF1.ORDERS o
            JOIN first_order f ON o.O_CUSTKEY = f.O_CUSTKEY
        )
        SELECT 
            cohort_date,
            periods_since_first,
            COUNT(DISTINCT O_CUSTKEY) as active_customers
        FROM customer_orders
        GROUP BY cohort_date, periods_since_first
        ORDER BY cohort_date, periods_since_first
        """
        return self.sf.execute_query(query)
    
    # ============================================
    # ANOMALY DETECTION & MONITORING
    # ============================================
    
    def detect_anomalies(self, metric='orders', threshold_std=2, lookback_days=90):
        """
        Detect statistical anomalies in time series data
        Essential for alerting and monitoring systems
        
        Uses z-score method to identify outliers
        """
        metric_map = {
            'orders': 'COUNT(*)',
            'revenue': 'SUM(O_TOTALPRICE)',
            'customers': 'COUNT(DISTINCT O_CUSTKEY)',
            'aov': 'AVG(O_TOTALPRICE)'
        }
        
        metric_sql = metric_map.get(metric, 'COUNT(*)')
        
        query = f"""
        WITH daily_metrics AS (
            SELECT 
                DATE_TRUNC('day', O_ORDERDATE) as metric_date,
                {metric_sql} as metric_value
            FROM SNOWFLAKE_SAMPLE_DATA.TPCH_SF1.ORDERS
            WHERE O_ORDERDATE >= DATEADD(day, -{lookback_days}, CURRENT_DATE())
            GROUP BY DATE_TRUNC('day', O_ORDERDATE)
        ),
        statistics AS (
            SELECT 
                AVG(metric_value) as avg_value,
                STDDEV(metric_value) as stddev_value
            FROM daily_metrics
        )
        SELECT 
            d.metric_date,
            d.metric_value,
            s.avg_value,
            s.stddev_value,
            (d.metric_value - s.avg_value) / NULLIF(s.stddev_value, 0) as z_score,
            CASE 
                WHEN ABS((d.metric_value - s.avg_value) / NULLIF(s.stddev_value, 0)) > {threshold_std}
                THEN 'ANOMALY'
                WHEN ABS((d.metric_value - s.avg_value) / NULLIF(s.stddev_value, 0)) > {threshold_std * 0.75}
                THEN 'WARNING'
                ELSE 'NORMAL'
            END as status,
            CASE 
                WHEN d.metric_value > s.avg_value THEN 'ABOVE_AVERAGE'
                ELSE 'BELOW_AVERAGE'
            END as direction
        FROM daily_metrics d
        CROSS JOIN statistics s
        ORDER BY d.metric_date DESC
        """
        return self.sf.execute_query(query)
    
    def get_performance_metrics(self, lookback_days=7):
        """
        Monitor system performance metrics
        Important for operational monitoring
        
        Note: Requires access to ACCOUNT_USAGE schema
        """
        query = f"""
        SELECT 
            DATE_TRUNC('hour', START_TIME) as query_hour,
            COUNT(*) as query_count,
            AVG(TOTAL_ELAPSED_TIME)/1000 as avg_duration_seconds,
            MAX(TOTAL_ELAPSED_TIME)/1000 as max_duration_seconds,
            PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY TOTAL_ELAPSED_TIME)/1000 as p95_duration,
            SUM(BYTES_SCANNED)/(1024*1024*1024) as gb_scanned,
            COUNT(CASE WHEN ERROR_CODE IS NOT NULL THEN 1 END) as error_count
        FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY
        WHERE START_TIME >= DATEADD(day, -{lookback_days}, CURRENT_DATE())
        GROUP BY DATE_TRUNC('hour', START_TIME)
        ORDER BY query_hour DESC
        LIMIT 168
        """
        try:
            return self.sf.execute_query(query)
        except Exception as e:
            print(f"Performance metrics require ACCOUNT_USAGE access: {str(e)}")
            return pd.DataFrame()
    
    # ============================================
    # GEOGRAPHIC & DIMENSIONAL ANALYSIS
    # ============================================
    
    def get_regional_performance(self):
        """
        Analyze performance by geographic region
        Uses TPCH sample data regions and nations
        """
        query = """
        SELECT 
            r.R_NAME as region,
            n.N_NAME as nation,
            COUNT(o.O_ORDERKEY) as order_count,
            SUM(o.O_TOTALPRICE) as total_revenue,
            AVG(o.O_TOTALPRICE) as avg_order_value,
            COUNT(DISTINCT o.O_CUSTKEY) as unique_customers
        FROM SNOWFLAKE_SAMPLE_DATA.TPCH_SF1.ORDERS o
        JOIN SNOWFLAKE_SAMPLE_DATA.TPCH_SF1.CUSTOMER c ON o.O_CUSTKEY = c.C_CUSTKEY
        JOIN SNOWFLAKE_SAMPLE_DATA.TPCH_SF1.NATION n ON c.C_NATIONKEY = n.N_NATIONKEY
        JOIN SNOWFLAKE_SAMPLE_DATA.TPCH_SF1.REGION r ON n.N_REGIONKEY = r.R_REGIONKEY
        GROUP BY r.R_NAME, n.N_NAME
        ORDER BY total_revenue DESC
        """
        return self.sf.execute_query(query)
    
    def get_priority_analysis(self):
        """
        Analyze orders by priority level
        Shows distribution of urgent vs standard orders
        """
        query = """
        SELECT 
            O_ORDERPRIORITY as priority,
            COUNT(*) as order_count,
            SUM(O_TOTALPRICE) as total_revenue,
            AVG(O_TOTALPRICE) as avg_order_value,
            COUNT(DISTINCT O_CUSTKEY) as unique_customers,
            ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) as percentage_of_orders
        FROM SNOWFLAKE_SAMPLE_DATA.TPCH_SF1.ORDERS
        GROUP BY O_ORDERPRIORITY
        ORDER BY order_count DESC
        """
        return self.sf.execute_query(query)
    
    # ============================================
    # ADVANCED ANALYTICS
    # ============================================
    
    def get_rfm_analysis(self):
        """
        RFM (Recency, Frequency, Monetary) analysis
        Gold standard for customer segmentation
        """
        query = """
        WITH customer_rfm AS (
            SELECT 
                O_CUSTKEY as customer_id,
                DATEDIFF(day, MAX(O_ORDERDATE), CURRENT_DATE()) as recency_days,
                COUNT(*) as frequency,
                SUM(O_TOTALPRICE) as monetary_value
            FROM SNOWFLAKE_SAMPLE_DATA.TPCH_SF1.ORDERS
            GROUP BY O_CUSTKEY
        ),
        rfm_scores AS (
            SELECT 
                customer_id,
                recency_days,
                frequency,
                monetary_value,
                NTILE(5) OVER (ORDER BY recency_days DESC) as r_score,
                NTILE(5) OVER (ORDER BY frequency ASC) as f_score,
                NTILE(5) OVER (ORDER BY monetary_value ASC) as m_score
            FROM customer_rfm
        )
        SELECT 
            CASE 
                WHEN r_score >= 4 AND f_score >= 4 AND m_score >= 4 THEN 'Champions'
                WHEN r_score >= 3 AND f_score >= 3 THEN 'Loyal Customers'
                WHEN r_score >= 4 AND f_score <= 2 THEN 'Potential Loyalists'
                WHEN r_score >= 3 AND m_score >= 3 THEN 'Big Spenders'
                WHEN r_score <= 2 AND f_score >= 3 THEN 'At Risk'
                WHEN r_score <= 2 AND f_score <= 2 THEN 'Lost'
                ELSE 'Regular'
            END as rfm_segment,
            COUNT(*) as customer_count,
            AVG(recency_days) as avg_recency,
            AVG(frequency) as avg_frequency,
            AVG(monetary_value) as avg_monetary_value,
            SUM(monetary_value) as total_value
        FROM rfm_scores
        GROUP BY rfm_segment
        ORDER BY total_value DESC
        """
        return self.sf.execute_query(query)
    
    def get_growth_rate(self, period='month'):
        """
        Calculate period-over-period growth rates
        Essential for reporting trends to leadership
        """
        query = f"""
        WITH period_metrics AS (
            SELECT 
                DATE_TRUNC('{period}', O_ORDERDATE) as period_date,
                COUNT(*) as orders,
                SUM(O_TOTALPRICE) as revenue,
                COUNT(DISTINCT O_CUSTKEY) as customers
            FROM SNOWFLAKE_SAMPLE_DATA.TPCH_SF1.ORDERS
            GROUP BY DATE_TRUNC('{period}', O_ORDERDATE)
        )
        SELECT 
            period_date,
            orders,
            revenue,
            customers,
            LAG(revenue, 1) OVER (ORDER BY period_date) as prev_revenue,
            ((revenue - LAG(revenue, 1) OVER (ORDER BY period_date)) * 100.0 / 
                NULLIF(LAG(revenue, 1) OVER (ORDER BY period_date), 0)) as revenue_growth_pct,
            LAG(orders, 1) OVER (ORDER BY period_date) as prev_orders,
            ((orders - LAG(orders, 1) OVER (ORDER BY period_date)) * 100.0 / 
                NULLIF(LAG(orders, 1) OVER (ORDER BY period_date), 0)) as orders_growth_pct
        FROM period_metrics
        ORDER BY period_date
        """
        return self.sf.execute_query(query)


# Example usage
if __name__ == "__main__":
    print("=" * 60)
    print("Snowflake Analytics Class - Example Usage")
    print("=" * 60)
    
    from snowflake_connection import SnowflakeConnection
    
    # Initialize connection
    sf_conn = SnowflakeConnection()
    analytics = SnowflakeAnalytics(sf_conn)
    
    print("\n📊 Running example analytics...")
    
    try:
        # Get KPI summary
        print("\n1. KPI Summary (Last 30 Days):")
        kpis = analytics.get_kpi_summary()
        print(kpis.to_string(index=False))
        
        # Customer segments
        print("\n2. Customer Segments:")
        segments = analytics.get_customer_segments()
        print(segments.to_string(index=False))
        
        # Detect anomalies
        print("\n3. Recent Anomalies:")
        anomalies = analytics.detect_anomalies(lookback_days=30)
        anomalies_only = anomalies[anomalies['STATUS'] == 'ANOMALY'].head(5)
        if not anomalies_only.empty:
            print(anomalies_only[['METRIC_DATE', 'METRIC_VALUE', 'Z_SCORE', 'STATUS']].to_string(index=False))
        else:
            print("No anomalies detected")
        
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        print("\nMake sure to set your Snowflake credentials first!")
    
    finally:
        sf_conn.close()
