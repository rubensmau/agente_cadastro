# Architecture Decisions

## Starlette vs FastAPI

### Current Choice: Starlette

The project currently uses **Starlette** as the web framework. Here's the rationale and comparison:

### Starlette Advantages
- **Lightweight**: Minimal dependencies, smaller footprint
- **Direct control**: Closer to ASGI, more explicit control over requests/responses
- **Sufficient for A2A**: A2A protocol has well-defined request/response formats
- **Performance**: Slightly less overhead than FastAPI
- **Simplicity**: Fewer abstractions, easier to understand flow

### FastAPI Advantages
- **Automatic validation**: Pydantic models for request/response validation
- **OpenAPI/Swagger**: Automatic API documentation generation
- **Type safety**: Better IDE support and type checking
- **Developer experience**: Less boilerplate, more intuitive
- **Dependency injection**: Built-in DI system
- **Better for complex APIs**: More features out of the box

### Recommendation: Upgrade to FastAPI

For an A2A agent, **FastAPI would be better** because:

1. **Type Safety**: A2A types (SendMessageRequest, AgentCard) can be validated automatically
2. **Documentation**: Auto-generated OpenAPI spec helps other developers integrate
3. **Validation**: Ensures incoming requests match A2A protocol format
4. **Modern**: FastAPI is the de-facto standard for modern Python APIs
5. **Same Performance**: Built on Starlette, so minimal overhead

### Migration Path

The migration is straightforward since FastAPI is built on Starlette:

```python
# Current (Starlette)
from starlette.applications import Starlette
from starlette.routing import Route
from starlette.responses import JSONResponse

app = Starlette(routes=[
    Route("/metadata", get_metadata, methods=["GET"])
])

# Upgraded (FastAPI)
from fastapi import FastAPI
from a2a.types import SendMessageRequest, AgentCard

app = FastAPI(title="Registration Agent")

@app.get("/metadata", response_model=AgentCard)
async def get_metadata():
    return agent.get_agent_card()

@app.post("/send_message")
async def send_message(request: SendMessageRequest):
    # Automatic validation!
    return process_request(request)
```

### When to Keep Starlette

Keep Starlette if:
- You need absolute minimal dependencies
- You're embedding in a larger system
- You have very specific ASGI requirements
- The API surface is tiny and won't grow

### Conclusion

For this A2A agent project, **migrating to FastAPI is recommended** for better developer experience, automatic validation, and built-in documentation.

## Additional Benefits with FastAPI

1. **Interactive docs at `/docs`**: Test API directly in browser
2. **ReDoc at `/redoc`**: Beautiful API documentation
3. **Validation errors**: Automatic 422 responses with detailed error info
4. **OpenAPI spec**: Machine-readable API definition for client generation
