"""
main.py

Main application entry point.
- Creates the FastAPI app instance.
- Configures middleware (CORS).
- Mounts static file directories.
- Includes API routers.
- Defines the main run block.
"""

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# Import configurations and routers
from config import UPLOAD_DIR, OUTPUT_DIR
from endpoints import router as api_router

# --- App Initialization ---
app = FastAPI()

# --- Middleware ---
# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Static File Mounts ---
# Serve uploaded files at /uploads/<filename>
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")
app.mount("/outputs", StaticFiles(directory=OUTPUT_DIR), name="outputs")


# --- Include Routers ---
app.include_router(api_router)     # All other endpoints


# --- Main Run Block ---
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)