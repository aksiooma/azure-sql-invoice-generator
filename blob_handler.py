from azure.storage.blob import BlobServiceClient

def upload_files_to_blob(files):
    try:
        # Azure Blob Storage connection
        blob_service_client = BlobServiceClient.from_connection_string("<your_connection_string>")
        container_name = "<your_container_name>"

        for xml_file, pdf_file in files:
            # Upload XML file
            with open(xml_file, "rb") as data:
                blob_service_client.get_blob_client(container=container_name, blob=xml_file).upload_blob(data)

            # Upload PDF file
            with open(pdf_file, "rb") as data:
                blob_service_client.get_blob_client(container=container_name, blob=pdf_file).upload_blob(data)

        return True
    except Exception as e:
        print(f"Error uploading files to blob: {e}")
        return False
