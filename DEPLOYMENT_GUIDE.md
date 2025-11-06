# Deployment Guide - Financial Fraud Detection Platform

## 🎯 Overview

This guide provides **free and low-cost deployment options** for students. The platform consists of:
- **Backend**: FastAPI (Python) + Ollama LLM
- **Frontend**: React (Vite) - Static build
- **Data**: ChromaDB (file-based), SQLite, NetworkX graphs

---

## 🆓 Free Tier Options

### Option 1: Railway.app (Recommended) ⭐

**Why Railway?**
- **Free tier**: $5 credit/month (enough for small apps)
- **Easy deployment**: GitHub integration
- **Persistent storage**: Included
- **No credit card required** for free tier

**Limitations**:
- 500 hours/month free (enough for 24/7 small app)
- 512MB RAM (may need upgrade for models)
- 1GB storage

**Steps**:

1. **Create Railway Account**:
   - Go to https://railway.app
   - Sign up with GitHub
   - No credit card needed

2. **Prepare Backend for Railway**:
   ```bash
   # Create Procfile for Railway
   echo "web: uvicorn src.api.advanced_main:app --host 0.0.0.0 --port \$PORT" > Procfile
   ```

3. **Create railway.json** (optional):
   ```json
   {
     "$schema": "https://railway.app/railway.schema.json",
     "build": {
       "builder": "NIXPACKS"
     },
     "deploy": {
       "startCommand": "uvicorn src.api.advanced_main:app --host 0.0.0.0 --port $PORT",
       "restartPolicyType": "ON_FAILURE",
       "restartPolicyMaxRetries": 10
     }
   }
   ```

4. **Deploy**:
   - Connect GitHub repo to Railway
   - Railway auto-detects Python project
   - Set environment variables (see `.env` section)
   - Deploy!

5. **Deploy Ollama Separately**:
   - Create second Railway service
   - Use Dockerfile (see below)
   - Or use external Ollama service

**Cost**: $0/month (free tier)

---

### Option 2: Render.com

**Why Render?**
- **Free tier**: 750 hours/month
- **Auto-deploy from GitHub**
- **Free PostgreSQL** (optional upgrade)

**Limitations**:
- Spins down after 15min inactivity (free tier)
- 512MB RAM
- Slower cold starts

**Steps**:

1. **Create Render Account**: https://render.com

