# -*- coding: utf-8 -*-
"""
Contact Extractor - Extract name, phone, and email from URLs in CSV file

Usage:
    python extract_contacts.py [contacts.csv]

Example:
    python extract_contacts.py
    python extract_contacts.py contacts.csv

The CSV file should have:
- Column A: URL
- Column B: Name (will be filled)
- Column C: Phone (will be filled)
- Column D: Email (will be filled)
"""
from DrissionPage import ChromiumPage
import time
import re
import sys
import csv
import os
from datetime import datetime


def get_playwright_chromium_path():
    """Get the path to Playwright's Chromium browser"""
    import glob
    
    # Method 1: Use Playwright's API
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            # Get the browser path from Playwright
            browser = p.chromium
            executable_path = browser.executable_path
            if executable_path and os.path.exists(executable_path):
                print(f"   ✅ Found via Playwright API: {executable_path}")
                return executable_path
    except Exception as e:
        print(f"   ⚠️  Playwright API failed: {e}")
    
    # Method 2: Try common cache locations
    cache_locations = [
        os.path.expanduser('~/.cache/ms-playwright'),
        '/opt/render/.cache/ms-playwright',
        '/root/.cache/ms-playwright',
        os.path.expanduser('~/.local/share/ms-playwright'),
    ]
    
    for cache_dir in cache_locations:
        if not os.path.exists(cache_dir):
            continue
        
        print(f"   🔍 Checking cache directory: {cache_dir}")
        
        # Look for chromium directories
        chromium_patterns = [
            os.path.join(cache_dir, 'chromium-*/chrome-linux/chrome'),
            os.path.join(cache_dir, 'chromium-*/chrome-linux/chromium'),
            os.path.join(cache_dir, 'chromium-*/headless_shell'),
        ]
        
        for pattern in chromium_patterns:
            matches = glob.glob(pattern)
            for match in matches:
                if os.path.exists(match) and os.access(match, os.X_OK):
                    print(f"   ✅ Found Chromium: {match}")
                    return match
                
                # Also check if it's a directory and look for chrome inside
                if os.path.isdir(match):
                    chrome_exe = os.path.join(match, 'chrome')
                    if os.path.exists(chrome_exe) and os.access(chrome_exe, os.X_OK):
                        print(f"   ✅ Found Chromium: {chrome_exe}")
                        return chrome_exe
    
    # Method 3: Check common Render/Heroku paths (limited search to avoid timeouts)
    print("   🔍 Checking Render-specific paths...")
    render_paths = [
        '/opt/render/project/src/.cache/ms-playwright',
        '/app/.cache/ms-playwright',
    ]
    
    for render_path in render_paths:
        if os.path.exists(render_path):
            chromium_pattern = os.path.join(render_path, 'chromium-*/chrome-linux/chrome')
            matches = glob.glob(chromium_pattern)
            for match in matches:
                if os.path.exists(match) and os.access(match, os.X_OK):
                    print(f"   ✅ Found Chromium in Render path: {match}")
                    return match
    
    print("   ❌ Could not find Playwright Chromium in any location")
    return None


def extract_email_from_text(text):
    """Extract email addresses from text"""
    if not text:
        return None
    email_pattern = r'\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b'
    matches = re.findall(email_pattern, text)
    if matches:
        # Filter out common fake/example emails
        filtered = [e for e in matches if not any(x in e.lower() for x in [
            'example.com', 'test.com', 'domain.com', 'email.com', 
            'facebook.com', 'placeholder.com', 'yourdomain.com'
        ])]
        if filtered:
            return filtered[0]
    return None


