import cv2
import numpy as np
import os
from PIL import Image

def find_button(sample_image_name, screenshot, samples_folder):
    sample_image_path = os.path.join(samples_folder, sample_image_name)
    sample_image = cv2.imread(sample_image_path, cv2.IMREAD_COLOR)

    result = cv2.matchTemplate(screenshot, sample_image, cv2.TM_CCOEFF_NORMED)
    threshold = 0.9
    loc = cv2.minMaxLoc(result)

    if loc[1] >= threshold:
        return True
    else:
        return False

def button_regions_of_interest():
    return [
        (501, 174, 35, 35),
        (733, 228, 35, 35),
        (680, 380, 40, 40),
        (368, 420, 37, 37),
        (180, 315, 35, 35),
        (194, 230, 35, 35)
        # Add other regions here
    ]

def find_button_in_screenshot(screenshot: Image, button_sample_folder):
    screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    button_sample_image_name = "dealer_button.png"  # Assuming the dealer_button image is named "dealer_button.png"

    for i, roi in enumerate(button_regions_of_interest()):
        roi_image = screenshot[roi[1]:roi[1] + roi[3], roi[0]:roi[0] + roi[2]]
        if find_button(button_sample_image_name, roi_image, button_sample_folder):
            return i
    print("Button not found")
    return None

if __name__ == "__main__":
    screenshot_path = r"C:\Users\matus\Desktop\PokerMain\screenshot_taken\screenshot_taken.png"
    button_sample_folder = r"C:\Users\matus\Desktop\PokerMain\image_templates\dealer_button"

    screenshot = Image.open(screenshot_path)
    find_button_in_screenshot(screenshot, button_sample_folder)
