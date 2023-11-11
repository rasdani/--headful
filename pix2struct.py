import requests
from PIL import Image
from transformers import Pix2StructForConditionalGeneration, Pix2StructProcessor

url = "https://www.ilankelman.org/stopsigns/australia.jpg"
image = Image.open(requests.get(url, stream=True).raw)

model_id = "gitlost-murali/pix2struct-refexp-base"
model = Pix2StructForConditionalGeneration.from_pretrained(model_id)
processor = Pix2StructProcessor.from_pretrained(model_id)

text = "What is in the picture?"
inputs = processor(images=image, text=text, return_tensors="pt")

predictions = model.generate(**inputs)
print(processor.decode(predictions[0], skip_special_tokens=True))
