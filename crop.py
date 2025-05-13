import cv2
import json
import os

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

    # Iterate over each crop entry in the JSON
    for key, coords in crop_data.items():
        x = coords['x']
        y = coords['y']
        w = coords['width']
        h = coords['height']

        # Crop region from the image
        cropped = image[y:y+h, x:x+w]

        # Save cropped image
        crop_filename = f"{key}.png"
        crop_path = os.path.join(output_dir, crop_filename)
        cv2.imwrite(crop_path, cropped)
        print(f"Saved crop {key} to {crop_path}")
