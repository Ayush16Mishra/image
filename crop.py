import cv2
import json
import os
import threading
from tqdm import tqdm

def crop_images_by_json(image_path, json_path, output_dir):
    # Load image
    image = cv2.imread(image_path)
    if image is None:
        print(f"Error: Could not read image {image_path}")
        return

    # Load JSON
    with open(json_path, 'r') as f:
        crop_data = json.load(f)

    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Convert keys to list and divide into chunks
    keys = list(crop_data.keys())
    num_threads = 2
    chunk_size = len(keys) // num_threads
    chunks = [keys[i*chunk_size:(i+1)*chunk_size] for i in range(num_threads)]

    # Add leftover keys to the last thread if any
    if len(keys) % num_threads != 0:
        chunks[-1].extend(keys[num_threads * chunk_size:])

    def crop_worker(thread_keys, thread_id):
        for key in tqdm(thread_keys, desc=f"Thread {thread_id}", position=thread_id):
            coords = crop_data[key]
            x = coords['x']
            y = coords['y']
            w = coords['width']
            h = coords['height']

            # Crop region
            cropped = image[y:y+h, x:x+w]

            # Save cropped image
            crop_filename = f"{key}.png"
            crop_path = os.path.join(output_dir, crop_filename)
            cv2.imwrite(crop_path, cropped)

    # Start threads
    threads = []
    for i in range(num_threads):
        t = threading.Thread(target=crop_worker, args=(chunks[i], i))
        threads.append(t)
        t.start()

    # Wait for threads to finish
    for t in threads:
        t.join()

    print("Cropping completed.")

