# paste_crops.py

import os
import json
from PIL import Image
from PyQt5.QtWidgets import QFileDialog, QMessageBox

def paste_edited_crops_dialog(parent=None):
    json_path, _ = QFileDialog.getOpenFileName(parent, "Select JSON File", "", "JSON Files (*.json)")
    if not json_path:
        return

    main_image_path, _ = QFileDialog.getOpenFileName(parent, "Select Main Image", "", "Image Files (*.png *.jpg *.jpeg *.bmp)")
    if not main_image_path:
        return

    edited_folder = QFileDialog.getExistingDirectory(parent, "Select Folder Containing Edited Crops")
    if not edited_folder:
        return

    try:
        with open(json_path, "r") as f:
            coords_data = json.load(f)
    except Exception as e:
        show_message("Error", f"Failed to load JSON: {e}", parent)
        return

    try:
        original_img = Image.open(main_image_path).convert("RGBA")
    except Exception as e:
        show_message("Error", f"Failed to load main image: {e}", parent)
        return

    for key, coords in coords_data.items():
        edited_path = os.path.join(edited_folder, f"{key}.png")
        if not os.path.exists(edited_path):
            show_message("Warning", f"Missing edited image: {key}", parent)
            continue

        try:
            edited_img = Image.open(edited_path).convert("RGBA")
            expected_size = (coords['width'], coords['height'])
            if edited_img.size != expected_size:
                edited_img = edited_img.resize(expected_size)

            original_img.paste(edited_img, (coords['x'], coords['y']), edited_img)
        except Exception as e:
            show_message("Error", f"Failed on region {key}: {e}", parent)

    output_path, _ = QFileDialog.getSaveFileName(parent, "Save Final Image", "", "PNG Files (*.png)")
    if output_path:
        try:
            original_img.save(output_path)
            show_message("Success", f"Saved image to: {output_path}", parent)
        except Exception as e:
            show_message("Error", f"Could not save: {e}", parent)

def show_message(title, message, parent=None):
    msg = QMessageBox(parent)
    msg.setWindowTitle(title)
    msg.setText(message)
    msg.exec_()
