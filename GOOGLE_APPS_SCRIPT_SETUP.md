# Google Apps Script Setup Guide

## Quick Setup (5 minutes)

### Step 1: Open Apps Script
1. Open your Google Sheet
2. Click **Extensions** → **Apps Script**
3. A new tab will open with the Apps Script editor

### Step 2: Paste the Code
1. Delete any default code in the editor
2. Copy the code from `google_apps_script.js`
3. Paste it into the editor
4. Click **Save** (💾 icon) or press `Cmd+S` (Mac) / `Ctrl+S` (Windows)
5. Give your project a name (e.g., "Read and Write Cells")

### Step 3: Run the Script
1. Select the function `readAndWriteCells` from the function dropdown (top of editor)
2. Click the **Run** button (▶️ icon)
3. First time: You'll be asked to authorize the script
   - Click **Review Permissions**
   - Choose your Google account
   - Click **Advanced** → **Go to [Project Name] (unsafe)**
   - Click **Allow**
4. The script will run and show a popup with the results

## What the Script Does

1. ✅ Reads the URL from cell **A2**
2. ✅ Prints/displays it in:
   - Logger (View → Logs)
   - Console (View → Executions)
   - Popup alert
3. ✅ Writes **"b2"** to cell **B2**
4. ✅ Writes **"c2"** to cell **C2**

## Viewing Results

### View Logs:
- In Apps Script editor: **View** → **Logs**
- Or: **View** → **Executions** to see execution history

### Check Your Sheet:
- Go back to your Google Sheet
- You should see:
  - Cell B2: `b2`
  - Cell C2: `c2`

## Automation Options

### Option 1: Run on Cell Edit (A2)
The script includes an `onEdit` function that runs automatically when A2 is edited:

1. In Apps Script: Click **Triggers** (⏰ clock icon)
2. Click **+ Add Trigger**
3. Configure:
   - Function: `onEdit`
   - Event source: `From spreadsheet`
   - Event type: `On edit`
4. Click **Save**

Now whenever you edit cell A2, the script will automatically run!

### Option 2: Run on a Schedule
Run the script automatically every minute/hour/day:

1. In Apps Script: Click **Triggers** (⏰ clock icon)
2. Click **+ Add Trigger**
3. Configure:
   - Function: `onTimeDriven`
   - Event source: `Time-driven`
   - Type: Choose frequency (every minute, hour, day, etc.)
4. Click **Save**

### Option 3: Create a Custom Menu
Add a menu item to your sheet:

1. Add this function to your script:
```javascript
function onOpen() {
  SpreadsheetApp.getUi()
    .createMenu('Custom Actions')
    .addItem('Read A2 and Write to B2/C2', 'readAndWriteCells')
    .addToUi();
}
```

2. Save and refresh your Google Sheet
3. You'll see a new menu "Custom Actions" with your function

## Troubleshooting

### "Authorization required"
- Click **Review Permissions** and allow access
- The script needs permission to read/write your sheet

### "Function not found"
- Make sure the function name is exactly `readAndWriteCells`
- Check for typos in the function name

### "Script execution failed"
- Check **View** → **Executions** for error details
- Make sure cell A2 exists and has a value

### Script runs but nothing happens
- Check **View** → **Logs** to see what the script is doing
- Make sure you're looking at the correct sheet tab
- Verify the sheet is not in view-only mode

## Advantages of Google Apps Script

✅ **No browser automation needed** - Runs directly in Google Sheets  
✅ **Fast** - No waiting for pages to load  
✅ **Reliable** - Native Google Sheets API  
✅ **Free** - Included with Google Workspace  
✅ **Can be automated** - Triggers, schedules, menus  
✅ **No external dependencies** - Everything built-in  

## Example Usage

1. Put a URL in cell A2: `https://example.com`
2. Run the script
3. Result:
   - A2: `https://example.com` (unchanged)
   - B2: `b2` (written by script)
   - C2: `c2` (written by script)
   - Popup shows: "URL from A2: https://example.com"
