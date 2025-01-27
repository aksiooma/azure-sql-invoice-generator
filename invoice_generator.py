from lxml import etree
from reportlab.pdfgen import canvas

def generate_invoice_files(data):
    """
    Generate XML and PDF invoice files for each record in the data.

    Args:
        data (list): List of dictionaries containing invoice data.

    Returns:
        list: A list of tuples with XML and PDF filenames.
    """
    invoice_files = []
    for record in data:
        # Extract required fields for file naming
        firstname = record.get("firstname", "Unknown")
        surname = record.get("surname", "Unknown")
        billable_company = record.get("billable_company", "Unknown")
        
        # Sanitize fields for filenames
        firstname = firstname.replace(" ", "_")
        surname = surname.replace(" ", "_")
        billable_company = billable_company.replace(" ", "_")
        
        # Generate file names
        base_filename = f"{firstname}_{surname}_{billable_company}_Invoice"
        xml_file = f"invoices/{base_filename}.xml"
        pdf_file = f"invoices/{base_filename}.pdf"

        # Generate XML and PDF files
        generate_xml(record, xml_file)
        generate_pdf(record, pdf_file)

        # Append generated files to the list
        invoice_files.append((xml_file, pdf_file))
    
    return invoice_files

def generate_xml(data, filename):
    """
    Generate an XML invoice file from the data.

    Args:
        data (dict): Invoice data.
        filename (str): File path to save the XML file.
    """
    root = etree.Element("Invoice")
    etree.SubElement(root, "OrderID").text = str(data.get("order_id", "Unknown"))
    etree.SubElement(root, "CustomerName").text = f"{data.get('firstname', '')} {data.get('surname', '')}"
    etree.SubElement(root, "BillableCompany").text = data.get("billable_company", "Unknown")
    etree.SubElement(root, "Amount").text = str(data.get("amount", "0"))

    tree = etree.ElementTree(root)
    tree.write(filename, pretty_print=True, xml_declaration=True, encoding="UTF-8")
    print(f"Generated XML: {filename}")

def generate_pdf(data, filename):
    """
    Generate a PDF invoice file from the data.

    Args:
        data (dict): Invoice data.
        filename (str): File path to save the PDF file.
    """
    c = canvas.Canvas(filename)
    c.drawString(100, 750, f"Invoice for Order {data.get('order_id', 'Unknown')}")
    c.drawString(100, 730, f"Customer: {data.get('firstname', 'Unknown')} {data.get('surname', 'Unknown')}")
    c.drawString(100, 710, f"Billable Company: {data.get('billable_company', 'Unknown')}")
    c.drawString(100, 690, f"Amount: {data.get('amount', '0')} EUR")
    c.save()
    print(f"Generated PDF: {filename}")
