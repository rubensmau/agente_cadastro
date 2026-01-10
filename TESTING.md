# Testing Guide

This guide explains how to test the Registration Data Agent with both server modes.

## Server Modes

The agent supports two server modes:

### 1. Simple Mode (Default)
Basic JSON API that accepts search parameters directly.

**Start server:**
```bash
python -m src.main
# or explicitly
python -m src.main --mode simple
```

**Request format:**
```json
{
  "name": "João",
  "city": "São Paulo"
}
```

### 2. A2A-Compliant Mode
Fully A2A-protocol compliant server that wraps messages in A2A format.

**Start server:**
```bash
python -m src.main --mode compliant
```

**Request format:**
```json
{
  "message": {
    "role": "user",
    "parts": [
      {
        "text": "{\"name\": \"João\"}"
      }
    ]
  }
}
```

## Testing with curl

### Simple Mode

```bash
# Start server
python -m src.main

# Test searches
curl -X POST http://localhost:8000/send_message \
  -H "Content-Type: application/json" \
  -d '{"name": "João"}'

curl -X POST http://localhost:8000/send_message \
  -H "Content-Type: application/json" \
  -d '{"city": "São Paulo"}'

curl -X POST http://localhost:8000/send_message \
  -H "Content-Type: application/json" \
  -d '{"surname": "Silva", "state": "SP"}'
```

### A2A-Compliant Mode

```bash
# Start server
python -m src.main --mode compliant

# Test A2A searches
curl -X POST http://localhost:8000/send_message \
  -H "Content-Type: application/json" \
  -d '{"message": {"role": "user", "parts": [{"text": "{\"name\": \"João\"}"}]}}'

curl -X POST http://localhost:8000/send_message \
  -H "Content-Type: application/json" \
  -d '{"message": {"role": "user", "parts": [{"text": "{\"city\": \"São Paulo\"}"}]}}'
```

## Testing with httpx (Python)

### Automated Test Suite

The project includes a comprehensive test suite using httpx for the A2A-compliant server.

**Run tests:**

1. Start the A2A-compliant server in one terminal:
```bash
python -m src.main --mode compliant
```

2. Run the test suite in another terminal:
```bash
# Run with pytest
pytest tests/test_a2a_compliant.py -v

# Or run directly
python tests/test_a2a_compliant.py
```

### Manual Testing Script

Create a test script `my_test.py`:

```python
import asyncio
import httpx
import json

async def test_a2a_search():
    """Test A2A-compliant search."""
    base_url = "http://localhost:8000"

    # A2A request format
    request = {
        "message": {
            "role": "user",
            "parts": [
                {"text": json.dumps({"name": "João"})}
            ]
        }
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{base_url}/send_message",
            json=request
        )

        print(f"Status: {response.status_code}")
        data = response.json()

        # Parse response
        result_text = data["message"]["parts"][0]["text"]
        result = json.loads(result_text)

        print(f"Results: {json.dumps(result, indent=2, ensure_ascii=False)}")

if __name__ == "__main__":
    asyncio.run(test_a2a_search())
```

Run it:
```bash
python my_test.py
```

## Test Coverage

The test suite (`tests/test_a2a_compliant.py`) includes:

1. **Health Check** - Verify server is running
2. **Get Metadata** - Retrieve agent card
3. **Search by Name** - Test single-field name search
4. **Search by City** - Test single-field city search
5. **Search by CPF** - Test searchable-but-not-exposed field
6. **Multi-field Search** - Test combining multiple criteria
7. **No Results** - Test queries with no matches
8. **Invalid Format** - Test error handling for malformed requests
9. **Invalid JSON** - Test error handling for invalid JSON in parts

## Expected Response Format

### Simple Mode Response
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

### A2A-Compliant Mode Response
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

## Troubleshooting

### Port Already in Use
```bash
# Find process using port 8000
lsof -i :8000

# Kill the process
kill -9 <PID>
```

### Connection Refused
Make sure the server is running before executing tests:
```bash
# Check if server is running
curl http://localhost:8000/health
```

### Import Errors
Ensure all dependencies are installed:
```bash
pip install -r requirements.txt
```

## Performance Testing

For load testing, use tools like:

```bash
# Using ab (Apache Bench)
ab -n 1000 -c 10 -p search.json -T application/json http://localhost:8000/send_message

# Using wrk
wrk -t12 -c400 -d30s http://localhost:8000/health
```

## Next Steps

- Add pytest fixtures for server startup/teardown
- Implement integration tests with real A2A clients
- Add performance benchmarks
- Create test data generators for various scenarios
