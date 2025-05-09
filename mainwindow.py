from PyQt5.QtWidgets import QMainWindow, QToolBar, QAction, QPushButton, QVBoxLayout, QWidget, QFileDialog, QLineEdit, QLabel, QFormLayout, QDialog, QDialogButtonBox
from image_viewer import ImageViewer
from PyQt5.QtCore import Qt
import os
from algo import process_images_in_directory
from replace import paste_edited_crops_dialog


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Image Annotator")
        self.resize(1000, 800)

        central_widget = QWidget()
        layout = QVBoxLayout()
        self.viewer = ImageViewer()
        layout.addWidget(self.viewer)

        # Add open image button
        self.open_button = QPushButton("Open Image", self)
        self.open_button.clicked.connect(self.open_image)
        layout.addWidget(self.open_button)

        # Add crop button
        self.crop_button = QPushButton("Crop Boxes", self)
        self.crop_button.clicked.connect(self.viewer.crop_boxes)
        layout.addWidget(self.crop_button)

        # Add processing settings button
        self.processing_settings_button = QPushButton("Set Processing Parameters", self)
        self.processing_settings_button.clicked.connect(self.open_processing_dialog)
        layout.addWidget(self.processing_settings_button)

        self.paste_button = QPushButton("Paste Edited Crops", self)
        self.paste_button.clicked.connect(lambda: paste_edited_crops_dialog(self))
        layout.addWidget(self.paste_button)
        

        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        self.create_toolbar()

        # Default values for processing parameters
        self.kernel_size = 2
        self.percentage = 75
        self.compare_value = 150

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

class ProcessingDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Set Processing Parameters")
        self.setModal(True)

        self.kernel_size = 2
        self.percentage = 75
        self.compare_value = 150

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
