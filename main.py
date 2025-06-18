import os
from typing import Optional, Dict, Any, List
from fastapi import FastAPI, HTTPException, Header, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx
from dotenv import load_dotenv
import subprocess
import json
import logging
import argparse


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
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
LLM_RELAY_API_KEY = os.getenv("LLM_RELAY_API_KEY")
if not LLM_RELAY_API_KEY:
    raise ValueError("LLM_RELAY_API_KEY environment variable is not set")

DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "openai/gpt-3.5-turbo")


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
        "Authorization": f"Bearer {LLM_RELAY_API_KEY}",
        "HTTP-Referer": "https://github.com/yourusername/llm-relay",  # Replace with your actual repository
        "X-Title": "LLM Relay Server"
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{base_url}/{endpoint}",
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
        # Only log in debug mode
        if logger.level == logging.DEBUG:
            # Log the raw request body
            body = await request.body()
            logger.debug(f"Raw request body: {body.decode()}")
            
            # Parse the request body
            data = await request.json()
            logger.debug(f"Parsed request data: {json.dumps(data, indent=2)}")
        else:
            data = await request.json()
        
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
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='LLM Relay Server')
    parser.add_argument("--base-url", type=str, default="https://api.openai.com/v1", help="Base URL of the endpoint")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode with detailed logging")
    args = parser.parse_args()
    
    base_url = args.base_url
    
    # Set logging level based on debug flag
    if args.debug:
        logger.setLevel(logging.DEBUG)
        logger.debug("Debug mode enabled")
        
    # Print server information
    print("\n" + "="*50)
    print("LLM Relay Server Starting...")
    print("="*50)
    print(subprocess.check_output(["ifconfig"]).decode())
    if args.debug:
        print("Debug mode: Enabled")
    print("="*50 + "\n")
    print("To connect to this server from another machine, use <server_ip>:8000 as the base URL.")
    print("You can find the server's IP from the above ifconfig output.")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)