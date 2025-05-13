import cv2
import numpy as np
import os
from tqdm import tqdm
import threading

def process_image(image_path, output_dir, kernel_size, percentage, compare_value, pbar_image):
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)

    if image is None:
        print(f"Error: Could not read image {image_path}")
        return

    height, width = image.shape
    processed_image = image.copy()
    total_iterations = (height - kernel_size + 1) * (width - kernel_size + 1)

    # Iterate over the image with a sliding window of size kernel_size x kernel_size
    for i in range(height - kernel_size + 1):
        for j in range(width - kernel_size + 1):
            block = image[i:i+kernel_size, j:j+kernel_size]
            count = np.sum(block >= compare_value)

            # If the count meets or exceeds the required percentage threshold,
            # set the entire block to white (255) in the processed image
            if count >= (kernel_size * kernel_size * (percentage / 100)):
                processed_image[i:i+kernel_size, j:j+kernel_size] = 255

            pbar_image.update(1)

    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Save the processed image to the output directory
    file_name = os.path.basename(image_path)
    output_path = os.path.join(output_dir, file_name)
    cv2.imwrite(output_path, processed_image)
    print(f"Processed image saved to {output_path}")

def process_images_in_directory(input_dir, output_dir, kernel_size, percentage, compare_value):
    # List all image files in the input directory
    image_files = [f for f in os.listdir(input_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp'))]

    # Create a progress bar for overall image processing
    with tqdm(total=len(image_files), desc="Processing Images") as pbar:
        # Create a list of threads to process images concurrently
        threads = []
        for filename in image_files:
            image_path = os.path.join(input_dir, filename)
            # Pass the overall progress bar (pbar) to update progress for each image
            t = threading.Thread(target=process_single_image, args=(image_path, output_dir, kernel_size, percentage, compare_value, pbar))
            threads.append(t)
            t.start()

        # Wait for all threads to finish
        for t in threads:
            t.join()

def process_single_image(image_path, output_dir, kernel_size, percentage, compare_value, pbar):
    # This function is called by each thread to process one image
    height, width = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE).shape
    total_iterations = (height - kernel_size + 1) * (width - kernel_size + 1)
    
    # Create a progress bar for each image processing
    with tqdm(total=total_iterations, desc=f"Processing {os.path.basename(image_path)}", position=1, leave=False) as pbar_image:
        process_image(image_path, output_dir, kernel_size, percentage, compare_value, pbar_image)
    
    # Update overall progress bar after each image is processed
    pbar.update(1)

