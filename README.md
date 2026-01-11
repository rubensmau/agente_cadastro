# Registration Data Agent (Agente de Cadastro)

A2A-compliant agent for querying Brazilian person registration data with configurable field exposure and privacy controls.

**Quick Links:**
- 🚀 [Quick Start (5 min)](QUICKSTART.md) - Get running fast!
- 📦 [Deployment Guide](DEPLOYMENT.md) - Local & Cloud Run
- 🧪 [Testing Guide](TESTING.md) - Test suites & examples

## Overview

This agent provides search capabilities over CSV registration data using the Google ADK (Agent Development Kit) framework and A2A (Agent-to-Agent) protocol. It's designed to be easily configurable for multiple deployments with different privacy requirements.

## Features

- **A2A Protocol Compliance**: Full support for Agent-to-Agent communication
- **Flexible Search**: Search by name, surname, CPF, phone, city, or state
- **Privacy Controls**: Configure which fields are exposed to clients
- **Configuration-Driven**: YAML-based configuration for easy customization
- **Brazilian Data Support**: UTF-8 encoding for Portuguese characters, CPF format support
- **Metadata Exposure**: Agent Card available at `/metadata` endpoint

## Project Structure

```
agente_cadastro/
├── src/
│   ├── config/          # Configuration loading and validation
│   ├── agent/           # ADK agent and metadata
│   ├── data/            # CSV reading and search logic
│   ├── server/          # A2A server implementation
│   └── tools/           # ADK tools (search functionality)
├── data/
│   └── registrations.csv    # Sample registration data
├── config/
│   └── fields_config.yaml   # Field exposure configuration
└── requirements.txt
```

## Installation

1. Clone the repository:
```bash
git clone https://github.com/rubensmau/agente_cadastro.git
cd agente_cadastro
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Configuration

Edit `config/fields_config.yaml` to customize the agent:

```yaml
agent:
  name: "Registration Data Agent"
  description: "Agent for querying Brazilian person registration data"
  version: "1.0.0"

data:
  csv_path: "data/registrations.csv"

fields:
  # Fields visible in search results
  exposed_fields:
    - name
    - surname
    - city
    - state
    - phone

  # Fields that can be used in searches
  searchable_fields:
    - name
    - surname
    - cpf
    - phone
    - city
    - state

server:
  host: "0.0.0.0"
  port: 8000
  metadata_endpoint: "/metadata"
```

### Privacy Configuration

The `exposed_fields` configuration controls which fields appear in search results. This allows you to:

- **Public deployment**: Expose only name, city, state
- **Internal deployment**: Expose all fields including CPF, address
- **Partner deployment**: Custom field subset per agreement

Note: Fields can be `searchable` without being `exposed`. For example, CPF can be used to search but won't appear in results for privacy.

## Running the Agent

### Local Development

**Simple Mode (for testing):**
```bash
python -m src.main
```

**A2A-Compliant Mode:**
```bash
python -m src.main --mode compliant
```

The server will start on `http://0.0.0.0:8000` (default) and display:
- Human UI: `/` (browser-friendly view)
- Metadata endpoint: `/metadata` (A2A Agent Card)
- Health check: `/health`
- Search endpoint: `/send_message`

### Changing the Port

You can change the port using any of these methods:

**Option 1: Environment variable (recommended)**
```bash
PORT=9000 python -m src.main --mode compliant
```

**Option 2: Export environment variable**
```bash
export PORT=9000
python -m src.main --mode compliant
```

**Option 3: Edit configuration file**

Edit `config/fields_config.yaml`:
```yaml
server:
  port: 9000  # Change from 8000
```

**Priority:** Environment variable `PORT` overrides the config file setting.

### Cloud Run Deployment

**Quick deployment:**
```bash
export GCP_PROJECT_ID="your-project-id"
./deploy.sh
```

**Automated CI/CD (production):**
```bash
pip install agent-starter-pack
agent-starter-pack setup-cicd  # One-time setup
# Then deployments happen automatically on git push
```

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment options, monitoring, and troubleshooting

