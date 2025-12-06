from sqlalchemy import create_engine, text
from snowflake.sqlalchemy import URL
import pandas as pd
import os
from dotenv import load_dotenv

class SnowflakeEngine:
    """SQLAlchemy engine wrapper for Snowflake"""
    
    def __init__(self):
        load_dotenv()
        
        self.engine = create_engine(URL(
            account=os.getenv('SNOWFLAKE_ACCOUNT'),
            user=os.getenv('SNOWFLAKE_USER'),
            password=os.getenv('SNOWFLAKE_PASSWORD'),
            database=os.getenv('SNOWFLAKE_DATABASE', 'SNOWFLAKE_SAMPLE_DATA'),
            schema=os.getenv('SNOWFLAKE_SCHEMA', 'TPCH_SF1'),
            warehouse=os.getenv('SNOWFLAKE_WAREHOUSE', 'COMPUTE_WH')
        ))
    
    def query(self, sql, params=None):
        """
        Execute query and return DataFrame
        Properly handles multi-line SQL queries
        
        Args:
            sql (str): SQL query (can be multi-line)
            params (dict): Optional parameters for parameterized queries
            
        Returns:
            pd.DataFrame: Query results
        """
        # Always wrap in text() for consistent handling
        if params:
            return pd.read_sql(text(sql), self.engine, params=params)
        else:
            return pd.read_sql(text(sql), self.engine)
    
    def execute(self, sql, params=None):
        """
        Execute query without returning results (INSERT, UPDATE, DELETE, etc.)
        
        Args:
            sql (str): SQL statement (can be multi-line)
            params (dict): Optional parameters
        """
        with self.engine.connect() as conn:
            if params:
                conn.execute(text(sql), params)
            else:
                conn.execute(text(sql))
            conn.commit()
    
    def test_connection(self):
        """Test the connection"""
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text("SELECT CURRENT_USER()"))
                user = result.fetchone()[0]
                print(f"Connected as: {user}")
                return True
        except Exception as e:
            print(f"Connection failed: {str(e)}")
            return False
    
    def dispose(self):
        """Dispose of the engine"""
        self.engine.dispose()
        print("Connection closed")
        

### USAGE
#sf = SnowflakeEngine()
#sf.test_connection()

# Query without warnings
#df = sf.query("SELECT * FROM CUSTOMER LIMIT 10")
#print(df)

# Query with parameters
#df = sf.query(
#    "SELECT * FROM ORDERS WHERE O_ORDERSTATUS = :status LIMIT 10",
#    params={'status': 'F'}
#)
#print(df)

#sf.close()