import pymssql
import os

# Load database connection info from environment variables
server = os.getenv("DB_SERVER")
database = os.getenv("DB_NAME")
username = os.getenv("DB_USER")
password = os.getenv("DB_PASSWORD")

print("DB_SERVER:", server)
print("DB_NAME:", database)

try:
    # Connect to SQL Server
    conn = pymssql.connect(
        server=server,
        user=f"{username}@{server.split('.')[0]}",
        password=password,
        database=database
    )
    print("✅ Connected to the database successfully!")

    # Create a cursor
    cursor = conn.cursor()

    # Fetch all table columns from INFORMATION_SCHEMA.COLUMNS
    cursor.execute("""
        SELECT TABLE_SCHEMA, TABLE_NAME, COLUMN_NAME
        FROM INFORMATION_SCHEMA.COLUMNS
        ORDER BY TABLE_SCHEMA, TABLE_NAME, COLUMN_NAME;
    """)
    columns = cursor.fetchall()

    # Organize columns by table
    table_columns = {}
    for schema, table, column in columns:
        table_name = f"{schema}.{table}"
        if table_name not in table_columns:
            table_columns[table_name] = []
        table_columns[table_name].append(column)

    print("\n🔍 Detected Tables & Columns:")
    for table, cols in table_columns.items():
        print(f" - {table}: {', '.join(cols)}")

    # Auto-detect key fields (for informational purposes)
    required_columns = {
        "ORDER_ID": ["SalesOrderID"],
        "CUSTOMER_ID": ["CustomerID"],
        "CUSTOMER_NAME": ["CompanyName"],
        "CUSTOMER_EMAIL": ["EmailAddress"],
        "DUE_DATE": ["DueDate"],
        "ORDER_LINE_ID": ["OrderQty"],
        "PRODUCT_ID": ["ProductID"],
        "PRODUCT_NAME": ["Name"],
        "QUANTITY": ["OrderQty"],
        "UNIT_PRICE": ["UnitPrice"],
        "CUSTOMER_ADDRESS": ["AddressID"]
    }

    detected_tables = {}
    table_aliases = {}  # For assigning unique aliases (if needed)
    used_aliases = set()
    alias_index = 1

    for field, expected_cols in required_columns.items():
        for table, cols in table_columns.items():
            for expected_col in expected_cols:
                if expected_col in cols:
                    detected_tables[field] = (table, expected_col)
                    # Assign a unique alias if not already assigned
                    if table not in table_aliases:
                        while f"t{alias_index}" in used_aliases:
                            alias_index += 1
                        table_aliases[table] = f"t{alias_index}"
                        used_aliases.add(f"t{alias_index}")
                    break
            if field in detected_tables:
                break

    missing_fields = set(required_columns.keys()) - set(detected_tables.keys())
    if missing_fields:
        print(f"\n⚠️ Warning: Could not find all required fields: {missing_fields}")
    else:
        print("\n✅ All required key fields detected:")
        for field, (table, col) in detected_tables.items():
            alias = table_aliases.get(table, "")
            print(f" - {field}: {table}.{col} (alias: {alias})")

    # Close the connection
    conn.close()

except pymssql.InterfaceError as e:
    print(f"⚠️ Connection failed: {e}")
except pymssql.DatabaseError as e:
    print(f"⚠️ Database error: {e}")
except Exception as e:
    print(f"⚠️ Unexpected error: {e}")
