import cv2
import pytesseract
from concurrent.futures import ThreadPoolExecutor
from typing import List, Tuple
from PIL import Image
import numpy as np
import time
import os

# Set the Tesseract path
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Define the regions to extract player names
name_regions = [
    (405, 98, 98, 21),
    (783, 162, 100, 21),
    (812, 366, 100, 21),
    (452, 487, 100, 21),
    (46, 366, 97, 21),
    (75, 161, 97, 21)
]

# Define the pot size region
pot_size_region = (470, 221, 100, 20)



# Function to find a stack in a given region of interest (ROI)
def find_stack(sample_image_name, screenshot, samples_folder):
    sample_image_path = os.path.join(samples_folder, sample_image_name)
    sample_image = cv2.imread(sample_image_path, cv2.IMREAD_COLOR)

    result = cv2.matchTemplate(screenshot, sample_image, cv2.TM_CCOEFF_NORMED)
    threshold = 0.99
    loc = np.where(result >= threshold)

    if loc[1].size > 0:
        stack_name = os.path.splitext(sample_image_name)[0]
        return [(stack_name, pt[0], pt[1]) for pt in zip(*loc[::-1])]
    else:
        return []
    
def get_text_from_region(img, region, config=None):
    x, y, w, h = region
    cropped_img = img[y:y + h, x:x + w]
    text = pytesseract.image_to_string(cropped_img, config=config).strip()
    return text

def get_pot_size(image: Image, pot_samples_folder: str) -> str:
    # Convert the screenshot image to OpenCV format
    screenshot = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

    # Define region of interest (ROI) for the pot size
    pot_size_region = (470, 221, 100, 20)

    # Crop ROI from the screenshot
    pot_size_roi = screenshot[pot_size_region[1]:pot_size_region[1] + pot_size_region[3], pot_size_region[0]:pot_size_region[0] + pot_size_region[2]]

    pot_size_results = []
    # Process stacks
    for sample_image_name in os.listdir(pot_samples_folder):
        pot_size_results.extend(find_stack(sample_image_name, pot_size_roi, pot_samples_folder))

    # Sort characters by their x-coordinates and then join them into a single string
    pot_size_results.sort(key=lambda x: x[1])
    pot_size_string = ''.join([result[0] for result in pot_size_results])
    pot_size_string = pot_size_string.replace('decimal_point', '.')

    return pot_size_string


def find_stacks_on_table(screenshot: Image, samples_folder):
    # Convert the screenshot image to OpenCV format
    screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

    # Define regions of interest (ROI)
    stack_regions = [
        (411, 124, 90, 22),
        (788, 188, 93, 22),
        (817, 392, 93, 22),
        (455, 512, 93, 22),
        (48, 392, 93, 22),
        (78, 186, 93, 22)
    ]

    found_stacks = []

    for stack_region in stack_regions:
        # Crop ROI from the screenshot
        stack_roi = screenshot[stack_region[1]:stack_region[1] + stack_region[3], stack_region[0]:stack_region[0] + stack_region[2]]

        character_results = []
        # Process stacks
        for sample_image_name in os.listdir(samples_folder):
            stack_results = find_stack(sample_image_name, stack_roi, samples_folder)
            character_results.extend(stack_results)

        # Sort characters by their x-coordinates and then join them into a single string
        character_results.sort(key=lambda x: x[1])
        stack_string = ''.join([result[0] for result in character_results])
        stack_string = stack_string.replace('decimal_point', '.')
        found_stacks.append(stack_string)

    return found_stacks

def get_player_stats(image: Image, stack_samples_folder, pot_samples_folder, check_names: bool = True) -> Tuple[List[str], List[str], str]:
    img = np.array(image.convert("RGB"))  # Ensure the image is in RGB mode
    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

    with ThreadPoolExecutor() as executor:
        if check_names:
            name_results = list(executor.map(lambda region: get_text_from_region(img, region), name_regions))
        else:
            name_results = []

        # Use the new template matching method for stack sizes
        stack_results = find_stacks_on_table(image, stack_samples_folder)

        pot_size_result = get_pot_size(image, pot_samples_folder)

    return name_results, stack_results, pot_size_result



if __name__ == "__main__":
    start_time = time.time()

    image_path = r"C:\Users\matus\Desktop\PokerMain\screenshot_taken\screenshot_taken.png"
    samples_folder = r"C:\Users\matus\Desktop\PokerMain\image_templates\stack_templates"
    pot_samples_folder = r"C:\Users\matus\Desktop\PokerMain\image_templates\pot_templates"
    
    # Open the image file and convert it into a PIL Image object
    image = Image.open(image_path)

    names, stacks, pot = get_player_stats(image, samples_folder, pot_samples_folder)
    for i, (name_text, stack_text) in enumerate(zip(names, stacks)):
        print(f"Player {i + 1}:")
        print(f"  Name: {name_text}")
        print(f"  Stack size: {stack_text}")
    print(f"Pot size: {pot}")

    end_time = time.time()
    print(f"\nTime taken to process: {end_time - start_time} seconds")

