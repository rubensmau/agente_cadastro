# A2A Agent Card & Discovery

## What is an Agent Card?

The **Agent Card** is a standardized metadata document that describes an A2A agent's capabilities, skills, and interface. It's similar to an OpenAPI specification for REST APIs - it allows clients to discover what an agent can do without needing external documentation.

## Why Agent Cards Are Required

A2A protocol requires agents to expose their capabilities via an agent card because:

1. **Discovery**: Clients can programmatically discover agent capabilities
2. **Validation**: Input/output schemas enable automatic validation
3. **Interoperability**: Standard format allows agent-to-agent communication
4. **Documentation**: Self-documenting agents reduce integration friction
5. **Registry**: Agent directories can catalog available agents

## How to Retrieve the Agent Card

### For Machines (JSON Format)

**Endpoint**: `GET /metadata`

```bash
curl http://localhost:8000/metadata
```

**Response** (example):
```json
{
  "name": "Registration Data Agent",
  "description": "Agent for querying Brazilian person registration data",
  "version": "1.0.0",
  "url": "http://0.0.0.0:8000",
  "capabilities": {
    "supports_message": true,
    "supports_task_creation": true,
    "supports_streaming": false
  },
  "skills": [
    {
      "id": "search_registration",
      "name": "search_registration",
      "description": "Search Brazilian person registration data...",
      "tags": ["search", "registration", "data-query"],
      "input_schema": {
        "type": "object",
        "properties": {
          "name": {"type": "string", "description": "First name..."},
          "surname": {"type": "string", "description": "Last name..."},
          "cpf": {"type": "string", "description": "CPF number..."}
        }
      },
      "output_schema": {
        "type": "object",
        "properties": {
          "status": {"type": "string"},
          "count": {"type": "integer"},
          "results": {"type": "array"}
        }
      }
    }
  ],
  "defaultInputModes": ["text"],
  "defaultOutputModes": ["text"]
}
```

### For Humans (HTML Format)

**Endpoint**: `GET /` (root)

Visit `http://localhost:8000/` in your browser to see a human-friendly HTML view of the agent card with:
- Agent capabilities
- Searchable and exposed fields
- Usage examples
- API endpoints
- Interactive links

## Agent Card Structure

### Core Fields

| Field | Description | Example |
|-------|-------------|---------|
| `name` | Agent display name | "Registration Data Agent" |
| `description` | What the agent does | "Agent for querying Brazilian..." |
| `version` | Semantic version | "1.0.0" |
| `url` | Agent base URL | "http://0.0.0.0:8000" |

### Capabilities

| Capability | Meaning |
|------------|---------|
| `supports_message` | Can receive A2A messages (synchronous) |
| `supports_task_creation` | Can create async tasks |
| `supports_streaming` | Can stream responses |

### Skills

Each skill represents a specific capability:

```json
{
  "id": "search_registration",
  "name": "search_registration",
  "description": "Search Brazilian person registration data",
  "tags": ["search", "registration"],
  "input_schema": { /* JSON Schema */ },
  "output_schema": { /* JSON Schema */ }
}
```

## Agent Discovery Flow

1. **Client discovers agent URL** (via registry, manual config, etc.)
2. **Client fetches agent card**: `GET /metadata`
3. **Client parses capabilities and skills**
4. **Client validates compatibility** (required skills, input/output formats)
5. **Client constructs A2A request** based on skill's `input_schema`
6. **Client sends message**: `POST /send_message`
7. **Agent validates request** against `input_schema`
8. **Agent processes and responds** per `output_schema`

## Example: Using the Agent Card

### Python Client Discovery

