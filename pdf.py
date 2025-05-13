from PyQt5.QtWidgets import QInputDialog
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import portrait

# Disable pixel limit to support large images
Image.MAX_IMAGE_PIXELS = None

def png_to_pdf(png_path, pdf_path):
    if not os.path.exists(png_path):
        print(f"Error: The file at {png_path} does not exist.")
        return

    img = Image.open(png_path)
    img = img.convert("RGB")
    width, height = img.size

    # Save image temporarily as JPEG
    temp_img_path = "temp_image.jpg"
    img.save(temp_img_path, "JPEG", quality=100)

    # Set the canvas size to match the image size
    c = canvas.Canvas(pdf_path, pagesize=(width, height))

    # Draw the image so it fills the page
    c.drawImage(temp_img_path, 0, 0, width, height)

    # Save and clean up
    c.save()
    os.remove(temp_img_path)

    print(f"PDF saved as {pdf_path}")
def open_pdf_dialog(self):
    # Step 1: Ask the user to select a PNG file
    png_path, _ = QFileDialog.getOpenFileName(self, "Open PNG File", "", "PNG Files (*.png)")
    if not png_path:
        return

    # Step 2: Ask the user to input a name for the PDF file
    pdf_name, ok = QInputDialog.getText(self, "Enter PDF Name", "Enter the name of the PDF (without extension):")
    if not ok or not pdf_name:
        return

    pdf_path = pdf_name + ".pdf"

    # Step 3: Call the function to convert the PNG to PDF
    self.png_to_pdf(png_path, pdf_path)