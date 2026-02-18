"""
MyFitnessPal API Client

Wrapper around the python-myfitnesspal library (local copy from GitHub).
Supports both browser cookie authentication and environment-based cookies.
"""

import sys
import os
import json
import glob
import logging
from pathlib import Path
from datetime import date, timedelta
from typing import Optional
from http.cookiejar import Cookie, CookieJar

logger = logging.getLogger(__name__)

# Add myfitnesspal library to path
myfitnesspal_path = Path(__file__).parent / "myfitnesspal"
sys.path.insert(0, str(myfitnesspal_path))

import myfitnesspal


class MyFitnessPalClient:
    """Simplified client wrapping python-myfitnesspal library"""
    
    def __init__(self):
        """
        Initialize client using cookies from browser or environment.
        
        Priority:
        1. MFP_COOKIES environment variable (for deployment)
        2. Browser cookies (for local development)
        """
        cookiejar = self._load_cookies_from_env()

        if not cookiejar:
            cookiejar = self._load_cookies_from_chrome()

        if cookiejar:
            self.client = myfitnesspal.Client(cookiejar=cookiejar)
        else:
            self.client = myfitnesspal.Client()
    
    def _load_cookies_from_chrome(self) -> Optional[CookieJar]:
        """Try loading MFP cookies from all Chrome profiles"""
        import browser_cookie3

        chrome_base = Path.home() / "Library" / "Application Support" / "Google" / "Chrome"
        profiles = [chrome_base / "Default"]
        profiles.extend(sorted(chrome_base.glob("Profile *")))

        for profile_dir in profiles:
            cookie_file = profile_dir / "Cookies"
            if not cookie_file.exists():
                continue
            try:
                jar = browser_cookie3.chrome(
                    domain_name='myfitnesspal.com',
                    cookie_file=str(cookie_file),
                )
                cookies = list(jar)
                if cookies:
                    logger.info(f"Found {len(cookies)} MFP cookies in {profile_dir.name}")
                    return jar
            except Exception as e:
                logger.debug(f"Could not read cookies from {profile_dir.name}: {e}")

        return None

    def _load_cookies_from_env(self) -> Optional[CookieJar]:
        """Load cookies from MFP_COOKIES environment variable if present"""
        cookies_json = os.getenv('MFP_COOKIES')
        
        if not cookies_json:
            return None
        
        try:
            cookie_dict = json.loads(cookies_json)
            jar = CookieJar()
            
            for name, data in cookie_dict.items():
                cookie = Cookie(
                    version=0,
                    name=name,
                    value=data['value'],
                    port=None,
                    port_specified=False,
                    domain=data.get('domain', '.myfitnesspal.com'),
                    domain_specified=True,
                    domain_initial_dot=data.get('domain', '').startswith('.'),
                    path=data.get('path', '/'),
                    path_specified=True,
                    secure=data.get('secure', False),
                    expires=None,
                    discard=True,
                    comment=None,
                    comment_url=None,
                    rest={},
                    rfc2109=False
                )
                jar.set_cookie(cookie)
            
            return jar
            
        except Exception as e:
            logger.warning(f"Failed to load cookies from environment: {e}")
            return None
    
    def get_day(self, target_date: date):
        """
        Get complete day data including meals, exercise, water, and notes.
        
        Returns a Day object with:
        - meals: List of Meal objects with entries
        - totals: Dict of total nutrition (calories, carbs, fat, protein, etc.)
        - goals: Dict of daily goals
        - water: Float (water intake)
        - exercises: List of Exercise objects
        - notes: String (food notes)
        - complete: Boolean (whether day is marked complete)
        """
        return self.client.get_date(target_date)
    
    def get_date_range(self, start_date: date, end_date: date):
        """
        Get data for multiple days.
        
        Yields Day objects for each date in the range.
        """
        current = start_date
        while current <= end_date:
            try:
                yield self.get_day(current)
            except Exception as e:
                logger.warning(f"Failed to fetch data for {current}: {e}")
            current = current + timedelta(days=1)
