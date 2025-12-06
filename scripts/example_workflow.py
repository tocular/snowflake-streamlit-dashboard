"""
Simple Example: Building a Monitoring Report
This script demonstrates a complete workflow for creating a monitoring product
"""
import pandas as pd
from datetime import datetime
from snowflake_connection import SnowflakeConnection
from snowflake_analytics import SnowflakeAnalytics


def generate_executive_report():
    """
    Generate a comprehensive executive report
    This is an example of a monitoring product you might build
    """
    
    print("=" * 70)
    print("EXECUTIVE SALES MONITORING REPORT")
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    # Initialize connection
    sf = SnowflakeConnection()
    analytics = SnowflakeAnalytics(sf)
    
    try:
        # Section 1: Current Performance
        print("\n📊 CURRENT PERFORMANCE (Last 30 Days)")
        print("-" * 70)
        
        kpis = analytics.get_kpi_summary()
        if not kpis.empty:
            row = kpis.iloc[0]
            print(f"Total Revenue:      ${row['TOTAL_REVENUE']:>15,.2f}")
            print(f"Total Orders:       {row['TOTAL_ORDERS']:>15,.0f}")
            print(f"Unique Customers:   {row['UNIQUE_CUSTOMERS']:>15,.0f}")
            print(f"Avg Order Value:    ${row['AVG_ORDER_VALUE']:>15,.2f}")
            print(f"Revenue per Day:    ${row['REVENUE_PER_DAY']:>15,.2f}")
        
        # Section 2: Trends
        print("\n📈 TREND ANALYSIS")
        print("-" * 70)
        
        comparison = analytics.get_kpi_comparison(current_days=30, comparison_days=30)
        if not comparison.empty:
            row = comparison.iloc[0]
            
            def format_change(pct):
                symbol = "↑" if pct > 0 else "↓"
                return f"{symbol} {abs(pct):.1f}%"
            
            print(f"Revenue Change:     {format_change(row['REVENUE_CHANGE_PCT']):>15}")
            print(f"Orders Change:      {format_change(row['ORDERS_CHANGE_PCT']):>15}")
            print(f"Customer Change:    {format_change(row['CUSTOMERS_CHANGE_PCT']):>15}")
        
        # Section 3: Customer Segmentation
        print("\n👥 CUSTOMER SEGMENTS")
        print("-" * 70)
        
        segments = analytics.get_customer_segments()
        if not segments.empty:
            print(f"{'Segment':<15} {'Count':>12} {'Avg LTV':>15} {'Total Value':>18}")
            print("-" * 70)
            for _, seg in segments.iterrows():
                print(f"{seg['SEGMENT']:<15} "
                      f"{int(seg['CUSTOMER_COUNT']):>12,} "
                      f"${seg['AVG_LIFETIME_VALUE']:>14,.2f} "
                      f"${seg['TOTAL_SEGMENT_VALUE']:>17,.2f}")
        
        # Section 4: Regional Performance
        print("\n🌍 TOP 5 REGIONS BY REVENUE")
        print("-" * 70)
        
        regional = analytics.get_regional_performance()
        if not regional.empty:
            top_regions = regional.nlargest(5, 'TOTAL_REVENUE')
            print(f"{'Region':<20} {'Revenue':>18} {'Orders':>12}")
            print("-" * 70)
            for _, reg in top_regions.iterrows():
                print(f"{reg['NATION']:<20} "
                      f"${reg['TOTAL_REVENUE']:>17,.2f} "
                      f"{int(reg['ORDER_COUNT']):>12,}")
        
        # Section 5: Anomaly Detection
        print("\n🚨 RECENT ANOMALIES")
        print("-" * 70)
        
        anomalies = analytics.detect_anomalies(metric='orders', lookback_days=30)
        if not anomalies.empty:
            alerts = anomalies[anomalies['STATUS'] == 'ANOMALY']
            
            if not alerts.empty:
                print(f"⚠️  {len(alerts)} anomalies detected in the last 30 days")
                print(f"\n{'Date':<12} {'Value':>12} {'Status':>12} {'Direction':>15}")
                print("-" * 70)
                for _, alert in alerts.head(5).iterrows():
                    print(f"{str(alert['METRIC_DATE'])[:10]:<12} "
                          f"{alert['METRIC_VALUE']:>12,.0f} "
                          f"{alert['STATUS']:>12} "
                          f"{alert['DIRECTION']:>15}")
            else:
                print("✅ No anomalies detected - all metrics within normal ranges")
        
        # Section 6: Recommendations
        print("\n💡 KEY INSIGHTS & RECOMMENDATIONS")
        print("-" * 70)
        
        # Analyze and provide insights
        if not segments.empty:
            vip_customers = segments[segments['SEGMENT'] == 'VIP']
            if not vip_customers.empty:
                vip_pct = (vip_customers['CUSTOMER_COUNT'].values[0] / 
                          segments['CUSTOMER_COUNT'].sum()) * 100
                vip_revenue_pct = (vip_customers['TOTAL_SEGMENT_VALUE'].values[0] / 
                                  segments['TOTAL_SEGMENT_VALUE'].sum()) * 100
                
                print(f"1. VIP customers represent {vip_pct:.1f}% of customers but")
                print(f"   generate {vip_revenue_pct:.1f}% of total revenue.")
                print(f"   💡 Focus retention efforts on this segment.")
        
        if not comparison.empty:
            row = comparison.iloc[0]
            if row['REVENUE_CHANGE_PCT'] < 0:
                print(f"\n2. Revenue declined by {abs(row['REVENUE_CHANGE_PCT']):.1f}% "
                      f"compared to previous period.")
                print(f"   💡 Investigate causes and implement corrective actions.")
            elif row['REVENUE_CHANGE_PCT'] > 10:
                print(f"\n2. Strong revenue growth of {row['REVENUE_CHANGE_PCT']:.1f}%!")
                print(f"   💡 Analyze what's working and scale successful strategies.")
        
        if not alerts.empty:
            print(f"\n3. Recent anomalies detected - requires investigation.")
            print(f"   💡 Review operational changes during anomaly periods.")
        
        print("\n" + "=" * 70)
        print("Report generated successfully!")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n❌ Error generating report: {str(e)}")
    
    finally:
        sf.close()


