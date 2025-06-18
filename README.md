# LLM Relay Server

This is a FastAPI-based relay server that forwards LLM requests from a private network to an external LLM endpoint that uses OpenAI-compatible API (such as OpenAI and OpenRouter). It's designed to work with agentic AI frameworks that need to communicate with the endpoint but are running on machines without direct internet access.

This relay server only works with OpenAI-compatible API. 

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

3. Create a `.env` file with your API key with the LLM provider:
```
LLM_RELAY_API_KEY=your_api_key_here
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

You can also set the `--base-url` flag to a specific base URL. 
By default, it is the default URL of OpenAI.

Add `--debug` flag to show HTTP payloads.

The server will be available at `http://your_server_ip:8000`.

## Usage

The relay server exposes the following endpoints:

- `POST /v1/chat/completions`: Forwards chat completion requests to endpoint
- `POST /v1/completions`: Forwards completion requests to endpoint

You can use these endpoints just like you would use an OpenAI-compatible API directly. The server will handle the authentication and forwarding of requests.

## Configuration

You can configure the following environment variables:
- `LLM_RELAY_API_KEY`: Your API key
- `DEFAULT_MODEL`: Default model to use if not specified in the request (optional) 