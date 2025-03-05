import os
import pymssql

server = os.getenv("DB_SERVER")
database = os.getenv("DB_NAME")
username = os.getenv("DB_USER")
password = os.getenv("DB_PASSWORD")

def get_schema():
    """Retrieve table structure and foreign key relationships."""
    try:
        conn = pymssql.connect(
            server=server,
            user=f"{username}@{server.split('.')[0]}", 
            password=password,
            database=database
        )
        cursor = conn.cursor()

        # Fetch foreign keys and relationships
        cursor.execute("""
            SELECT 
                tp.name AS ParentTable,
                cp.name AS ParentColumn,
                tr.name AS ReferencedTable,
                cr.name AS ReferencedColumn,
                SCHEMA_NAME(tp.schema_id) AS ParentSchema,
                SCHEMA_NAME(tr.schema_id) AS ReferencedSchema
            FROM sys.foreign_keys fk
            JOIN sys.foreign_key_columns fkc ON fk.object_id = fkc.constraint_object_id
            JOIN sys.tables tp ON fkc.parent_object_id = tp.object_id
            JOIN sys.columns cp ON fkc.parent_object_id = cp.object_id AND fkc.parent_column_id = cp.column_id
            JOIN sys.tables tr ON fkc.referenced_object_id = tr.object_id
            JOIN sys.columns cr ON fkc.referenced_object_id = cr.object_id AND fkc.referenced_column_id = cr.column_id
        """)
        foreign_keys = cursor.fetchall()
        conn.close()
        return foreign_keys

    except pymssql.DatabaseError as e:
        print(f"⚠️ Database error: {e}")
        return None

# Generate SQL Query with correct schema references
sql_query = """SELECT
    SalesLT.SalesOrderHeader.SalesOrderID AS ORDER_ID,
    SalesLT.Customer.CustomerID AS CUSTOMER_ID,
    SalesLT.Customer.CompanyName AS CUSTOMER_NAME,
    SalesLT.Customer.EmailAddress AS CUSTOMER_EMAIL,
    SalesLT.SalesOrderHeader.DueDate AS DUE_DATE,
    SalesLT.SalesOrderDetail.SalesOrderDetailID AS ORDER_LINE_ID,
    SalesLT.Product.ProductID AS PRODUCT_ID,
    SalesLT.Product.Name AS PRODUCT_NAME,
    SalesLT.SalesOrderDetail.OrderQty AS QUANTITY,
    SalesLT.SalesOrderDetail.UnitPrice AS UNIT_PRICE,
    SalesLT.CustomerAddress.AddressID AS CUSTOMER_ADDRESS
FROM SalesLT.SalesOrderHeader
JOIN SalesLT.Customer ON SalesLT.SalesOrderHeader.CustomerID = SalesLT.Customer.CustomerID
JOIN SalesLT.CustomerAddress ON SalesLT.Customer.CustomerID = SalesLT.CustomerAddress.CustomerID
JOIN SalesLT.SalesOrderDetail ON SalesLT.SalesOrderHeader.SalesOrderID = SalesLT.SalesOrderDetail.SalesOrderID
JOIN SalesLT.Product ON SalesLT.SalesOrderDetail.ProductID = SalesLT.Product.ProductID
ORDER BY SalesLT.SalesOrderHeader.SalesOrderID;"""

# Save query to file
with open("invoice_query.sql", "w") as f:
    f.write(sql_query)

print("\n✅ Successfully generated `invoice_query.sql`!")
