# --headful 👤
Make a web browser multimodal, give it eyes and ears.

Make it `--headful`, the opposite of `--headless`.

Use a vision/UI model (currently GPT-V) to recognize website elements 👁️.

Use Whisper and GPT function calling to listen and understand commands 🧏.
 
Use playwright to direct your browser 🕹️.


 ## Setup

- Install the requirements.
- Run `playwright install chromium` to install the browser.
- Fire up `server.py`.
- Run `python main.py` in a different terminal.

## Breakdown
GPT function calling translates user request into URL to visit.
Hitting 'f' fires up Vimium and highlights clickable elements on the page.
The Vimium fork renders and sends bounding box coordinated of clickable elements to a Flask server.
Even clicking via Vimimum key bindings fails seldomly. Bounding boxes can be use to click (into the middle of) UI elements.
A screenshot is taken an sent to a GPT-Vision model together with the user request.


In doing:
- Record and transcribe audio during normal browsing to create a captioned UI dataset for finetuning.


## Take aways & ressources
Check out the 'experiments' branch for a bunch of things I tried out:
- [UIED](https://github.com/MulongXie/UIED)
    - Accurate bounding boxes, but not for all UI elements.
- Adept's [Fuyu-8B](https://huggingface.co/adept/fuyu-8b) to detect UI element bounding box for user request.
    - See [HF space](https://huggingface.co/spaces/adept/fuyu-8b-demo/blob/beaba43434072de08478e7a1f90e621ece81aa93/app.py#L67) for how to properly prompt for bounding boxes. Works primarly for written text, so more akin to OCR.
    - Tried hard coding `<bbox>` tags into their transformers class to force to return bounding boxes for non text UI elements. Got bounding boxes for any request, but they were not accurate.
- (finetuned) Donot
- RICO dataset
- RefExp
- pix2struct-refexp
    - more lightweight than Vision LLMs/large multimodal models
    - finetuning this should be easier
- GPT-Vision dropped
    - hit or miss with Vimium labels
    - tried passing before and after screenshot in case labels occlude UI elements
    - tried bounding boxes as visual aid
    - mobile user agent for slimmed down websites
    - tried single highlighted UI element per image and batched request for simple yes/no classification, turns out ChatCompletion doesn't support batching (without workarounds)!
    - tried cutouts of single UI elements
    - some of these are quite slow and all are still hit or miss