2. **Deploy Backend**:
   - New → Web Service
   - Connect GitHub repo
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn src.api.advanced_main:app --host 0.0.0.0 --port $PORT`
   - Environment: Python 3.11

3. **Set Environment Variables** (see below)

4. **Deploy Frontend**:
   - New → Static Site
   - Build Command: `cd prd-pathfinder-69 && npm install && npm run build`
   - Publish Directory: `prd-pathfinder-69/dist`

**Cost**: $0/month (free tier)

---

### Option 3: Fly.io

**Why Fly.io?**
- **Free tier**: 3 shared VMs
- **Persistent volumes**: Included
- **Global edge network**

**Limitations**:
- 256MB RAM per VM (may need upgrade)
- 3GB storage per volume

**Steps**:

1. **Install Fly CLI**:
   ```bash
   # Windows (PowerShell)
   powershell -Command "iwr https://fly.io/install.ps1 -useb | iex"
   ```

2. **Create fly.toml**:
   ```toml
   app = "finance-fraud-api"
   primary_region = "iad"

   [build]

   [env]
     PORT = "8001"

   [[services]]
     internal_port = 8001
     protocol = "tcp"

     [[services.ports]]
       handlers = ["http"]
       port = 80

     [[services.ports]]
       handlers = ["tls", "http"]
       port = 443
   ```

3. **Deploy**:
   ```bash
   fly launch
   fly deploy
   ```

**Cost**: $0/month (free tier)

---

### Option 4: Vercel (Frontend Only)

**Why Vercel?**
- **Free tier**: Unlimited static sites
- **Automatic HTTPS**
- **CDN included**

**Steps**:

1. **Build Frontend**:
   ```bash
   cd prd-pathfinder-69
   npm run build
   ```

2. **Deploy to Vercel**:
   - Install Vercel CLI: `npm i -g vercel`
   - Run: `vercel` in `prd-pathfinder-69/`
   - Or connect GitHub repo on vercel.com

3. **Update API URL**:
   - Set `VITE_API_URL` environment variable
   - Point to your backend (Railway/Render/Fly.io)

**Cost**: $0/month (free tier)

---

## 🐳 Docker Deployment (Self-Hosting)

### Option 5: Docker + Free VPS (Oracle Cloud, etc.)

**Why Docker?**
- **Portable**: Run anywhere
- **Isolated**: No conflicts
- **Easy scaling**

**Free VPS Options**:
- **Oracle Cloud**: Always Free (2 VMs, 1GB RAM each)
- **Google Cloud**: Free tier (f1-micro)
- **AWS**: Free tier (t2.micro, 12 months)

**Steps**:

1. **Create Dockerfile** (Backend):
   ```dockerfile
   FROM python:3.11-slim

   WORKDIR /app

   # Install system dependencies
   RUN apt-get update && apt-get install -y \
       build-essential \
       && rm -rf /var/lib/apt/lists/*

   # Copy requirements
   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt

   # Copy application
   COPY . .

   # Expose port
   EXPOSE 8001

   # Run application
   CMD ["uvicorn", "src.api.advanced_main:app", "--host", "0.0.0.0", "--port", "8001"]
   ```

2. **Create docker-compose.yml**:
   ```yaml
   version: '3.8'

   services:
     backend:
       build: .
       ports:
         - "8001:8001"
       environment:
         - API_HOST=0.0.0.0
         - API_PORT=8001
         - OLLAMA_HOST=http://ollama:11434
       volumes:
         - ./data:/app/data
         - ./models:/app/models
       depends_on:
         - ollama

     ollama:
       image: ollama/ollama:latest
       ports:
         - "11434:11434"
       volumes:
         - ollama_data:/root/.ollama

     frontend:
       build:
         context: ./prd-pathfinder-69
         dockerfile: Dockerfile
       ports:
         - "8080:80"
       environment:
         - VITE_API_URL=http://localhost:8001

   volumes:
     ollama_data:
   ```

3. **Deploy**:
   ```bash
   docker-compose up -d
   ```

**Cost**: $0/month (free VPS)

---

## 🔧 Environment Variables

Create `.env` file or set in deployment platform:

```bash
# Environment
ENVIRONMENT=production
DEBUG=False

# API Configuration
API_HOST=0.0.0.0
API_PORT=8001
API_KEY=your-secret-api-key-change-this

# CORS (update with your frontend URL)
CORS_ORIGINS=https://your-frontend.vercel.app,http://localhost:8080

# Database (relative paths work in containers)
CHROMA_PERSIST_DIRECTORY=./data/chroma_db
CASES_DB_PATH=./data/cases.db
GRAPHS_DIRECTORY=./data/graphs

# Ollama (use service name in Docker, or external URL)
OLLAMA_HOST=http://ollama:11434  # Docker
# OLLAMA_HOST=https://your-ollama-service.com  # External

OLLAMA_MODEL=llama3.1:8b

# Model Configuration
EMBEDDING_MODEL=./models/fin-e5
DEVICE=cpu  # Use 'cpu' for free tiers (no GPU)
USE_FP16=False  # Disable for CPU

# Security
SECRET_KEY=your-secret-key-change-this
```

---

## 📦 Deployment Checklist

### Pre-Deployment
- [ ] Test locally: `python start_api.py`
- [ ] Build frontend: `cd prd-pathfinder-69 && npm run build`
- [ ] Verify models exist: `ls models/fin-e5/`
- [ ] Verify data exists: `ls data/chroma_db/`
- [ ] Update CORS origins
- [ ] Change default API keys
- [ ] Set production environment variables

### Backend Deployment
- [ ] Choose platform (Railway/Render/Fly.io)
- [ ] Connect GitHub repo
- [ ] Set environment variables
- [ ] Configure build/start commands
- [ ] Deploy and test: `curl https://your-api.com/health`

### Frontend Deployment
- [ ] Build: `npm run build`
- [ ] Deploy to Vercel/Netlify
- [ ] Set `VITE_API_URL` environment variable
- [ ] Update CORS in backend
- [ ] Test: Open frontend, verify API calls work

### Ollama Deployment
- [ ] Option A: Deploy separately (Railway/Render)
- [ ] Option B: Use external Ollama service
- [ ] Option C: Use Anthropic API instead (paid)
- [ ] Test: `curl http://ollama:11434/api/tags`

### Post-Deployment
- [ ] Test all endpoints
- [ ] Verify data persistence
- [ ] Check logs for errors
- [ ] Monitor resource usage
- [ ] Set up health checks

---

## 🚀 Quick Start: Railway Deployment

### Step 1: Prepare Repository
```bash
# Add Procfile
echo "web: uvicorn src.api.advanced_main:app --host 0.0.0.0 --port \$PORT" > Procfile

# Add runtime.txt (optional, Railway auto-detects)
echo "python-3.11" > runtime.txt

# Commit and push
git add Procfile runtime.txt
git commit -m "Add Railway deployment config"
git push
```

### Step 2: Deploy on Railway
1. Go to https://railway.app
2. New Project → Deploy from GitHub
3. Select your repository
4. Add environment variables (see above)
5. Deploy!

### Step 3: Deploy Frontend
1. Go to Vercel.com
2. Import Git Repository
3. Root Directory: `prd-pathfinder-69`
4. Build Command: `npm run build`
5. Output Directory: `dist`
6. Environment Variable: `VITE_API_URL=https://your-railway-app.railway.app`

### Step 4: Update CORS
In Railway, add environment variable:
```
CORS_ORIGINS=https://your-vercel-app.vercel.app
```

---

## 💰 Cost Comparison

| Platform | Free Tier | RAM | Storage | Best For |
|----------|-----------|-----|---------|----------|
| **Railway** | $5 credit/month | 512MB | 1GB | Easy deployment |
| **Render** | 750 hrs/month | 512MB | - | Auto-deploy |
| **Fly.io** | 3 VMs | 256MB | 3GB | Global edge |
| **Vercel** | Unlimited | - | - | Frontend only |
| **Oracle Cloud** | Always Free | 1GB | 50GB | Self-hosting |

**Recommended**: Railway (backend) + Vercel (frontend) = **$0/month**

---

## 🔍 Troubleshooting

### Issue: Models not found
**Solution**: Ensure models are in repository or use persistent volume
```bash
# Add models to git (if < 100MB) or use external storage
git lfs track "models/**"
```

### Issue: Ollama connection failed
**Solution**: 
- Check `OLLAMA_HOST` environment variable
- Ensure Ollama service is running
- Use external Ollama service if needed

### Issue: Out of memory
**Solution**:
- Use CPU mode: `DEVICE=cpu`
- Disable FP16: `USE_FP16=False`
- Upgrade to paid tier (if needed)

### Issue: Slow queries
**Solution**:
- Enable caching (already enabled)
- Use GPU if available
- Optimize model size

---

## 📚 Additional Resources

- **Railway Docs**: https://docs.railway.app
- **Render Docs**: https://render.com/docs
- **Fly.io Docs**: https://fly.io/docs
- **Vercel Docs**: https://vercel.com/docs
- **Docker Docs**: https://docs.docker.com

---

## 🎓 Student Discounts

Some platforms offer student discounts:
- **GitHub Student Pack**: Free credits for various services
- **AWS Educate**: Free AWS credits
- **Google Cloud**: $300 free credit (one-time)
- **Azure for Students**: $100 free credit

---

**Last Updated**: January 2025
**Recommended**: Railway + Vercel = $0/month

