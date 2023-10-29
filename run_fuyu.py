from transformers import FuyuProcessor, FuyuForCausalLM
import accelerate
from PIL import Image
import pynvml
import torch
import time

BBOX_OPEN_STRING = "<0x00>"  # <bbox>
BBOX_CLOSE_STRING = "<0x01>"  # </bbox>
POINT_OPEN_STRING = "<0x02>"  # <point>
POINT_CLOSE_STRING = "<0x03>"  # </point>

TEXT_REPR_BBOX_OPEN = "<box>"
TEXT_REPR_BBOX_CLOSE = "</box>"
TEXT_REPR_POINT_OPEN = "<point>"
TEXT_REPR_POINT_CLOSE = "</point>"

TOKEN_BBOX_OPEN_STRING = BBOX_OPEN_STRING = "<0x00>"  # <bbox>
BBOX_CLOSE_STRING = "<0x01>"  # </bbox>
TOKEN_BBOX_CLOSE_STRING = TOKEN_POINT_OPEN_STRING = POINT_OPEN_STRING = "<0x02>"  # <point>
TOKEN_POINT_CLOSE_STRING = POINT_CLOSE_STRING = "<0x03>"  # </point>
BEGINNING_OF_ANSWER_STRING = "<0x04>"  # <boa>


pynvml.nvmlInit()
handle = pynvml.nvmlDeviceGetHandleByIndex(0)  # 0 for the first GPU
info = pynvml.nvmlDeviceGetMemoryInfo(handle)
print(f'Total memory: {info.total / 1024**2} MiB')
print(f'Free memory: {info.free / 1024**2} MiB')
print(f'Used memory: {info.used / 1024**2} MiB')

# load model and processor
model_id = "adept/fuyu-8b"
processor = FuyuProcessor.from_pretrained(model_id)
model = FuyuForCausalLM.from_pretrained(model_id, device_map="cuda:0", torch_dtype=torch.bfloat16)
print("MODEL LOADED")
info = pynvml.nvmlDeviceGetMemoryInfo(handle)
print(f'Total memory: {info.total / 1024**2} MiB')
print(f'Free memory: {info.free / 1024**2} MiB')
print(f'Used memory: {info.used / 1024**2} MiB')

# prepare inputs for the model
# text_prompt = "Tell me the pixel coordinates of the play button.\n"
# text_prompt = "The bounding box of the 'Startpage' logo is: "
# text_prompt = "The bounding box of the 'Google' logo is: "
# text_prompt = "The bounding box of the button that says 'I'm Feeling Lucky' is: "
# text_prompt = "The bounding box of the search box is: "
text_prompt = "Describe what you can see in the image"
# image_path = "screenshot.jpg"
image_path = "example_screenshot.png"
# image = Image.open(image_path)
image = Image.open(image_path).convert('RGB')

start = time.time()
inputs = processor(text=text_prompt, images=image, return_tensors="pt")
for k, v in inputs.items():
    inputs[k] = v.to("cuda:0")

# autoregressively generate text
max_new_tokens = 50
# generation_output = model.generate(**inputs, max_new_tokens=max_new_tokens)
generation_output = model.generate(**inputs, max_new_tokens=max_new_tokens, temperature=0.01)
# generation_text = processor.batch_decode(generation_output[:, -7:], skip_special_tokens=True)
generation_text = processor.batch_decode(generation_output[:, -max_new_tokens:], skip_special_tokens=False)
print("TIME: ", time.time() - start)
print(f"{generation_text=}")

print("AFTER")
info = pynvml.nvmlDeviceGetMemoryInfo(handle)
print(f'Total memory: {info.total / 1024**2} MiB')
print(f'Free memory: {info.free / 1024**2} MiB')
print(f'Used memory: {info.used / 1024**2} MiB')
pynvml.nvmlShutdown()
