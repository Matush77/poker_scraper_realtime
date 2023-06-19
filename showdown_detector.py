import cv2
import os
from concurrent.futures import ThreadPoolExecutor
from PIL import Image
import numpy as np

def find_showdown(sample_image_name, screenshot, samples_folder):
    sample_image_path = os.path.join(samples_folder, sample_image_name)
    sample_image = cv2.imread(sample_image_path, cv2.IMREAD_COLOR)

    result = cv2.matchTemplate(screenshot, sample_image, cv2.TM_CCOEFF_NORMED)
    threshold = 0.999
    loc = cv2.minMaxLoc(result)

    if loc[1] >= threshold:
        showdown_name = os.path.splitext(sample_image_name)[0]
        return showdown_name, loc[3][0]  # Return the name of the showdown and its x-coordinate
    else:
        return None

def find_showdown_on_table(screenshot: Image, samples_folder):
    # Convert the screenshot image to OpenCV format
    screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

    # Define regions of interest (ROI)
    showdown_regions = [
        (409, 43, 130, 48),
        (752, 106, 130, 48),
        (785, 311, 130, 48),
        (415, 432, 130, 48),
        (50, 311, 130, 48),
        (79, 106, 130, 48),
    ]

    # Process all showdown regions
    found_showdown = {}
    with ThreadPoolExecutor() as executor:
        for i, roi in enumerate(showdown_regions):
            # Crop ROI from the screenshot
            roi_img = screenshot[roi[1]:roi[1] + roi[3], roi[0]:roi[0] + roi[2]]

            showdown_results = executor.map(
                lambda sample_image_name: find_showdown(sample_image_name, roi_img, samples_folder),
                os.listdir(samples_folder))

            found_card = next((result for result in showdown_results if result is not None), None)
            if found_card is not None:
                found_showdown[i] = found_card[0]  # Use player index as key

    # Return the card names only
    return found_showdown



if __name__ == "__main__":
    screenshot_path = r"C:\Users\matus\Desktop\PokerMain\screenshot_taken\screenshot_taken.png"
    samples_folder = r"C:\Users\matus\Desktop\PokerMain\image_templates\showdowns_templates"

    screenshot = Image.open(screenshot_path)
    found_showdowns = find_showdown_on_table(screenshot, samples_folder)
    print(found_showdowns)