def quick_health_check():
    """
    Quick health check - runs fast checks on key metrics
    Perfect for automated monitoring
    """
    
    print("\n🏥 SYSTEM HEALTH CHECK")
    print("=" * 50)
    
    sf = SnowflakeConnection()
    analytics = SnowflakeAnalytics(sf)
    
    try:
        # Check 1: Data freshness
        query = """
        SELECT MAX(O_ORDERDATE) as latest_date
        FROM SNOWFLAKE_SAMPLE_DATA.TPCH_SF1.ORDERS
        """
        result = sf.execute_query(query)
        latest_date = result['LATEST_DATE'][0]
        print(f"✓ Latest data: {latest_date}")
        
        # Check 2: Today's metrics
        kpis = analytics.get_kpi_summary()
        if not kpis.empty:
            print(f"✓ Today's orders: {kpis['TOTAL_ORDERS'][0]:,.0f}")
            print(f"✓ Today's revenue: ${kpis['TOTAL_REVENUE'][0]:,.2f}")
        
        # Check 3: Anomalies
        anomalies = analytics.detect_anomalies(metric='orders', lookback_days=7)
        recent_anomalies = anomalies[anomalies['STATUS'] == 'ANOMALY']
        
        if recent_anomalies.empty:
            print("✓ No recent anomalies")
        else:
            print(f"⚠️  {len(recent_anomalies)} anomalies in last 7 days")
        
        print("\n✅ Health check complete!")
        
    except Exception as e:
        print(f"❌ Health check failed: {str(e)}")
    
    finally:
        sf.close()


if __name__ == "__main__":
    import sys
    
    print("\n" + "=" * 70)
    print("SNOWFLAKE MONITORING PRODUCT EXAMPLE")
    print("=" * 70)
    
    # Check if connection is configured
    import os
    if not os.getenv('SNOWFLAKE_USER'):
        print("\n⚠️  Snowflake credentials not configured!")
        print("\nPlease set environment variables:")
        print("  export SNOWFLAKE_USER='your_username'")
        print("  export SNOWFLAKE_PASSWORD='your_password'")
        print("  export SNOWFLAKE_ACCOUNT='your_account'")
        print("\nOr create a .env file with these values.")
        sys.exit(1)
    
    # Menu
    print("\nAvailable Reports:")
    print("  1. Full Executive Report")
    print("  2. Quick Health Check")
    print("  3. Both")
    
    choice = input("\nSelect option (1-3): ").strip()
    
    if choice == '1':
        generate_executive_report()
    elif choice == '2':
        quick_health_check()
    elif choice == '3':
        generate_executive_report()
        quick_health_check()
    else:
        print("Invalid option. Running full report...")
        generate_executive_report()
