import os
import base64
import mimetypes
from io import BytesIO
from urllib.parse import urlparse
from typing import List, Dict, Any

import pandas as pd
from PIL import Image
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.messages.base import BaseMessage

from config import UPLOAD_DIR, OUTPUT_DIR, CONTAINER_NAME

def convert_to_langchain_messages(messages: List[Dict[str, Any]]) -> List[BaseMessage]:
    """
    Convert UI messages to LangChain format.
    - For images: Fetches local URLs and converts to base64.
    - For files: Passes the name and URL as text for a tool to handle.
    """
    langchain_messages = []
    
    for msg in messages:
        role = msg.get("role", "user")
        content = msg.get("content")
        attachments = msg.get("attachments", [])
        
        message_content = []
        
        # 1. Handle base text content
        if isinstance(content, list):
            for part in content:
                if part.get("type") == "text":
                    text = part.get("text", "")
                    if text:
                        message_content.append({"type": "text", "text": text})
        elif isinstance(content, str):
            message_content.append({"type": "text", "text": content})
        
        # 2. Process attachments
        for attachment in attachments:
            attachment_type = attachment.get("type") # 'file' or 'image'
            attachment_name = attachment.get("name", "file")
            attachment_content_list = attachment.get("content", [])

            if not attachment_content_list:
                continue

            if attachment_type == "file":
                file_part = attachment_content_list[0]
                file_url = file_part.get("text") if file_part.get("type") == "text" else None
                file_url=file_url.replace("localhost",CONTAINER_NAME) #Convert to docker path
                if file_url:
                    # Just pass the file's metadata as text.
                    # The LLM can then use this URL in a tool call.
                    file_info_text = f"\n[Attached File: {attachment_name}]\n[URL: {file_url}]\n This is excel file, can used further to analyze."
                    message_content.append({
                        "type": "text",
                        "text": file_info_text
                    })
            
            # --- LOGIC FOR IMAGES (unchanged) ---
            # We assume you still want to fetch local *images* for vision
            elif attachment_type == "image":
                for att_part in attachment_content_list:
                    if att_part.get("type") == "image":
                        image_data = att_part.get("image", "") # URL or base64
                        if image_data.startswith("http"): #Local or dockerfile
                            try:
                                path_from_url = urlparse(image_data).path
                            # 2. Create the full local file path
                            # os.path.join('./public', 'uploads/image.png')
                            # The lstrip('/') removes the leading slash from the path
                                local_file_path = os.path.join(".", path_from_url.lstrip('/'))
                                if os.path.exists(local_file_path):
                                # 3. Read the file as bytes
                                    with open(local_file_path, 'rb') as f:
                                        image_bytes = f.read()
                                    
                                    # 4. Get MIME type and encode
                                    mime_type, _ = mimetypes.guess_type(local_file_path)
                                    if not mime_type:
                                        mime_type = 'image/jpeg' # Fallback
                                    
                                    b64_data = base64.b64encode(image_bytes).decode('utf-8')
                                    data_uri = f"data:{mime_type};base64,{b64_data}"
                                    message_content.append({"type": "image", "source_type": "base64", "data": b64_data,"mime_type":mime_type})
                                else:
                                    print(f"File not found at local path: {local_file_path}")
                                    message_content.append({"type": "text", "text": f"[Failed to load local image: {attachment_name}]"})
                            except Exception as e:
                                print(f"Error fetching local image {image_data}: {e}")
                                message_content.append({"type": "text", "text": f"[Failed to load local image: {attachment_name}]"})
                        elif image_data.startswith("https"):
                            # Public image URL, model can access this
                            message_content.append({"type": "image_url", "image_url": {"url": image_data}})
                        elif image_data:
                            # Data is already base64
                            mime_type = "image/jpeg" # Add your logic to guess mime type
                            data_uri = f"data:{mime_type};base64,{image_data}"
                            message_content.append({"type": "image", "source_type": "base64", "data": image_data,"mime_type":mime_type})

        # 3. Create the final LangChain message
        if message_content:
            if role == "user":
                langchain_messages.append(HumanMessage(content=message_content))
            elif role == "assistant":
                text_only = " ".join([p["text"] for p in message_content if p.get("type") == "text"])
                langchain_messages.append(AIMessage(content=text_only))
            elif role == "system":
                text_only = " ".join([p["text"] for p in message_content if p.get("type") == "text"])
                langchain_messages.append(SystemMessage(content=text_only))
    
    return langchain_messages


def save_image_from_artifact(artifact, save_dir=OUTPUT_DIR, base_filename="chart"):
    """
    Saves an image from a LangGraph artifact to a file.

    Args:
        artifact: The ImageContent object from the LangGraph stream.
        save_dir: The directory to save the file in.
        base_filename: The base name for the saved file.
    """
    # Ensure the object is a valid image artifact
    if not (hasattr(artifact, 'type') and artifact.type == 'image' and hasattr(artifact, 'data')):
        print("Error: Not a valid image artifact.")
        return None

    # 1. Get the Base64 data and MIME type
    base64_data = artifact.data
    mime_type = artifact.mimeType

    # 2. Decode the Base64 string into binary data
    try:
        image_data = base64.b64decode(base64_data)
    except Exception as e:
        print(f"Error decoding Base64 data: {e}")
        return None

    # 3. Determine the file extension from the MIME type
    if not mime_type:
        print("Warning: No MIME type provided. Defaulting to .png")
        file_extension = ".png"
    else:
        
        file_extension = mimetypes.guess_extension(mime_type)
        if not file_extension:
            print(f"Warning: Unknown MIME type '{mime_type}'. Using .bin")
            file_extension = ".bin" # Fallback for unknown types

    # 4. Create the full file path
    os.makedirs(save_dir, exist_ok=True)
    file_path = os.path.join(save_dir, f"{base_filename}{file_extension}")

    # 5. Write the binary data to the file
    try:
        with open(file_path, "wb") as f:
            f.write(image_data)
        print(f"Successfully saved image to: {file_path}")
        return file_path
    except IOError as e:
        print(f"Error writing file to disk: {e}")
        return None