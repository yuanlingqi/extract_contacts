# -*- coding: utf-8 -*-
"""
API Server for Contact Extractor

Usage:
    python api_server.py

API Endpoint:
    GET /extract?url=<URL>
    
Example:
    http://localhost:5000/extract?url=https://www.facebook.com/FidelidadeSeguros.Portugal

Response:
    {
        "success": true,
        "data": {
            "name": "Fidelidade Seguros",
            "email": "apoiocliente@fidelidade.pt",
            "phone": "21 794 8800"
        }
    }
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
import os

# Import extract_contacts function from extract_contacts.py
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from extract_contacts import extract_contacts, clean_name

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes


@app.route('/favicon.ico')
def favicon():
    """Handle favicon requests to prevent 404 errors"""
    return '', 204  # No Content


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "Contact Extractor API"
    }), 200


@app.route('/extract', methods=['GET'])
def extract_contact_api():
    """Extract contact information from a URL"""
    # Get URL from query parameter
    url = request.args.get('url')
    
    if not url:
        return jsonify({
            "success": False,
            "error": "Missing 'url' parameter. Usage: /extract?url=<URL>"
        }), 400
    
    if not url.startswith(('http://', 'https://')):
        return jsonify({
            "success": False,
            "error": "URL must start with http:// or https://"
        }), 400
    
    try:
        # Extract contacts using the existing function
        # Note: This requires Chrome to be running with --remote-debugging-port=9222
        # For production deployment, you might need to use a headless browser service
        result = extract_contacts(url, page=None)
        
        if result is None:
            return jsonify({
                "success": False,
                "error": "Failed to connect to browser. Make sure Chrome is running with --remote-debugging-port=9222",
                "url": url
            }), 500
        
        results, page = result
        
        if results:
            # Clean the name
            name = clean_name(results.get('name', '') or '')
            email = results.get('email', '') or ''
            phone = results.get('phone', '') or ''
            
            # Print results to console
            print("\n" + "=" * 60)
            print("📊 EXTRACTION RESULTS")
            print("=" * 60)
            print(f"URL:   {url}")
            print(f"Name:  {name if name else 'Not found'}")
            print(f"Email: {email if email else 'Not found'}")
            print(f"Phone: {phone if phone else 'Not found'}")
            print("=" * 60 + "\n")
            
            return jsonify({
                "success": True,
                "data": {
                    "name": name,
                    "email": email,
                    "phone": phone,
                    "url": url
                }
            }), 200
        else:
            return jsonify({
                "success": False,
                "error": "Failed to extract contacts from the URL",
                "url": url
            }), 500
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "url": url
        }), 500


@app.route('/extract/batch', methods=['POST'])
def extract_contact_batch_api():
    """Extract contact information from multiple URLs"""
    try:
        data = request.get_json()
        
        if not data or 'urls' not in data:
            return jsonify({
                "success": False,
                "error": "Missing 'urls' array in request body"
            }), 400
        
        urls = data['urls']
        if not isinstance(urls, list):
            return jsonify({
                "success": False,
                "error": "'urls' must be an array"
            }), 400
        
        results = []
        errors = []
        
        # Import page connection
        from DrissionPage import ChromiumPage
        try:
            page = ChromiumPage(addr_or_opts=9222)
        except Exception as e:
            return jsonify({
                "success": False,
                "error": f"Failed to connect to browser: {str(e)}"
            }), 500
        
        for url in urls:
            if not url.startswith(('http://', 'https://')):
                errors.append({
                    "url": url,
                    "error": "Invalid URL format"
                })
                continue
            
            try:
                result = extract_contacts(url, page=page)
                if result is None:
                    errors.append({
                        "url": url,
                        "error": "Failed to extract contacts"
                    })
                    continue
                
                extracted_results, page = result
                if extracted_results:
                    name = clean_name(extracted_results.get('name', '') or '')
                    email = extracted_results.get('email', '') or ''
                    phone = extracted_results.get('phone', '') or ''
                    
                    # Print result to console
                    print(f"✅ [{len(results) + 1}/{len(urls)}] {url[:50]}...")
                    print(f"   Name:  {name if name else 'Not found'}")
                    print(f"   Email: {email if email else 'Not found'}")
                    print(f"   Phone: {phone if phone else 'Not found'}\n")
                    
                    results.append({
                        "url": url,
                        "name": name,
                        "email": email,
                        "phone": phone
                    })
                else:
                    print(f"❌ Failed to extract from: {url}\n")
                    errors.append({
                        "url": url,
                        "error": "Failed to extract contacts"
                    })
            except Exception as e:
                errors.append({
                    "url": url,
                    "error": str(e)
                })
        
        return jsonify({
            "success": True,
            "results": results,
            "errors": errors,
            "total": len(urls),
            "successful": len(results),
            "failed": len(errors)
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


if __name__ == '__main__':
    # Get port from environment variable or use default 5001 (5000 is often used by AirPlay on macOS)
    port = int(os.environ.get('PORT', 5001))
    
    print("=" * 60)
    print("🚀 Contact Extractor API Server")
    print("=" * 60)
    print("\n📡 API Endpoints:")
    print("  GET  /health - Health check")
    print("  GET  /extract?url=<URL> - Extract contacts from a single URL")
    print("  POST /extract/batch - Extract contacts from multiple URLs")
    print(f"\n💡 Example:")
    print(f"  http://localhost:{port}/extract?url=https://www.facebook.com/FidelidadeSeguros.Portugal")
    print("\n⚠️  Note: Make sure Chrome is running with:")
    print("  chrome --remote-debugging-port=9222")
    print("=" * 60)
    print()
    
    # Run the Flask app
    app.run(host='0.0.0.0', port=port, debug=True)
