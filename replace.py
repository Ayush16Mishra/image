import os
import json
from PIL import Image
from PyQt5.QtWidgets import QFileDialog, QMessageBox
from tqdm import tqdm
import threading

def paste_edited_crops_dialog(parent=None):
    # Select JSON file
    json_path, _ = QFileDialog.getOpenFileName(parent, "Select JSON File", "", "JSON Files (*.json)")
    if not json_path:
        return

    # Select main image
    main_image_path, _ = QFileDialog.getOpenFileName(parent, "Select Main Image", "", "Image Files (*.png *.jpg *.jpeg *.bmp)")
    if not main_image_path:
        return

    # Select folder with edited crops
    edited_folder = QFileDialog.getExistingDirectory(parent, "Select Folder Containing Edited Crops")
    if not edited_folder:
        return

    # Load JSON
    try:
        with open(json_path, "r") as f:
            coords_data = json.load(f)
    except Exception as e:
        show_message("Error", f"Failed to load JSON: {e}", parent)
        return

    # Load main image
    try:
        original_img = Image.open(main_image_path).convert("RGBA")
    except Exception as e:
        show_message("Error", f"Failed to load main image: {e}", parent)
        return

    # Shared lock for thread-safe image pasting
    paste_lock = threading.Lock()

    # Split the work into two chunks
    keys = list(coords_data.keys())
    midpoint = len(keys) // 2
    chunks = [keys[:midpoint], keys[midpoint:]]

    def paste_worker(thread_keys, thread_id):
        for key in tqdm(thread_keys, desc=f"Thread {thread_id}", position=thread_id):
            coords = coords_data[key]
            edited_path = os.path.join(edited_folder, f"{key}.png")
            if not os.path.exists(edited_path):
                tqdm.write(f"[Thread {thread_id}] Warning: Missing edited image: {key}")
                continue
            try:
                edited_img = Image.open(edited_path).convert("RGBA")
                expected_size = (coords['width'], coords['height'])
                if edited_img.size != expected_size:
                    edited_img = edited_img.resize(expected_size)

                # Thread-safe paste
                with paste_lock:
                    original_img.paste(edited_img, (coords['x'], coords['y']), edited_img)

            except Exception as e:
                print(f"[Thread {thread_id}] Error on region {key}: {e}")

    # Start both threads
    threads = []
    for i in range(2):
        t = threading.Thread(target=paste_worker, args=(chunks[i], i))
        threads.append(t)
        t.start()

    # Wait for both threads to complete
    for t in threads:
        t.join()

    # Save the final image
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
