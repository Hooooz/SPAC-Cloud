"""
1688 Browser Automation Helper
Shared utilities for 1688 price checking and product search
"""

import asyncio
import json
import logging
import re
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime

from playwright.async_api import async_playwright, Browser, Page, BrowserContext

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ProductInfo:
    """Product information extracted from 1688"""
    url: str
    title: str
    price: Optional[str] = None
    price_min: Optional[float] = None
    price_max: Optional[float] = None
    moq: Optional[str] = None
    shop_name: Optional[str] = None
    shop_url: Optional[str] = None
    sales: Optional[str] = None
    images: List[str] = None
    models: List[Dict[str, str]] = None
    collected_at: str = None
    
    def __post_init__(self):
        if self.images is None:
            self.images = []
        if self.models is None:
            self.models = []
        if self.collected_at is None:
            self.collected_at = datetime.now().isoformat(timespec="seconds")
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class Browser1688:
    """Browser automation for 1688 with cookie management"""
    
    def __init__(self, cookie_file: str = "1688cookie.json"):
        self.cookie_file = Path(cookie_file)
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        
    async def __aenter__(self):
        await self.start()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
    
    async def start(self, headless: bool = False):
        """Start browser with cookies"""
        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch(headless=headless)
        
        self.context = await self.browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080}
        )
        
        await self.context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            })
        """)
        
        if self.cookie_file.exists():
            cookies = json.loads(self.cookie_file.read_text())
            # Fix cookie format for Playwright
            for cookie in cookies:
                if 'sameSite' in cookie:
                    if cookie['sameSite'] == 'no_restriction':
                        cookie['sameSite'] = 'None'
                    elif cookie['sameSite'] == 'unspecified':
                        cookie['sameSite'] = 'Lax'
                    elif cookie['sameSite'] not in ['Strict', 'Lax', 'None']:
                        cookie['sameSite'] = 'Lax'
                else:
                    cookie['sameSite'] = 'Lax'
            await self.context.add_cookies(cookies)
            logger.info(f"Loaded {len(cookies)} cookies from {self.cookie_file}")
        
        self.page = await self.context.new_page()
    
    async def close(self):
        """Close browser"""
        if self.browser:
            await self.browser.close()
    
    async def save_cookies(self):
        """Save current cookies to file"""
        if self.context:
            cookies = await self.context.cookies()
            self.cookie_file.write_text(json.dumps(cookies, indent=2))
            logger.info(f"Saved {len(cookies)} cookies to {self.cookie_file}")
    
    async def visit_product(self, url: str, wait_time: int = 3000) -> ProductInfo:
        """Visit a product page and extract information"""
        logger.info(f"Visiting product: {url}")
        
        try:
            await self.page.goto(url, timeout=30000, wait_until='domcontentloaded')
            await self.page.wait_for_timeout(wait_time)
            
            title = await self.page.title()
            
            body_text = await self.page.inner_text('body')
            
            prices = re.findall(r'¥\s*([0-9]+(?:\.[0-9]{1,2})?)', body_text)
            price_min = float(min(prices)) if prices else None
            price_max = float(max(prices)) if prices else None
            price_text = f"¥{price_min}-{price_max}" if price_min and price_max and price_min != price_max else f"¥{price_min}" if price_min else None
            
            shop_name = None
            try:
                shop_elem = await self.page.query_selector('a[href*="company"]')
                if shop_elem:
                    shop_name = await shop_elem.inner_text()
            except:
                pass
            
            images = []
            try:
                img_elements = await self.page.query_selector_all('img[src*="cbu01.alicdn.com"]')
                for img in img_elements[:5]:
                    src = await img.get_attribute('src')
                    if src:
                        images.append(src)
            except:
                pass
            
            sales = None
            try:
                sales_match = re.search(r'已售([0-9万+]+)', body_text)
                if sales_match:
                    sales = sales_match.group(0)
            except:
                pass
            
            return ProductInfo(
                url=url,
                title=title.replace('\n', '').strip()[:100],
                price=price_text,
                price_min=price_min,
                price_max=price_max,
                shop_name=shop_name,
                images=images,
                sales=sales
            )
            
        except Exception as e:
            logger.error(f"Error visiting {url}: {e}")
            return ProductInfo(url=url, title="Error", price=None)
    
    async def search_products(self, keyword: str, max_results: int = 20) -> List[ProductInfo]:
        """Search for products on 1688"""
        logger.info(f"Searching for: {keyword}")
        
        search_url = f"https://s.1688.com/selloffer/offer_search.htm?keywords={keyword}"
        
        try:
            await self.page.goto(search_url, timeout=30000, wait_until='domcontentloaded')
            await self.page.wait_for_timeout(5000)
            
            await self.page.mouse.wheel(0, 1000)
            await self.page.wait_for_timeout(2000)
            
            links = await self.page.query_selector_all("a[href*='offer']")
            
            products = []
            seen_urls = set()
            
            for link in links:
                if len(products) >= max_results:
                    break
                
                try:
                    href = await link.get_attribute('href')
                    if not href or 'offer' not in href:
                        continue
                    
                    if href.startswith('//'):
                        href = 'https:' + href
                    
                    if href in seen_urls:
                        continue
                    seen_urls.add(href)
                    
                    title = await link.inner_text()
                    title = title.strip()
                    
                    if len(title) < 10:
                        continue
                    
                    if any(kw in title for kw in ['找货源', '工业品', '找相似', '旺旺在线']):
                        continue
                    
                    products.append(ProductInfo(url=href, title=title[:100]))
                    
                except Exception as e:
                    logger.debug(f"Error extracting link: {e}")
                    continue
            
            logger.info(f"Found {len(products)} products")
            return products
            
        except Exception as e:
            logger.error(f"Error searching for {keyword}: {e}")
            return []


async def check_price(url: str, cookie_file: str = "1688cookie.json") -> Dict[str, Any]:
    """Check price for a single product URL"""
    async with Browser1688(cookie_file) as browser:
        product = await browser.visit_product(url)
        return product.to_dict()


async def search(keyword: str, cookie_file: str = "1688cookie.json", max_results: int = 20) -> List[Dict[str, Any]]:
    """Search for products by keyword"""
    async with Browser1688(cookie_file) as browser:
        products = await browser.search_products(keyword, max_results)
        return [p.to_dict() for p in products]


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python browser_1688.py check <url>")
        print("  python browser_1688.py search <keyword>")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "check" and len(sys.argv) >= 3:
        url = sys.argv[2]
        result = asyncio.run(check_price(url))
        print(json.dumps(result, indent=2, ensure_ascii=False))
    
    elif command == "search" and len(sys.argv) >= 3:
        keyword = sys.argv[2]
        results = asyncio.run(search(keyword))
        print(json.dumps(results, indent=2, ensure_ascii=False))
    
    else:
        print("Invalid command")
        sys.exit(1)
