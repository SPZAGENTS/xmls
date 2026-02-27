#!/usr/bin/env python3
"""
Moltbook Poster for CatofSpike
Author: Shpitzi
Usage: python catofspike_moltbook_poster.py "Title" "Content" [submolt]
"""

import urllib.request
import urllib.error
import json
import sys
import ssl

API_KEY = "moltbook_sk_LntdFJK5lWThtIE-lHzXZO5MMN5HYBLZ"
BASE_URL = "https://www.moltbook.com/api/v1"

def post_to_moltbook(title, content, submolt="introductions"):
    url = f"{BASE_URL}/posts"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    data = {
        "title": title,
        "content": content,
        "submolt": submolt
    }
    
    ssl_context = ssl.create_default_context()
    req = urllib.request.Request(
        url,
        data=json.dumps(data).encode('utf-8'),
        headers=headers,
        method='POST'
    )
    
    try:
        with urllib.request.urlopen(req, context=ssl_context, timeout=30) as response:
            result = json.loads(response.read().decode('utf-8'))
            print(f"SUCCESS! Post: {result.get('id', 'unknown')}")
            return result
    except urllib.error.HTTPError as e:
        print(f"HTTP ERROR: {e.code}")
        return None
    except Exception as e:
        print(f"ERROR: {e}")
        return None

def main():
    print("Moltbook Poster")
    if len(sys.argv) < 3:
        print('Usage:')
        print('  python poster.py "Title" "Content" [submolt]')
        sys.exit(1)
    
    result = post_to_moltbook(sys.argv[1], sys.argv[2], 
                               sys.argv[3] if len(sys.argv)>3 else "introductions")
    return 0 if result else 1

if __name__ == "__main__":
    sys.exit(main())
