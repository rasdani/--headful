import os
from PIL import Image, ImageDraw
import json


with open("coordinates.json", "r") as f:
    bbox_list = json.load(f)
    bbox_list = bbox_list.values()
# bbox_list = [
#     {"bottom": 276.953125, "top": 246.95314025878906, "left": 99.33160400390625, "right": 182.42189025878906, "width": 83.09028625488281, "height": 29.999984741210938},
#     # Add more bounding boxes here...
# ]

output_dir = "bbox-images"
os.makedirs(output_dir, exist_ok=True)

# Iterate over the list of bounding boxes
for i, bbox_coords in enumerate(bbox_list):
    with Image.open("screenshot_before.png") as img:
        draw = ImageDraw.Draw(img, "RGBA")
        # bbox = [
        #     (bbox_coords["left"], bbox_coords["top"]),
        #     (bbox_coords["right"], bbox_coords["bottom"]),
        # ]
        bbox = (
            bbox_coords["left"],
            bbox_coords["top"],
            bbox_coords["right"],
            bbox_coords["bottom"],
        )
        draw.rectangle(bbox, outline=(255, 0, 0), width=3)
        img.save(os.path.join(output_dir, f"screenshot_after_bbox_{i}.png"))
        # try cut outs
        # cutout = img.crop(bbox)
        # cutout.save(os.path.join(output_dir, f"screenshot_after_bbox_{i}.png"))
