# Quick Deploy to Render.com

## 🚀 Fast Deployment (5 minutes)

### Step 1: Push to GitHub

```bash
git init
git add .
git commit -m "Deploy contact extractor API"
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git push -u origin main
```

### Step 2: Deploy on Render

1. Go to https://dashboard.render.com
2. Click **"New +"** → **"Blueprint"**
3. Connect your GitHub repository
4. Render will auto-detect `render.yaml` and deploy!

### Step 3: Wait & Test

- Deployment takes ~5-10 minutes
- You'll get a URL like: `https://contact-extractor-api.onrender.com`
- Test: `https://your-app.onrender.com/health`

## 📋 Files Needed

Make sure these files are in your repo:
- ✅ `api_server.py`
- ✅ `extract_contacts.py`
- ✅ `requirements_api.txt`
- ✅ `render.yaml`
- ✅ `build.sh`
- ✅ `Procfile`

## ⚠️ Important Notes

1. **Free Tier:** Service spins down after 15 min inactivity (first request takes ~30s)
2. **Chrome:** Automatically installed via `build.sh`
3. **Port:** Automatically set by Render (don't set manually)

## 🔧 Troubleshooting

**Build fails?**
- Check Render logs
- Ensure `build.sh` is executable: `chmod +x build.sh`

**API returns 500?**
- Check if Chrome started (see logs)
- Verify browser connection in logs

**Need help?**
- Check `DEPLOY_RENDER.md` for detailed guide
- View logs in Render dashboard
