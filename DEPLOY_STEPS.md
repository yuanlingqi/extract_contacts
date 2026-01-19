# 🚀 Deploy to Render.com - Step by Step

## Step 1: Prepare Your Code

Make sure you have these files in your project:
- ✅ `api_server.py`
- ✅ `extract_contacts.py`
- ✅ `requirements_api.txt`
- ✅ `render.yaml`
- ✅ `build.sh`
- ✅ `Procfile`

## Step 2: Initialize Git (if not already done)

```bash
cd /Users/chenjianping/Desktop/facebook_scraper

# Check if git is initialized
git status

# If not initialized, run:
git init
git add .
git commit -m "Initial commit - Contact Extractor API"
```

## Step 3: Create GitHub Repository

1. Go to https://github.com/new
2. Create a new repository (name it something like `contact-extractor-api`)
3. **Don't** initialize with README (you already have files)
4. Copy the repository URL

## Step 4: Push to GitHub

```bash
# Add your GitHub repository as remote
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git

# Push your code
git branch -M main
git push -u origin main
```

Replace `YOUR_USERNAME` and `YOUR_REPO_NAME` with your actual GitHub username and repository name.

## Step 5: Deploy on Render

### Option A: Using Blueprint (Easiest - Recommended)

1. Go to https://dashboard.render.com/
2. Sign up or log in (free account works)
3. Click **"New +"** button (top right)
4. Select **"Blueprint"**
5. Connect your GitHub account (if not already connected)
6. Select your repository (`contact-extractor-api` or whatever you named it)
7. Click **"Apply"**
8. Render will automatically detect `render.yaml` and configure everything
9. Click **"Apply"** to confirm
10. Wait for deployment (5-10 minutes)

### Option B: Manual Setup

1. Go to https://dashboard.render.com/
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository
4. Configure:
   - **Name:** `contact-extractor-api`
   - **Region:** Choose closest to you
   - **Branch:** `main`
   - **Root Directory:** (leave empty)
   - **Environment:** `Python 3`
   - **Build Command:** `pip install -r requirements_api.txt && chmod +x build.sh && ./build.sh`
   - **Start Command:** `gunicorn api_server:app --bind 0.0.0.0:$PORT --workers 1 --timeout 300 --worker-class sync`
5. Click **"Create Web Service"**

## Step 6: Wait for Deployment

- First deployment takes **5-10 minutes**
- You'll see build logs in real-time
- Watch for:
  - ✅ Installing Python packages
  - ✅ Running build.sh (installing Chrome)
  - ✅ Starting gunicorn server

## Step 7: Get Your API URL

Once deployed, Render will give you a URL like:
```
https://contact-extractor-api.onrender.com
```

## Step 8: Test Your API

### Test Health Check:
```bash
curl https://your-app-name.onrender.com/health
```

Expected response:
```json
{
    "status": "healthy",
    "service": "Contact Extractor API"
}
```

### Test Contact Extraction:
```bash
curl "https://your-app-name.onrender.com/extract?url=https://www.facebook.com/FidelidadeSeguros.Portugal"
```

Or open in browser:
```
https://your-app-name.onrender.com/extract?url=https://www.facebook.com/FidelidadeSeguros.Portugal
```

## 🎉 Done!

Your API is now live on the internet!

## 📝 Important Notes

### Free Tier Limitations:
- ⚠️ Service spins down after **15 minutes** of inactivity
- ⚠️ First request after spin-down takes **~30 seconds** (cold start)
- ⚠️ Limited to **512MB RAM**

### To Avoid Spin-Down:
- Upgrade to **Starter Plan** ($7/month) - no spin-down
- Or use a service like **UptimeRobot** to ping your API every 10 minutes

### View Logs:
- Go to Render Dashboard → Your Service → **Logs** tab
- See all print statements and errors in real-time

### Update Your API:
1. Make changes to your code
2. Commit and push to GitHub:
   ```bash
   git add .
   git commit -m "Update API"
   git push
   ```
3. Render automatically redeploys (takes 2-5 minutes)

## 🔧 Troubleshooting

### Build Fails?
- Check **Logs** in Render dashboard
- Common issues:
  - Missing file (check all files are committed)
  - Build script error (check `build.sh` permissions)
  - Python version mismatch

### API Returns 500 Error?
- Check logs for browser connection errors
- Verify Chrome/Chromium installed (check build logs)
- Check if port 9222 is accessible

### Service Keeps Restarting?
- Check memory usage (free tier: 512MB limit)
- Reduce workers: Change `--workers 1` to `--workers 1` (already set)
- Check for memory leaks

## 📞 Need Help?

- Render Docs: https://render.com/docs
- Check logs in Render dashboard
- Review `DEPLOY_RENDER.md` for detailed guide
