# API Server Deployment Guide

## Local Development

### 1. Install Dependencies

```bash
pip install -r requirements_api.txt
```

### 2. Start Chrome with Remote Debugging

```bash
# macOS
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222

# Linux
google-chrome --remote-debugging-port=9222

# Windows
chrome.exe --remote-debugging-port=9222
```

### 3. Run the API Server

```bash
python api_server.py
```

The API will be available at: `http://localhost:5000`

## API Endpoints

### Health Check
```
GET /health
```

### Extract Contacts (Single URL)
```
GET /extract?url=<URL>
```

Example:
```
GET http://localhost:5000/extract?url=https://www.facebook.com/FidelidadeSeguros.Portugal
```

Response:
```json
{
    "success": true,
    "data": {
        "name": "Fidelidade Seguros",
        "email": "apoiocliente@fidelidade.pt",
        "phone": "21 794 8800",
        "url": "https://www.facebook.com/FidelidadeSeguros.Portugal"
    }
}
```

### Extract Contacts (Batch)
```
POST /extract/batch
Content-Type: application/json

{
    "urls": [
        "https://www.facebook.com/page1",
        "https://www.facebook.com/page2"
    ]
}
```

## Production Deployment

### Option 1: Using Render.com

1. Create a `render.yaml` file (see below)
2. Push to GitHub
3. Connect your GitHub repo to Render
4. Deploy

### Option 2: Using Heroku

1. Create a `Procfile`:
```
web: gunicorn api_server:app --bind 0.0.0.0:$PORT
```

2. Deploy:
```bash
heroku create your-app-name
git push heroku main
```

### Option 3: Using DigitalOcean / AWS / GCP

1. Set up a server with Python 3.8+
2. Install dependencies
3. Use a process manager like PM2 or systemd
4. Set up nginx as reverse proxy
5. Configure Chrome/Chromium in headless mode

## Important Notes for Production

1. **Browser Setup**: For production, you'll need to run Chrome/Chromium in headless mode:
   ```bash
   google-chrome --headless --remote-debugging-port=9222 --no-sandbox --disable-dev-shm-usage
   ```

2. **Process Manager**: Use a process manager to keep the server running:
   - PM2: `pm2 start api_server.py --interpreter python3`
   - systemd: Create a service file

3. **Environment Variables**: Consider using environment variables for configuration

4. **Security**: 
   - Add authentication/API keys
   - Rate limiting
   - Input validation
   - CORS configuration

5. **Monitoring**: Set up logging and monitoring for production use
