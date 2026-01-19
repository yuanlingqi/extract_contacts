# -*- coding: utf-8 -*-
"""
Google Sheets Reader/Writer - Read URL from A2, write to B2 and C2

Usage:
    python read_google_sheet.py [sheet_url]

Example:
    python read_google_sheet.py https://docs.google.com/spreadsheets/d/1NLyjL7x47W8ulhK3lFjtMTNQiclk4cpgz38HG07hxJ8/edit
"""
from DrissionPage import ChromiumPage
from DrissionPage.common import Keys
import time
import sys
import re


def read_and_write_google_sheet(url):
    """Read URL from A2, print it, and write to B2 and C2"""
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
        
        print("📖 Reading cell A2...")
        
        # Step 1: Read URL from cell A2
        a2_value = page.run_js("""
            // Find the sheet grid
            const sheet = document.querySelector('[role="grid"]') || 
                         document.querySelector('.grid-container') ||
                         document.querySelector('.kix-appview-editor');
            
            if (!sheet) {
                return {error: 'Sheet grid not found'};
            }
            
            // Find cell A2 (row 2, column A = colindex 1)
            // Google Sheets uses 1-based indexing for aria-rowindex and aria-colindex
            let cellA2 = null;
            
            // Method 1: Find by aria attributes (row 2, col 1)
            const allCells = sheet.querySelectorAll('[role="gridcell"]');
            for (let cell of allCells) {
                const rowIndex = cell.getAttribute('aria-rowindex');
                const colIndex = cell.getAttribute('aria-colindex');
                
                // Check if it's row 2, column 1 (A2)
                if (rowIndex === '2' && colIndex === '1') {
                    cellA2 = cell;
                    break;
                }
            }
            
            // Method 2: If not found, try finding by row position
            if (!cellA2) {
                const rows = sheet.querySelectorAll('[role="row"]');
                if (rows.length >= 2) {
                    const row2 = rows[1]; // Second row (index 1)
                    const cells = row2.querySelectorAll('[role="gridcell"]');
                    if (cells.length > 0) {
                        cellA2 = cells[0]; // First cell in row 2
                    }
                }
            }
            
            if (!cellA2) {
                return {error: 'Cell A2 not found'};
            }
            
            // Get the text content
            const text = cellA2.textContent.trim();
            return {value: text, success: true};
        """)
        
        if not a2_value or 'error' in a2_value:
            print(f"❌ Error reading A2: {a2_value.get('error', 'Unknown error') if a2_value else 'No response'}")
            return None
        
        url_from_a2 = a2_value.get('value', '')
        print(f"\n✅ URL from A2: {url_from_a2}")
        print(f"📋 Displaying URL on screen: {url_from_a2}\n")
        
        # Step 2: Write "b2" to cell B2
        print("✍️  Writing 'b2' to cell B2...")
        
        # Find and click on cell B2
        b2_found = page.run_js("""
            const sheet = document.querySelector('[role="grid"]') || 
                         document.querySelector('.grid-container') ||
                         document.querySelector('.kix-appview-editor');
            
            if (!sheet) {
                return {error: 'Sheet grid not found'};
            }
            
            // Find cell B2 (row 2, column B = colindex 2)
            let cellB2 = null;
            const allCells = sheet.querySelectorAll('[role="gridcell"]');
            
            for (let cell of allCells) {
                const rowIndex = cell.getAttribute('aria-rowindex');
                const colIndex = cell.getAttribute('aria-colindex');
                
                if (rowIndex === '2' && colIndex === '2') {
                    cellB2 = cell;
                    break;
                }
            }
            
            // Fallback: Find row 2, then second cell
            if (!cellB2) {
                const rows = sheet.querySelectorAll('[role="row"]');
                if (rows.length >= 2) {
                    const row2 = rows[1];
                    const cells = row2.querySelectorAll('[role="gridcell"]');
                    if (cells.length >= 2) {
                        cellB2 = cells[1]; // Second cell in row 2
                    }
                }
            }
            
            if (!cellB2) {
                return {error: 'Cell B2 not found'};
            }
            
            // Scroll cell into view and click
            cellB2.scrollIntoView({ behavior: 'smooth', block: 'center' });
            cellB2.click();
            cellB2.focus();
            
            return {success: true, element: 'B2'};
        """)
        
        if not b2_found or 'error' in b2_found:
            print(f"   ⚠️  Could not find cell B2: {b2_found.get('error', 'Unknown') if b2_found else 'No response'}")
        else:
            time.sleep(1)  # Wait for cell to be ready
            
            # Try to find and type into the active editor
            try:
                # Look for the active editor element
                editor = page.ele('[contenteditable="true"]', timeout=2) or page.ele('.kix-cell-input', timeout=2)
                if editor:
                    editor.clear()
                    editor.input('b2')
                    time.sleep(0.5)
                    # Press Enter to confirm
                    editor.input(Keys.ENTER)
                    print("   ✅ Successfully wrote 'b2' to B2")
                else:
                    # Fallback: Use JavaScript
                    page.run_js("""
                        const editor = document.querySelector('[contenteditable="true"]') ||
                                      document.querySelector('.kix-cell-input') ||
                                      document.activeElement;
                        if (editor) {
                            editor.focus();
                            editor.textContent = 'b2';
                            editor.innerText = 'b2';
                            editor.dispatchEvent(new Event('input', { bubbles: true }));
                            editor.dispatchEvent(new Event('change', { bubbles: true }));
                        }
                    """)
                    time.sleep(0.5)
                    print("   ✅ Attempted to write 'b2' to B2 (using JavaScript)")
            except Exception as e:
                print(f"   ⚠️  Error writing to B2: {e}")
            time.sleep(1)
        
        # Step 3: Write "c2" to cell C2
        print("✍️  Writing 'c2' to cell C2...")
        
        # Find and click on cell C2
        c2_found = page.run_js("""
            const sheet = document.querySelector('[role="grid"]') || 
                         document.querySelector('.grid-container') ||
                         document.querySelector('.kix-appview-editor');
            
            if (!sheet) {
                return {error: 'Sheet grid not found'};
            }
            
            // Find cell C2 (row 2, column C = colindex 3)
            let cellC2 = null;
            const allCells = sheet.querySelectorAll('[role="gridcell"]');
            
            for (let cell of allCells) {
                const rowIndex = cell.getAttribute('aria-rowindex');
                const colIndex = cell.getAttribute('aria-colindex');
                
                if (rowIndex === '2' && colIndex === '3') {
                    cellC2 = cell;
                    break;
                }
            }
            
            // Fallback: Find row 2, then third cell
            if (!cellC2) {
                const rows = sheet.querySelectorAll('[role="row"]');
                if (rows.length >= 2) {
                    const row2 = rows[1];
                    const cells = row2.querySelectorAll('[role="gridcell"]');
                    if (cells.length >= 3) {
                        cellC2 = cells[2]; // Third cell in row 2
                    }
                }
            }
            
            if (!cellC2) {
                return {error: 'Cell C2 not found'};
            }
            
            // Scroll cell into view and click
            cellC2.scrollIntoView({ behavior: 'smooth', block: 'center' });
            cellC2.click();
            cellC2.focus();
            
            return {success: true, element: 'C2'};
        """)
        
        if not c2_found or 'error' in c2_found:
            print(f"   ⚠️  Could not find cell C2: {c2_found.get('error', 'Unknown') if c2_found else 'No response'}")
        else:
            time.sleep(1)  # Wait for cell to be ready
            
            # Try to find and type into the active editor
            try:
                # Look for the active editor element
                editor = page.ele('[contenteditable="true"]', timeout=2) or page.ele('.kix-cell-input', timeout=2)
                if editor:
                    editor.clear()
                    editor.input('c2')
                    time.sleep(0.5)
                    # Press Enter to confirm
                    editor.input(Keys.ENTER)
                    print("   ✅ Successfully wrote 'c2' to C2")
                else:
                    # Fallback: Use JavaScript
                    page.run_js("""
                        const editor = document.querySelector('[contenteditable="true"]') ||
                                      document.querySelector('.kix-cell-input') ||
                                      document.activeElement;
                        if (editor) {
                            editor.focus();
                            editor.textContent = 'c2';
                            editor.innerText = 'c2';
                            editor.dispatchEvent(new Event('input', { bubbles: true }));
                            editor.dispatchEvent(new Event('change', { bubbles: true }));
                        }
                    """)
                    time.sleep(0.5)
                    print("   ✅ Attempted to write 'c2' to C2 (using JavaScript)")
            except Exception as e:
                print(f"   ⚠️  Error writing to C2: {e}")
            time.sleep(1)
        
        print("\n✅ Operations completed!")
        print(f"   📖 Read from A2: {url_from_a2}")
        print("   ✍️  Wrote 'b2' to B2")
        print("   ✍️  Wrote 'c2' to C2")
        
        return {
            'a2_value': url_from_a2,
            'b2_written': b2_found.get('success', False) if b2_found else False,
            'c2_written': c2_found.get('success', False) if c2_found else False
        }
            
    except Exception as e:
        print(f"❌ Error: {e}")
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
    print("📊 Google Sheets Reader/Writer")
    print("=" * 60)
    print("Tasks:")
    print("  1. Read URL from cell A2")
    print("  2. Print URL on screen")
    print("  3. Write 'b2' to cell B2")
    print("  4. Write 'c2' to cell C2")
    print("=" * 60)
    print()
    
    result = read_and_write_google_sheet(url)
    
    if result:
        print(f"\n✅ Successfully completed all operations!")
    else:
        print("\n❌ Failed to complete operations")


if __name__ == "__main__":
    main()
