#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速测试 API 服务
"""
import requests
import json
import sys

def test_api(url):
    """测试 API 端点"""
    api_url = f"http://localhost:5001/extract?url={url}"
    
    print(f"🔍 Testing API: {api_url}")
    print("-" * 60)
    
    try:
        response = requests.get(api_url, timeout=60)
        data = response.json()
        
        print(f"📊 Status Code: {response.status_code}")
        print(f"📄 Response:")
        print(json.dumps(data, indent=2, ensure_ascii=False))
        
        if data.get('success'):
            print("\n✅ Success!")
            print(f"   📝 Name:  {data['data'].get('name', 'N/A')}")
            print(f"   📧 Email: {data['data'].get('email', 'N/A')}")
            print(f"   📞 Phone: {data['data'].get('phone', 'N/A')}")
        else:
            print(f"\n❌ Error: {data.get('error', 'Unknown error')}")
            
        return data.get('success', False)
        
    except requests.exceptions.ConnectionError:
        print("❌ Error: Cannot connect to API server")
        print("💡 Make sure the API server is running:")
        print("   python extract_contacts.py --server")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_health():
    """测试健康检查端点"""
    try:
        response = requests.get("http://localhost:5001/health", timeout=5)
        data = response.json()
        print(f"✅ Health check: {data}")
        return True
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("🧪 API 测试工具")
    print("=" * 60)
    print()
    
    # 测试健康检查
    print("1️⃣  Testing health endpoint...")
    if not test_health():
        print("\n⚠️  Health check failed. Is the server running?")
        sys.exit(1)
    
    print("\n" + "=" * 60)
    
    # 测试提取端点
    if len(sys.argv) > 1:
        test_url = sys.argv[1]
    else:
        test_url = "https://www.facebook.com/FidelidadeSeguros.Portugal"
        print(f"💡 Using default URL. You can specify a URL:")
        print(f"   python test_api.py <URL>")
        print()
    
    print("2️⃣  Testing extract endpoint...")
    success = test_api(test_url)
    
    print("\n" + "=" * 60)
    sys.exit(0 if success else 1)
