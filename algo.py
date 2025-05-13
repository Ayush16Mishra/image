import cv2
import numpy as np
import os
from tqdm import tqdm
import time

def process_image(image_path, output_dir, kernel_size, percentage, compare_value):
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)

    if image is None:
        print(f"Error: Could not read image {image_path}")
        return

    height, width = image.shape
    processed_image = image.copy()
    total_iterations = (height - kernel_size + 1) * (width - kernel_size + 1)
    # Iterate over the image with a sliding window of size kernel_size x kernel_size
    with tqdm(total=total_iterations, desc="Processing image") as pbar:
        for i in range(height - kernel_size + 1):
            for j in range(width - kernel_size + 1):
                block = image[i:i+kernel_size, j:j+kernel_size]
                count = np.sum(block >= compare_value)


                # If the count meets or exceeds the required percentage threshold,
                # set the entire block to white (255) in the processed image
                if count >= (kernel_size * kernel_size * (percentage / 100)):
                    processed_image[i:i+kernel_size, j:j+kernel_size] = 255
                pbar.update(1)

    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)


    # Save the processed image to the output directory
    file_name = os.path.basename(image_path)
    output_path = os.path.join(output_dir, file_name)
    cv2.imwrite(output_path, processed_image)
    print(f"Processed image saved to {output_path}")

def process_images_in_directory(input_dir, output_dir, kernel_size, percentage, compare_value):
    # Iterate through each file in the input directory
    for filename in os.listdir(input_dir):
        image_path = os.path.join(input_dir, filename)
        
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp')):
            process_image(image_path, output_dir, kernel_size, percentage, compare_value)