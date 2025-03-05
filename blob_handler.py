import os
from datetime import datetime

# Environment variables
blob_sas_url = os.getenv("BLOB_STRING")
blob_container = os.getenv("BLOB_CONTAINER")

def upload_files_to_blob(files):
    """
    Tallenna tiedostot paikallisesti, koska Azure Blob Storage ei ole käytettävissä.
    """
    try:
        # Luo output-kansio jos ei ole olemassa
        local_output = "output_files"
        os.makedirs(local_output, exist_ok=True)
        
        for xml_file, pdf_file in files:
            # Kopioi XML
            if os.path.exists(xml_file):
                new_xml = os.path.join(local_output, os.path.basename(xml_file))
                with open(xml_file, "rb") as src, open(new_xml, "wb") as dst:
                    dst.write(src.read())
                print(f"✅ Tallennettu paikallisesti: {new_xml}")

            # Kopioi PDF
            if os.path.exists(pdf_file):
                new_pdf = os.path.join(local_output, os.path.basename(pdf_file))
                with open(pdf_file, "rb") as src, open(new_pdf, "wb") as dst:
                    dst.write(src.read())
                print(f"✅ Tallennettu paikallisesti: {new_pdf}")

        print(f"""
✅ Tiedostot tallennettu paikallisesti kansioon '{local_output}'
⚠️ Azure Blob Storage ei käytettävissä - tilaus deaktivoitu.

Voit:
1. Aktivoida Azure-tilauksen uudelleen
2. Jatkaa tiedostojen paikallista tallennusta
""")
        return True

    except Exception as e:
        print(f"⚠️ Virhe tiedostojen tallennuksessa: {str(e)}")
        return False