## Usage

### Quick Testing with Helper Script

The easiest way to test your agent:

```bash
# Search by name
python agent_helper.py --name João

# Search by city and state
python agent_helper.py --city "São Paulo" --state SP

# Get agent metadata
python agent_helper.py --metadata
```

See [TESTING.md](TESTING.md) for complete helper script documentation.

### Check Agent Metadata

Retrieve the Agent Card to see capabilities and skills:

```bash
curl http://localhost:8000/metadata
```

Response includes:
- Agent name, description, version
- Capabilities (supports_message, supports_task_creation)
- Skills with input/output schemas

### Search Registration Data

Use the `/send_message` endpoint to search for records. The endpoint accepts JSON with search parameters.

**Search by name:**
```bash
curl -X POST http://localhost:8000/send_message \
  -H "Content-Type: application/json" \
  -d '{"name": "João"}'
```

**Search by name and city:**
```bash
curl -X POST http://localhost:8000/send_message \
  -H "Content-Type: application/json" \
  -d '{"name": "Maria", "city": "São Paulo"}'
```

**Search by CPF:**
```bash
curl -X POST http://localhost:8000/send_message \
  -H "Content-Type: application/json" \
  -d '{"cpf": "123.456.789-00"}'
```

**Search by city:**
```bash
curl -X POST http://localhost:8000/send_message \
  -H "Content-Type: application/json" \
  -d '{"city": "Rio de Janeiro"}'
```

**Search by state:**
```bash
curl -X POST http://localhost:8000/send_message \
  -H "Content-Type: application/json" \
  -d '{"state": "SP"}'
```

**Search by phone:**
```bash
curl -X POST http://localhost:8000/send_message \
  -H "Content-Type: application/json" \
  -d '{"phone": "(11) 98765-4321"}'
```

**Multi-field search:**
```bash
curl -X POST http://localhost:8000/send_message \
  -H "Content-Type: application/json" \
  -d '{"surname": "Silva", "state": "SP"}'
```

### Search Response Format

Successful search returns:

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

Note: Only `exposed_fields` appear in results, even if other fields were searched.

## Sample Data

The included `data/registrations.csv` contains 15 sample Brazilian person records with:
- Brazilian names (with Portuguese characters)
- Brazilian addresses
- Major Brazilian cities and states
- Valid CPF number format (XXX.XXX.XXX-XX)
- Brazilian phone format ((XX) XXXXX-XXXX)

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/metadata` | GET | Agent Card with capabilities and skills |
| `/health` | GET | Health check endpoint |
| `/send_message` | POST | Search registration data with query parameters |

## Development

### Adding New Fields

1. Add field to CSV: `data/registrations.csv`
2. Update configuration: Add to `searchable_fields` in `config/fields_config.yaml`
3. Optionally add to `exposed_fields` if it should appear in results
4. Update field descriptions in `src/agent/metadata.py`

### Running Tests

```bash
pytest tests/
```

## Architecture

The agent follows a layered architecture:

- **Configuration Layer** (`src/config/`): YAML loading and validation
- **Data Layer** (`src/data/`): CSV reading, caching, and search logic
- **Agent Layer** (`src/agent/`): ADK agent, tools, and metadata
- **Server Layer** (`src/server/`): A2A protocol implementation with Starlette

Key design patterns:
- **Configuration-driven filtering**: Privacy controls via YAML
- **Tool factory with closure**: Search tool captures config and searcher
- **Layer separation**: Clear boundaries between responsibilities

## Dependencies

- **google-adk**: Agent Development Kit framework
- **a2a-client / a2a-server**: A2A protocol implementation
- **starlette / uvicorn**: ASGI web framework and server
- **pandas**: Data manipulation and search
- **pyyaml**: Configuration file parsing
- **pydantic**: Configuration validation

## License

This project is open source and available for use as a template for building A2A agents.

## Contributing

This agent serves as a template for building configurable A2A agents. Feel free to fork and adapt for your use case.