def extract_phone_from_text(text):
    """Extract phone numbers from text"""
    if not text:
        return None
    
    # Common phone patterns - improved to handle spaces and various formats
    patterns = [
        # Portuguese format: 21 794 8800 (2 digits, space, 3 digits, space, 4 digits)
        r'\b\d{2}\s+\d{3}\s+\d{4}\b',
        # General format with spaces: +1 234 567 8900 or 1 234 567 8900
        r'\+?\d{1,4}[\s\-]?\d{1,4}[\s\-]?\d{1,4}[\s\-]?\d{1,4}[\s\-]?\d{1,9}',
        # Portuguese mobile: 9XX XXX XXX
        r'\b9\d{2}[\s\-]?\d{3}[\s\-]?\d{3}\b',
        # Portuguese landline: 2X XXX XXXX
        r'\b2\d{1}[\s\-]?\d{3}[\s\-]?\d{4}\b',
        # US format: (XXX) XXX-XXXX
        r'\(?\d{3}\)?[\s\-]?\d{3}[\s\-]?\d{4}',
        # General: 9-15 digits
        r'\b\d{9,15}\b'
    ]
    
    # Also try to find phone numbers near keywords
    phone_keywords = ['phone', 'telephone', 'tel', 'call', 'contact', 'telefone', 'telefone:', '电话']
    for keyword in phone_keywords:
        # Look for pattern: keyword followed by phone number
        keyword_pattern = rf'(?i){re.escape(keyword)}[:\s]*([\d\s\+\-\(\)]{8,20})'
        matches = re.findall(keyword_pattern, text)
        if matches:
            phone = matches[0].strip()
            phone_clean = re.sub(r'[^\d+]', '', phone)
            if len(phone_clean) >= 9:
                return phone
    
    # Try all patterns
    for pattern in patterns:
        matches = re.findall(pattern, text)
        if matches:
            # Filter out matches that are too short or look like dates/years
            for match in matches:
                phone = match.strip()
                phone_clean = re.sub(r'[^\d+]', '', phone)
                # Phone should be at least 9 digits and not look like a year (1900-2099)
                if len(phone_clean) >= 9 and not (1900 <= int(phone_clean[:4]) <= 2099 if len(phone_clean) >= 4 else False):
                    return phone
    
    return None


