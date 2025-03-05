import pymssql
import os
from collections import defaultdict
from dotenv import load_dotenv

load_dotenv()

# OS environment variables. Change to dotenv the os.getenv is not used.
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
    
def load_invoice_query():
    query_file = os.getenv("INVOICE_QUERY_FILE")
    if query_file:
        with open(query_file, "r") as file:
            return file.read()
    return os.getenv("INVOICE_QUERY", "")  # Fallback to .env if no file exists
    

def fetch_order_details():
    """
    Fetch detailed order data using the dynamically generated SQL query.
    """
    base_query = load_invoice_query()

    if not base_query:
        return None  # If no query, return empty

    print("\n✅ Executing Dynamic Query:\n", base_query)

    try:
        data = fetch_data(base_query)
    except Exception as e:
        print(f"⚠️ Query Execution Failed: {e}")
        return None

    
    if data:
        print("✅ Successfully retrieved order details:")
        for row in data:
            print(row)  # Print detailed order data
    else:
        print("⚠️ No order details found.")
    
    return data

def group_orders_by_invoice():
    """
    Fetch and group order details from database using the generated query.
    """
    try:
        # Lue generoitu SQL-kysely tiedostosta
        with open("invoice_query.sql", "r") as f:
            sql_query = f.read()
        
        print("\n✅ Käytetään generoitua kyselyä:")
        print(sql_query)
        
        conn = pymssql.connect(
            server=server,
            user=f"{username}@{server.split('.')[0]}",
            password=password,
            database=database
        )
        cursor = conn.cursor(as_dict=True)
        
        cursor.execute(sql_query)
        orders = cursor.fetchall()
        
        if not orders:
            print("⚠️ Tilauksia ei löytynyt.")
            return None
            
        # Ryhmittele tilaukset ORDER_ID:n mukaan
        grouped_orders = {}
        for order in orders:
            order_id = order['ORDER_ID']
            if order_id not in grouped_orders:
                grouped_orders[order_id] = []
            grouped_orders[order_id].append(order)
            
        conn.close()
        return grouped_orders

    except pymssql.Error as e:
        print(f"⚠️ Tietokantavirhe: {e}")
        return None
    except Exception as e:
        print(f"⚠️ Odottamaton virhe: {e}")
        return None
