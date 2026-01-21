function fetchContactsFromUrls_batch() {
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();

  const startRow = 2;
  const lastRow = sheet.getLastRow();
  if (lastRow < startRow) return;

  // —— Configurable Parameters ——
  const BATCH_SIZE = 15;          // Maximum rows to process per batch (recommended: 10~30)
  const SOFT_TIME_LIMIT_MS = 4.5 * 60 * 1000; // Soft time limit: 4.5 minutes (leaves time for writing to sheet)
  const SLEEP_MS = 150;           // Small delay between requests to prevent rate limiting

  const props = PropertiesService.getScriptProperties();
  const nextRowStr = props.getProperty("NEXT_ROW");
  let fromRow = nextRowStr ? parseInt(nextRowStr, 10) : startRow;
  if (isNaN(fromRow) || fromRow < startRow) fromRow = startRow;
  if (fromRow > lastRow) {
    Logger.log("All done.");
    props.deleteProperty("NEXT_ROW");
    return;
  }

  const t0 = Date.now();

  // Number of rows to process in this run
  const maxRowsThisRun = Math.min(BATCH_SIZE, lastRow - fromRow + 1);

  const urlValues = sheet.getRange(fromRow, 1, maxRowsThisRun, 1).getValues();
  const output = [];

  for (let i = 0; i < urlValues.length; i++) {
    const rowNumber = fromRow + i;
    const url = (urlValues[i][0] || "").toString().trim();

    if (!url) {
      output.push(["", "", ""]);
      continue;
    }

    const apiUrl =
      "https://fb16cab9ef0d.ngrok-free.app/extract?url=" +
      encodeURIComponent(url);

    try {
      const response = UrlFetchApp.fetch(apiUrl, {
        method: "get",
        muteHttpExceptions: true,
        followRedirects: true,
        headers: {
          "ngrok-skip-browser-warning": "true",
          "Accept": "application/json",
        },
      });

      const status = response.getResponseCode();
      const text = response.getContentText();

      if (status !== 200) {
        Logger.log(`Row ${rowNumber} HTTP ${status}`);
        output.push(["", "", ""]);
      } else if (text.trim().startsWith("<")) {
        Logger.log(`Row ${rowNumber} got HTML, not JSON`);
        output.push(["", "", ""]);
      } else {
        const json = JSON.parse(text);

        if (json.success === true && json.data) {
          const name = json.data.name || "";
          const email = json.data.email || "";
          const phone = json.data.phone || "";
          Logger.log(`Row ${rowNumber} OK: ${name}, ${email}, ${phone}`);
          output.push([name, email, phone]);
        } else {
          Logger.log(`Row ${rowNumber} failed: ${text.slice(0, 200)}`);
          output.push(["", "", ""]);
        }
      }
    } catch (err) {
      Logger.log(`Row ${rowNumber} error: ${err}`);
      output.push(["", "", ""]);
    }

    Utilities.sleep(SLEEP_MS);

    // Stop early if approaching time limit (leaves time to write back)
    if (Date.now() - t0 > SOFT_TIME_LIMIT_MS) {
      Logger.log("Stopping early to avoid timeout...");
      break;
    }
  }

  // Write back to columns B:C:D (only write the actual number of rows processed)
  if (output.length > 0) {
    sheet.getRange(fromRow, 2, output.length, 3).setValues(output);
  }

  // Record where to continue next time
  const nextRow = fromRow + output.length;
  if (nextRow <= lastRow) {
    props.setProperty("NEXT_ROW", String(nextRow));
    Logger.log(`Progress saved. Next run starts at row ${nextRow}.`);
  } else {
    props.deleteProperty("NEXT_ROW");
    Logger.log("All done.");
  }
}
