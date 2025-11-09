#!/usr/bin/env python3
"""
Cookie Export Utility for MyFitnessPal MCP Server

Extracts MyFitnessPal cookies from your browser and saves them to .env file
for deployment scenarios where browser access isn't available (servers, containers, etc.)
"""

import browser_cookie3
import json
from pathlib import Path


def export_cookies_to_env(browser='auto'):
    """Extract cookies from browser and save to .env file"""
    print(f"🍪 Extracting MyFitnessPal cookies from {browser}...")
    
    # Get cookies from browser
    if browser == 'chrome':
        cookies = browser_cookie3.chrome(domain_name='myfitnesspal.com')
    elif browser == 'firefox':
        cookies = browser_cookie3.firefox(domain_name='myfitnesspal.com')
    elif browser == 'edge':
        cookies = browser_cookie3.edge(domain_name='myfitnesspal.com')
    elif browser == 'safari':
        cookies = browser_cookie3.safari(domain_name='myfitnesspal.com')
    else:
        # Try all browsers (may fail on Safari)
        cookies = browser_cookie3.load(domain_name='myfitnesspal.com')
    
    # Convert to dict
    cookie_dict = {}
    for cookie in cookies:
        cookie_dict[cookie.name] = {
            'value': cookie.value,
            'domain': cookie.domain,
            'path': cookie.path,
            'secure': cookie.secure,
        }
    
    if not cookie_dict:
        print("❌ No cookies found! Make sure you're logged into MyFitnessPal in your browser.")
        return False
    
    print(f"✓ Found {len(cookie_dict)} cookies")
    
    # Save to .env file
    env_path = Path(__file__).parent / '.env'
    
    # Convert to JSON string for single env var
    cookies_json = json.dumps(cookie_dict, indent=None)
    
    with open(env_path, 'w') as f:
        f.write("# MyFitnessPal Cookies (extracted from browser)\n")
        f.write("# Use this for deployment without browser access\n\n")
        f.write(f'MFP_COOKIES={cookies_json}\n')
    
    print(f"✓ Saved cookies to {env_path}")
    print("\n📝 Key cookies found:")
    important_cookies = ['_mfp_session', '__Secure-next-auth.session-token', 'known_user', 'remember_me']
    for key in important_cookies:
        if key in cookie_dict:
            value = cookie_dict[key]['value']
            print(f"  - {key}: {value[:20]}...")
    
    print("\n⚠️  Security Notes:")
    print("  - These cookies grant access to your MyFitnessPal account")
    print("  - Keep .env file secure and never commit to git")
    print("  - Cookies expire after ~30 days, re-run this script when needed")
    
    return True


def export_cookies_to_json():
    """Extract cookies and save as JSON file (alternative format)"""
    print("🍪 Extracting MyFitnessPal cookies from browser...")
    
    cookies = browser_cookie3.load(domain_name='myfitnesspal.com')
    
    cookie_list = []
    for cookie in cookies:
        cookie_list.append({
            'name': cookie.name,
            'value': cookie.value,
            'domain': cookie.domain,
            'path': cookie.path,
            'secure': cookie.secure,
            'httpOnly': cookie.has_nonstandard_attr('HttpOnly'),
        })
    
    if not cookie_list:
        print("❌ No cookies found! Make sure you're logged into MyFitnessPal in your browser.")
        return False
    
    print(f"✓ Found {len(cookie_list)} cookies")
    
    json_path = Path(__file__).parent / 'mfp_cookies.json'
    
    with open(json_path, 'w') as f:
        json.dump(cookie_list, f, indent=2)
    
    print(f"✓ Saved cookies to {json_path}")
    print("\n⚠️  Keep this file secure - it grants access to your account!")
    
    return True


if __name__ == '__main__':
    import sys
    
    print("=" * 60)
    print("MyFitnessPal Cookie Export Utility")
    print("=" * 60)
    print()
    
    # Check for help flag
    if '--help' in sys.argv or '-h' in sys.argv:
        print("Usage: python export_cookies.py [OPTIONS]")
        print()
        print("Options:")
        print("  --chrome       Extract cookies from Chrome")
        print("  --firefox      Extract cookies from Firefox")
        print("  --edge         Extract cookies from Edge")
        print("  --safari       Extract cookies from Safari (requires Full Disk Access)")
        print("  --json         Export to JSON file instead of .env")
        print("  --help, -h     Show this help message")
        print()
        print("Examples:")
        print("  python export_cookies.py --chrome")
        print("  python export_cookies.py --firefox --json")
        print()
        print("Note: Safari on macOS requires 'Full Disk Access' permission.")
        print("      Use Chrome or Firefox for easier setup.")
        sys.exit(0)
    
    # Parse command line arguments
    browser = 'auto'
    use_json = False
    
    for arg in sys.argv[1:]:
        if arg == '--json':
            use_json = True
        elif arg in ['--chrome', '--firefox', '--edge', '--safari']:
            browser = arg.replace('--', '')
        elif arg.startswith('--browser='):
            browser = arg.split('=')[1]
    
    if use_json:
        success = export_cookies_to_json()
    else:
        success = export_cookies_to_env(browser=browser)
    
    if success:
        print("\n✅ Cookie export complete!")
        print("\nNext steps:")
        print("  1. Deploy your server with the .env file")
        print("  2. The server will use cookies from .env instead of browser")
        print("  3. Re-run this script when cookies expire (~30 days)")
    else:
        print("\n❌ Cookie export failed")
        sys.exit(1)
