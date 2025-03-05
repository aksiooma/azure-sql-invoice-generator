import os
import json
import pymssql
from typing import Dict, List, Tuple
from dotenv import load_dotenv
from config import load_config

# Lataa asetukset
config = load_config()
if not config:
    raise Exception("Asetukset puuttuvat!")

# Käytä asetuksia
server = config["DB_SERVER"]
database = config["DB_NAME"]
username = config["DB_USER"]
password = config["DB_PASSWORD"]

def check_database_connection():
    """Tarkista tietokantayhteyden tila ja palauta virheilmoitus."""
    try:
        conn = pymssql.connect(
            server=server,
            user=f"{username}@{server.split('.')[0]}",
            password=password,
            database=database,
            timeout=10  # Lisätään timeout-arvo
        )
        conn.close()
        return True, None
    except pymssql.OperationalError as e:
        if "is not currently available" in str(e):
            return False, """
⚠️ Tietokanta ei ole saatavilla. Mahdollisia syitä:
1. Azure SQL -tietokannan palvelutaso on keskeytetty
2. Tietokanta on pysäytetty
3. Ilmaisjakso on päättynyt

Korjaustoimenpiteet:
1. Tarkista Azure-portaalista tietokannan tila
2. Käynnistä tietokanta uudelleen Azure-portaalista
3. Tarkista palvelutaso ja päivitä tarvittaessa
4. Varmista laskutustiedot Azure-portaalista

Azure Portal: https://portal.azure.com
"""
        else:
            return False, f"⚠️ Yhteysvirhe: {str(e)}"
    except Exception as e:
        return False, f"⚠️ Odottamaton virhe: {str(e)}"

def scan_database_structure():
    """Skannaa tietokannan rakenne."""
    # Tarkista yhteys ensin
    connection_ok, error_message = check_database_connection()
    if not connection_ok:
        print(error_message)
        return None, None

    try:
        conn = pymssql.connect(
            server=server,
            user=f"{username}@{server.split('.')[0]}",
            password=password,
            database=database,
            timeout=30  # Pidempi timeout skannauksen ajaksi
        )
        cursor = conn.cursor(as_dict=True)

        # Hae taulut ja sarakkeet
        cursor.execute("""
            SELECT 
                c.TABLE_SCHEMA,
                c.TABLE_NAME,
                c.COLUMN_NAME,
                c.DATA_TYPE
            FROM INFORMATION_SCHEMA.COLUMNS c
            JOIN sys.tables t ON OBJECT_ID(c.TABLE_SCHEMA + '.' + c.TABLE_NAME) = t.object_id
            ORDER BY c.TABLE_SCHEMA, c.TABLE_NAME, c.COLUMN_NAME;
        """)
        columns = cursor.fetchall()

        # Hae vierasavainsuhteet
        cursor.execute("""
            SELECT 
                SCHEMA_NAME(tp.schema_id) AS parent_schema,
                tp.name AS parent_table,
                cp.name AS parent_column,
                SCHEMA_NAME(tr.schema_id) AS referenced_schema,
                tr.name AS referenced_table,
                cr.name AS referenced_column
            FROM sys.foreign_keys fk
            JOIN sys.foreign_key_columns fkc ON fk.object_id = fkc.constraint_object_id
            JOIN sys.tables tp ON fkc.parent_object_id = tp.object_id
            JOIN sys.columns cp ON fkc.parent_object_id = cp.object_id AND fkc.parent_column_id = cp.column_id
            JOIN sys.tables tr ON fkc.referenced_object_id = tr.object_id
            JOIN sys.columns cr ON fkc.referenced_object_id = cr.object_id AND fkc.referenced_column_id = cr.column_id
        """)
        relationships = cursor.fetchall()

        return columns, relationships

    except pymssql.Error as e:
        print(f"""
⚠️ Tietokantavirhe: {e}
📋 Vianetsintä:
1. Tarkista ympäristömuuttujat:
   - DB_SERVER: {server}
   - DB_NAME: {database}
   - DB_USER: {username}
2. Varmista että palomuurisäännöt sallivat yhteyden
3. Tarkista Azure SQL -tietokannan tila portaalista
""")
        return None, None
    except Exception as e:
        print(f"⚠️ Odottamaton virhe: {e}")
        return None, None
    finally:
        if 'conn' in locals():
            conn.close()

