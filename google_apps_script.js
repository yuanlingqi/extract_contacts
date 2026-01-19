function fetchContactsFromUrls() {
    const sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
  
    const startRow = 2; // Starting from A2
    const lastRow = sheet.getLastRow();
    if (lastRow < startRow) return;
  
    // Read A2:A in one batch
    const urlValues = sheet
      .getRange(startRow, 1, lastRow - startRow + 1, 1)
      .getValues();
  
    // Prepare to write back to B/C/D columns
    const output = [];
  
    for (let i = 0; i < urlValues.length; i++) {
      const rowNumber = startRow + i;
      const url = (urlValues[i][0] || "").toString().trim();
  
      // If column A is empty, skip (don't write to B/C/D)
      if (!url) {
        output.push(["", "", ""]);
        continue;
      }
  
      const apiUrl =
        "https://contact-extractor-api-h86v.onrender.com/extract?url=" +
        encodeURIComponent(url);
  
      try {
        const response = UrlFetchApp.fetch(apiUrl, {
          method: "get",
          muteHttpExceptions: true,
          followRedirects: true,
        });
  
        const status = response.getResponseCode();
        const text = response.getContentText();
  
        if (status !== 200) {
          Logger.log(`Row ${rowNumber} HTTP ${status}`);
          output.push(["", "", ""]);
          continue;
        }
  
        const json = JSON.parse(text);
  
        if (json.success === true && json.data) {
          const name = json.data.name || "";
          const email = json.data.email || "";
          const phone = json.data.phone || "";
  
          Logger.log(
            `Row ${rowNumber} OK: ${name}, ${email}, ${phone}`
          );
  
          output.push([name, email, phone]);
        } else {
          Logger.log(`Row ${rowNumber} failed: ${text}`);
          output.push(["", "", ""]);
        }
      } catch (err) {
        Logger.log(`Row ${rowNumber} error: ${err}`);
        output.push(["", "", ""]);
      }
    }
  
    // Write back to B2:D in one batch
    sheet
      .getRange(startRow, 2, output.length, 3)
      .setValues(output);
  }
  