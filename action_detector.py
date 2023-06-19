import cv2
import os
import numpy as np
from PIL import Image

def find_player_action(sample_image_name, screenshot, samples_folder):
    sample_image_path = os.path.join(samples_folder, sample_image_name)
    sample_image = cv2.imread(sample_image_path, cv2.IMREAD_COLOR)

    result = cv2.matchTemplate(screenshot, sample_image, cv2.TM_CCOEFF_NORMED)
    threshold = 0.9
    loc = cv2.minMaxLoc(result)

    if loc[1] >= threshold:
        action_name = os.path.splitext(sample_image_name)[0]
        return action_name, loc[3]  # return action name instead of image name
    else:
        return None

def find_player_actions(screenshot: Image, samples_folder):
    screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

    regions_of_interest = [
        (405, 98, 98, 21),
        (783, 162, 100, 21),
        (812, 366, 100, 21),
        (452, 487, 100, 21),
        (46, 366, 97, 21),
        (75, 161, 97, 21)
    ]

    found_actions = {}

    for i, roi in enumerate(regions_of_interest):
        cropped_screenshot = screenshot[roi[1]:roi[1] + roi[3], roi[0]:roi[0] + roi[2]]
        for sample_image_name in os.listdir(samples_folder):
            action_result = find_player_action(sample_image_name, cropped_screenshot, samples_folder)
            if action_result is not None:
                # Assign the action to the player at the corresponding position
                found_actions[i] = action_result[0]  # extract action name
                break

    return found_actions

if __name__ == "__main__":
    screenshot_path = r"C:\Users\matus\Desktop\PokerMain\screenshot_taken\screenshot_taken.png"
    samples_folder = r"C:\Users\matus\Desktop\PokerMain\image_templates\action_templates"

    screenshot = Image.open(screenshot_path)
    found_actions = find_player_actions(screenshot, samples_folder)
    if found_actions:
        print("Found actions: ", found_actions)
    else:
        print("No actions found.")
