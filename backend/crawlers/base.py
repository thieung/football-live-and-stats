"""
Base crawler class with common functionality
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Optional
import httpx
from playwright.async_api import async_playwright
import structlog
import random
from datetime import datetime

logger = structlog.get_logger()


class BaseCrawler(ABC):
    """
    Base crawler class with common utilities
    """

    def __init__(self, use_proxy: bool = False):
        self.use_proxy = use_proxy
        self.session: Optional[httpx.AsyncClient] = None

        # User agents for rotation
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
        ]

    def get_random_user_agent(self) -> str:
        """Get random user agent"""
        return random.choice(self.user_agents)

    async def init_session(self):
        """Initialize HTTP session"""
        if not self.session:
            headers = {
                'User-Agent': self.get_random_user_agent(),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate, br',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            }

            self.session = httpx.AsyncClient(
                headers=headers,
                timeout=30.0,
                follow_redirects=True
            )

    async def close_session(self):
        """Close HTTP session"""
        if self.session:
            await self.session.aclose()
            self.session = None

    async def fetch_html(self, url: str, use_playwright: bool = False) -> Optional[str]:
        """
        Fetch HTML content from URL

        Args:
            url: URL to fetch
            use_playwright: Use Playwright for JavaScript-rendered content

        Returns:
            HTML content as string
        """
        try:
            if use_playwright:
                return await self._fetch_with_playwright(url)
            else:
                return await self._fetch_with_httpx(url)

        except Exception as e:
            logger.error("fetch_html_failed", url=url, error=str(e))
            return None

    async def _fetch_with_httpx(self, url: str) -> Optional[str]:
        """Fetch with httpx (fast, no JS rendering)"""
        await self.init_session()

        try:
            response = await self.session.get(url)
            response.raise_for_status()
            return response.text

        except httpx.HTTPError as e:
            logger.error("httpx_fetch_failed", url=url, error=str(e))
            return None

    async def _fetch_with_playwright(self, url: str) -> Optional[str]:
        """Fetch with Playwright (slower, JS rendering)"""
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)

                context = await browser.new_context(
                    user_agent=self.get_random_user_agent(),
                    viewport={'width': 1920, 'height': 1080}
                )

                page = await context.new_page()

                # Navigate and wait for page load
                await page.goto(url, wait_until='domcontentloaded')
                await page.wait_for_timeout(2000)  # Wait 2 seconds for dynamic content

                html = await page.content()

                await browser.close()

                return html

        except Exception as e:
            logger.error("playwright_fetch_failed", url=url, error=str(e))
            return None

    @abstractmethod
    async def crawl_match(self, match_id: str) -> Optional[Dict]:
        """
        Crawl single match data

        Args:
            match_id: External match ID

        Returns:
            Match data dict
        """
        pass

    @abstractmethod
    async def crawl_fixtures(self, days_ahead: int = 7) -> List[Dict]:
        """
        Crawl upcoming fixtures

        Args:
            days_ahead: Number of days to look ahead

        Returns:
            List of fixture dicts
        """
        pass

    @abstractmethod
    async def crawl_league_table(self, league_id: str) -> Optional[Dict]:
        """
        Crawl league standings

        Args:
            league_id: League identifier

        Returns:
            League table dict
        """
        pass

    def parse_score(self, score_text: str) -> Dict[str, int]:
        """
        Parse score string like "2 - 1" to dict

        Args:
            score_text: Score string

        Returns:
            Dict with 'home' and 'away' scores
        """
        try:
            parts = score_text.strip().split('-')
            return {
                'home': int(parts[0].strip()),
                'away': int(parts[1].strip())
            }
        except:
            return {'home': 0, 'away': 0}

    def parse_minute(self, minute_text: str) -> Optional[int]:
        """
        Parse minute string like "67'" to int

        Args:
            minute_text: Minute string

        Returns:
            Minute as integer
        """
        try:
            return int(minute_text.replace("'", "").strip())
        except:
            return None
