from PIL import Image, ImageDraw

# {
#     "bottom": 53.25,
#     "top": 18.75,
#     "left": 16,
#     "right": 48,
#     "width": 32,
#     "height": 34.5
# }
# Open an image file
with Image.open("screenshot_after.png") as img:
    # Create ImageDraw object
    draw = ImageDraw.Draw(img)
    # Define bounding box coordinates
    bbox = [(16, 18.75), (48, 53.25)]
    # Draw rectangle on image
    draw.rectangle(bbox, outline="red")
    # Save the image
    img.save("screenshot_after_bbox.png")
