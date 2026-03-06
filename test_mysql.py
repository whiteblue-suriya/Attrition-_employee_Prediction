import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from urllib.parse import quote_plus

# Load .env file
load_dotenv()

# Test MySQL connection
print("Testing MySQL Connection...")
print(f"DB Type: {os.getenv('DB_TYPE')}")
print(f"DB Host: {os.getenv('DB_HOST')}")
print(f"DB Port: {os.getenv('DB_PORT')}")
print(f"DB Name: {os.getenv('DB_DATABASE')}")
print(f"DB User: {os.getenv('DB_USERNAME')}")
print(f"DB Pass: {os.getenv('DB_PASSWORD')}")

# Try to connect with URL encoding
try:
    # URL encode password to handle special characters
    password = quote_plus(os.getenv('DB_PASSWORD', ''))
    username = quote_plus(os.getenv('DB_USERNAME', 'root'))
    
    connection_string = (
        f"mysql+pymysql://{username}:{password}"
        f"@{os.getenv('DB_HOST', 'localhost')}:{os.getenv('DB_PORT', '3306')}"
        f"/{os.getenv('DB_DATABASE', 'employee_performance')}"
    )
    
    print(f"\nEncoded connection string: {connection_string}")
    
    engine = create_engine(connection_string)
    with engine.connect() as conn:
        print("\n[SUCCESS] MySQL Connection Successful!")
        
        # Check tables
        result = conn.execute("SHOW TABLES")
        tables = [row[0] for row in result]
        print(f"\nTables in database: {tables}")
        
        # Check attrition data
        result = conn.execute("SELECT COUNT(*) FROM attrition_data")
        count = result.scalar()
        print(f"Records in attrition_data: {count}")
        
except Exception as e:
    print(f"\n[FAILED] Connection Failed: {e}")
    print("\nPlease check:")
    print("1. MySQL server is running")
    print("2. Username and password are correct")
    print("3. Database 'employee_performance' exists")
    print("4. Run attrition_schema_mysql.sql in MySQL Workbench first")