def extract_name_from_page(page, url=None):
    """Extract name/title from page"""
    name = None
    
    try:
        # Get URL from page if not provided
        if url is None:
            try:
                url = page.url
            except:
                url = ""
        
        # For Facebook pages, use JavaScript to find the page name more reliably
        if is_facebook_url(url):
            try:
                # Use JavaScript to find Facebook page name - more reliable
                name = page.run_js("""
                    // Method 1: Find h1 with page name (most reliable)
                    const h1s = document.querySelectorAll('h1');
                    for (let h1 of h1s) {
                        const text = h1.textContent.trim();
                        // Filter out common UI elements
                        if (text && text.length > 2 && text.length < 200 && 
                            !text.match(/^\\d+/) && 
                            !['Facebook', 'Home', 'Posts', 'About', 'Contact', 'Menu', '简介', '帖子'].includes(text) &&
                            !text.includes('粉丝') && !text.includes('followers') && !text.includes('likes')) {
                            return text;
                        }
                    }
                    
                    // Method 2: Find span with page name near profile picture
                    const spans = document.querySelectorAll('span[dir="auto"]');
                    const candidates = [];
                    for (let span of spans) {
                        const text = span.textContent.trim();
                        if (text && text.length > 2 && text.length < 200 && 
                            !text.match(/^\\d+/) && 
                            !['Facebook', 'Home', 'Posts', 'About', 'Contact', 'Menu', '简介', '帖子'].includes(text) &&
                            !text.includes('粉丝') && !text.includes('followers') && !text.includes('likes')) {
                            candidates.push(text);
                        }
                    }
                    // Return the first candidate that looks like a name (has letters)
                    for (let candidate of candidates) {
                        if (/[a-zA-ZÀ-ÿ]/.test(candidate)) {
                            return candidate;
                        }
                    }
                    
                    return null;
                """)
                if name and len(name) > 2 and len(name) < 200:
                    # Remove "已认证" and "已认证账户" (verified badge) and other common suffixes
                    name = name.strip()
                    name = re.sub(r'\s*已认证账户\s*$', '', name)
                    name = re.sub(r'\s*已认证\s*$', '', name)
                    name = re.sub(r'\s*Verified\s*Account\s*$', '', name, flags=re.IGNORECASE)
                    name = re.sub(r'\s*Verified\s*$', '', name, flags=re.IGNORECASE)
                    return name
            except Exception as e:
                print(f"      ⚠️ JavaScript name extraction failed: {e}")
        
        # Try h1 tag (works for both Facebook and general pages)
        try:
            h1_elements = page.eles('css:h1', timeout=2)
            for h1 in h1_elements:
                if h1:
                    name = h1.text.strip()
                    # Filter out common UI text and numbers
                    if name and len(name) > 2 and len(name) < 200:
                        # Skip if it's just numbers, followers count, or common UI text
                        if (not name.isdigit() and 
                            name.lower() not in ['facebook', 'home', 'posts', 'about', 'contact', 'menu', '简介', '帖子'] and
                            '粉丝' not in name and 'followers' not in name.lower() and 'likes' not in name.lower()):
                            # Remove "已认证" and "已认证账户" (verified badge) and other common suffixes
                            name = re.sub(r'\s*已认证账户\s*$', '', name)
                            name = re.sub(r'\s*已认证\s*$', '', name)
                            name = re.sub(r'\s*Verified\s*Account\s*$', '', name, flags=re.IGNORECASE)
                            name = re.sub(r'\s*Verified\s*$', '', name, flags=re.IGNORECASE)
                            return name
        except:
            pass
        
        # Try page title
        title = page.title
        if title:
            # Remove common suffixes like "| Facebook", "- Facebook", etc.
            title = re.sub(r'\s*[-|]\s*Facebook.*$', '', title, flags=re.IGNORECASE)
            title = re.sub(r'\s*[-|]\s*.*$', '', title)
            # Remove "已认证" and "已认证账户" (verified badge)
            title = re.sub(r'\s*已认证账户\s*$', '', title)
            title = re.sub(r'\s*已认证\s*$', '', title)
            title = re.sub(r'\s*Verified\s*Account\s*$', '', title, flags=re.IGNORECASE)
            title = re.sub(r'\s*Verified\s*$', '', title, flags=re.IGNORECASE)
            if title and len(title) > 2 and len(title) < 200:
                return title.strip()
        
        # Try meta tags (og:title, title)
        try:
            name = page.run_js("""
                const meta = document.querySelector('meta[property="og:title"]') || 
                            document.querySelector('meta[name="title"]');
                return meta ? (meta.content || '').trim() : null;
            """)
            if name and len(name) > 2 and len(name) < 200:
                return name
        except:
            pass
            
    except Exception as e:
        print(f"      ⚠️ Name extraction error: {e}")
    
    return name


def is_facebook_url(url):
    """Check if URL is a Facebook page"""
    return 'facebook.com' in url.lower() or 'fb.com' in url.lower()


