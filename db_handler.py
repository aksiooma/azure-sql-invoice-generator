import pymssql
import os
from collections import defaultdict

# Environment variables
server = os.getenv("DB_SERVER")
database = os.getenv("DB_NAME")
username = os.getenv("DB_USER")
password = os.getenv("DB_PASSWORD")


def fetch_data(query):
    """
    Fetch data from the database using the provided SQL query.
    """
    try:
        # Establish connection
        with pymssql.connect(
            server=server,
            user=f"{username}@{server.split('.')[0]}", 
            password=password,
            database=database
        ) as conn:

            cursor = conn.cursor(as_dict=True) 
            cursor.execute(query)
            results = cursor.fetchall()
            return results

    except pymssql.InterfaceError as e:
        print(f"⚠️ Connection error: {e}")
        return None
    except pymssql.DatabaseError as e:
        print(f"⚠️ Database error: {e}")
        return None
    except Exception as e:
        print(f"⚠️ Unexpected error: {e}")
        return None

def fetch_order_details():
    """
    Fetch detailed order data, including customer, product, and price info.
    """
    query = """
    SELECT 
        o.orderId,
        o.customerId,
        c.name AS customerName,  -- ✅ Fetch customer name correctly
        c.address AS customerAddress,
        c.email AS customerEmail,
        o.dueDate,
        ol.orderLineId,
        ol.productId,
        p.productName,
        ol.quantity,
        p.price AS unitPrice,  
        (ol.quantity * p.price) AS totalPrice  -- ✅ Compute total price correctly
    FROM orders o
    JOIN orderLines ol ON o.orderId = ol.orderId  -- ✅ Correct join
    JOIN products p ON ol.productId = p.productId  -- ✅ Fetch product details
    JOIN customers c ON o.customerId = c.customerId  -- ✅ Fetch customer details
    ORDER BY o.orderId;
    """
    
    
    data = fetch_data(query)
    
    if data:
        print("✅ Successfully retrieved order details:")
        for row in data:
            print(row)  # Print detailed order data
    else:
        print("⚠️ No order details found.")
    
    return data

def group_orders_by_invoice():
    """Group fetched order details by OrderID to structure invoice data."""
    order_details = fetch_order_details()
    orders = defaultdict(list)

    if not order_details:
        print("⚠️ No orders found.")
        return None

    for row in order_details:
        order_id = row['orderId']
        orders[order_id].append(row)

    return orders
