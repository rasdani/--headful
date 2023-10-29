import re
from transformers import FuyuProcessor, FuyuForCausalLM
import accelerate
from PIL import Image
import pynvml
import torch
import time


pynvml.nvmlInit()
handle = pynvml.nvmlDeviceGetHandleByIndex(0)  # 0 for the first GPU

# load model and processor
model_id = "adept/fuyu-8b"
processor = FuyuProcessor.from_pretrained(model_id)
model = FuyuForCausalLM.from_pretrained(model_id, device_map="cuda:0", torch_dtype=torch.bfloat16)

info = pynvml.nvmlDeviceGetMemoryInfo(handle)
print(f'Total memory: {info.total / 1024**2} MiB')
print(f'Free memory: {info.free / 1024**2} MiB')
print(f'Used memory: {info.used / 1024**2} MiB')

# prepare inputs for the model
input_dict = {
    "yellow triangle": "calibration_image_1.png",
    "magenta circle": "calibration_image_2.png",
    "green square": "calibration_image_3.png",
    "green triangle": "calibration_image_4.png",
    "red circle": "calibration_image_5.png"
}

for obj, image_path in input_dict.items():
    start = time.time()
    image = Image.open(image_path).convert('RGB')
    # text_prompt = f"The bounding box of the {obj} is: "
    text_prompt = f"The {obj} is located at: "
    print(f"{text_prompt=}")
    inputs = processor(text=text_prompt, images=image, return_tensors="pt")
    for k, v in inputs.items():
        inputs[k] = v.to("cuda:0")

    # autoregressively generate text
    max_new_tokens = 50
    # generation_output = model.generate(**inputs, max_new_tokens=max_new_tokens)
    generation_output = model.generate(**inputs, max_new_tokens=max_new_tokens, temperature=0.01)
    # generation_text = processor.batch_decode(generation_output[:, -7:], skip_special_tokens=True)
    generation_text = processor.batch_decode(generation_output[:, -max_new_tokens:], skip_special_tokens=False)
    # generation_text = processor.batch_decode(generation_output, skip_special_tokens=False)
    print(f"{generation_text=}")
    print("TIME: ", time.time() - start)

print("AFTER")
info = pynvml.nvmlDeviceGetMemoryInfo(handle)
print(f'Total memory: {info.total / 1024**2} MiB')
print(f'Free memory: {info.free / 1024**2} MiB')
print(f'Used memory: {info.used / 1024**2} MiB')
pynvml.nvmlShutdown()
