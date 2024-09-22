import cv2
import numpy as np
import os
import shutil

def calculate_warmth_score(image_path):
    img = cv2.imread(image_path)
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
    # Calculate warmth based on red color intensity
    red_intensity = np.average(img_rgb[:, :, 0])  # Index 0 represents the red channel
    
    # Calculate image brightness (average intensity)
    brightness_score = np.average(img_rgb)

    # Combine warmth and coldness scores
    warmth_score = red_intensity - brightness_score

    return warmth_score

def sort_images_by_warmth(directory_path):
    image_paths = [os.path.join(directory_path, file) for file in os.listdir(directory_path) if file.lower().endswith(('.png', '.jpg', '.jpeg'))]
    
    # Sort images based on warmth score
    sorted_image_paths = sorted(image_paths, key=lambda path: calculate_warmth_score(path))
    return sorted_image_paths
    
def save_sorted_images(sorted_image_paths, output_folder):
    os.makedirs(output_folder, exist_ok=True)

    # Save the sorted images
    for i, image_path in enumerate(sorted_image_paths):
        output_path = os.path.join(output_folder, f"{i + 1}.jpg")
        
        shutil.copy(image_path, output_path)

input_directory = ""
output_directory = ""

sorted_images = sort_images_by_warmth(input_directory)
save_sorted_images(sorted_images, output_directory)
