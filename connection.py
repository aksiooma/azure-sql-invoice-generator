import pyodbc
import os

server = os.getenv("DB_SERVER")
database = os.getenv("DB_NAME")
username = os.getenv("DB_USER")
password = os.getenv("DB_PASSWORD")
print("DB_SERVER:", os.getenv("DB_SERVER"))
print("db:", os.getenv("DB_NAME"))

# Database connection string
connection_string = (
    f"DRIVER={{ODBC Driver 18 for SQL Server}};"
    f"Server=tcp:{server},1433;"
    f"Database={database};"
    f"Uid={username};"
    f"Pwd={password};"
    f"Encrypt=yes;"
    f"TrustServerCertificate=no;"
    f"Connection Timeout=60;"
)
    
# Fetch data from the database
try:
    with pyodbc.connect(connection_string) as conn:
        print("Connected to the database successfully!")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM orders")
        rows = cursor.fetchall()
        for row in rows:
            print(row)
except pyodbc.OperationalError as e:
    print(f"Connection failed: {e}")