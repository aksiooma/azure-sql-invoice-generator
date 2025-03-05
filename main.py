from db_handler import group_orders_by_invoice
from invoice_generator import generate_invoice_files
from blob_handler import upload_files_to_blob
from scan_schema import check_database_connection

def main():
    """
    Main function to fetch data, generate invoices, and upload to Azure Blob Storage.
    """
    # Tarkista tietokantayhteys ensin
    connection_ok, error_message = check_database_connection()
    if not connection_ok:
        print(error_message)
        return

    try:
        # Fetch and group order details
        print("📊 Haetaan tilauksia...")
        orders = group_orders_by_invoice()
        
        if not orders:
            print("⚠️ Tilauksia ei löytynyt. Lopetetaan.")
            return

        # Generate XML and PDF invoices
        print("📄 Generoidaan laskuja...")
        invoice_files = generate_invoice_files()
        
        if not invoice_files:
            print("⚠️ Laskuja ei voitu generoida. Lopetetaan.")
            return

        # Upload invoices to Azure Blob Storage
        print("☁️ Ladataan tiedostoja Azure Blob Storageen...")
        upload_success = upload_files_to_blob(invoice_files)
        
        if upload_success:
            print("✅ Tiedostot ladattu onnistuneesti Azure Blob Storageen.")
        else:
            print("⚠️ Tiedostojen lataus Azure Blob Storageen epäonnistui.")

    except Exception as e:
        print(f"""
⚠️ Virhe ohjelman suorituksessa: {str(e)}

Vianetsintä:
1. Tarkista että tietokantayhteys toimii
2. Varmista että kaikki ympäristömuuttujat on asetettu
3. Tarkista Azure-palveluiden tila

Voit ajaa yksittäiset vaiheet erikseen:
1. python scan_schema.py (tietokantayhteyden testaus)
2. python db_handler.py (tilausten haku)
3. python invoice_generator.py (laskujen generointi)
""")

if __name__ == "__main__":
    main()
