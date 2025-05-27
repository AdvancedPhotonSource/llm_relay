import os
from typing import Optional, Dict, Any, List
from fastapi import FastAPI, HTTPException, Header, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx
from dotenv import load_dotenv
import socket
import requests
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

app = FastAPI(title="LLM Relay Server")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# OpenRouter API configuration
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
if not OPENROUTER_API_KEY:
    raise ValueError("OPENROUTER_API_KEY environment variable is not set")

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "openai/gpt-3.5-turbo")

def get_public_ip() -> str:
    """Get the server's public IP address"""
    try:
        response = requests.get('https://api.ipify.org?format=json')
        return response.json()['ip']
    except Exception as e:
        return "Could not determine public IP"

def get_local_ip() -> str:
    """Get the server's local IP address"""
    try:
        # Create a socket connection to determine the local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception:
        return "Could not determine local IP"

# Models for request/response
class Message(BaseModel):
    role: str
    content: Any  # Changed from str to Any to handle different content types

class ChatCompletionRequest(BaseModel):
    model: Optional[str] = DEFAULT_MODEL
    messages: List[Message]
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = None
    stream: Optional[bool] = False

class CompletionRequest(BaseModel):
    model: Optional[str] = DEFAULT_MODEL
    prompt: str
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = None
    stream: Optional[bool] = False

async def forward_request(endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """Forward request to OpenRouter API"""
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "HTTP-Referer": "https://github.com/yourusername/llm-relay",  # Replace with your actual repository
        "X-Title": "LLM Relay Server"
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{OPENROUTER_BASE_URL}/{endpoint}",
                json=data,
                headers=headers
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            raise HTTPException(
                status_code=e.response.status_code if hasattr(e, 'response') else 500,
                detail=str(e)
            )

@app.post("/v1/chat/completions")
async def chat_completions(request: Request):
    """Handle chat completion requests"""
    try:
        # Log the raw request body
        body = await request.body()
        logger.info(f"Raw request body: {body.decode()}")
        
        # Parse the request body
        data = await request.json()
        logger.info(f"Parsed request data: {json.dumps(data, indent=2)}")
        
        # Forward the request
        return await forward_request("chat/completions", data)
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        raise HTTPException(status_code=422, detail=str(e))

@app.post("/v1/completions")
async def completions(request: CompletionRequest):
    """Handle completion requests"""
    return await forward_request("completions", request.dict(exclude_none=True))

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    
    # Get IP addresses
    public_ip = get_public_ip()
    local_ip = get_local_ip()
    
    # Print server information
    print("\n" + "="*50)
    print("LLM Relay Server Starting...")
    print("="*50)
    print(f"Local IP:  http://{local_ip}:8000")
    print(f"Public IP: http://{public_ip}:8000")
    print("="*50 + "\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8000) 