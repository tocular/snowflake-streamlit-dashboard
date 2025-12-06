"""
Snowflake Connection Helper
Handles connection setup with best practices
"""
import os
import snowflake.connector
from sqlalchemy import create_engine
from snowflake.sqlalchemy import URL
import pandas as pd


class SnowflakeConnection:
    """Manages Snowflake connections with multiple methods"""
    
    def __init__(self, use_env_vars=True):
        """
        Initialize connection parameters
        
        Args:
            use_env_vars (bool): If True, load from environment variables
        """
        if use_env_vars:
            self.user = os.getenv('SNOWFLAKE_USER')
            self.password = os.getenv('SNOWFLAKE_PASSWORD')
            self.account = os.getenv('SNOWFLAKE_ACCOUNT')
            self.warehouse = os.getenv('SNOWFLAKE_WAREHOUSE', 'COMPUTE_WH')
            self.database = os.getenv('SNOWFLAKE_DATABASE', 'SNOWFLAKE_SAMPLE_DATA')
            self.schema = os.getenv('SNOWFLAKE_SCHEMA', 'TPCH_SF1')
        else:
            # Manual configuration
            self.user = None
            self.password = None
            self.account = None
            self.warehouse = 'COMPUTE_WH'
            self.database = 'SNOWFLAKE_SAMPLE_DATA'
            self.schema = 'TPCH_SF1'
        
        self._conn = None
        self._engine = None
    
    def set_credentials(self, user, password, account):
        """Manually set credentials"""
        self.user = user
        self.password = password
        self.account = account
    
    def get_connector_connection(self):
        """Get a native Snowflake connector connection"""
        if not self._conn:
            try:
                self._conn = snowflake.connector.connect(
                    user=self.user,
                    password=self.password,
                    account=self.account,
                    warehouse=self.warehouse,
                    database=self.database,
                    schema=self.schema
                )
                print(f"✓ Connected to Snowflake account: {self.account}")
            except Exception as e:
                print(f"✗ Connection failed: {str(e)}")
                raise
        return self._conn
    
    def get_sqlalchemy_engine(self):
        """Get a SQLAlchemy engine for pandas integration"""
        if not self._engine:
            try:
                self._engine = create_engine(URL(
                    account=self.account,
                    user=self.user,
                    password=self.password,
                    database=self.database,
                    schema=self.schema,
                    warehouse=self.warehouse
                ))
                print(f"✓ SQLAlchemy engine created for {self.account}")
            except Exception as e:
                print(f"✗ Engine creation failed: {str(e)}")
                raise
        return self._engine
    
    def test_connection(self):
        """Test the connection with a simple query"""
        try:
            conn = self.get_connector_connection()
            cur = conn.cursor()
            cur.execute("SELECT CURRENT_VERSION()")
            version = cur.fetchone()[0]
            print(f"✓ Connection successful! Snowflake version: {version}")
            
            # Test sample data access
            cur.execute("SELECT COUNT(*) FROM SNOWFLAKE_SAMPLE_DATA.TPCH_SF1.CUSTOMER")
            count = cur.fetchone()[0]
            print(f"✓ Sample data accessible! Customer count: {count:,}")
            
            return True
        except Exception as e:
            print(f"✗ Connection test failed: {str(e)}")
            return False
    
    def execute_query(self, query, return_df=True):
        """
        Execute a query and return results
        
        Args:
            query (str): SQL query to execute
            return_df (bool): If True, return pandas DataFrame
            
        Returns:
            pd.DataFrame or list: Query results
        """
        try:
            if return_df:
                engine = self.get_sqlalchemy_engine()
                return pd.read_sql(query, engine)
            else:
                conn = self.get_connector_connection()
                cur = conn.cursor()
                cur.execute(query)
                return cur.fetchall()
        except Exception as e:
            print(f"✗ Query execution failed: {str(e)}")
            raise
    
    def list_databases(self):
        """List available databases"""
        query = "SHOW DATABASES"
        return self.execute_query(query, return_df=True)
    
    def list_schemas(self, database=None):
        """List schemas in a database"""
        db = database or self.database
        query = f"SHOW SCHEMAS IN DATABASE {db}"
        return self.execute_query(query, return_df=True)
    
    def list_tables(self, schema=None):
        """List tables in a schema"""
        sch = schema or self.schema
        query = f"SHOW TABLES IN SCHEMA {self.database}.{sch}"
        return self.execute_query(query, return_df=True)
    
    def get_table_info(self, table_name, schema=None):
        """Get information about a specific table"""
        sch = schema or self.schema
        query = f"DESCRIBE TABLE {self.database}.{sch}.{table_name}"
        return self.execute_query(query, return_df=True)
    
    def close(self):
        """Close connections"""
        if self._conn:
            self._conn.close()
            print("✓ Connection closed")
        if self._engine:
            self._engine.dispose()
            print("✓ Engine disposed")


# Example usage
if __name__ == "__main__":
    print("=" * 60)
    print("Snowflake Connection Helper - Quick Start")
    print("=" * 60)
    
    # Method 1: Using environment variables (recommended)
    print("\n📋 Method 1: Environment Variables")
    print("Set these environment variables:")
    print("  export SNOWFLAKE_USER='your_username'")
    print("  export SNOWFLAKE_PASSWORD='your_password'")
    print("  export SNOWFLAKE_ACCOUNT='your_account'")
    
    # Method 2: Manual setup
    print("\n📋 Method 2: Manual Configuration")
    print("Example code:")
    print("""
    sf = SnowflakeConnection(use_env_vars=False)
    sf.set_credentials(
        user='your_username',
        password='your_password',
        account='your_account'  # e.g., 'xy12345.us-east-1'
    )
    sf.test_connection()
    """)
    
    # Quick test if env vars are set
    if os.getenv('SNOWFLAKE_USER'):
        print("\n🔧 Testing connection with environment variables...")
        sf = SnowflakeConnection()
        sf.test_connection()
        
        # Show sample data
        print("\n📊 Sample query:")
        df = sf.execute_query("""
            SELECT O_ORDERPRIORITY, COUNT(*) as count
            FROM SNOWFLAKE_SAMPLE_DATA.TPCH_SF1.ORDERS
            GROUP BY O_ORDERPRIORITY
            LIMIT 5
        """)
        print(df)
        
        sf.close()
