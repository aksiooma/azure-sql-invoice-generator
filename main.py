from db_handler import group_orders_by_invoice
from invoice_generator import generate_invoice_files
from blob_handler import upload_files_to_blob

def main():
    """
    Main function to fetch data, generate invoices, and upload to Azure Blob Storage.
    """
    # Fetch and group order details
    orders = group_orders_by_invoice()
    
    if not orders:
        print("⚠️ No orders found. Exiting.")
        return

    # Generate XML and PDF invoices
    invoice_files = generate_invoice_files()
    
    if not invoice_files:
        print("⚠️ No invoices were generated. Exiting.")
        return

    # # Upload invoices to Azure Blob Storage
    upload_success = upload_files_to_blob(invoice_files)
    
    if upload_success:
        print("✅ Files successfully uploaded to Azure Blob Storage.")
    else:
        print("⚠️ Failed to upload files to Azure Blob Storage.")

if __name__ == "__main__":
    main()
