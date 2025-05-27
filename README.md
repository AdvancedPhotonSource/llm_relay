# LLM Relay Server

This is a FastAPI-based relay server that forwards LLM requests from a private network to OpenRouter. It's designed to work with agentic AI frameworks that need to communicate with OpenRouter's API but are running on machines without direct internet access.

## Setup

1. Create a virtual environment using uv:
```bash
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

2. Install dependencies using uv:
```bash
uv pip install -r requirements.txt
```

3. Create a `.env` file with your OpenRouter API key:
```
OPENROUTER_API_KEY=your_api_key_here
```

## Running the Server

Start the server with:
```bash
python main.py
```
or
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

Add `--debug` flag to show HTTP payloads.

The server will be available at `http://your_server_ip:8000`.

## Usage

The relay server exposes the following endpoints:

- `POST /v1/chat/completions`: Forwards chat completion requests to OpenRouter
- `POST /v1/completions`: Forwards completion requests to OpenRouter

You can use these endpoints just like you would use OpenRouter's API directly. The server will handle the authentication and forwarding of requests.

## Configuration

You can configure the following environment variables:
- `OPENROUTER_API_KEY`: Your OpenRouter API key
- `DEFAULT_MODEL`: Default model to use if not specified in the request (optional) 