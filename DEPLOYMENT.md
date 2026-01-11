# Deployment Guide

This guide covers deploying the Registration Agent both locally and to Google Cloud Run.

## Table of Contents
- [Local Deployment](#local-deployment)
- [Google Cloud Run Deployment](#google-cloud-run-deployment)
- [Environment Variables](#environment-variables)
- [Monitoring & Logging](#monitoring--logging)
- [Troubleshooting](#troubleshooting)

---

## Local Deployment

### Prerequisites
- Python 3.11+
- pip

### Quick Start

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Run in Simple Mode (for testing):**
```bash
python -m src.main
```

3. **Run in A2A-Compliant Mode:**
```bash
python -m src.main --mode compliant
```

4. **Access the agent:**
- Human UI: http://localhost:8000/
- Agent Card: http://localhost:8000/metadata
- Health: http://localhost:8000/health

### Configuration

Edit `config/fields_config.yaml` to customize:
- Agent name and description
- Exposed fields (privacy controls)
- Searchable fields
- Server port and host

### Changing the Port

**Method 1: Environment variable (recommended)**
```bash
PORT=9000 python -m src.main --mode compliant
```

**Method 2: Export environment variable**
```bash
export PORT=9000
python -m src.main --mode compliant
```

**Method 3: Edit config file**

Edit `config/fields_config.yaml`:
```yaml
server:
  port: 9000  # Change from default 8000
```

**Priority:** The `PORT` environment variable overrides the config file setting.

---

## Google Cloud Run Deployment

### Prerequisites

1. **Google Cloud Account** with billing enabled
2. **gcloud CLI** installed: https://cloud.google.com/sdk/docs/install
3. **GCP Project** created
4. **Docker** installed (for manual deployment only)

### Deployment Options

Choose one of three deployment methods:

#### Option 1: Deploy Script (Recommended)

One-command deployment with full control.

```bash
# Set your project ID
export GCP_PROJECT_ID="your-project-id"

# Run deployment script
./deploy.sh
```

The script will:
- Enable required GCP APIs
- Build the Docker image
- Push to Google Container Registry
- Deploy to Cloud Run
- Output the service URL

#### Option 2: Automated CI/CD with agent-starter-pack

Setup automated deployment that triggers on git push:

```bash
# Install agent-starter-pack
pip install agent-starter-pack

# Setup CI/CD infrastructure (one-time setup)
agent-starter-pack setup-cicd

# Configure for Cloud Build or GitHub Actions
# Follow the prompts to select:
# - Deployment target: cloud_run
# - CI/CD runner: google_cloud_build or github_actions
```

Once setup, deployments happen automatically:
```bash
# Make changes, commit, and push
git add .
git commit -m "Update agent"
git push origin main
# Automatic build and deploy!
```

**Features:**
- ✓ Automatic deployment on git push
- ✓ Terraform infrastructure as code
- ✓ Cloud Build or GitHub Actions support
- ✓ Production-ready CI/CD pipeline

#### Option 3: Manual Deployment

See [Manual Deployment Steps](#manual-deployment-steps) below for full control.

### Manual Deployment Steps

#### 1. Authenticate with GCP

```bash
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
```

#### 2. Enable Required APIs

```bash
gcloud services enable \
    cloudbuild.googleapis.com \
    run.googleapis.com \
    containerregistry.googleapis.com
```

#### 3. Build the Docker Image

```bash
docker build -t gcr.io/YOUR_PROJECT_ID/registration-agent:latest .
```

#### 4. Test Locally (Optional)

```bash
docker run -p 8080:8080 \
    -e PORT=8080 \
    -e SERVER_MODE=compliant \
    gcr.io/YOUR_PROJECT_ID/registration-agent:latest
```

Test: http://localhost:8080/health

#### 5. Push to Google Container Registry

```bash
docker push gcr.io/YOUR_PROJECT_ID/registration-agent:latest
```

#### 6. Deploy to Cloud Run

```bash
gcloud run deploy registration-agent \
    --image=gcr.io/YOUR_PROJECT_ID/registration-agent:latest \
    --region=us-central1 \
    --platform=managed \
    --allow-unauthenticated \
    --port=8080 \
    --cpu=1 \
    --memory=512Mi \
    --min-instances=0 \
    --max-instances=10 \
    --timeout=300 \
    --set-env-vars=SERVER_MODE=compliant
```

#### 7. Get Service URL

```bash
gcloud run services describe registration-agent \
    --region=us-central1 \
    --format='value(status.url)'
```

---

## Deployment Method Comparison

| Feature | deploy.sh | CI/CD (agent-starter-pack) | Manual |
|---------|-----------|---------------------------|--------|
| **Ease of use** | ⭐⭐⭐ Easiest | ⭐⭐ Medium | ⭐ Complex |
| **Setup time** | 2 minutes | 5 minutes (one-time) | 5-10 minutes |
| **Configuration** | Environment vars | Terraform + prompts | Full manual |
| **Docker required** | Yes | Yes (automatic) | Yes |
| **Ongoing deployment** | Manual | Automatic on push | Manual |
| **Customization** | Medium | High (Terraform) | Full control |
| **Best for** | Quick/manual deploys | Production automation | Advanced users |

**Recommendation:**
- **Use deploy.sh** for quick manual deployments and testing
- **Use CI/CD setup** for production with automated deployments on git push
- **Use manual** only if integrating with existing infrastructure

---

## Continuous Deployment with Cloud Build

### Setup

1. **Connect GitHub Repository:**
```bash
gcloud builds triggers create github \
    --repo-name=agente_cadastro \
    --repo-owner=rubensmau \
    --branch-pattern="^main$" \
    --build-config=cloudbuild.yaml
```

2. **Push to trigger deployment:**
```bash
git push origin main
```

Cloud Build will automatically:
- Build Docker image
- Push to GCR
- Deploy to Cloud Run

### View Build Logs

```bash
gcloud builds list
gcloud builds log BUILD_ID
```

---

## Environment Variables

### Local Development

You can use environment variables to configure the agent without editing files.

**Set inline:**
```bash
PORT=9000 HOST=0.0.0.0 SERVER_MODE=compliant python -m src.main --mode compliant
```

**Or create `.env` file** (not committed to git):
```bash
PORT=8000
HOST=0.0.0.0
SERVER_MODE=compliant
```

Then load with:
```bash
# If using python-dotenv
python -m src.main --mode compliant
```

### Cloud Run

Set via deployment command:
```bash
gcloud run services update registration-agent \
    --region=us-central1 \
    --set-env-vars=SERVER_MODE=compliant,CUSTOM_VAR=value
```

### Available Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PORT` | 8080 (Cloud Run) / 8000 (local) | Server port |
| `HOST` | 0.0.0.0 | Server host |
| `SERVER_MODE` | compliant | Server mode: 'simple' or 'compliant' |

---

## Monitoring & Logging

### View Logs (Cloud Run)

```bash
# Real-time logs
gcloud run services logs tail registration-agent --region=us-central1

# Recent logs
gcloud run services logs read registration-agent \
    --region=us-central1 \
    --limit=50
```

### Metrics Dashboard

1. Go to [Cloud Console](https://console.cloud.google.com)
2. Navigate to: Cloud Run → registration-agent → Metrics
3. View:
   - Request count
   - Request latency
   - Container instances
   - CPU/Memory utilization

### Custom Monitoring

Add Cloud Monitoring client:
```bash
pip install google-cloud-monitoring
```

Instrument code with custom metrics (optional).

---

## Deployment Options

### Resource Configuration

#### Small (Default)
```bash
--cpu=1 --memory=512Mi --max-instances=10
```
- Best for: Development, low traffic
- Cost: ~$0.05/day (idle) + usage

#### Medium
```bash
--cpu=2 --memory=1Gi --max-instances=50
```
- Best for: Production, moderate traffic
- Cost: ~$0.10/day (idle) + usage

#### Large
```bash
--cpu=4 --memory=2Gi --max-instances=100
```
- Best for: High traffic, large CSV files
- Cost: ~$0.20/day (idle) + usage

### Authentication Options

#### Public (No Authentication)
```bash
--allow-unauthenticated
```
Anyone can access the agent.

#### Private (IAM Authentication)
```bash
--no-allow-unauthenticated
```

Call with authentication:
```bash
curl -H "Authorization: Bearer $(gcloud auth print-identity-token)" \
    https://your-service-url.run.app/health
```

#### Service-to-Service
```bash
gcloud run services add-iam-policy-binding registration-agent \
    --region=us-central1 \
    --member=serviceAccount:caller@project.iam.gserviceaccount.com \
    --role=roles/run.invoker
```

---

## Deployment Checklist

### Before Deployment

- [ ] Test locally with both modes
- [ ] Review `config/fields_config.yaml` for production settings
- [ ] Verify CSV data is appropriate for production
- [ ] Check exposed vs searchable fields (privacy)
- [ ] Set appropriate resource limits
- [ ] Choose authentication strategy
- [ ] Review CORS settings if needed

### After Deployment

- [ ] Test health endpoint
- [ ] Verify agent card retrieval
- [ ] Test search functionality
- [ ] Check logs for errors
- [ ] Monitor resource usage
- [ ] Set up alerts (optional)
- [ ] Document service URL
- [ ] Share with team/users

---

## Cost Estimation

### Cloud Run Pricing (us-central1)

**Free Tier:**
- 2 million requests/month
- 360,000 GB-seconds/month
- 180,000 vCPU-seconds/month

**Paid (after free tier):**
- Requests: $0.40 per million
- Memory: $0.0000025 per GB-second
- CPU: $0.00002400 per vCPU-second
- Networking: $0.12 per GB (egress)

**Example: Small deployment**
- 100,000 requests/month
- Avg 200ms response time
- 512Mi memory, 1 vCPU
- **Cost: ~$2-5/month**

### Container Registry Storage

- $0.026 per GB/month (for stored images)
- Typically < $1/month for this project

---

## Updating the Deployment

### Code Changes

1. Make changes locally
2. Test: `python -m src.main`
3. Commit: `git commit -am "Update message"`
4. Deploy:
   - **Automatic**: Push to main branch (if Cloud Build configured)
   - **Manual**: Run `./deploy.sh`

### Configuration Changes

1. Edit `config/fields_config.yaml`
2. Rebuild and redeploy:
```bash
./deploy.sh
```

### Update Environment Variables

```bash
gcloud run services update registration-agent \
    --region=us-central1 \
    --set-env-vars=SERVER_MODE=compliant,NEW_VAR=value
```

---

## Troubleshooting

### Local Issues

**Port already in use:**
```bash
# Find process
lsof -i :8000
# Kill it
kill -9 <PID>
# Or use different port
PORT=8001 python -m src.main
```

**Import errors:**
```bash
pip install -r requirements.txt --upgrade
```

### Cloud Run Issues

**Deployment fails:**
```bash
# Check Cloud Build logs
gcloud builds list --limit=1
gcloud builds log <BUILD_ID>
```

**Service not starting:**
```bash
# View logs
gcloud run services logs read registration-agent \
    --region=us-central1 \
    --limit=100
```

**Timeout errors:**
```bash
# Increase timeout
gcloud run services update registration-agent \
    --region=us-central1 \
    --timeout=600
```

**Memory issues:**
```bash
# Increase memory
gcloud run services update registration-agent \
    --region=us-central1 \
    --memory=1Gi
```

### Common Errors

**Error: "Could not find module"**
- Check Dockerfile COPY paths
- Verify directory structure in image
- Rebuild: `docker build --no-cache`

**Error: "Permission denied"**
- Check IAM permissions
- Verify service account roles
- Use: `gcloud auth login`

**Error: "Container failed to start"**
- Check `PORT` environment variable
- Verify app listens on `0.0.0.0`
- Review startup logs

---

## Security Best Practices

### For Production

1. **Use Private Services:**
```bash
--no-allow-unauthenticated
```

2. **Implement Rate Limiting:**
Add middleware for request throttling

3. **Enable Audit Logs:**
```bash
gcloud services enable cloudaudit.googleapis.com
```

4. **Use Secret Manager:**
For sensitive configuration (if needed)
```bash
gcloud secrets create agent-config --data-file=config.yaml
```

5. **Regular Updates:**
```bash
pip list --outdated
pip install -r requirements.txt --upgrade
```

---

## Rollback

### Revert to Previous Version

```bash
# List revisions
gcloud run revisions list --service=registration-agent --region=us-central1

# Route traffic to specific revision
gcloud run services update-traffic registration-agent \
    --region=us-central1 \
    --to-revisions=registration-agent-00002-abc=100
```

---

## Additional Resources

- [Cloud Run Documentation](https://cloud.google.com/run/docs)
- [Cloud Build Documentation](https://cloud.google.com/build/docs)
- [Container Registry](https://cloud.google.com/container-registry/docs)
- [A2A Protocol](https://github.com/google/adk)
- [Google ADK](https://github.com/google/adk)

---

## Support

For issues or questions:
1. Check logs: `gcloud run services logs tail`
2. Review troubleshooting section above
3. Open GitHub issue: https://github.com/rubensmau/agente_cadastro/issues
