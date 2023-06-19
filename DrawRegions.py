from PIL import Image, ImageDraw

def highlight_regions(image_path, name_regions, stack_regions, seat_regions):
    # Open the image
    image = Image.open(image_path)
    
    # Create a draw object
    draw = ImageDraw.Draw(image)
    
    # Define the color and width for the rectangles
    rectangle_color = (255, 0, 0)  # Red color
    rectangle_width = 2

    


    # Draw rectangles around empty seat regions
    for region in hole_card_regions:
            x1, y1, width, height = region
            x2, y2 = x1 + width, y1 + height
            draw.rectangle([x1, y1, x2, y2], outline=rectangle_color, width=rectangle_width)
    # Show the image with highlighted regions
    image.show()

# Example usage
image_path = r"C:\Users\matus\Desktop\Testing Credit\saved_screenshot\screenshot.png"
name_regions = [
    (405, 98, 98, 21),
    (783, 162, 100, 21),
    (812, 366, 100, 21),
    #(452, 487, 100, 21),
    (415, 432, 130, 48),
    #(46, 366, 97, 21),
    (48, 377, 130, 48),
    #(75, 161, 97, 21)
    (79, 106, 130, 48)
]
stack_regions = [
    (411, 124, 90, 22),
    (788, 188, 93, 22),
    (817, 392, 93, 22),
    (455, 512, 93, 22),
    (48, 392, 93, 22),
    (78, 186, 93, 22)
]


seat_regions = [
        (425, 102, 110, 43),
        (429, 488, 110, 43)
    ]

hole_card_regions = [
    (245, 455,500,79)
    
        ]

highlight_regions(image_path, name_regions, stack_regions, seat_regions)
