import os
from dotenv import load_dotenv, find_dotenv
if 'PRODUCTION' not in os.environ:
    ENV_FILE = find_dotenv()
    load_dotenv(ENV_FILE)

import json
from fastapi import FastAPI, Request
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from io import BytesIO
import base64
from PIL import Image
from openai import OpenAI

import pickle
import json


app = FastAPI()

# Define origins - add the URL of your frontend or use ["*"] to allow all origins
origins = ['*']
# origins = [
#     "http://localhost",  # Adjust this with the appropriate URL for your Chrome extension or development server
#     "chrome-extension://<your-extension-id>",  # Allow your Chrome extension to access FastAPI
# ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)


# Function to encode the image
def _encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


def _get_picture_category(image_data):
    prompt = """Given the image of the webpage, your task is to generate the following metadata:
- type: the webpage's type
- primary_category: the primary category the webpage falls under
- description: a short description of the webpage
- secondary_categories: a list of relevant secondary categories

##Instructions:
Return your answer in the following JSON format
{
    "type": "",
    "primary_category": "...",
    "description": "...",
    "secondary_categories": ["..."]
}

##Output:
"""

    # Getting the base64 string
    base64_image = _encode_image("captured_image.png")

    client = OpenAI(
        api_key=os.environ['OPENAI_KEY'],

    )

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt,
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url":  f"data:image/jpeg;base64,{base64_image}"
                        },
                    },
                ],
            }
        ],
        response_format = { "type": "json_object" }
    )

    # print("RESPONSE:", response)

    data = json.loads(response.choices[0].message.content)
    return data


class ScreenshotData(BaseModel):
    data_url: str
    metadata: dict


@app.post("/process_user_save_request")
async def capture_screenshot(data: ScreenshotData):
    base64_data = data.data_url.split(",")[1]
    image_data = base64.b64decode(base64_data)

    # Convert to an image and save it
    image = Image.open(BytesIO(image_data))
    image.save("captured_image.png", "PNG")

    print('generating category...')

    response_data = _get_picture_category(
        image_data = image_data
    )

    print(response_data)

    # application_data_list.append(response_data)
    with open('tmp_result.json', 'a') as fp:
        fp.write(json.dumps(response_data) + '\n')

    # TODO: 
        # create frontend UI and present this data

    return {"status": "success", "message": "Image saved successfully"}

# '```json\n{\n    "type": "documentation",\n    "primary_category": "technology",\n    "description": "A guide on how to use OpenAI\'s vision capabilities to understand and analyze images.",\n    "secondary_categories": ["API documentation", "machine learning", "computer vision"]\n}\n```'
