# Usage Guide

## Starting Services

### Start All Services (Chrome + API Server + ngrok)

```bash
./start_with_ngrok.sh
```

This script will automatically:
- ✅ Start Chrome (remote debugging mode, port 9222)
- ✅ Start API server (port 5001)
- ✅ Start ngrok (expose local service to public internet)

After successful startup, the script will display the ngrok public URL, similar to:
```
🌐 ngrok Public URL:
   https://abc123.ngrok-free.app
```

### Stop All Services

```bash
./stop_services.sh
```

## Configuring Google Apps Script

### Step 1: Open Apps Script

1. Open your Google Sheets
2. Click **Extensions** → **Apps Script**
3. Open `google_apps_script.js` in the editor

### Step 2: Update ngrok URL

Find this line in `google_apps_script.js` (around line 40-42):

```javascript
const apiUrl =
  "https://fb16cab9ef0d.ngrok-free.app/extract?url=" +
  encodeURIComponent(url);
```

Replace `https://fb16cab9ef0d.ngrok-free.app` with the ngrok URL shown by the startup script:

```javascript
const apiUrl =
  "https://YOUR_NGROK_URL.ngrok-free.app/extract?url=" +
  encodeURIComponent(url);
```

**Note:** Each time you restart `start_with_ngrok.sh`, the ngrok URL may change (free tier), so you need to update it again.

### Step 3: Run the Script

1. In Google Sheets, ensure column A contains the URLs to process (starting from row 2)
2. In the Apps Script editor, select the function `fetchContactsFromUrls_batch`
3. Click the **Run** button (▶️)
4. First-time run requires authorization: Click **Review Permissions** → Select account → **Advanced** → **Allow**

**Important: Batch Processing & Multiple Runs**

Due to Google Apps Script execution timeout limitations (6 minutes), the script processes URLs in batches. You need to **run the script multiple times** until all URLs are processed:

- The script processes a limited number of rows per run (default: 15 rows)
- After each run, it saves progress and continues from where it left off
- **Keep clicking Run** until you see "All done." in the logs
- Each run will process the next batch of URLs automatically
- Progress is saved between runs, so you can safely stop and resume later

**How to know when it's done:**
- Check the logs: **View** → **Logs** in Apps Script editor
- When you see "All done." message, all URLs have been processed

### Step 4: View Results

The script will automatically write extracted contact information to:
- **Column B**: Name
- **Column C**: Email
- **Column D**: Phone

