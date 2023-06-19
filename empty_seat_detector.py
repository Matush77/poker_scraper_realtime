import cv2
import os
import numpy as np
from PIL import Image

empty_seat_folder_path = r"C:\Users\matus\Desktop\PokerMain\image_templates\empty_seats_templates"  # Your new path


seat_regions = [
    (400, 94, 150, 54),
    (730, 158, 150, 54),
    (777, 362, 150, 54),
    (415, 480, 150, 54),
    (40, 365, 150, 54),
    (70, 157, 150, 54),
]

def load_empty_seats(empty_seat_folder_path):
    empty_seats = []
    for filename in os.listdir(empty_seat_folder_path):
        if filename.endswith(".png") or filename.endswith(".jpg"):
            img_path = os.path.join(empty_seat_folder_path, filename)
            empty_seat_img = Image.open(img_path)  # use PIL to open image
            empty_seat_img = np.array(empty_seat_img)  # convert to numpy array
            empty_seat_img = cv2.cvtColor(empty_seat_img, cv2.COLOR_RGB2BGR)  # convert to BGR format for cv2
            empty_seats.append(empty_seat_img)
    return empty_seats


def check_empty_seats(screenshot_pil, empty_seat_folder_path, threshold=0.8):
    img = np.array(screenshot_pil.convert('RGB'))
    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)  # Convert RGB to BGR 

    empty_seats_list = load_empty_seats(empty_seat_folder_path)

    empty_seats = []
    for idx, region in enumerate(seat_regions):
        x, y, w, h = region
        cropped_img = img[y:y+h, x:x+w]
        
        max_val_list = []
        for empty_seat in empty_seats_list:
            res = cv2.matchTemplate(cropped_img, empty_seat, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, _ = cv2.minMaxLoc(res)
            max_val_list.append(max_val)

        max_val = max(max_val_list)
        if max_val > threshold:
            empty_seats.append(idx)

    return empty_seats


