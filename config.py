import os
from dotenv import load_dotenv

def load_config():
    """Load configuration from .env file and/or environment variables"""
    # Yritä ladata .env tiedosto jos se löytyy
    if os.path.exists('.env'):
        load_dotenv()
        print("✅ Ladattu asetukset .env tiedostosta")
    
    # Hae asetukset
    config = {
        "DB_SERVER": os.getenv("DB_SERVER"),
        "DB_NAME": os.getenv("DB_NAME"),
        "DB_USER": os.getenv("DB_USER"),
        "DB_PASSWORD": os.getenv("DB_PASSWORD"),
        "BLOB_STRING": os.getenv("BLOB_STRING"),
        "BLOB_CONTAINER": os.getenv("BLOB_CONTAINER")
    }
    
    # Tarkista pakolliset DB-asetukset
    missing_db = [k for k, v in config.items() if v is None and k.startswith("DB_")]
    if missing_db:
        print("""
⚠️ Tietokantayhteyden asetukset puuttuvat!

Varmista että joko:
1. Ympäristömuuttujat on asetettu tai
2. .env tiedosto sisältää seuraavat:

Puuttuvat asetukset:
{}
""".format("\n".join(f"- {key}" for key in missing_db)))
        return None
        
    return config 