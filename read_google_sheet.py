# -*- coding: utf-8 -*-
"""
Google Sheets Reader - Read column A from a Google Sheet URL

Usage:
    python read_google_sheet.py [sheet_url]

Example:
    python read_google_sheet.py https://docs.google.com/spreadsheets/d/1NLyjL7x47W8ulhK3lFjtMTNQiclk4cpgz38HG07hxJ8/edit
"""
from DrissionPage import ChromiumPage
import time
import sys
import re


def read_google_sheet_column_a(url):
    """Open Google Sheet and read column A"""
    print(f"🌐 Opening Google Sheet: {url}")
    
    # Connect to browser (assumes Chrome is running with --remote-debugging-port=9222)
    try:
        page = ChromiumPage(addr_or_opts=9222)
    except Exception as e:
        print(f"❌ Error connecting to browser: {e}")
        print("\n💡 Make sure Chrome is running with remote debugging:")
        print("   chrome --remote-debugging-port=9222")
        return None
    
    try:
        # Navigate to Google Sheet
        page.get(url)
        page.wait.doc_loaded(timeout=10)
        print("⏳ Waiting for Google Sheets to load...")
        time.sleep(5)  # Wait longer for Google Sheets to fully load
        
        # Try to wait for the grid to appear
        try:
            page.wait.ele_displayed('[role="grid"]', timeout=10)
        except:
            pass
        
        print("📖 Reading column A...")
        
        # Google Sheets uses a specific structure
        # We'll use JavaScript to extract column A values
        column_a_values = page.run_js("""
            // Try to find the sheet grid - Google Sheets uses different selectors
            const sheet = document.querySelector('[role="grid"]') || 
                         document.querySelector('.grid-container') ||
                         document.querySelector('.grid-layout') ||
                         document.querySelector('[data-sheet-container]') ||
                         document.querySelector('.kix-appview-editor');
            
            if (!sheet) {
                // Try to find any element that might contain the sheet
                const possibleSheets = document.querySelectorAll('[role="grid"], [class*="grid"], [class*="sheet"]');
                if (possibleSheets.length > 0) {
                    return {error: 'Sheet found but structure unclear', found: possibleSheets.length};
                }
                return {error: 'Sheet grid not found'};
            }
            
            const columnA = [];
            
            // Method 1: Try to find rows and get first cell of each row
            const rows = sheet.querySelectorAll('[role="row"]');
            if (rows.length > 0) {
                for (let i = 0; i < rows.length; i++) {
                    const row = rows[i];
                    // Get first gridcell in the row
                    const firstCell = row.querySelector('[role="gridcell"]');
                    if (firstCell) {
                        const text = firstCell.textContent.trim();
                        // Skip empty cells and header-like cells
                        if (text && text.length > 0 && !text.match(/^[A-Z]+$/)) {
                            columnA.push(text);
                        }
                    }
                }
            }
            
            // Method 2: If Method 1 didn't work, try finding cells by aria-colindex
            if (columnA.length === 0) {
                const allCells = sheet.querySelectorAll('[role="gridcell"]');
                const seenRows = new Set();
                
                for (let cell of allCells) {
                    const colIndex = cell.getAttribute('aria-colindex');
                    const rowIndex = cell.getAttribute('aria-rowindex') || 
                                    (cell.closest('[role="row"]') && 
                                     Array.from(cell.closest('[role="row"]').parentElement.children).indexOf(cell.closest('[role="row"]')));
                    
                    // Check if it's column A (aria-colindex="1" or first cell in row)
                    if (colIndex === '1' || colIndex === 1) {
                        const text = cell.textContent.trim();
                        if (text && text.length > 0) {
                            // Avoid duplicates by tracking row
                            const rowKey = rowIndex || cell.closest('[role="row"]')?.textContent;
                            if (!seenRows.has(rowKey)) {
                                columnA.push(text);
                                seenRows.add(rowKey);
                            }
                        }
                    }
                }
            }
            
            // Method 3: Try to find cells by data attributes
            if (columnA.length === 0) {
                const cells = sheet.querySelectorAll('[data-col="0"], [data-col="1"], [data-column="0"], [data-column="1"]');
                for (let cell of cells) {
                    const text = cell.textContent.trim();
                    if (text && text.length > 0) {
                        columnA.push(text);
                    }
                }
            }
            
            // Method 4: Fallback - get all visible text from first column area
            if (columnA.length === 0) {
                // Try to scroll to top and get visible cells
                const gridCells = sheet.querySelectorAll('[role="gridcell"]');
                const firstColumnCells = [];
                
                // Group cells by row and take first from each
                const rowMap = new Map();
                for (let cell of gridCells) {
                    const row = cell.closest('[role="row"]');
                    if (row) {
                        const rowId = Array.from(row.parentElement.children).indexOf(row);
                        if (!rowMap.has(rowId)) {
                            const text = cell.textContent.trim();
                            if (text) {
                                firstColumnCells.push(text);
                                rowMap.set(rowId, true);
                            }
                        }
                    }
                }
                
                if (firstColumnCells.length > 0) {
                    return {values: firstColumnCells, method: 'fallback-grouped'};
                }
            }
            
            return {values: columnA, method: columnA.length > 0 ? 'standard' : 'none'};
        """)
        
        if column_a_values and 'values' in column_a_values:
            values = column_a_values['values']
            print(f"\n✅ Found {len(values)} values in column A:\n")
            for idx, value in enumerate(values, start=1):
                print(f"  {idx}. {value}")
            return values
        elif column_a_values and 'error' in column_a_values:
            print(f"❌ Error: {column_a_values['error']}")
            print("\n💡 Trying alternative method...")
            
            # Alternative: Try to get visible text from the page
            try:
                page_text = page.ele('tag:body').text if page.ele('tag:body') else ""
                # Try to extract URLs or text that looks like column A
                lines = [line.strip() for line in page_text.split('\n') if line.strip()]
                print(f"\n📝 Found {len(lines)} text lines (alternative method):\n")
                for idx, line in enumerate(lines[:20], start=1):  # Show first 20
                    print(f"  {idx}. {line}")
                return lines
            except Exception as e:
                print(f"❌ Alternative method also failed: {e}")
                return None
        else:
            print("❌ Could not extract column A values")
            return None
            
    except Exception as e:
        print(f"❌ Error reading Google Sheet: {e}")
        import traceback
        traceback.print_exc()
        return None


def main():
    """Main function"""
    default_url = "https://docs.google.com/spreadsheets/d/1NLyjL7x47W8ulhK3lFjtMTNQiclk4cpgz38HG07hxJ8/edit?pli=1&gid=0#gid=0"
    
    url = sys.argv[1] if len(sys.argv) > 1 else default_url
    
    if not url.startswith(('http://', 'https://')):
        print("❌ Error: URL must start with http:// or https://")
        sys.exit(1)
    
    print("=" * 60)
    print("📊 Google Sheets Reader - Column A")
    print("=" * 60)
    print()
    
    values = read_google_sheet_column_a(url)
    
    if values:
        print(f"\n✅ Successfully read {len(values)} values from column A")
    else:
        print("\n❌ Failed to read column A")


if __name__ == "__main__":
    main()
