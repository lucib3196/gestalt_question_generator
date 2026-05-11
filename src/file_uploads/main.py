import base64
from langchain_core.messages import HumanMessage, ImageContentBlock
from langchain_openai import ChatOpenAI
import httpx  # A library to fetch image from a URL, you can use other methods too
from dotenv import load_dotenv

load_dotenv()


image_url = "https://api.nga.gov/iiif/a2e6da57-3cd1-4235-b20e-95dcaefed6c8/full/!800,800/0/default.jpg"

headers = {
    "User-Agent": "Mozilla/5.0 (compatible; LangGraphBot/1.0;+https://your.site)"
}
resp = httpx.get(image_url, headers=headers)
resp.raise_for_status()
mime_type = resp.headers.get("Content-Type")  # ← IMPORTANT
image_bytes = resp.content

image_data = base64.b64encode(image_bytes).decode("utf-8")

image_payload = [
    {
        "type": "image_url",
        "image_url": {"url": f"data:{mime_type};base64,{image_data}"},
    }
]

message = {
    "role": "user",
    "content": [{"type": "text", "text": "What is in the image"}, *image_payload],
}

model = ChatOpenAI(model="gpt-4.1-mini")
response = model.invoke([message])
print(response.content)
