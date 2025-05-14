import cv2
import numpy as np
import os
from tqdm import tqdm
import threading

def process_image(image_path, output_dir, kernel_size, percentage, compare_value, set_value, comparison_operator, pbar_image):
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)

    if image is None:
        print(f"Error: Could not read image {image_path}")
        return

    height, width = image.shape
    processed_image = image.copy()

    for i in range(height - kernel_size + 1):
        for j in range(width - kernel_size + 1):
            block = image[i:i+kernel_size, j:j+kernel_size]
            
            if comparison_operator == '>=':
                count = np.sum(block >= compare_value)
            else:
                count = np.sum(block <= compare_value)

            if count >= (kernel_size * kernel_size * (percentage / 100)):
                processed_image[i:i+kernel_size, j:j+kernel_size] = set_value

            pbar_image.update(1)

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    file_name = os.path.basename(image_path)
    output_path = os.path.join(output_dir, file_name)
    cv2.imwrite(output_path, processed_image)
    print(f"Processed image saved to {output_path}")


def process_single_image(image_path, output_dir, kernel_size, percentage, compare_value, set_value, comparison_operator, pbar):
    height, width = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE).shape
    total_iterations = (height - kernel_size + 1) * (width - kernel_size + 1)

    with tqdm(total=total_iterations, desc=f"Processing {os.path.basename(image_path)}", position=1, leave=False) as pbar_image:
        process_image(image_path, output_dir, kernel_size, percentage, compare_value, set_value, comparison_operator, pbar_image)

    pbar.update(1)


def process_images_in_directory(input_dir, output_dir, kernel_size, percentage, compare_value, set_value, comparison_operator):
    image_files = [f for f in os.listdir(input_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp'))]

    with tqdm(total=len(image_files), desc="Processing Images") as pbar:
        threads = []
        for filename in image_files:
            image_path = os.path.join(input_dir, filename)
            t = threading.Thread(
                target=process_single_image,
                args=(image_path, output_dir, kernel_size, percentage, compare_value, set_value, comparison_operator, pbar)
            )
            threads.append(t)
            t.start()

        for t in threads:
            t.join()
