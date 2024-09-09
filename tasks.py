from robocorp.tasks import task
from robocorp import browser

from RPA.HTTP import HTTP
from RPA.Tables import Tables
from RPA.PDF import PDF
from RPA.Archive import Archive

@task
def order_robots_from_RobotSpareBin():
    """
    Orders robots from RobotSpareBin Industries Inc.
    Saves the order HTML receipt as a PDF file.
    Saves the screenshot of the ordered robot.
    Embeds the screenshot of the robot to the PDF receipt.
    Creates ZIP archive of the receipts and the images.
    """
    browser.configure(slowmo=200)
    open_robot_order_website()
    enter_orders_and_save_receipts()
    archive_receipts('output/receipts/', 'receipts.zip')

page = browser.page()
pdf = PDF()

def get_orders():
    """Downloads csv file from the given URL"""
    http = HTTP()
    http.download(url="https://robotsparebinindustries.com/orders.csv", overwrite=True) 

    """Save orders to the table variable"""  
    table = Tables()
    return table.read_table_from_csv("orders.csv")

def open_robot_order_website():
    browser.goto("https://robotsparebinindustries.com/#/robot-order")

def enter_orders_and_save_receipts():
    orders = get_orders()

    for order in orders:
        order_number = order["Order number"]
        alert = page.locator(".alert-danger")
        receipt = page.locator("#receipt")
    
        fill_form(order)
        if alert.count() > 0:
            while not alert.count() == 0:
                page.click("#order")
        
        receipt_path = store_receipt_as_pdf(order_number)
        screenshot_path = screenshot_robot(order_number)
        embed_screenshot_to_receipt(screenshot_path, receipt_path)
        page.click("#order-another")          
        
        if receipt.count() > 0:
            page.click("#order-another")
            
def close_annoying_modal():
    page.click("button:text('OK')")

def fill_form(order):
    close_annoying_modal()

    page.select_option ("#head", str(order["Head"]))
    body_part_number = order["Body"]
    page.check(f"#id-body-{body_part_number}")
    page.fill("input[placeholder='Enter the part number for the legs']", order["Legs"])
    page.fill("#address", order["Address"])
    page.click("#order")

def store_receipt_as_pdf(order_number):
    receipt = page.locator("#receipt").inner_html()
    receipt_path = f"output/receipts/{order_number}_robot_receipt.pdf"
    pdf.html_to_pdf(receipt, receipt_path)
    return receipt_path

def screenshot_robot(order_number):
    robot = page.locator("#robot-preview-image")
    screenshot_path = f"output/screenshots/{order_number}_robot_screenshot.png"
    robot.screenshot(path=screenshot_path)
    return screenshot_path

def embed_screenshot_to_receipt(screenshot, pdf_file): 
    pdf.add_watermark_image_to_pdf(
        image_path=screenshot,
        source_path=pdf_file,
        output_path=pdf_file
    )

def archive_receipts(folder_name, archive_name):
    lib = Archive()
    lib.archive_folder_with_zip(folder_name, archive_name)
