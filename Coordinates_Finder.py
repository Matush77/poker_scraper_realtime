import cv2

def click_event(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        print("Coordinates: (", x, ",", y, ")")

img_path = 'C:/Users/matus/Desktop/Poker OCR/cropped_screenshot.png'
image = cv2.imread(img_path)
cv2.namedWindow('image')
cv2.setMouseCallback('image', click_event)

while True:
    cv2.imshow('image', image)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()
