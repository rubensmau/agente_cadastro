# Quick Start Guide

Get the Registration Agent running in 5 minutes!

## Local Testing (Fastest)

### 1. Clone and Install
```bash
git clone https://github.com/rubensmau/agente_cadastro.git
cd agente_cadastro
pip install -r requirements.txt
```

### 2. Run the Agent
```bash
python -m src.main
```

Default port is 8000. To use a different port:
```bash
PORT=9000 python -m src.main
```

### 3. Test It
Open browser: http://localhost:8000/

Or test with curl:
```bash
# Health check
curl http://localhost:8000/health

# Search by name
curl -X POST http://localhost:8000/send_message \
  -H "Content-Type: application/json" \
  -d '{"name": "João"}'
```

**That's it!** You now have a working A2A agent.

---

## Cloud Run Deployment (2 Minutes)

### Prerequisites
- Google Cloud account with billing
- gcloud CLI installed: https://cloud.google.com/sdk/docs/install

### Quick Deploy with Script

```bash
# 1. Authenticate
gcloud auth login

# 2. Set your project
export GCP_PROJECT_ID="your-project-id"

# 3. Deploy
./deploy.sh
```

The script will:
- ✓ Enable GCP APIs
- ✓ Build and push Docker image
- ✓ Deploy to Cloud Run
- ✓ Output your service URL

### Access Your Agent
```bash
# Your agent will be at:
https://registration-agent-xxx-uc.a.run.app

# Test it:
curl https://your-url.run.app/health
```

---

## Next Steps

### Customize Your Agent

Edit `config/fields_config.yaml`:
```yaml
agent:
  name: "My Custom Agent"
  description: "My agent description"

fields:
  exposed_fields:
    - name
    - city
    # Add/remove fields as needed
```

### Add Your Data

Replace `data/registrations.csv` with your CSV:
```csv
name,surname,cpf,city,state
John,Doe,123.456.789-00,New York,NY
```

### Run Tests
```bash
# Start server (terminal 1)
python -m src.main --mode compliant

# Run tests (terminal 2)
python tests/test_a2a_compliant.py
```

---

## Common Tasks

### Test with A2A Format
```bash
curl -X POST http://localhost:8000/send_message \
  -H "Content-Type: application/json" \
  -d '{
    "message": {
      "role": "user",
      "parts": [{"text": "{\"name\": \"João\"}"}]
    }
  }'

curl -X POST https://registration-agent-153799711060.us-central1.run.app/send_message \
  -H "Content-Type: application/json" \
  -d '{"message": {"role": "user", "parts": [{"text": "{\"name\": \"João\"}"}]}}'


```

### View Agent Card
```bash
curl http://localhost:8000/metadata | jq
```

### Update Deployment
```bash
# Make changes, then redeploy:
./deploy.sh
```

### View Cloud Run Logs
```bash
gcloud run services logs tail registration-agent --region=us-central1
```

---

## Troubleshooting

**Port already in use?**
```bash
# Use a different port
PORT=9000 python -m src.main

# Or find and kill the process using port 8000
lsof -i :8000
kill -9 <PID>
```

**Import errors?**
```bash
pip install -r requirements.txt --upgrade
```

**Cloud deployment fails?**
```bash
gcloud builds list
gcloud builds log BUILD_ID
```

---

## Learn More

- 📖 [Full Documentation](README.md)
- 🚀 [Deployment Guide](DEPLOYMENT.md)
- 🧪 [Testing Guide](TESTING.md)
- 🏗️ [Architecture Decisions](ARCHITECTURE_DECISIONS.md)
- 🎴 [A2A Agent Card](A2A_AGENT_CARD.md)
- ⚖️ [Server Comparison](SERVER_COMPARISON.md)

---

## Support

Issues? Questions?
- Check [DEPLOYMENT.md](DEPLOYMENT.md) troubleshooting section
- Review logs: `gcloud run services logs tail`
- Open issue: https://github.com/rubensmau/agente_cadastro/issues

---

**You're all set!** Your A2A agent is ready for both local testing and cloud deployment. 🎉
