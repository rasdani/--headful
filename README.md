# --headful 👤
Make a web browser multimodal, give it eyes and ears.

Make it `--headful`, the opposite of `--headless`.

Use a vision/UI model (currently GPT4-V) to recognize website elements 👁️.

Use GPT function calling to understand commands 🧏.
 
Use Playwright to direct your browser 🕹️.

Use Whisper to record a captioned UI element dataset for finetuning. 🎙️


 ## Setup

- Install the requirements.
- Run `playwright install chromium` to install the browser.
- Fire up `server.py`.
- Run `python main.py` in a different terminal.

## Breakdown
- GPT function calling and `instructor` translate user request into URL to visit.
- Hitting 'f' fires up a Vimium fork and highlights clickable elements on the page.
- The Vimium fork renders and sends bounding box coordinates of clickable elements to a Flask server.
    - Even clicking via Vimimum key bindings fails seldomly. Bounding boxes can be used to simulate a click into the middle of UI elements.
- A screenshot is taken and sent to GPT4-Vision together with the user request.
- GPT4-Vision selects webpage element and user can confirm click.


In doing:
- Record and transcribe audio during normal browsing to create a captioned UI dataset for finetuning.


## Take aways & ressources
Check out the 'experiments' branch or these links for a bunch of things I tried out:
- [UIED](https://github.com/MulongXie/UIED)
    - Accurate bounding boxes, but not for all UI elements.
- Adept's [Fuyu-8B](https://huggingface.co/adept/fuyu-8b) to detect UI element bounding box for user request.
    - See [HF space](https://huggingface.co/spaces/adept/fuyu-8b-demo/blob/beaba43434072de08478e7a1f90e621ece81aa93/app.py#L67) for how to properly prompt for bounding boxes. Works primarly for written text, so more akin to OCR.
    - Tried hard coding `<bbox>` tags into their transformers class to force to return bounding boxes for non text UI elements. Got bounding boxes for any request, but they were not accurate.
- [RICO dataset](https://github.com/google-research-datasets/uibert/tree/main/ref_exp)
- this UI detection task is called RefExp
- [pix2struct](https://github.com/google-research/pix2struct/tree/main)-refexp [base](https://huggingface.co/gitlost-murali/pix2struct-refexp-base) [large](https://huggingface.co/gitlost-murali/pix2struct-refexp-large)
    - more lightweight than Vision LLMs/large multimodal models
    - finetuning/inference should be easier/faster
- GPT4-Vision dropped
    - hit or miss with Vimium labels
    - tried passing before and after screenshot in case labels occlude UI elements
    - tried bounding boxes as visual aid
    - mobile user agent for slimmed down websites
    - tried single highlighted UI element per image and batched request for simple yes/no classification, turns out ChatCompletion doesn't support batching ([without workarounds](https://github.com/openai/openai-cookbook/blob/main/examples/api_request_parallel_processor.py))!
    - tried cutouts of single UI elements
    - some of these are quite slow and all are still hit or miss

- One could try one of the more recent large OSS multimodal models
    - e.g. [BakLLaVA](https://huggingface.co/SkunkworksAI/BakLLaVA-1), [CogVLM](https://github.com/THUDM/CogVLM)
    - finetune them with your own captioned data

## Similiar projects
- [globot](https://github.com/Globe-Engineer/globot)
- [vimGPT](https://github.com/ishan0102/vimGPT)
