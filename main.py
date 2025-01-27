import sys
from db_handler import fetch_data
from invoice_generator import generate_invoice_files
from blob_handler import upload_files_to_blob

def main(query):
    # Fetch data from the database
    data = fetch_data(query)
    if not data:
        print("Failed to fetch data from the database.")
        return

    # Generate XML and PDF invoices
    invoice_files = generate_invoice_files(data)

    # Upload files to Azure Blob Storage
    upload_success = upload_files_to_blob(invoice_files)
    if upload_success:
        print("Files successfully uploaded to Azure Blob Storage.")
    else:
        print("Failed to upload files to Azure Blob Storage.")

if __name__ == "__main__":
    # Ensure a query is provided as an argument
    if len(sys.argv) < 2:
        print("Usage: python main.py '<SQL_QUERY>'")
        sys.exit(1)

    # Pass the query to main()
    query = sys.argv[1]
    main(query)
