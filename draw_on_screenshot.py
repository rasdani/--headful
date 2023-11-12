### adapted from pix2struct
import sys
from PIL import Image, ImageDraw, ImageFont
import textwrap
import io
from typing import Optional

def render_text(text: str,
                text_size: int = 36,
                text_color: str = "black",
                background_color: str = "white",
                left_padding: int = 5,
                right_padding: int = 5,
                top_padding: int = 5,
                bottom_padding: int = 5,
                font_bytes: Optional[bytes] = None) -> Image.Image:
  """Render text."""
  # Add new lines so that each line is no more than 80 characters.
  wrapper = textwrap.TextWrapper(width=80)
  lines = wrapper.wrap(text=text)
  wrapped_text = "\n".join(lines)

  if font_bytes is not None:
    font_spec = io.BytesIO(font_bytes)
  else:
    # font_spec = DEFAULT_FONT_PATH
    if sys.platform == "darwin":
      font_spec = "/System/Library/Fonts/Supplemental/Arial.ttf"
  font = ImageFont.truetype(font_spec, encoding="UTF-8", size=text_size)

  # Use a temporary canvas to determine the width and height in pixels when
  # rendering the text.
  temp_draw = ImageDraw.Draw(Image.new("RGB", (1, 1), background_color))
  _, _, text_width, text_height = temp_draw.textbbox((0, 0), wrapped_text, font)

  # Create the actual image with a bit of padding around the text.
  image_width = text_width + left_padding + right_padding
  image_height = text_height + top_padding + bottom_padding
  image = Image.new("RGB", (image_width, image_height), background_color)
  draw = ImageDraw.Draw(image)
  draw.text(
      xy=(left_padding, top_padding),
      text=wrapped_text,
      fill=text_color,
      font=font)
  return image

def render_header(image: Image.Image, header: str) -> Image.Image:
  """Renders a header on a PIL image and returns a new PIL image."""
  header_image = render_text(header)
  new_width = max(header_image.width, image.width)

  new_height = int(image.height *  (new_width / image.width))
  new_header_height = int(
      header_image.height * (new_width / header_image.width))

  new_image = Image.new(
      "RGB",
      (new_width, new_height + new_header_height),
      "white")
  new_image.paste(header_image.resize((new_width, new_header_height)), (0, 0))
  new_image.paste(image.resize((new_width, new_height)), (0, new_header_height))
  return new_image

# bbox_coords = {
#     "bottom": 172.96876525878906,
#     "top": 142.96875,
#     "left": 115.32986450195312,
#     "right": 198.42015075683594,
#     "width": 83.09028625488281,
#     "height": 30.000015258789062,
# }
bbox_coords = {"bottom": 276.953125, "top": 246.95314025878906, "left": 99.33160400390625, "right": 182.42189025878906, "width": 83.09028625488281, "height": 29.999984741210938}
# Push coords a set amount to the left and up
push_amount_x = 10
push_amount_y = 20
bbox_coords["left"] -= push_amount_x
bbox_coords["top"] -= push_amount_y
bbox_coords["right"] -= push_amount_x
bbox_coords["bottom"] -= push_amount_y
# Open an image file
# with Image.open("screenshot_after.png") as img:
with Image.open("screenshot_before.png") as img:
    # Create ImageDraw object
    draw = ImageDraw.Draw(img, "RGBA")
    # Define bounding box coordinates
    # bbox = [(16, 18.75), (48, 53.25)]
    # Adjust this to use bbox_coords
    bbox = [
        (bbox_coords["left"], bbox_coords["top"]),
        (bbox_coords["right"], bbox_coords["bottom"]),
    ]
    # Draw rectangle on image
    draw.rectangle(bbox, 
                #    fill=(0, 0, 255, 1), 
                   outline=(0, 0, 255, 255))
    img = render_header(img, "click on 'Issues'")
    # Draw rectangle on image with thicker outline
    # outline_width = 3
    # for i in range(outline_width):
    #     draw.rectangle(
    #         [(bbox[0][0] - i, bbox[0][1] - i), (bbox[1][0] + i, bbox[1][1] + i)],
    #         outline="red",
    #     )
    # Save the image
    img.save("screenshot_after_bbox.png")
