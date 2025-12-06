"""
Snowflake Connection Test
Test if connection to Snowflake is working
"""
import os
from dotenv import load_dotenv
import snowflake.connector

# Load variables from .env
load_dotenv()

try:
    conn = snowflake.connector.connect(
        user = os.getenv('SNOWFLAKE_USER'),
        password = os.getenv('SNOWFLAKE_PASSWORD'),
        account = os.getenv('SNOWFLAKE_ACCOUNT'),
        warehouse = os.getenv('SNOWFLAKE_WAREHOUSE', 'COMPUTE_WH'),
        database = os.getenv('SNOWFLAKE_DATABASE', 'SNOWFLAKE_SAMPLE_DATA'),
        schema = os.getenv('SNOWFLAKE_SCHEMA', 'TPCH_SF1')
    )
    
    print("✅ Successfully connected to Snowflake!")

    # get connection info
    cur = conn.cursor()
    cur.execute("SELECT CURRENT_VERSION()")
    version = cur.fetchone()[0]
    print(f"Snowflake version: {version}")

    cur.execute("SELECT CURRENT_USER()")
    user = cur.fetchone()[0]
    print(f"Connected as: {user}")

    cur.execute("SELECT CURRENT_ACCOUNT()")
    account = cur.fetchone()[0]
    print(f"Account: {account}")

    cur.execute("SELECT CURRENT_WAREHOUSE()")
    warehouse = cur.fetchone()[0]
    print(f"Warehouse: {warehouse}")

    cur.execute("SELECT CURRENT_DATABASE()")
    database = cur.fetchone()[0]
    print(f"Database: {database}")
    
    cur.execute("SELECT CURRENT_SCHEMA()")
    schema = cur.fetchone()[0]
    print(f"Schema: {schema}")
    
    cur.close()
    
except Exception as e:
    print(f"Connection failed!")
    print(f"Error: {str(e)}")
    print("Tip: Double check your account name, username, and password.")