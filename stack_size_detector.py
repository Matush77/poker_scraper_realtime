import cv2
import os
from PIL import Image
import numpy as np

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

if __name__ == "__main__":
    screenshot_path = r"C:\Users\matus\Desktop\PokerMain\screenshot_taken\screenshot_taken.png"
    samples_folder = r"C:\Users\matus\Desktop\PokerMain\image_templates\stack_templates"

    screenshot = Image.open(screenshot_path)
    found_stacks = find_stacks_on_table(screenshot, samples_folder)
    print(*found_stacks, sep="\n")
