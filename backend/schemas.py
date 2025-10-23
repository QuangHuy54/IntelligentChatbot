from pydantic import BaseModel
from typing import List, Dict, Any, Union, Literal, Optional

# Pydantic model for the POST request body
class ChatRequest(BaseModel):
    messages: List[Dict[str, Any]]