```python
import httpx
import json

async def discover_and_use_agent(agent_url: str):
    """Discover agent capabilities and use them."""

    async with httpx.AsyncClient() as client:
        # 1. Fetch agent card
        card_response = await client.get(f"{agent_url}/metadata")
        agent_card = card_response.json()

        print(f"Agent: {agent_card['name']}")
        print(f"Version: {agent_card['version']}")
        print(f"Capabilities: {agent_card['capabilities']}")

        # 2. Find search skill
        search_skill = next(
            (s for s in agent_card['skills']
             if s['id'] == 'search_registration'),
            None
        )

        if not search_skill:
            print("Search skill not available")
            return

        # 3. Check what fields are searchable
        searchable_fields = search_skill['input_schema']['properties'].keys()
        print(f"Searchable fields: {list(searchable_fields)}")

        # 4. Construct request based on schema
        request = {
            "message": {
                "role": "user",
                "parts": [
                    {"text": json.dumps({"name": "João"})}
                ]
            }
        }

        # 5. Send message
        response = await client.post(
            f"{agent_url}/send_message",
            json=request
        )

        print(f"Response: {response.json()}")

# Usage
await discover_and_use_agent("http://localhost:8000")
```

## Validation with Agent Card

The agent card's schemas enable automatic validation:

```python
from jsonschema import validate

# Get skill's input schema
input_schema = skill['input_schema']

# User input
user_query = {"name": "João", "city": "São Paulo"}

# Validate before sending
validate(instance=user_query, schema=input_schema)
```

## Agent Registry Integration

Agent cards enable agent registries/marketplaces:

```yaml
# Example agent registry entry
agents:
  - id: "registration-agent-brazil"
    url: "https://agents.example.com/registration-br"
    card_url: "https://agents.example.com/registration-br/metadata"
    category: "data-search"
    region: "Brazil"
    rating: 4.5
```

Clients can:
1. Browse registry
2. Fetch agent cards
3. Compare capabilities
4. Choose appropriate agent
5. Integrate programmatically

## Best Practices

### 1. Keep Agent Card Current
Update the agent card whenever you:
- Add/remove skills
- Change input/output schemas
- Modify capabilities
- Update version

### 2. Use Semantic Versioning
```
MAJOR.MINOR.PATCH
- MAJOR: Breaking changes to API
- MINOR: New features (backward compatible)
- PATCH: Bug fixes
```

### 3. Provide Descriptive Schemas
```json
{
  "name": {
    "type": "string",
    "description": "First name to search (partial match, case-insensitive)",
    "examples": ["João", "Maria"]
  }
}
```

### 4. Tag Skills Appropriately
```json
{
  "tags": ["search", "registration", "brazilian-data", "privacy-compliant"]
}
```

### 5. Version Your Skills
```json
{
  "id": "search_registration_v2",
  "name": "search_registration",
  "version": "2.0.0"
}
```

## Security Considerations

### What to Expose
- ✅ Skill names and descriptions
- ✅ Input/output schemas (field names, types)
- ✅ Capabilities and supported operations
- ✅ API version and endpoints

### What NOT to Expose
- ❌ Internal implementation details
- ❌ Database schema or table names
- ❌ Authentication credentials
- ❌ Rate limit details (could enable abuse)
- ❌ Server infrastructure information

## Testing Agent Card

```bash
# Fetch and validate agent card
curl http://localhost:8000/metadata | jq

# Check specific capabilities
curl http://localhost:8000/metadata | jq '.capabilities'

# List all skills
curl http://localhost:8000/metadata | jq '.skills[].name'

# Get input schema for a skill
curl http://localhost:8000/metadata | jq '.skills[] | select(.id=="search_registration") | .input_schema'
```

## Comparison with Other Standards

| Standard | Purpose | Similarity to Agent Card |
|----------|---------|-------------------------|
| OpenAPI/Swagger | REST API documentation | Very similar - describes endpoints, schemas |
| GraphQL Schema | GraphQL API definition | Similar - typed queries, introspection |
| WSDL | SOAP web services | Similar - service description |
| AsyncAPI | Async/event-driven APIs | Similar concept for async operations |

Agent Card is essentially **"OpenAPI for agents"** - a standard way to describe what an AI agent can do.

## Further Reading

- [A2A Protocol Specification](https://github.com/google/adk)
- [Google ADK Documentation](https://github.com/google/adk)
- [JSON Schema](https://json-schema.org/)
- [Agent Card Examples](https://github.com/google/adk/tree/main/examples)
