from azure.storage.blob import BlobServiceClient
import os

# Environment variables
blob_sas_url = os.getenv("BLOB_STRING")
blob_container = os.getenv("BLOB_CONTAINER")

def upload_files_to_blob(files):
    try:
        # Use the SAS URL to connect to Azure Blob Storage
        blob_service_client = BlobServiceClient(account_url=blob_sas_url)
        container_name = blob_container

        for xml_file, pdf_file in files:
            # Upload XML file
            with open(xml_file, "rb") as data:
                blob_service_client.get_blob_client(container=container_name, blob=xml_file).upload_blob(data)

            # Upload PDF file
            with open(pdf_file, "rb") as data:
                blob_service_client.get_blob_client(container=container_name, blob=pdf_file).upload_blob(data)

        print("✅ Files successfully uploaded to Azure Blob Storage.")
        return True

    except Exception as e:
        print(f"⚠️ Error uploading files to blob: {e}")
        return False