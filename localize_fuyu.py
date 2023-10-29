import time
import re
import torch
from PIL import Image
from transformers import AutoTokenizer, FuyuForCausalLM, FuyuImageProcessor, FuyuProcessor

model_id = "adept/fuyu-8b"
dtype = torch.bfloat16
device = "cuda"

tokenizer = AutoTokenizer.from_pretrained(model_id)
model = FuyuForCausalLM.from_pretrained(model_id, device_map="auto", torch_dtype=dtype)
processor = FuyuProcessor(image_processor=FuyuImageProcessor(), tokenizer=tokenizer)

CAPTION_PROMPT = "Generate a coco-style caption.\n"
DETAILED_CAPTION_PROMPT = "What is happening in this image?"

def resize_to_max(image, max_width=1920, max_height=1080):
    width, height = image.size
    if width <= max_width and height <= max_height:
        return image

    scale = min(max_width/width, max_height/height)
    width = int(width*scale)
    height = int(height*scale)

    return image.resize((width, height), Image.LANCZOS)

def pad_to_size(image, canvas_width=1920, canvas_height=1080):
    width, height = image.size
    if width >= canvas_width and height >= canvas_height:
        return image

    # Paste at (0, 0)
    canvas = Image.new("RGB", (canvas_width, canvas_height))
    canvas.paste(image)
    return canvas

def predict(image, prompt):
    # image = image.convert('RGB')
    model_inputs = processor(text=prompt, images=[image])
    model_inputs = {k: v.to(dtype=dtype if torch.is_floating_point(v) else v.dtype, device=device) for k,v in model_inputs.items()}

    generation_output = model.generate(**model_inputs, max_new_tokens=50)
    prompt_len = model_inputs["input_ids"].shape[-1]
    return tokenizer.decode(generation_output[0][prompt_len:], skip_special_tokens=True)

def caption(image, detailed_captioning):
    if detailed_captioning:
        caption_prompt = DETAILED_CAPTION_PROMPT
    else:
        caption_prompt = CAPTION_PROMPT
    return predict(image, caption_prompt).lstrip()

def scale_factor_to_fit(original_size, target_size=(1920, 1080)):
    width, height = original_size
    max_width, max_height = target_size
    if width <= max_width and height <= max_height:
        return 1.0
    return min(max_width/width, max_height/height)
    
def tokens_to_box(tokens, original_size):
    bbox_start = tokenizer.convert_tokens_to_ids("<0x00>")
    bbox_end = tokenizer.convert_tokens_to_ids("<0x01>")
    try:
        # Assumes a single box
        bbox_start_pos = (tokens == bbox_start).nonzero(as_tuple=True)[0].item()
        bbox_end_pos = (tokens == bbox_end).nonzero(as_tuple=True)[0].item()
        
        if bbox_end_pos != bbox_start_pos + 5:
            return tokens

        # Retrieve transformed coordinates from tokens
        coords = tokenizer.convert_ids_to_tokens(tokens[bbox_start_pos+1:bbox_end_pos])

        # Scale back to original image size and multiply by 2
        scale = scale_factor_to_fit(original_size)
        top, left, bottom, right = [2 * int(float(c)/scale) for c in coords]
        
        # Replace the IDs so they get detokenized right
        replacement = f" <box>{top}, {left}, {bottom}, {right}</box>"
        replacement = tokenizer.tokenize(replacement)[1:]
        replacement = tokenizer.convert_tokens_to_ids(replacement)
        replacement = torch.tensor(replacement).to(tokens)

        tokens = torch.cat([tokens[:bbox_start_pos], replacement, tokens[bbox_end_pos+1:]], 0)
        return tokens
    except:
        print("Can't convert tokens.")
        return tokens

def coords_from_response(response):
    # y1, x1, y2, x2
    pattern = r"<box>(\d+),\s*(\d+),\s*(\d+),\s*(\d+)</box>"

    match = re.search(pattern, response)
    if match:
        # Unpack and change order
        y1, x1, y2, x2 = [int(coord) for coord in match.groups()]
        return (x1, y1, x2, y2)
    else:
        print("The string is malformed or does not match the expected pattern.")
        
def localize(image, query):
    # prompt = f"When presented with a box, perform OCR to extract text contained within it. If provided with text, generate the corresponding bounding box.\n{query}"
    prompt = f"Perform image recognition for the object provided in the following query, generate the corresponding bounding box.\n{query}"

    # Downscale and/or pad to 1920x1080
    padded = resize_to_max(image)
    padded = pad_to_size(padded)

    model_inputs = processor(text=prompt, images=[padded])
    model_inputs = {k: v.to(dtype=dtype if torch.is_floating_point(v) else v.dtype, device=device) for k,v in model_inputs.items()}
    
    generation_output = model.generate(**model_inputs, max_new_tokens=40)
    prompt_len = model_inputs["input_ids"].shape[-1]
    tokens = generation_output[0][prompt_len:]
    tokens = tokens_to_box(tokens, image.size)
    decoded = tokenizer.decode(tokens, skip_special_tokens=True)
    coords = coords_from_response(decoded)
    return image, [(coords, f"Location of \"{query}\"")]


input_dict = {
    "yellow triangle": "calibration_image_1.png",
    "magenta circle": "calibration_image_2.png",
    "green square": "calibration_image_3.png",
    "green triangle": "calibration_image_4.png",
    "red circle": "calibration_image_5.png"
}

start = time.time()
image = Image.open("example_screenshot.png").convert("RGB")
# query = "I'm Feeling Lucky"
# query = "search box"
query = "Google logo"
_, coords = localize(image, query)
print(f"{coords=}")
print("TIME: ", time.time() - start)