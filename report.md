# Integration Development Plan: XML/PDF Invoices to Azure Blob Storage

---

## Project Overview
This integration system will:
1. Extract data from Azure SQL database tables (`customers`, `products`, `orders`, `orderLines`).
2. Generate XML and PDF invoices for each order.
3. Upload the files to an Azure Blob Storage container.

---

## Prerequisites Checklist
- **Azure SQL Database:**
  - Obtain connection string and credentials.
  - Ensure IP address is allowed in the database firewall.

- **Azure Blob Storage:**
  - Obtain Blob Storage connection string.
  - Verify the container exists (named after the developer).

- **Development Environment:**
  - Install Python libraries: `pyodbc`, `azure-storage-blob`, `lxml`, `reportlab`.
  - Set up a project structure:
    ```
    integration-project/
    ├── invoices/             # For temporary files (XML and PDF invoices)
    ├── main.py               # Main script to orchestrate the integration
    ├── db_handler.py         # Module for database connection and data fetching
    ├── invoice_generator.py  # Module for generating XML and PDF invoice files
    ├── blob_handler.py       # Module for uploading files to Azure Blob Storage
    ├── requirements.txt      # Dependencies for the project
    └── README.md             # Project documentation
    ```

---

## Next Steps

- The development enviroment used in this project is WSL (Windows Subsystem Linux - Ubuntu) + VENV. Initially Docker was planned but had early problems with the setup.

1. **Create Virtual Environment (Venv):**
    - Use WSL to create a Python virtual environment for integration development.

2. **Validate Access:**
   - Test connectivity to Azure SQL Database using `pyodbc`. Did not work with pyodbc.
   - Test connectivity to Azure SQL Database using `pymssql`. Changing to pymssql worked.
   - Test file upload to Azure Blob Storage using `azure-storage-blob`.
   
3. **Start Coding:**
   - Draft the Python script for data fetching, file generation, and uploading.

---

## Progress Tracking
- [X] Validate SQL Database credentials.
- [x] Validate Blob Storage credentials.
- [X] Ensure dependencies and project setup are complete.

# Integration Script

The integration will be implemented in five stages:

1. ## Read Data from Database

    - ### Objective: Fetch data from the customers, products, orders, and orderLines tables using SQL queries.
    - ### Implementation:
        - Use pyodbc to query the database and retrieve data.
        - Ensure the results are properly structured for easy mapping.
        - Validate that the data contains the required fields for generating invoices.

## Current Status:

  - Database Connection: establishe a connection to the Azure SQL Database after a HYT00 login timeout error.
  - Blob Storage: Blob storage connectivity has been tested and working
  - Code Testing: Manually tested. No automation.

## Next Steps
  - Resolve the database connection issue (HYT00 timeout). [✅FIXED]
  - Test each module (db_handler.py, invoice_generator.py, blob_handler.py) independently to verify functionality. [TESTED_MANUALLY]
  - Integrate the modules and run end-to-end tests.
  - Document the final integration process. [✅]

### **✅ Updated Integration Flow Summary**

#### **1. Database Connection**
- **Switched from `pyodbc` to `pymssql`** for connecting to Azure SQL Database.
- Fetch data from the tables: `customers`, `orders`, `orderLines`, and `products`.

#### **2. Data Fetching**
- Extract detailed order data, including **customer info, products, quantities, and prices**.
- Ensure correct field mapping based on the actual database schema.

#### **3. Invoice Generation**
- **Generate invoices in XML & PDF** formats using `lxml` and `reportlab`.
- **Include key details**: Order ID, Due Date, Creation Date, Customer & Billing Info.
- **File Naming Convention**:  

#### **4. File Upload**
- **Switched to SAS URL authentication** for **Azure Blob Storage**.
- Use `BlobServiceClient(account_url=sas_url)` instead of a connection string.
- **Ensure correct filenames** and **overwrite existing files if needed**.

This integration **automates the entire process** of fetching data, generating invoices, and uploading them for further use. 🚀


### Yhteenveto:

1. **Tietokantayhteys**:
   - Yhdistetään yrityksen Azure SQL -tietokantaan ja haetaan tiedot seuraavista tauluista: `Customers`, `Orders`, `OrderLines` ja `Products`.

2. **Tietojen haku**:
   - Poimitaan asiakkaiden, tilausten ja tuotteiden tiedot yhdistämällä taulut. 
   - python main.py "SELECT * FROM orders" suorittaa skriptin

3. **Laskujen generointi**:
   - Luodaan laskutiedostot **XML**- ja **PDF**-muodoissa haettujen tietojen perusteella.
   - Tiedostot nimetään muodossa `[Etunimi]_[Sukunimi]_[LaskutettavaYritys]_Invoice.xml/pdf`.

4. **Tiedostojen lähetys**:
   - Laskutiedostot ladataan Azure Blob Storage -säilöön kolmannen osapuolen käsittelyä varten.


