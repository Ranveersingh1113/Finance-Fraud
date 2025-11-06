# Quick Start Deployment Guide

## 🚀 Fastest Path to Deployment (15 minutes)

### Prerequisites
- GitHub account
- Railway account (free) - https://railway.app
- Vercel account (free) - https://vercel.com

---

## Step 1: Prepare Your Code (5 min)

### 1.1 Add Deployment Files
The following files are already created:
- ✅ `Procfile` - For Railway
- ✅ `Dockerfile` - For Docker deployments
- ✅ `railway.json` - Railway configuration
- ✅ `docker-compose.yml` - Local Docker setup

### 1.2 Commit and Push
```bash
git add Procfile Dockerfile railway.json docker-compose.yml
git commit -m "Add deployment configuration"
git push origin main
```

---

## Step 2: Deploy Backend to Railway (5 min)

### 2.1 Create Railway Project
1. Go to https://railway.app
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Choose your repository
5. Railway will auto-detect Python

### 2.2 Configure Environment Variables
In Railway dashboard, go to Variables tab and add:

```bash
API_KEY=your-secret-key-here
ENVIRONMENT=production
DEBUG=False
DEVICE=cpu
USE_FP16=False
OLLAMA_HOST=https://your-ollama-service.com  # Or use external service
OLLAMA_MODEL=llama3.1:8b
CORS_ORIGINS=https://your-frontend.vercel.app
```

### 2.3 Deploy
- Railway will automatically build and deploy
- Wait for deployment to complete (~2-3 minutes)
- Copy your Railway URL (e.g., `https://your-app.railway.app`)

### 2.4 Test Backend
```bash
curl https://your-app.railway.app/health
```

---

## Step 3: Deploy Frontend to Vercel (5 min)

### 3.1 Create Vercel Project
1. Go to https://vercel.com
2. Click "Add New" → "Project"
3. Import your GitHub repository
4. Configure:
   - **Framework Preset**: Vite
   - **Root Directory**: `prd-pathfinder-69`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`

### 3.2 Add Environment Variable
In Vercel dashboard, go to Settings → Environment Variables:
```
VITE_API_URL=https://your-app.railway.app
```

### 3.3 Deploy
- Click "Deploy"
- Wait for build to complete (~1-2 minutes)
- Copy your Vercel URL (e.g., `https://your-app.vercel.app`)

### 3.4 Update CORS in Railway
Go back to Railway, update CORS_ORIGINS:
```
CORS_ORIGINS=https://your-app.vercel.app
```
Redeploy if needed.

---

## Step 4: Deploy Ollama (Choose One)

### Option A: Separate Railway Service (Recommended)
1. Create new Railway service
2. Use Docker image: `ollama/ollama:latest`
3. Expose port 11434
4. Update `OLLAMA_HOST` in backend to Railway Ollama URL

### Option B: Use External Ollama Service
- Use a free Ollama hosting service
- Or run Ollama locally and use ngrok for tunneling

### Option C: Use Anthropic API (Paid)
- Replace Ollama with Anthropic Claude
- Update backend code to use Anthropic instead

---

## Step 5: Verify Deployment

### Test Backend
```bash
# Health check
curl https://your-app.railway.app/health

# Simple query (no auth)
curl https://your-app.railway.app/query/simple?query=test
```

### Test Frontend
1. Open your Vercel URL
2. Try a search query
3. Check browser console for errors
4. Verify API calls are working

---

## 🎉 You're Live!

Your application is now deployed:
- **Backend**: https://your-app.railway.app
- **Frontend**: https://your-app.vercel.app
- **API Docs**: https://your-app.railway.app/docs

---

## 🔧 Troubleshooting

### Backend won't start
- Check Railway logs
- Verify environment variables
- Ensure models/data are accessible

### Frontend can't connect to backend
- Check `VITE_API_URL` environment variable
- Verify CORS settings in backend
- Check browser console for errors

### Ollama connection failed
- Verify `OLLAMA_HOST` is correct
- Check if Ollama service is running
- Test Ollama directly: `curl http://ollama-host:11434/api/tags`

---

## 📊 Cost Summary

| Service | Cost |
|---------|------|
| Railway (Backend) | $0/month (free tier) |
| Vercel (Frontend) | $0/month (free tier) |
| Ollama (External) | $0-5/month (depending on service) |
| **Total** | **$0-5/month** |

---

## 🚀 Next Steps

1. **Monitor**: Check Railway/Vercel dashboards for usage
2. **Optimize**: Enable caching, reduce model size if needed
3. **Scale**: Upgrade to paid tiers if you hit limits
4. **Custom Domain**: Add custom domain in Railway/Vercel settings

---

**Need Help?**
- Railway Docs: https://docs.railway.app
- Vercel Docs: https://vercel.com/docs
- Check `DEPLOYMENT_GUIDE.md` for detailed options

