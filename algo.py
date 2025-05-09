import cv2
import numpy as np
import os

def process_image(image_path, output_dir, kernel_size, percentage, compare_value):
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)

    if image is None:
        print(f"Error: Could not read image {image_path}")
        return

    height, width = image.shape
    processed_image = image.copy()

    for i in range(height - kernel_size + 1):
        for j in range(width - kernel_size + 1):
            block = image[i:i+kernel_size, j:j+kernel_size]
            count = np.sum(block >= compare_value)

            if count >= (kernel_size * kernel_size * (percentage / 100)):
                processed_image[i:i+kernel_size, j:j+kernel_size] = 255

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    file_name = os.path.basename(image_path)
    output_path = os.path.join(output_dir, file_name)
    cv2.imwrite(output_path, processed_image)
    print(f"Processed image saved to {output_path}")

def process_images_in_directory(input_dir, output_dir, kernel_size, percentage, compare_value):
    for filename in os.listdir(input_dir):
        image_path = os.path.join(input_dir, filename)
        
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp')):
            process_image(image_path, output_dir, kernel_size, percentage, compare_value)
