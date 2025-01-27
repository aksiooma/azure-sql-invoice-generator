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
   - Test connectivity to Azure SQL Database using `pyodbc`.
   - Test file upload to Azure Blob Storage using `azure-storage-blob`.
   
3. **Start Coding:**
   - Draft the Python script for data fetching, file generation, and uploading.

---

## Progress Tracking
- [ ] Validate SQL Database credentials.
- [ ] Validate Blob Storage credentials.
- [ ] Ensure dependencies and project setup are complete.

# Integration Script

The integration will be implemented in five stages:

1. ## Read Data from Database

    - ### Objective: Fetch data from the customers, products, orders, and orderLines tables using SQL queries.
    - ### Implementation:
        - Use pyodbc to query the database and retrieve data.
        - Ensure the results are properly structured for easy mapping.
        - Validate that the data contains the required fields for generating invoices.

## Current Status:

  - Database Connection: Failed to establish a connection to the Azure SQL Database due to a HYT00 login timeout error.
  - Blob Storage: Blob storage connectivity has not been tested due to the failed connection.
  - Code Testing: Not completed due to database connection failure.

## Next Steps
  - Resolve the database connection issue (HYT00 timeout).
  - Test each module (db_handler.py, invoice_generator.py, blob_handler.py) independently to verify functionality.
  - Integrate the modules and run end-to-end tests.
  - Document the final integration process.

### **Integration Flow Summary**

1. **Database Connection**:
   - Connect to the company's Azure SQL Database to fetch data from the tables: `Customers`, `Orders`, `OrderLines`, and `Products`.

2. **Data Fetching**:
   - Extract customer, order, and product information by joining the database tables.

3. **Invoice Generation**:
   - Create invoice files in **XML** and **PDF** formats using the fetched data.
   - Name files as `[Firstname]_[Surname]_[BillableCompany]_Invoice.xml/pdf`.

4. **File Upload**:
   - Upload the generated invoice files to Azure Blob Storage for third-party processing.

This flow automates the entire process of fetching data, generating invoices, and uploading them for further use.


### Yhteenveto:

1. **Tietokantayhteys**:
   - Yhdistetään yrityksen Azure SQL -tietokantaan ja haetaan tiedot seuraavista tauluista: `Customers`, `Orders`, `OrderLines` ja `Products`. Epäonnistuin luomaan yhteyden aikamääreessä.

2. **Tietojen haku**:
   - Poimitaan asiakkaiden, tilausten ja tuotteiden tiedot yhdistämällä taulut. 
   - python main.py "SELECT * FROM orders"

3. **Laskujen generointi**:
   - Luodaan laskutiedostot **XML**- ja **PDF**-muodoissa haettujen tietojen perusteella.
   - Tiedostot nimetään muodossa `[Etunimi]_[Sukunimi]_[LaskutettavaYritys]_Invoice.xml/pdf`.

4. **Tiedostojen lähetys**:
   - Laskutiedostot ladataan Azure Blob Storage -säilöön kolmannen osapuolen käsittelyä varten.


