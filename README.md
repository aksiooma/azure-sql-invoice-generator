# **Integraatioprojekti: Azure SQL → Laskujen Generointi → Azure Blob Storage**

## **📌 Yleiskatsaus**
Tämä projekti automatisoi **laskujen luomisen ja tallentamisen pilveen** seuraavilla vaiheilla:
1. **Haetaan tilausdata Azure SQL -tietokannasta**  
2. **Generoidaan laskut XML- ja PDF-muodossa**  
3. **Lähetetään laskut Azure Blob Storageen** kolmannen osapuolen käyttöön  

Teknologiat: **Python, pymssql, lxml, reportlab, Azure Blob Storage**

---

# 🚀 Käyttöönotto

## 1️⃣ Asenna riippuvuudet

        pip install -r requirements.txt

## 2️⃣ Lisää ympäristömuuttujat
```
DB_SERVER=<sql_server_nimi>.database.windows.net
DB_NAME=<tietokannan_nimi>
DB_USER=<käyttäjänimi>
DB_PASSWORD=<salasana>
BLOB_STRING=<azure_blob_sas_url>
BLOB_CONTAINER=<container_nimi>
```

## **📂 Projektin Rakenne**
```plaintext
integration-project/
├── invoices/             # Generoidut laskutiedostot
├── db_handler.py         # SQL-yhteys ja tietojen haku
├── invoice_generator.py  # Laskujen XML/PDF-generointi
├── blob_handler.py       # Azure Blob Storage -tiedostonsiirto
├── main.py               # Integraation ajoskripti
├── connection.py         # SQL-yhteyden testaamiseen
├── requirements.txt      # Projektin riippuvuudet
└── README.md             # Tämä tiedosto
```

## 3️⃣ Suorita integraatio

- ```python main.py "SELECT * FROM orders"```

## **Integraatioprojektin Esittely**

### **Miksi Python?**
- Python valittiin, koska se soveltuu hyvin konsolipohjaisten ratkaisujen rakentamiseen ja testaamiseen.
- Konsolipohjainen toteutus helpotti:
  - Tietokantayhteyden testausta.
  - Tilausten käsittelyn ja laskujen generoinnin testausta.
- Jos kaikki toiminnot toimisivat, seuraava vaihe olisi rakentaa käyttäjäystävällinen UI.

### **Docker ja Ympäristöhaasteet**
- Dockerin käyttöä harkittiin kehitysympäristön yhdenmukaistamiseksi, mutta asennuksen aikana ilmeni ongelmia:
  - ODBC-ajurien asentaminen WSL:ssä ei toiminut odotetusti.
  - Azure SQL -yhteyden luonti ei onnistunut helposti.
- Lopulta päätettiin käyttää VENV:illä luotua **Python-ympäristöä** WSL:ssä ilman Dockeria.

### **Python-kirjastot**
- **pymssql**: Tietokantayhteyden luomiseen ja SQL-kyselyjen suorittamiseen.  
- **lxml**: XML-tiedostojen generointiin laskutietoja varten.  
- **azure-storage-blob**: Laskutiedostojen siirtoon Azure Blob Storageen.  
- **reportlab**: PDF-laskujen generointiin.

### **Toteutuksen Toiminnot**
1. **Yhteys Azure SQL -tietokantaan**  
   - **ODBC korvattiin `pymssql`:llä**, mikä mahdollisti vakaamman yhteyden.  
2. **Tietojen haku**  
   - SQL-kyselyillä haetaan asiakkaiden, tilausten ja tuotteiden tiedot.  
3. **Laskuparin generointi**  
   - Tilauksista luodaan **XML- ja PDF-tiedostot**, jotka sisältävät asiakastiedot ja eritellyt ostot.  
4. **Tiedostojen lähetys**  
   - Generoidut laskut siirretään **Azure Blob Storageen SAS-avaimen kautta**.

### **Kiteytys**
- **Python tarjosi joustavan alustan** integraation toteuttamiselle ja testaamiselle.  
- **Dockerin käyttöönotto ei onnistunut**, joten siirryttiin suoraan Python-ympäristöön.  
- Toteutus sisältää **tietokantayhteyden, laskujen generoinnin ja pilvitallennuksen**.  
- **Seuraavat vaiheet:**  
  - SQL-yhteyden optimointi ja virheenkäsittely.  
  - Toiminnallisuuden laajentaminen ja testaus.  
