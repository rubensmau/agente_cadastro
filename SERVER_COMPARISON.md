# Server Implementation Comparison

This document compares the two server implementations available in the project.

## Overview

| Feature | Simple Mode | A2A-Compliant Mode |
|---------|-------------|-------------------|
| File | `src/server/a2a_server_simple.py` | `src/server/a2a_server_compliant.py` |
| Start Command | `python -m src.main` | `python -m src.main --mode compliant` |
| Protocol | Direct JSON | A2A Protocol |
| Request Format | Simple JSON object | A2A message wrapper |
| Response Format | Direct JSON result | A2A message wrapper |
| Use Case | Quick testing, simple clients | Full A2A protocol compliance |

## Request Format Comparison

### Simple Mode

**Request:**
```json
{
  "name": "João",
  "city": "São Paulo"
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Found 2 matching record(s)",
  "count": 2,
  "results": [
    {
      "name": "João",
      "surname": "Silva",
      "city": "São Paulo",
      "state": "SP",
      "phone": "(11) 98765-4321"
    }
  ]
}
```

### A2A-Compliant Mode

**Request:**
```json
{
  "message": {
    "role": "user",
    "parts": [
      {
        "text": "{\"name\": \"João\", \"city\": \"São Paulo\"}"
      }
    ]
  }
}
```

**Response:**
```json
{
  "message": {
    "role": "agent",
    "parts": [
      {
        "text": "{\"status\": \"success\", \"message\": \"Found 2 matching record(s)\", \"count\": 2, \"results\": [...]}"
      }
    ]
  }
}
```

## Testing Examples

### With curl

**Simple Mode:**
```bash
curl -X POST http://localhost:8000/send_message \
  -H "Content-Type: application/json" \
  -d '{"name": "João"}'
```

**A2A-Compliant Mode:**
```bash
curl -X POST http://localhost:8000/send_message \
  -H "Content-Type: application/json" \
  -d '{
    "message": {
      "role": "user",
      "parts": [{"text": "{\"name\": \"João\"}"}]
    }
  }'
```

### With httpx (Python)

**Simple Mode:**
```python
import httpx
import asyncio

async def test_simple():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/send_message",
            json={"name": "João"}
        )
        print(response.json())

asyncio.run(test_simple())
```

**A2A-Compliant Mode:**
```python
import httpx
import asyncio
import json

async def test_a2a():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/send_message",
            json={
                "message": {
                    "role": "user",
                    "parts": [{"text": json.dumps({"name": "João"})}]
                }
            }
        )
        # Parse A2A response
        data = response.json()
        result = json.loads(data["message"]["parts"][0]["text"])
        print(result)

asyncio.run(test_a2a())
```

## Test Files

| Server Mode | Test File | Command |
|-------------|-----------|---------|
| Simple | `tests/test_simple_httpx.py` | `python tests/test_simple_httpx.py` |
| A2A-Compliant | `tests/test_a2a_compliant.py` | `python tests/test_a2a_compliant.py` |

## Implementation Details

### Simple Mode (`a2a_server_simple.py`)

**Key Features:**
- Direct JSON parameter extraction from request body
- Straightforward request/response handling
- Easy to test with curl or basic HTTP clients
- Minimal protocol overhead
- Backward compatible with existing simple clients

**Code Structure:**
```python
async def send_message(self, request: Request):
    body = await request.json()
    search_params = body.get("parameters", body)
    results = self.agent.searcher.search(search_params)
    return JSONResponse({
        "status": "success",
        "count": len(results),
        "results": formatted_results
    })
```

### A2A-Compliant Mode (`a2a_server_compliant.py`)

**Key Features:**
- Full A2A protocol compliance
- Message wrapping with role and parts
- Search parameters embedded in message text as JSON
- Error handling with A2A response format
- Validation of A2A message structure
- Compatible with A2A clients and ecosystem

**Code Structure:**
```python
async def send_message(self, request: Request):
    body = await request.json()
    send_request = self._parse_send_message_request(body)
    search_params = self._extract_search_params(send_request)
    results = self.agent.searcher.search(search_params)

    # Return A2A-compliant response
    return JSONResponse({
        "message": {
            "role": "agent",
            "parts": [{"text": json.dumps(result_data)}]
        }
    })
```

## When to Use Each Mode

### Use Simple Mode When:
- Rapid prototyping and development
- Testing with curl or simple HTTP clients
- Building custom integrations without A2A requirements
- Minimizing request/response overhead
- Working with clients that don't support A2A protocol

### Use A2A-Compliant Mode When:
- Integrating with A2A ecosystem
- Ensuring protocol compliance for production deployments
- Working with A2A-aware clients
- Need standardized agent-to-agent communication
- Following A2A specifications strictly

## Error Handling

### Simple Mode
Returns direct error JSON:
```json
{
  "status": "error",
  "message": "Error description"
}
```

### A2A-Compliant Mode
Returns A2A-wrapped error:
```json
{
  "message": {
    "role": "agent",
    "parts": [
      {
        "text": "{\"status\": \"error\", \"message\": \"Error description\"}"
      }
    ]
  }
}
```

## Migration Path

To migrate from Simple to A2A-Compliant:

1. **Update your client to wrap requests:**
   ```python
   # Before (Simple)
   request = {"name": "João"}

   # After (A2A-Compliant)
   request = {
       "message": {
           "role": "user",
           "parts": [{"text": json.dumps({"name": "João"})}]
       }
   }
   ```

2. **Update response parsing:**
   ```python
   # Before (Simple)
   data = response.json()
   results = data["results"]

   # After (A2A-Compliant)
   data = response.json()
   result_text = data["message"]["parts"][0]["text"]
   parsed_data = json.loads(result_text)
   results = parsed_data["results"]
   ```

3. **Switch server mode:**
   ```bash
   # Before
   python -m src.main

   # After
   python -m src.main --mode compliant
   ```

## Conclusion

Both implementations provide the same search functionality with different protocol layers:

- **Simple Mode**: Best for quick testing and simple integrations
- **A2A-Compliant Mode**: Best for production A2A ecosystem integration

Choose based on your integration requirements and client capabilities.