def extract_contacts(url, page=None):
    """Extract name, email, and phone from a URL"""
    print(f"🌐 Opening URL: {url}")
    
    # Connect to browser (assumes Chrome is running with --remote-debugging-port=9222)
    if page is None:
        try:
            # Try to connect to existing browser instance
            page = ChromiumPage(addr_or_opts=9222)
        except Exception as e:
            # If connection fails, try to start browser automatically (for production)
            try:
                import subprocess
                import os
                # Check if we're in a production environment (Render, Heroku, etc.)
                if os.environ.get('RENDER') or os.environ.get('DYNO') or os.path.exists('/.dockerenv'):
                    print("🔧 Production environment detected, starting headless browser...")
                    # Try to start chromium in headless mode
                    chromium_paths = []
                    
                    # Check if we're in Docker (has /.dockerenv file)
                    in_docker = os.path.exists('/.dockerenv')
                    
                    if in_docker:
                        # In Docker, prioritize system Chromium
                        print("   🐳 Docker environment detected, using system Chromium")
                        chromium_paths = [
                            '/usr/bin/chromium',  # Docker/Ubuntu (most common)
                            '/usr/bin/chromium-browser',  # Debian
                        ]
                    else:
                        # Not in Docker, try Playwright first
                        playwright_path = get_playwright_chromium_path()
                        if playwright_path:
                            chromium_paths.append(playwright_path)
                            print(f"   Found Playwright Chromium: {playwright_path}")
                        
                        # Also try to find it manually
                        import glob
                        playwright_chromium_patterns = [
                            os.path.expanduser('~/.cache/ms-playwright/chromium-*/chrome-linux/chrome'),
                            '/opt/render/.cache/ms-playwright/chromium-*/chrome-linux/chrome',
                        ]
                        for pattern in playwright_chromium_patterns:
                            matches = glob.glob(pattern)
                            if matches:
                                chromium_paths.extend(matches)
                    
                    # Add system paths (standard Linux locations)
                    chromium_paths.extend([
                        '/usr/bin/chromium',
                        '/usr/bin/chromium-browser',
                        '/usr/bin/google-chrome',
                        '/usr/bin/google-chrome-stable',
                        '/snap/bin/chromium',
                        os.path.expanduser('~/.local/bin/chromium-browser'),
                        os.path.expanduser('~/.local/chromium/chrome')
                    ])
                    
                    # Also try to find chromium in PATH
                    import shutil
                    chromium_in_path = shutil.which('chromium-browser') or shutil.which('chromium') or shutil.which('google-chrome')
                    if chromium_in_path:
                        chromium_paths.insert(0, chromium_in_path)
                    
                    for chromium_path in chromium_paths:
                        if chromium_path and os.path.exists(chromium_path):
                            try:
                                print(f"   Trying to start: {chromium_path}")
                                subprocess.Popen([
                                    chromium_path,
                                    '--headless',
                                    '--remote-debugging-port=9222',
                                    '--no-sandbox',
                                    '--disable-dev-shm-usage',
                                    '--disable-gpu',
                                    '--disable-software-rasterizer',
                                    '--disable-extensions'
                                ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                                time.sleep(3)  # Wait for browser to start
                                try:
                                    page = ChromiumPage(addr_or_opts=9222)
                                    print(f"   ✅ Successfully connected to browser at {chromium_path}")
                                    break
                                except Exception as conn_err:
                                    print(f"   ⚠️  Could not connect: {conn_err}")
                                    continue
                            except Exception as start_err:
                                print(f"   ⚠️  Could not start {chromium_path}: {start_err}")
                                continue
                    
                    if page is None:
                        # Last resort: try using DrissionPage's built-in browser management
                        playwright_chromium = None
                        try:
                            print("   🔄 Trying DrissionPage browser management...")
                            from DrissionPage import ChromiumOptions
                            
                            # Get Playwright Chromium path
                            playwright_chromium = get_playwright_chromium_path()
                            
                            # If not found, try to install Playwright browsers
                            if not playwright_chromium:
                                print("   ⚠️  Playwright Chromium not found, attempting to install...")
                                try:
                                    import subprocess
                                    result = subprocess.run(
                                        ['python', '-m', 'playwright', 'install', 'chromium'],
                                        capture_output=True,
                                        text=True,
                                        timeout=300
                                    )
                                    if result.returncode == 0:
                                        print("   ✅ Playwright Chromium installed successfully")
                                        playwright_chromium = get_playwright_chromium_path()
                                    else:
                                        print(f"   ⚠️  Installation failed: {result.stderr}")
                                except Exception as install_err:
                                    print(f"   ⚠️  Could not install Playwright browsers: {install_err}")
                            
                            co = ChromiumOptions()
                            co.headless(True)
                            co.set_argument('--no-sandbox')
                            co.set_argument('--disable-dev-shm-usage')
                            co.set_argument('--disable-gpu')
                            co.set_argument('--disable-software-rasterizer')
                            
                            # Set browser path if we found Playwright's Chromium
                            if playwright_chromium and os.path.exists(playwright_chromium):
                                print(f"   📍 Configuring browser path: {playwright_chromium}")
                                co.set_browser_path(playwright_chromium)
                            else:
                                print("   ⚠️  No browser path found, DrissionPage will try to find it automatically")
                            
                            page = ChromiumPage(co)
                            print("   ✅ Browser started via DrissionPage")
                        except Exception as drission_err:
                            error_msg = str(drission_err)
                            if not playwright_chromium:
                                error_msg += " (Playwright Chromium path not found)"
                            
                            # Last resort: Try using Playwright directly (it handles browser discovery automatically)
                            print("   🔄 Trying Playwright directly (auto-discovers browser)...")
                            try:
                                from playwright.sync_api import sync_playwright
                                
                                # Playwright will automatically find/install browsers
                                p = sync_playwright().start()
                                browser = p.chromium.launch(
                                    headless=True,
                                    args=['--no-sandbox', '--disable-dev-shm-usage', '--disable-gpu', '--disable-software-rasterizer']
                                )
                                
                                # Launch browser with remote debugging so DrissionPage can connect
                                browser_with_debug = p.chromium.launch(
                                    headless=True,
                                    args=[
                                        '--remote-debugging-port=9222',
                                        '--no-sandbox',
                                        '--disable-dev-shm-usage',
                                        '--disable-gpu',
                                        '--disable-software-rasterizer'
                                    ]
                                )
                                browser.close()  # Close the first browser
                                
                                # Wait a moment for remote debugging to be ready
                                time.sleep(2)
                                
                                # Now try to connect with DrissionPage
                                try:
                                    page = ChromiumPage(addr_or_opts=9222)
                                    print("   ✅ Browser started via Playwright, connected with DrissionPage")
                                except:
                                    # If DrissionPage can't connect, we need a different approach
                                    raise Exception("Playwright browser started but DrissionPage couldn't connect")
                                    
                            except Exception as playwright_err:
                                raise Exception(f"Could not start or connect to browser. Tried all methods. DrissionPage error: {error_msg}. Playwright error: {playwright_err}")
                else:
                    raise e
            except Exception as e2:
                print(f"❌ Error connecting to browser: {e2}")
                print("\n💡 Make sure Chrome is running with remote debugging:")
                print("   chrome --remote-debugging-port=9222")
                return None, None
    
    name = None
    email = None
    phone = None
    
    try:
        # Navigate to URL
        page.get(url)
        page.wait.doc_loaded(timeout=10)
        time.sleep(2)
        
        # For Facebook pages, try to click "About" section first to get better data
        if is_facebook_url(url):
            print("📘 Detected Facebook page, trying to access About section...")
            try:
                about_btn = (
                    page.ele('xpath://a[contains(text(), "About")]', timeout=3) or
                    page.ele('xpath://span[contains(text(), "About")]', timeout=3) or
                    page.ele('xpath://a[contains(text(), "简介")]', timeout=3) or
                    page.ele('xpath://span[contains(text(), "简介")]', timeout=3)
                )
                if about_btn:
                    about_btn.scroll.to_see(center=True)
                    time.sleep(0.5)
                    about_btn.click()
                    time.sleep(2)
                    print("   ✅ Clicked About section")
            except:
                pass
        # For general webpages, try to click "Contact" link
        else:
            print("🌍 Detected general webpage, trying to access Contact section...")
            try:
                contact_btn = (
                    page.ele('xpath://a[contains(translate(text(), "ABCDEFGHIJKLMNOPQRSTUVWXYZ", "abcdefghijklmnopqrstuvwxyz"), "contact")]', timeout=3) or
                    page.ele('xpath://a[contains(translate(@href, "ABCDEFGHIJKLMNOPQRSTUVWXYZ", "abcdefghijklmnopqrstuvwxyz"), "contact")]', timeout=3)
                )
                if contact_btn:
                    contact_btn.scroll.to_see(center=True)
                    time.sleep(0.5)
                    contact_btn.click()
                    page.wait.doc_loaded(timeout=10)
                    time.sleep(2)
                    print("   ✅ Clicked Contact section")
            except:
                pass
        
        # Extract name after navigating to About/Contact section
        print("📝 Extracting name...")
        name = extract_name_from_page(page, url)
        
        # Get all text from page (HTML + visible text)
        print("🔍 Searching for email and phone...")
        page_text = page.html
        try:
            visible_text = page.ele('tag:body').text if page.ele('tag:body') else ""
            page_text += " " + visible_text
        except:
            pass
        
        # Extract email and phone
        email = extract_email_from_text(page_text)
        phone = extract_phone_from_text(page_text)
        
        # Close any popups
        try:
            page.run_js("""
                document.querySelectorAll('.modal, .popup, .overlay').forEach(el => {
                    if (el.style) el.style.display = 'none';
                    el.remove();
                });
                document.body.style.overflow = 'auto';
            """)
        except:
            pass
        
    except Exception as e:
        print(f"❌ Error extracting contacts: {e}")
        return None, page
    
    return {
        'name': name,
        'email': email,
        'phone': phone
    }, page


def read_csv_urls(filename):
    """Read URLs from CSV file (column A)"""
    urls = []
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            # Skip header row
            next(reader, None)
            
            for row_num, row in enumerate(reader, start=2):
                if len(row) > 0 and row[0].strip():
                    url = row[0].strip()
                    if url.startswith(('http://', 'https://')):
                        urls.append({
                            'row': row_num,
                            'url': url,
                            'name': row[1].strip() if len(row) > 1 else '',
                            'phone': row[2].strip() if len(row) > 2 else '',
                            'email': row[3].strip() if len(row) > 3 else ''
                        })
        
        return urls
    except Exception as e:
        print(f"❌ Error reading CSV: {e}")
        return []


def clean_name(name):
    """Clean name by removing verified badges"""
    if not name:
        return name
    name = name.strip()
    name = re.sub(r'\s*已认证账户\s*$', '', name)
    name = re.sub(r'\s*已认证\s*$', '', name)
    name = re.sub(r'\s*Verified\s*Account\s*$', '', name, flags=re.IGNORECASE)
    name = re.sub(r'\s*Verified\s*$', '', name, flags=re.IGNORECASE)
    return name.strip()


def rewrite_csv_clean_names(filename):
    """Read CSV, clean all names, and rewrite the file"""
    try:
        # Read all rows
        rows = []
        with open(filename, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            rows = list(reader)
        
        # Clean names in all rows (skip header row)
        cleaned_count = 0
        for i in range(1, len(rows)):
            if len(rows[i]) > 1 and rows[i][1]:
                original_name = rows[i][1]
                cleaned_name = clean_name(original_name)
                if cleaned_name != original_name:
                    rows[i][1] = cleaned_name
                    cleaned_count += 1
        
        # Write back to file
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerows(rows)
        
        print(f"✅ Cleaned {cleaned_count} names in CSV")
        return True
    except Exception as e:
        print(f"❌ Error rewriting CSV: {e}")
        return False


def update_csv_row(filename, row_num, name, phone, email):
    """Update a specific row in CSV file"""
    try:
        # Clean the name before saving
        name = clean_name(name)
        
        # Read all rows
        rows = []
        with open(filename, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            rows = list(reader)
        
        # Update the specific row (row_num is 1-indexed, rows list is 0-indexed)
        if row_num <= len(rows):
            row_idx = row_num - 1
            # Ensure row has enough columns
            while len(rows[row_idx]) < 4:
                rows[row_idx].append('')
            
            # Update columns B, C, D (indices 1, 2, 3)
            rows[row_idx][1] = name
            rows[row_idx][2] = phone
            rows[row_idx][3] = email
        
        # Write back to file
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerows(rows)
        
        return True
    except Exception as e:
        print(f"❌ Error updating CSV: {e}")
        return False


def main():
    """Main function"""
    # Check if user wants to just clean the CSV
    if len(sys.argv) > 1 and sys.argv[1] == '--clean':
        csv_file = sys.argv[2] if len(sys.argv) > 2 else 'contacts.csv'
        if not os.path.exists(csv_file):
            print(f"❌ Error: CSV file not found: {csv_file}")
            sys.exit(1)
        print("=" * 60)
        print("🧹 Cleaning Names in CSV")
        print("=" * 60)
        if rewrite_csv_clean_names(csv_file):
            print(f"\n✅ CSV file cleaned: {csv_file}")
        else:
            print(f"\n❌ Failed to clean CSV file")
        return
    
    csv_file = sys.argv[1] if len(sys.argv) > 1 else 'contacts.csv'
    
    if not os.path.exists(csv_file):
        print(f"❌ Error: CSV file not found: {csv_file}")
        print("\n💡 Create a CSV file with:")
        print("   Column A: URL")
        print("   Column B: Name (will be filled)")
        print("   Column C: Phone (will be filled)")
        print("   Column D: Email (will be filled)")
        sys.exit(1)
    
    print("=" * 60)
    print("📞 Contact Extractor - CSV Batch Processing")
    print("=" * 60)
    print(f"📖 Reading URLs from: {csv_file}\n")
    
    # First, clean existing names in CSV
    print("🧹 Cleaning existing names in CSV...")
    rewrite_csv_clean_names(csv_file)
    print()
    
    # Read URLs from CSV
    urls = read_csv_urls(csv_file)
    
    if not urls:
        print("❌ No URLs found in CSV file")
        sys.exit(1)
    
    print(f"✅ Found {len(urls)} URLs to process")
    
    # Filter out URLs that already have all data (but process if name needs cleaning)
    urls_to_process = []
    for url_data in urls:
        name = url_data.get('name', '')
        phone = url_data.get('phone', '')
        email = url_data.get('email', '')
        
        # Process if missing data OR if name contains "已认证账户" (needs cleaning)
        needs_cleaning = '已认证账户' in name or '已认证' in name
        missing_data = not (name and phone and email)
        
        if missing_data or needs_cleaning:
            urls_to_process.append(url_data)
        else:
            print(f"⏭️  Skipping {url_data['url'][:50]}... (already has all data)")
    
    if not urls_to_process:
        print("\n✅ All URLs already processed!")
        return
    
    print(f"📋 Processing {len(urls_to_process)} URLs...\n")
    
    # Connect to browser once
    try:
        page = ChromiumPage(addr_or_opts=9222)
    except Exception as e:
        print(f"❌ Error connecting to browser: {e}")
        print("\n💡 Make sure Chrome is running with remote debugging:")
        print("   chrome --remote-debugging-port=9222")
        sys.exit(1)
    
    # Statistics
    total_processed = 0
    total_found_name = 0
    total_found_email = 0
    total_found_phone = 0
    total_errors = 0
    
    # Process each URL
    for idx, url_data in enumerate(urls_to_process, start=1):
        url = url_data['url']
        row_num = url_data['row']
        
        print(f"\n[{idx}/{len(urls_to_process)}] Processing row {row_num}: {url[:60]}...")
        
        try:
            results, page = extract_contacts(url, page)
            
            if results:
                name = results.get('name', '') or ''
                phone = results.get('phone', '') or ''
                email = results.get('email', '') or ''
                
                # Update statistics
                if name:
                    total_found_name += 1
                if email:
                    total_found_email += 1
                if phone:
                    total_found_phone += 1
                
                # Update CSV
                if update_csv_row(csv_file, row_num, name, phone, email):
                    print(f"   ✅ Updated CSV row {row_num}")
                    if name:
                        print(f"      Name:  {name}")
                    if email:
                        print(f"      Email: {email}")
                    if phone:
                        print(f"      Phone: {phone}")
                else:
                    print(f"   ⚠️  Failed to update CSV row {row_num}")
                
                total_processed += 1
                
                # Add delay between requests
                time.sleep(2)
            else:
                print(f"   ❌ Failed to extract contacts")
                total_errors += 1
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
            total_errors += 1
            time.sleep(3)
    
    # Final summary
    print("\n" + "=" * 60)
    print("📊 FINAL STATISTICS")
    print("=" * 60)
    print(f"✅ Processed: {total_processed}")
    print(f"✅ Found Name: {total_found_name}")
    print(f"✅ Found Email: {total_found_email}")
    print(f"✅ Found Phone: {total_found_phone}")
    print(f"❌ Errors: {total_errors}")
    print("=" * 60)
    print(f"\n💾 Results saved to: {csv_file}")


if __name__ == "__main__":
    main()
