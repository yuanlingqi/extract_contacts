# Docker Deployment Guide

## Why Docker?

Docker provides a consistent environment with all dependencies pre-installed, including Chromium. This eliminates the issues with finding browsers in different environments.

## Files Created

- `Dockerfile` - Defines the Docker image with Python, Chromium, and all dependencies
- `.dockerignore` - Excludes unnecessary files from the Docker build
- Updated `render.yaml` - Configured to use Docker

## Deploying to Render with Docker

### Option 1: Using render.yaml (Automatic)

1. Push your code to GitHub (make sure `Dockerfile` is included)
2. Go to [Render Dashboard](https://dashboard.render.com/)
3. Click **"New +"** → **"Blueprint"**
4. Connect your GitHub repository
5. Render will automatically detect the `Dockerfile` and deploy

### Option 2: Manual Setup

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository
4. Configure:
   - **Name:** `contact-extractor-api`
   - **Environment:** `Docker`
   - **Dockerfile Path:** `./Dockerfile`
   - **Docker Context:** `.`
5. Click **"Create Web Service"**

## Testing Locally

### Build the Docker image:

```bash
docker build -t contact-extractor-api .
```

### Run the container:

```bash
docker run -p 5000:5000 -e PORT=5000 contact-extractor-api
```

### Test the API:

```bash
curl http://localhost:5000/health
curl "http://localhost:5000/extract?url=https://www.facebook.com/FidelidadeSeguros.Portugal"
```

## Advantages of Docker

1. ✅ **Consistent Environment** - Same setup everywhere (local, staging, production)
2. ✅ **Pre-installed Chromium** - No need to find/install browsers at runtime
3. ✅ **Faster Builds** - Dependencies are cached in layers
4. ✅ **Easier Debugging** - Can test locally with exact production setup
5. ✅ **No Build Script Issues** - Everything is in the Dockerfile

## What Changed

- **Before**: Tried to install browsers via build script (failed in read-only environments)
- **After**: Chromium is pre-installed in the Docker image

## Troubleshooting

### Build fails?

- Check that `Dockerfile` is in the root directory
- Verify all files are committed to Git
- Check Render build logs for specific errors

### Container won't start?

- Check that `PORT` environment variable is set (Render sets this automatically)
- Verify gunicorn is installed in requirements
- Check container logs: `docker logs <container-id>`

### Browser not found?

- Docker image includes Chromium at `/usr/bin/chromium`
- Code automatically detects Docker environment (checks for `/.dockerenv`)
- Should work automatically without any configuration
