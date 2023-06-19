import cv2
import os
from concurrent.futures import ThreadPoolExecutor
from PIL import Image
import numpy as np

def find_card(sample_image_name, screenshot, samples_folder):
    sample_image_path = os.path.join(samples_folder, sample_image_name)
    sample_image = cv2.imread(sample_image_path, cv2.IMREAD_COLOR)

    result = cv2.matchTemplate(screenshot, sample_image, cv2.TM_CCOEFF_NORMED)
    threshold = 0.999
    loc = cv2.minMaxLoc(result)

    if loc[1] >= threshold:
        card_name = os.path.splitext(sample_image_name)[0]
        return card_name, loc[3][0]  # Return the name of the card and its x-coordinate
    else:
        return None

def find_cards_on_table(screenshot: Image, samples_folder):
    # Convert the screenshot image to OpenCV format
    screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

    # Define regions of interest (ROI)
    hole_cards_roi = (415, 432, 130, 48)
    community_cards_roi = (316, 239, 320, 50)

    # Crop ROIs from the screenshot
    hole_cards = screenshot[hole_cards_roi[1]:hole_cards_roi[1] + hole_cards_roi[3], hole_cards_roi[0]:hole_cards_roi[0] + hole_cards_roi[2]]
    community_cards = screenshot[community_cards_roi[1]:community_cards_roi[1] + community_cards_roi[3], community_cards_roi[0]:community_cards_roi[0] + community_cards_roi[2]]

    found_cards = []

    with ThreadPoolExecutor() as executor:
        # Process hole cards
        hole_cards_results = executor.map(lambda sample_image_name: find_card(sample_image_name, hole_cards, samples_folder),
                                          os.listdir(samples_folder))
        found_hole_cards = [result for result in hole_cards_results if result is not None]

        # Process community cards
        community_cards_results = executor.map(lambda sample_image_name: find_card(sample_image_name, community_cards, samples_folder),
                                               os.listdir(samples_folder))
        found_community_cards = [result for result in community_cards_results if result is not None]

    found_cards.extend(found_hole_cards)
    found_cards.extend(found_community_cards)

    # Sort the cards based on their x-coordinate
    found_hole_cards = sorted(found_hole_cards, key=lambda x: x[1])
    found_community_cards = sorted(found_community_cards, key=lambda x: x[1])

    # Return the card names only
    return [card[0] for card in found_hole_cards], [card[0] for card in found_community_cards]




if __name__ == "__main__":
    screenshot_path = r"C:\Users\matus\Desktop\PokerMain\screenshot_taken\screenshot_taken.png"
    samples_folder = r"C:\Users\matus\Desktop\PokerMain\image_templates\cards_templates"

    screenshot = Image.open(screenshot_path)
    found_cards = find_cards_on_table(screenshot, samples_folder)
    print(found_cards)
