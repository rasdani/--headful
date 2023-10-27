from transformers import FuyuProcessor, FuyuForCausalLM
import accelerate
from PIL import Image
import pynvml


pynvml.nvmlInit()
handle = pynvml.nvmlDeviceGetHandleByIndex(0)  # 0 for the first GPU
info = pynvml.nvmlDeviceGetMemoryInfo(handle)
print(f'Total memory: {info.total / 1024**2} MiB')
print(f'Free memory: {info.free / 1024**2} MiB')
print(f'Used memory: {info.used / 1024**2} MiB')

# load model and processor
model_id = "adept/fuyu-8b"
processor = FuyuProcessor.from_pretrained(model_id)
model = FuyuForCausalLM.from_pretrained(model_id, device_map="cuda:0")
print("MODEL LOADED")
print(f'Total memory: {info.total / 1024**2} MiB')
print(f'Free memory: {info.free / 1024**2} MiB')
print(f'Used memory: {info.used / 1024**2} MiB')

# prepare inputs for the model
text_prompt = "Tell me the pixel coordinates of the play button.\n"
image_path = "screenshot.jpg"
image = Image.open(image_path)

inputs = processor(text=text_prompt, images=image, return_tensors="pt")
for k, v in inputs.items():
    inputs[k] = v.to("cuda:0")
print("AFTER processor")
print(f'Total memory: {info.total / 1024**2} MiB')
print(f'Free memory: {info.free / 1024**2} MiB')
print(f'Used memory: {info.used / 1024**2} MiB')

# autoregressively generate text
generation_output = model.generate(**inputs, max_new_tokens=7)
generation_text = processor.batch_decode(generation_output[:, -7:], skip_special_tokens=True)
print(f"{generation_text=}")

print("AFTER")
print(f'Total memory: {info.total / 1024**2} MiB')
print(f'Free memory: {info.free / 1024**2} MiB')
print(f'Used memory: {info.used / 1024**2} MiB')
pynvml.nvmlShutdown()
