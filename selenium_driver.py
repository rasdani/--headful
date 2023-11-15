import os
import json
from time import sleep
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By


# Setup Chrome options
chrome_options = Options()
home_dir = os.getenv("HOME")
path_to_extension = os.path.join(home_dir, "git/vimium")
# path_to_extension = os.path.join(path_to_extension, "vimium.crx")
print(path_to_extension)
chrome_options.add_argument(f'load-extension={path_to_extension}')
# chrome_options.add_extension(path_to_extension)

# Setup driver
driver = webdriver.Chrome(options=chrome_options)

# Navigate to webpage
# url = "http://github.com/rasdani/--headful"
url =f"file://{os.getcwd()}/calibration.html"
driver.get(url)

# Take screenshot
sleep(2)
driver.save_screenshot('selenium_screenshot_before.png')
actions = ActionChains(driver)
actions.send_keys("f")
actions.perform()
# Find the clickable elements on the webpage
# elements = driver.find_elements(By.CSS_SELECTOR, "*")
# elements = driver.find_elements(By.CSS_SELECTOR, "*[clickable]")
# Step through elements and check if they are clickable
# Step through elements and check if they are clickable
# clickable_elements = []
# Check if the element has the onclick attribute
# for element in elements:
#     if element.get_attribute('onclick') is not None:
#         print("Element has the onclick attribute")
#         clickable_elements.append(element)


# Store the bounding box coordinates
# bounding_boxes = []
# for element in clickable_elements:
#     location = element.location
#     size = element.size
#     left = location['x']
#     top = location['y']
#     width = size['width']
#     height = size['height']
#     right = left + width
#     bottom = top + height
#     bounding_box = {
#         'left': left,
#         'top': top,
#         'right': right,
#         'bottom': bottom,
#         'width': width,
#         'height': height
#     }
#     bounding_boxes.append(bounding_box)

# Write the bounding box coordinates to a JSON file
# with open('bounding_boxes_selenium.json', 'w') as file:
#     json.dump(bounding_boxes, file)

sleep(2)
driver.save_screenshot('selenium_screenshot_after.png')
input("Press Enter to continue...")


# Close driver
driver.quit()
