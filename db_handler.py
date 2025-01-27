import pyodbc
import os

# Environment variables
server = os.getenv("DB_SERVER")
database = os.getenv("DB_NAME")
username = os.getenv("DB_USER")
password = os.getenv("DB_PASSWORD")

# Database connection string
connection_string = (
    f"DRIVER={{ODBC Driver 18 for SQL Server}};"
    f"Server=tcp:{server},1433;"
    f"Database={database};"
    f"Uid={username};"
    f"Pwd={password};"
    f"Encrypt=yes;"
    f"TrustServerCertificate=no;"
    f"Connection Timeout=30;"
)

def fetch_data(query):
    """
    Fetch data from the database using the provided SQL query.
    """
    try:
        # Connect to the database
        with pyodbc.connect(connection_string) as conn:
            cursor = conn.cursor()
            # Execute the query
            cursor.execute(query)
            results = cursor.fetchall()
            return results
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None
