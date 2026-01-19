# Deploy to Render.com - Step by Step Guide

## Prerequisites

1. A GitHub account
2. Your code pushed to a GitHub repository
3. A Render.com account (free tier available)

## Step 1: Prepare Your Code

Make sure all these files are in your repository:
- `api_server.py`
- `extract_contacts.py`
- `requirements_api.txt`
- `render.yaml`
- `build.sh` (for installing Chrome/Chromium)

## Step 2: Push to GitHub

```bash
# Initialize git if not already done
git init
git add .
git commit -m "Initial commit - API server for contact extractor"

# Create a new repository on GitHub, then:
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
git branch -M main
git push -u origin main
```

## Step 3: Deploy on Render

### Option A: Using render.yaml (Recommended)

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click **"New +"** → **"Blueprint"**
3. Connect your GitHub repository
4. Render will automatically detect `render.yaml` and deploy

### Option B: Manual Setup

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository
4. Configure:
   - **Name:** `contact-extractor-api`
   - **Environment:** `Python 3`
   - **Build Command:** `pip install -r requirements_api.txt && chmod +x build.sh && ./build.sh`
   - **Start Command:** `gunicorn api_server:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120`
   - **Environment Variables:**
     - `PYTHON_VERSION` = `3.11.0`
     - `PORT` = (auto-set by Render)

## Step 4: Wait for Deployment

Render will:
1. Install dependencies
2. Run the build script to install Chrome/Chromium
3. Start your API server

This takes about 5-10 minutes the first time.

## Step 5: Test Your API

Once deployed, you'll get a URL like:
```
https://contact-extractor-api.onrender.com
```

Test it:
```bash
curl "https://contact-extractor-api.onrender.com/health"
curl "https://contact-extractor-api.onrender.com/extract?url=https://www.facebook.com/FidelidadeSeguros.Portugal"
```

## Important Notes

1. **Free Tier Limitations:**
   - Services spin down after 15 minutes of inactivity
   - First request after spin-down takes ~30 seconds (cold start)
   - Consider upgrading to paid tier for production

2. **Chrome/Chromium:**
   - The build script installs Chromium automatically
   - Runs in headless mode (no GUI)
   - Uses remote debugging on port 9222

3. **Environment Variables:**
   - `PORT` is automatically set by Render
   - No need to set it manually

4. **Logs:**
   - View logs in Render dashboard
   - All print statements will appear in logs

## Troubleshooting

### Build Fails
- Check logs in Render dashboard
- Ensure `build.sh` is executable
- Verify all dependencies in `requirements_api.txt`

### API Returns 500 Error
- Check if Chrome/Chromium is installed (check logs)
- Verify remote debugging port 9222 is accessible
- Check browser connection in logs

### Service Keeps Restarting
- Check memory limits (free tier has 512MB)
- Reduce number of workers in gunicorn command
- Check for memory leaks in code

## Updating Your Deployment

After pushing changes to GitHub:
1. Render automatically detects changes
2. Triggers a new deployment
3. Updates your service (zero downtime)

## Cost

- **Free Tier:** $0/month (with limitations)
- **Starter Plan:** $7/month (no spin-down, better performance)
- **Standard Plan:** $25/month (more resources)
