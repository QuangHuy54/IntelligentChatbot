import os
import json
import pandas as pd
from PIL import Image
from fastapi import APIRouter, Request, UploadFile, File
from fastapi.responses import StreamingResponse
import aiofiles
# Import components from our other files
from config import UPLOAD_DIR
from schemas import ChatRequest
from utils import convert_to_langchain_messages
from chat_service import stream_langchain_response

router = APIRouter()

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    ext = file.filename.split(".")[-1].lower()
    path = os.path.join(UPLOAD_DIR, file.filename)

    # Save file to local folder
    async with aiofiles.open(path, "wb") as f:
        await f.write(await file.read())

    # Build accessible URL
    file_url = f"http://localhost:8000/uploads/{file.filename}"

    # Optional: handle by file type
    if ext in ["xlsx", "xls", "csv"]:
        df = pd.read_excel(path) if ext != "csv" else pd.read_csv(path)
        return {"type": "excel", "url": file_url}

    elif ext in ["png", "jpg", "jpeg", "gif", "webp"]:
        img = Image.open(path)
        return {
            "type": "image",
            "url": file_url,
            "width": img.width,
            "height": img.height,
        }

    else:
        return {"type": "unknown", "url": file_url}


@router.post("/api/chat")
async def http_chat(chat_request: ChatRequest):
    """HTTP POST endpoint for streaming chat responses via SSE with attachment support"""
    print(f"Received HTTP chat request with {len(chat_request.messages)} messages")
    
    try:
        langchain_messages = convert_to_langchain_messages(chat_request.messages)
        
        # Log message types for debugging
        for msg in langchain_messages:
            print(f"Message type: {type(msg).__name__}, Content preview: {str(msg.content)}")
        
        return StreamingResponse(
            stream_langchain_response(langchain_messages),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
            }
        )
    except Exception as e:
        print(f"Error processing request: {e}")
        
        async def error_stream():
            error_data = {
                "type": "error",
                "error": str(e)
            }
            yield f"data: {json.dumps(error_data)}\n\n"
        
        return StreamingResponse(
            error_stream(),
            media_type="text/event-stream"
        )


@router.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy"}