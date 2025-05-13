# paste_crops.py

import os
import json
from PIL import Image
from PyQt5.QtWidgets import QFileDialog, QMessageBox
from tqdm import tqdm 

def paste_edited_crops_dialog(parent=None):
    # Prompt user to select the JSON file containing coordinates
    json_path, _ = QFileDialog.getOpenFileName(parent, "Select JSON File", "", "JSON Files (*.json)")
    if not json_path:
        return

    # Prompt user to select the main image onto which crops will be pasted
    main_image_path, _ = QFileDialog.getOpenFileName(parent, "Select Main Image", "", "Image Files (*.png *.jpg *.jpeg *.bmp)")
    if not main_image_path:
        return

    # Prompt user to select the folder containing edited crop images
    edited_folder = QFileDialog.getExistingDirectory(parent, "Select Folder Containing Edited Crops")
    if not edited_folder:
        return

    # Attempt to read the JSON file
    try:
        with open(json_path, "r") as f:
            coords_data = json.load(f)
    except Exception as e:
        show_message("Error", f"Failed to load JSON: {e}", parent)
        return

    # Attempt to load the main image and convert it to RGBA mode for transparency support
    try:
        original_img = Image.open(main_image_path).convert("RGBA")
    except Exception as e:
        show_message("Error", f"Failed to load main image: {e}", parent)
        return

    # Iterate over all regions defined in the JSON file
    for key in tqdm(coords_data, desc="Pasting edited crops"):
        coords = coords_data[key]
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

    # Prompt user to save the final image
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
