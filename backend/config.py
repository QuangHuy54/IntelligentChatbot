import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from mcp import StdioServerParameters

# Load environment variables from .env file
load_dotenv()

# --- Directory Setup ---
# Make sure folder exists
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)
OUTPUT_DIR = "outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

MCP_SERVER_URL = "http://localhost:8017/mcp"
# --- OpenAI LLM Client ---
# Initialize LangChain ChatOpenAI
llm = ChatOpenAI(
    model="gpt-4o-mini",
    api_key=os.getenv("OPENAI_API_KEY"),
    streaming=True,
    temperature=0.7,
)