import pymssql
import os

server = os.getenv("DB_SERVER")
database = os.getenv("DB_NAME")
username = os.getenv("DB_USER")
password = os.getenv("DB_PASSWORD")
print("DB_SERVER:", os.getenv("DB_SERVER"))
print("db:", os.getenv("DB_NAME"))

try:
    # Reconnect to SQL Server
    conn = pymssql.connect(
        server=server,
        user=f"{username}@{server.split('.')[0]}", 
        password=password,
        database=database
    )
    print("✅ Connected to the database successfully!")

    # Create a cursor
    cursor = conn.cursor()

    # List columns in all relevant tables
    print("\n🔍 Listing columns in each table:")
    cursor.execute("""
        SELECT TABLE_NAME, COLUMN_NAME 
        FROM INFORMATION_SCHEMA.COLUMNS 
        WHERE TABLE_NAME IN ('Customers', 'Orders', 'OrderLines', 'Products')
        ORDER BY TABLE_NAME, COLUMN_NAME
    """)
    columns = cursor.fetchall()

    for table, column in columns:
        print(f" - {table}.{column}")

    conn.close()

except pymssql.InterfaceError as e:
    print(f"⚠️ Connection failed: {e}")
except pymssql.DatabaseError as e:
    print(f"⚠️ Database error: {e}")
except Exception as e:
    print(f"⚠️ Unexpected error: {e}")