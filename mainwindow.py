from PyQt5.QtWidgets import QMainWindow, QToolBar, QAction, QPushButton, QVBoxLayout,QHBoxLayout, QWidget, QFileDialog, QLineEdit, QLabel, QFormLayout, QDialog, QDialogButtonBox,QInputDialog
from image_viewer import ImageViewer
from PyQt5.QtCore import Qt
from reportlab.pdfgen import canvas
import os
from PIL import Image  # Add this import at the top of your file
from algo import process_images_in_directory
from replace import paste_edited_crops_dialog
from crop import crop_images_by_json
from pdf import png_to_pdf


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Image Annotator")
        self.resize(1000, 800)

        central_widget = QWidget()
        layout = QVBoxLayout()
        self.viewer = ImageViewer()
        layout.addWidget(self.viewer)

        
# First horizontal button row
        top_button_layout = QHBoxLayout()
        self.open_button = QPushButton("Open Image", self)
        self.crop_button = QPushButton("Crop Boxes", self)
        self.processing_settings_button = QPushButton("Set Parameters", self)
        for btn in [self.open_button, self.crop_button, self.processing_settings_button]:
            btn.setFixedWidth(150)
            top_button_layout.addWidget(btn)
        
        # Connect buttons
        self.open_button.clicked.connect(self.open_image)
        self.crop_button.clicked.connect(self.viewer.crop_boxes)
        self.processing_settings_button.clicked.connect(self.open_processing_dialog)
        
        # Second horizontal button row
        bottom_button_layout = QHBoxLayout()
        self.paste_button = QPushButton("Paste Crops", self)
        self.cp_button = QPushButton("Crop by JSON", self)
        self.pdf_button = QPushButton("Convert to PDF", self)
        for btn in [self.paste_button, self.cp_button, self.pdf_button]:
            btn.setFixedWidth(150)
            bottom_button_layout.addWidget(btn)
        
        # Connect buttons
        self.paste_button.clicked.connect(lambda: paste_edited_crops_dialog(self))
        self.cp_button.clicked.connect(self.crop_by_json_dialog)
        self.pdf_button.clicked.connect(self.open_pdf_dialog)
        
        # Add both button rows to main layout
        layout.addLayout(top_button_layout)
        layout.addLayout(bottom_button_layout)
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        self.create_toolbar()

        # Default values for processing parameters
        self.kernel_size = 2
        self.percentage = 75
        self.compare_value = 100

    def create_toolbar(self):
        toolbar = QToolBar("Tools")
        self.addToolBar(toolbar)

        # Draw / Pan Toggle
        self.draw_action = QAction("Draw", self)
        self.draw_action.setCheckable(True)
        self.draw_action.triggered.connect(self.toggle_draw_mode)
        toolbar.addAction(self.draw_action)

        # Erase action in toolbar
        self.erase_action = QAction("Erase", self)
        self.erase_action.triggered.connect(lambda: self.viewer.toggle_erase_mode(True))
        toolbar.addAction(self.erase_action)

    def toggle_draw_mode(self, checked):
        if checked:
            self.draw_action.setText("Pan")
            self.viewer.enable_drawing(True)
        else:
            self.draw_action.setText("Draw")
            self.viewer.enable_drawing(False)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_O:
            self.open_image()
        elif event.key() == Qt.Key_D:
            self.draw_action.setChecked(True)
            self.toggle_draw_mode(True)
        elif event.key() == Qt.Key_P:
            self.draw_action.setChecked(False)
            self.toggle_draw_mode(False)
        elif event.key() == Qt.Key_E:
            self.viewer.toggle_erase_mode(True)  # Press 'E' to toggle erase mode
        else:
            super().keyPressEvent(event)

    def open_image(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Image", "", "Images (*.png *.jpg *.jpeg *.bmp)")
        if file_path:
            self.viewer.load_image(file_path)
   
   
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
   
    def png_to_pdf(self, png_path, pdf_path):
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
   
    def open_processing_dialog(self):
        dialog = ProcessingDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            # Get the values from the dialog and process the image
            self.kernel_size = dialog.kernel_size
            self.percentage = dialog.percentage
            self.compare_value = dialog.compare_value
            # Get input and output directories
            input_directory = QFileDialog.getExistingDirectory(self, "Select Input Directory")
            output_directory = QFileDialog.getExistingDirectory(self, "Select Output Directory")
            if input_directory and output_directory:
                # Call the image processing function
                process_images_in_directory(input_directory, output_directory, self.kernel_size, self.percentage, self.compare_value)


    def crop_by_json_dialog(self):
        image_path, _ = QFileDialog.getOpenFileName(self, "Select Image", "", "Images (*.png *.jpg *.jpeg *.bmp)")
        if not image_path:
            return
    
        json_path, _ = QFileDialog.getOpenFileName(self, "Select JSON File", "", "JSON Files (*.json)")
        if not json_path:
            return
    
        output_dir = QFileDialog.getExistingDirectory(self, "Select Output Directory")
        if not output_dir:
            return
    
        crop_images_by_json(image_path, json_path, output_dir)


class ProcessingDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Set Processing Parameters")
        self.setModal(True)

        self.kernel_size = 2
        self.percentage = 75
        self.compare_value = 100

        # Layout for the dialog
        layout = QFormLayout()

        # Kernel size input
        self.kernel_size_input = QLineEdit(self)
        self.kernel_size_input.setText(str(self.kernel_size))
        layout.addRow("Kernel Size (e.g., 2 for 2x2):", self.kernel_size_input)

        # Percentage threshold input
        self.percentage_input = QLineEdit(self)
        self.percentage_input.setText(str(self.percentage))
        layout.addRow("Percentage (e.g., 75 for 75%):", self.percentage_input)

        # Compare value input
        self.compare_value_input = QLineEdit(self)
        self.compare_value_input.setText(str(self.compare_value))
        layout.addRow("Compare Value (e.g., 150):", self.compare_value_input)

        # Add OK and Cancel buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

        layout.addWidget(button_box)
        self.setLayout(layout)

    def accept(self):
        # Update the parameters with the user's inputs
        try:
            self.kernel_size = int(self.kernel_size_input.text())
            self.percentage = int(self.percentage_input.text())
            self.compare_value = int(self.compare_value_input.text())
            super().accept()  # Close the dialog and return accepted
        except ValueError:
            print("Please enter valid numeric values for kernel size, percentage, and compare value.")
            return  # Stay in the dialog if values are invalid

    def reject(self):
        super().reject()  # Close the dialog without any changes

