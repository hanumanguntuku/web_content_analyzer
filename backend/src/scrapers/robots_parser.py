import aiohttp
from urllib.parse import urlparse, urljoin
import re

class RobotsParser:
    """Minimal async robots.txt parser for respectful crawling"""
    def __init__(self, user_agent: str = "*"):
        self.user_agent = user_agent
        self.rules = {}
        self.crawl_delay = None

    async def fetch_robots(self, base_url: str):
        parsed = urlparse(base_url)
        robots_url = urljoin(f"{parsed.scheme}://{parsed.netloc}", "/robots.txt")
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(robots_url, timeout=5) as resp:
                    if resp.status == 200:
                        text = await resp.text()
                        self.parse(text)
        except Exception:
            pass  # Fail open if robots.txt is not available

    def parse(self, robots_txt: str):
        current_agent = None
        for line in robots_txt.splitlines():
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if line.lower().startswith('user-agent:'):
                current_agent = line.split(':', 1)[1].strip()
            elif line.lower().startswith('disallow:') and current_agent:
                path = line.split(':', 1)[1].strip()
                self.rules.setdefault(current_agent, []).append(('disallow', path))
            elif line.lower().startswith('allow:') and current_agent:
                path = line.split(':', 1)[1].strip()
                self.rules.setdefault(current_agent, []).append(('allow', path))
            elif line.lower().startswith('crawl-delay:') and current_agent:
                try:
                    self.crawl_delay = float(line.split(':', 1)[1].strip())
                except Exception:
                    pass

    def is_allowed(self, url: str) -> bool:
        parsed = urlparse(url)
        path = parsed.path or '/'
        # Check rules for our user-agent, then fallback to *
        for agent in (self.user_agent, '*'):
            rules = self.rules.get(agent, [])
            allowed = True
            for rule, rule_path in rules:
                if rule == 'disallow' and path.startswith(rule_path) and rule_path != '':
                    allowed = False
                if rule == 'allow' and path.startswith(rule_path):
                    allowed = True
            if not allowed:
                return False
        return True

    def get_crawl_delay(self) -> float:
        return self.crawl_delay or 0.0
