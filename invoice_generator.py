from lxml import etree
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
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
    Asks for the number of customer invoices to generate.
    Skipped orders (due to missing details) do not count toward the total.
    """
    orders = group_orders_by_invoice()
    
    # Debug: Check what orders look like
    if not orders:
        print("⚠️ No orders found for invoice generation.")
        return None
    else:
        print(f"DEBUG: Found {len(orders)} order(s) for invoice generation.")
        for order_id, items in orders.items():
            print(f"DEBUG: Order ID: {order_id} - First item keys: {list(items[0].keys()) if items else 'No items'}")

    invoice_files = []

    # Ask user for the number of customer invoices to generate.
    target_count = None
    target_input = input("Enter number of customer invoices to generate (or press Enter for all): ").strip()
    if target_input:
        try:
            target_count = int(target_input)
            if target_count <= 0:
                print("Number must be positive. Invoices will be generated for all customers.")
                target_count = None
        except ValueError:
            print("Invalid number entered. Invoices will be generated for all customers.")

    successful_count = 0  # Count of successfully generated invoices

    for order_id, items in orders.items():
        # Check that there is at least one item in the order
        if not items:
            print(f"DEBUG: Skipping order {order_id} because it contains no items.")
            continue

        # Extract required fields using the correct keys.
        customer_name = items[0].get("CUSTOMER_NAME", "Unknown")
        billable_company = customer_name if customer_name != "Unknown" else "NoCompany"
        due_date = items[0].get("DUE_DATE", "Unknown")  # Extract due date

        # Debug: Show extracted values
        print(f"DEBUG: Order {order_id} - Customer: '{customer_name}', Due Date: '{due_date}'")

        # Sanitize fields for filenames
        customer_filename = sanitize_filename(customer_name)
        billable_company_sanitized = sanitize_filename(billable_company)

        # Ensure valid filename and required customer details.
        if customer_filename == "Unknown" or billable_company_sanitized == "NoCompany":
            print(f"⚠️ Skipping invoice for order {order_id}: Missing customer details (customer_name='{customer_name}')")
            continue

        # Generate file names
        base_filename = f"{customer_filename}_{billable_company_sanitized}_Invoice_{order_id}"
        xml_file = f"invoices/{base_filename}.xml"
        pdf_file = f"invoices/{base_filename}.pdf"

        # Ensure invoice directory exists
        os.makedirs("invoices", exist_ok=True)

        # Generate XML and PDF invoice files.
        try:
            generate_xml(order_id, customer_name, billable_company, due_date, items, xml_file)
            generate_pdf(order_id, customer_name, billable_company, due_date, items, pdf_file)
        except Exception as e:
            print(f"⚠️ Error generating invoice for order {order_id}: {e}")
            continue

        # Append generated files to the list and count the successful creation.
        invoice_files.append((xml_file, pdf_file))
        successful_count += 1
        print(f"DEBUG: Successfully generated invoice for order {order_id}.")

        # If a target count was provided and reached, stop processing further orders.
        if target_count is not None and successful_count >= target_count:
            print(f"Reached target of {target_count} customer invoices.")
            break

    print(f"DEBUG: Generated {successful_count} invoice(s) in total.")
    return invoice_files

# XML generation function
def generate_xml(order_id, customer_name, billable_company, due_date, items, filename):
    """
    Generate an XML invoice file for a grouped order.
    Calculates each line's total as quantity * unit_price.
    """
    creation_date = datetime.today().strftime("%Y-%m-%d")
    root = etree.Element("Invoice")
    etree.SubElement(root, "OrderID").text = str(order_id)
    etree.SubElement(root, "CreationDate").text = creation_date
    etree.SubElement(root, "CustomerName").text = customer_name
    etree.SubElement(root, "BillableCompany").text = billable_company
    etree.SubElement(root, "DueDate").text = str(due_date)
    items_element = etree.SubElement(root, "Items")

    for item in items:
        item_element = etree.SubElement(items_element, "Item")
        etree.SubElement(item_element, "ProductName").text = str(item.get("PRODUCT_NAME", "Unknown"))
        etree.SubElement(item_element, "Quantity").text = str(item.get("QUANTITY", 0))
        etree.SubElement(item_element, "UnitPrice").text = str(item.get("UNIT_PRICE", 0))
        # Calculate total price from quantity * unit_price
        quantity = item.get("QUANTITY", 0)
        unit_price = item.get("UNIT_PRICE", 0)
        try:
            total_price = quantity * unit_price
        except Exception:
            total_price = 0
        etree.SubElement(item_element, "TotalPrice").text = str(total_price)

    tree = etree.ElementTree(root)
    tree.write(filename, pretty_print=True, xml_declaration=True, encoding="UTF-8")
    print(f"✅ Generated XML: {filename}")

# PDF generation function
def generate_pdf(order_id, customer_name, billable_company, due_date, items, filename):
    """
    Generate a well-formatted PDF invoice file for a grouped order.
    Calculates each line's amount as quantity * unit_price and sums the totals.
    """
    c = canvas.Canvas(filename, pagesize=A4)
    width, height = A4

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

    # Table of items
    y_position = height - 200
    table_data = [["Product", "Qty", "Price (€)", "Amount (€)"]]
    total_amount = 0

    for item in items:
        product_name = item.get("PRODUCT_NAME", "Unknown")
        quantity = item.get("QUANTITY", 0)
        unit_price = item.get("UNIT_PRICE", 0)
        # Calculate total price as quantity * unit_price
        try:
            line_total = quantity * unit_price
        except Exception:
            line_total = 0

        total_amount += line_total
        table_data.append([product_name, str(quantity), f"{unit_price:.2f}", f"{line_total:.2f}"])

    table_data.append(["", "", "Total", f"{total_amount:.2f}"])

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

    table.wrapOn(c, width, height)
    table.drawOn(c, 50, y_position - (len(table_data) * 20))

    c.save()
    print(f"✅ Generated PDF: {filename}")

# For testing purposes, call generate_invoice_files() when this script is executed directly.
if __name__ == "__main__":
    generate_invoice_files()
