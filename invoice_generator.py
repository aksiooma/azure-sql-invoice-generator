from lxml import etree
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import Table, TableStyle
import os
from db_handler import group_orders_by_invoice
from datetime import datetime

def sanitize_filename(value):
    """Sanitize filenames by replacing spaces and invalid characters."""
    return value.replace(" ", "_").replace("/", "_").replace("\\", "_").strip()

def generate_invoice_files():
    """
    Generate XML and PDF invoice files for each order.
    """
    orders = group_orders_by_invoice()
    invoice_files = []

    if not orders:
        print("⚠️ No orders found for invoice generation.")
        return None

    for order_id, items in orders.items():
        # Extract required fields
        customer_name = items[0].get("customerName", "Unknown")  
        billable_company = customer_name if customer_name != "Unknown" else "NoCompany"
        due_date = items[0].get("dueDate", "Unknown")  # ✅ Extract due date

        # Sanitize fields for filenames
        customer_filename = sanitize_filename(customer_name)
        billable_company = sanitize_filename(billable_company)

        # Ensure valid filename
        if customer_filename == "Unknown" or billable_company == "NoCompany":
            print(f"⚠️ Skipping invoice for order {order_id}: Missing customer details")
            continue  

        # Generate file names
        base_filename = f"{customer_filename}_{billable_company}_Invoice_{order_id}"
        xml_file = f"invoices/{base_filename}.xml"
        pdf_file = f"invoices/{base_filename}.pdf"

        # Ensure invoice directory exists
        os.makedirs("invoices", exist_ok=True)

        # ✅ FIX: Ensure function calls match their expected parameters
        generate_xml(order_id, customer_name, billable_company, due_date, items, xml_file)
        generate_pdf(order_id, customer_name, billable_company, due_date, items, pdf_file)

        # Append generated files to the list
        invoice_files.append((xml_file, pdf_file))

    return invoice_files

#XML
def generate_xml(order_id, customer_name, billable_company, due_date, items, filename):
    """
    Generate an XML invoice file for a grouped order.
    """
    # Generate today's date for invoice creation
    creation_date = datetime.today().strftime("%Y-%m-%d")

    root = etree.Element("Invoice")
    etree.SubElement(root, "OrderID").text = str(order_id)
    etree.SubElement(root, "CreationDate").text = creation_date
    etree.SubElement(root, "CustomerName").text = customer_name
    etree.SubElement(root, "BillableCompany").text = billable_company
    etree.SubElement(root, "DueDate").text = str(due_date)
    items_element = etree.SubElement(root, "Items")

    # Loop through items in the order
    for item in items:
        item_element = etree.SubElement(items_element, "Item")
        etree.SubElement(item_element, "ProductName").text = item.get("productName", "Unknown")
        etree.SubElement(item_element, "Quantity").text = str(item.get("quantity", 0))
        etree.SubElement(item_element, "UnitPrice").text = str(item.get("unitPrice", 0))
        etree.SubElement(item_element, "TotalPrice").text = str(item.get("totalPrice", 0))

    tree = etree.ElementTree(root)
    tree.write(filename, pretty_print=True, xml_declaration=True, encoding="UTF-8")
    print(f"✅ Generated XML: {filename}")

#PDF
def generate_pdf(order_id, customer_name, billable_company, due_date, items, filename):
    """
    Generate a well-formatted PDF invoice file for a grouped order.
    """
    c = canvas.Canvas(filename, pagesize=A4)
    width, height = A4  # Get page dimensions

    # Generate today's date for invoice creation
    creation_date = datetime.today().strftime("%Y-%m-%d")

    # Header
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, height - 50, "[LOGO]")  # Placeholder for logo
    c.setFont("Helvetica-Bold", 12)
    c.drawString(400, height - 50, "Invoice")
    c.drawString(400, height - 70, f"Invoice ID: {order_id}")
    c.drawString(400, height - 90, f"Creation Date: {creation_date}")

    # Due Date
    c.setFont("Helvetica", 10)
    c.drawString(50, height - 100, f"Due Date: {due_date}")

    # Customer Information
    c.setFont("Helvetica-Bold", 10)
    c.drawString(50, height - 130, "Billed to:")
    c.setFont("Helvetica", 10)
    c.drawString(50, height - 145, f"{customer_name}")
    c.drawString(50, height - 160, f"{billable_company}")

    # Move cursor down for the table
    y_position = height - 200

    # Table Data (Headers + Items)
    table_data = [["Product", "Qty", "Price (€)", "Amount (€)"]] 
    total_amount = 0

    for item in items:
        product_name = item.get("productName", "Unknown")
        quantity = item.get("quantity", 0)
        unit_price = item.get("unitPrice", 0)
        total_price = item.get("totalPrice", 0)
        total_amount += total_price

        table_data.append([product_name, str(quantity), f"{unit_price:.2f}", f"{total_price:.2f}"])

    # Add Total Row
    table_data.append(["", "", "Total", f"{total_amount:.2f}"])

    # Define Table
    table = Table(table_data, colWidths=[250, 50, 80, 80])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.grey), 
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white), 
        ("ALIGN", (1, 1), (-1, -1), "CENTER"), 
        ("GRID", (0, 0), (-1, -1), 0.5, colors.black), 
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 5),
        ("TOPPADDING", (0, 0), (-1, 0), 5),
        ("BACKGROUND", (0, -1), (-1, -1), colors.lightgrey), 
        ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
    ]))

    # Draw Table
    table.wrapOn(c, width, height)
    table.drawOn(c, 50, y_position - (len(table_data) * 20))

    # Save PDF
    c.save()
    print(f"✅ Generated PDF: {filename}")