def find_required_tables(columns: List[Dict], relationships: List[Dict], required_fields: Dict[str, str]) -> Dict:
    """Etsi tarvittavat taulut ja niiden väliset suhteet."""
    field_locations = {}
    table_relationships = {}
    
    # Määritä päätaulu ja sen skeema
    main_table = "SalesLT.SalesOrderHeader"  # Tämä on päätaulu
    
    # Etsi sarakkeiden sijainnit ja varmista oikeat taulut
    field_table_mapping = {
        "ORDER_ID": "SalesOrderHeader",
        "CUSTOMER_ID": "Customer",
        "CUSTOMER_NAME": "Customer",
        "CUSTOMER_EMAIL": "Customer",
        "DUE_DATE": "SalesOrderHeader",
        "ORDER_LINE_ID": "SalesOrderDetail",
        "PRODUCT_ID": "Product",
        "PRODUCT_NAME": "Product",
        "QUANTITY": "SalesOrderDetail",
        "UNIT_PRICE": "SalesOrderDetail",
        "CUSTOMER_ADDRESS": "CustomerAddress"
    }

    # Etsi sarakkeiden sijainnit
    for field, expected_name in required_fields.items():
        target_table = field_table_mapping[field]
        for col in columns:
            if (col['COLUMN_NAME'].lower() == expected_name.lower() and 
                col['TABLE_NAME'] == target_table):
                field_locations[field] = {
                    'schema': col['TABLE_SCHEMA'],
                    'table': col['TABLE_NAME'],
                    'column': col['COLUMN_NAME']
                }
                break

    # Määritä tarvittavat JOIN-suhteet
    required_joins = [
        ("SalesOrderHeader", "Customer", "CustomerID"),
        ("Customer", "CustomerAddress", "CustomerID"),
        ("SalesOrderHeader", "SalesOrderDetail", "SalesOrderID"),
        ("SalesOrderDetail", "Product", "ProductID")
    ]

    # Rakenna JOIN-lausekkeet
    for parent_table, child_table, join_column in required_joins:
        key = f"SalesLT.{parent_table}"
        if key not in table_relationships:
            table_relationships[key] = []
        
        # Etsi vastaava suhde relationships-listasta
        for rel in relationships:
            if (rel['parent_table'] == parent_table and 
                rel['referenced_table'] == child_table and 
                (rel['parent_column'] == join_column or 
                 rel['referenced_column'] == join_column)):
                table_relationships[key].append({
                    'referenced_table': f"{rel['referenced_schema']}.{rel['referenced_table']}",
                    'parent_column': rel['parent_column'],
                    'referenced_column': rel['referenced_column']
                })
                break

    return field_locations, table_relationships

def generate_sql_query(field_locations: Dict, table_relationships: Dict) -> str:
    """Generoi SQL-kysely täsmälleen oikealla rakenteella."""
    
    # Määritä kiinteä järjestys SELECT-lauseelle
    select_order = [
        "ORDER_ID",
        "CUSTOMER_ID",
        "CUSTOMER_NAME",
        "CUSTOMER_EMAIL",
        "DUE_DATE",
        "ORDER_LINE_ID",
        "PRODUCT_ID",
        "PRODUCT_NAME",
        "QUANTITY",
        "UNIT_PRICE",
        "CUSTOMER_ADDRESS"
    ]

    # Rakenna SELECT-lauseke oikeassa järjestyksessä
    select_parts = []
    for field in select_order:
        location = field_locations[field]
        select_parts.append(
            f"{location['schema']}.{location['table']}.{location['column']} AS {field}"
        )

    # Määritä kiinteät JOIN-lausekkeet oikeassa järjestyksessä
    joins = [
        "JOIN SalesLT.Customer ON SalesLT.SalesOrderHeader.CustomerID = SalesLT.Customer.CustomerID",
        "JOIN SalesLT.CustomerAddress ON SalesLT.Customer.CustomerID = SalesLT.CustomerAddress.CustomerID",
        "JOIN SalesLT.SalesOrderDetail ON SalesLT.SalesOrderHeader.SalesOrderID = SalesLT.SalesOrderDetail.SalesOrderID",
        "JOIN SalesLT.Product ON SalesLT.SalesOrderDetail.ProductID = SalesLT.Product.ProductID"
    ]

    # Kokoa kysely
    select_clause = ",\n    ".join(select_parts)
    join_clause = "\n".join(joins)
    
    query = f"""SELECT
    {select_clause}
FROM SalesLT.SalesOrderHeader
{join_clause}
ORDER BY SalesLT.SalesOrderHeader.SalesOrderID;"""

    return query

def main():
    print("🔍 Skannataan tietokantarakennetta...")
    columns, relationships = scan_database_structure()
    
    if not columns or not relationships:
        print("⚠️ Tietokantarakennetta ei voitu lukea!")
        return

    print("🔍 Etsitään tarvittavia kenttiä...")
    field_locations, table_relationships = find_required_tables(columns, relationships, {
        "ORDER_ID": "SalesOrderID",
        "CUSTOMER_ID": "CustomerID",
        "CUSTOMER_NAME": "CompanyName",
        "CUSTOMER_EMAIL": "EmailAddress",
        "DUE_DATE": "DueDate",
        "ORDER_LINE_ID": "SalesOrderDetailID",
        "PRODUCT_ID": "ProductID",
        "PRODUCT_NAME": "Name",
        "QUANTITY": "OrderQty",
        "UNIT_PRICE": "UnitPrice",
        "CUSTOMER_ADDRESS": "AddressID"
    })

    # Tallenna skeemaraportti debug-tarkoituksiin
    with open("debug_schema.json", "w") as f:
        json.dump({
            "field_locations": field_locations,
            "table_relationships": table_relationships
        }, f, indent=2)

    try:
        print("📝 Generoidaan SQL-kyselyä...")
        sql_query = generate_sql_query(field_locations, table_relationships)
        
        with open("invoice_query.sql", "w") as f:
            f.write(sql_query)
        
        print("✅ SQL-kysely generoitu onnistuneesti!")
        print("📋 Debug-tiedot tallennettu: debug_schema.json")
        
    except Exception as e:
        print(f"⚠️ Virhe kyselyn generoinnissa: {e}")

if __name__ == "__main__":
    main()
