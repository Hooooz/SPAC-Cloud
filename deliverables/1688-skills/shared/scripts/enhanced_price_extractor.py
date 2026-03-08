"""
Enhanced 1688 price extractor with detailed selectors
"""
import asyncio
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime

from playwright.async_api import async_playwright, Browser, Page, BrowserContext

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class DetailedPriceInfo:
    """Detailed price information"""
    url: str
    title: str
    # Price information
    price_range: Optional[str] = None  # e.g., "¥10.5-15.0"
    price_min: Optional[float] = None
    price_max: Optional[float] = None
    # SKU prices
    sku_prices: List[Dict[str, Any]] = None  # Different SKU prices
    # MOQ prices
    moq_prices: List[Dict[str, Any]] = None  # Prices by quantity
    # Member prices
    member_price: Optional[str] = None
    # Promotion prices
    promotion_price: Optional[str] = None
    # Product details
    sales: Optional[str] = None
    shop_name: Optional[str] = None
    shop_url: Optional[str] = None
    location: Optional[str] = None
    # Images
    images: List[str] = None
    # Metadata
    collected_at: str = None
    
    def __post_init__(self):
        if self.sku_prices is None:
            self.sku_prices = []
        if self.moq_prices is None:
            self.moq_prices = []
        if self.images is None:
            self.images = []
        if self.collected_at is None:
            self.collected_at = datetime.now().isoformat(timespec="seconds")
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class Enhanced1688Extractor:
    """Enhanced browser automation for 1688 with detailed price extraction"""
    
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
    
    async def extract_price_info(self, url: str, wait_time: int = 5000) -> DetailedPriceInfo:
        """Extract detailed price information from product page"""
        logger.info(f"Visiting product: {url}")
        
        try:
            await self.page.goto(url, timeout=30000, wait_until='domcontentloaded')
            await self.page.wait_for_timeout(wait_time)
            
            # Extract title
            title = await self.page.title()
            
            # Initialize price info
            price_info = DetailedPriceInfo(url=url, title=title.replace('\n', '').strip())
            
            # Extract main price range
            await self._extract_main_price(price_info)
            
            # Extract SKU prices
            await self._extract_sku_prices(price_info)
            
            # Extract MOQ prices
            await self._extract_moq_prices(price_info)
            
            # Extract member price
            await self._extract_member_price(price_info)
            
            # Extract promotion price
            await self._extract_promotion_price(price_info)
            
            # Extract sales
            await self._extract_sales(price_info)
            
            # Extract shop info
            await self._extract_shop_info(price_info)
            
            # Extract images
            await self._extract_images(price_info)
            
            # Extract location
            await self._extract_location(price_info)
            
            return price_info
            
        except Exception as e:
            logger.error(f"Error extracting price info from {url}: {e}")
            return DetailedPriceInfo(url=url, title="Error")
    
    async def _extract_main_price(self, price_info: DetailedPriceInfo):
        """Extract main price range"""
        try:
            # Try multiple selectors for price
            price_selectors = [
                '.price-text',
                '.price-value',
                '.price-original',
                '[class*="price"]',
                'span[class*="Price"]'
            ]
            
            for selector in price_selectors:
                elements = await self.page.query_selector_all(selector)
                if elements:
                    prices = []
                    for elem in elements:
                        text = await elem.inner_text()
                        if '¥' in text or '￥' in text:
                            prices.append(text.strip())
                    
                    if prices:
                        price_info.price_range = prices[0]
                        # Extract min and max prices
                        import re
                        price_numbers = re.findall(r'[¥￥]?\s*(\d+\.?\d*)', ' '.join(prices))
                        if price_numbers:
                            price_floats = [float(p) for p in price_numbers if float(p) > 0]
                            if price_floats:
                                price_info.price_min = min(price_floats)
                                price_info.price_max = max(price_floats)
                        break
        except Exception as e:
            logger.debug(f"Error extracting main price: {e}")
    
    async def _extract_sku_prices(self, price_info: DetailedPriceInfo):
        """Extract SKU-specific prices"""
        try:
            # Look for SKU table or list
            sku_selectors = [
                '.sku-table',
                '.sku-list',
                '[class*="sku"]',
                '.spec-item'
            ]
            
            for selector in sku_selectors:
                try:
                    elements = await self.page.query_selector_all(selector)
                    if elements:
                        for elem in elements:
                            text = await elem.inner_text()
                            if '¥' in text or '￥' in text:
                                # Parse SKU info
                                lines = text.strip().split('\n')
                                for line in lines:
                                    if '¥' in line or '￥' in line:
                                        price_info.sku_prices.append({
                                            'text': line.strip()
                                        })
                        break
                except:
                    continue
        except Exception as e:
            logger.debug(f"Error extracting SKU prices: {e}")
    
    async def _extract_moq_prices(self, price_info: DetailedPriceInfo):
        """Extract MOQ (Minimum Order Quantity) prices"""
        try:
            # Look for quantity-based pricing
            moq_selectors = [
                '.price-range',
                '.quantity-price',
                '[class*="moq"]',
                '.ladder-price'
            ]
            
            for selector in moq_selectors:
                try:
                    elements = await self.page.query_selector_all(selector)
                    if elements:
                        for elem in elements:
                            text = await elem.inner_text()
                            if text.strip():
                                price_info.moq_prices.append({
                                    'text': text.strip()
                                })
                        break
                except:
                    continue
        except Exception as e:
            logger.debug(f"Error extracting MOQ prices: {e}")
    
    async def _extract_member_price(self, price_info: DetailedPriceInfo):
        """Extract member price"""
        try:
            member_selectors = [
                '[class*="member"]',
                '[class*="vip"]',
                '[class*="plus"]'
            ]
            
            for selector in member_selectors:
                try:
                    elements = await self.page.query_selector_all(selector)
                    for elem in elements:
                        text = await elem.inner_text()
                        if '¥' in text or '￥' in text or '会员' in text:
                            price_info.member_price = text.strip()
                            return
                except:
                    continue
        except Exception as e:
            logger.debug(f"Error extracting member price: {e}")
    
    async def _extract_promotion_price(self, price_info: DetailedPriceInfo):
        """Extract promotion price"""
        try:
            promo_selectors = [
                '[class*="promo"]',
                '[class*="discount"]',
                '[class*="coupon"]'
            ]
            
            for selector in promo_selectors:
                try:
                    elements = await self.page.query_selector_all(selector)
                    for elem in elements:
                        text = await elem.inner_text()
                        if '¥' in text or '￥' in text or '券' in text or '折' in text:
                            price_info.promotion_price = text.strip()
                            return
                except:
                    continue
        except Exception as e:
            logger.debug(f"Error extracting promotion price: {e}")
    
    async def _extract_sales(self, price_info: DetailedPriceInfo):
        """Extract sales information"""
        try:
            sales_selectors = [
                '[class*="sales"]',
                '[class*="sold"]',
                '[class*="deal"]'
            ]
            
            for selector in sales_selectors:
                try:
                    elements = await self.page.query_selector_all(selector)
                    for elem in elements:
                        text = await elem.inner_text()
                        if '售' in text or 'sold' in text.lower():
                            price_info.sales = text.strip()
                            return
                except:
                    continue
            
            # Fallback: search in entire page
            body_text = await self.page.inner_text('body')
            import re
            sales_match = re.search(r'已售[0-9万+]+', body_text)
            if sales_match:
                price_info.sales = sales_match.group(0)
        except Exception as e:
            logger.debug(f"Error extracting sales: {e}")
    
    async def _extract_shop_info(self, price_info: DetailedPriceInfo):
        """Extract shop information"""
        try:
            shop_selectors = [
                'a[href*="company"]',
                '.shop-name',
                '[class*="shop"]'
            ]
            
            for selector in shop_selectors:
                try:
                    elements = await self.page.query_selector_all(selector)
                    for elem in elements:
                        text = await elem.inner_text()
                        href = await elem.get_attribute('href')
                        if text.strip() and len(text.strip()) > 2:
                            price_info.shop_name = text.strip()
                            if href:
                                price_info.shop_url = href
                            return
                except:
                    continue
        except Exception as e:
            logger.debug(f"Error extracting shop info: {e}")
    
    async def _extract_images(self, price_info: DetailedPriceInfo):
        """Extract product images"""
        try:
            img_elements = await self.page.query_selector_all('img[src*="cbu01.alicdn.com"]')
            for img in img_elements[:10]:  # Limit to 10 images
                src = await img.get_attribute('src')
                if src:
                    price_info.images.append(src)
        except Exception as e:
            logger.debug(f"Error extracting images: {e}")
    
    async def _extract_location(self, price_info: DetailedPriceInfo):
        """Extract shipping location"""
        try:
            location_selectors = [
                '[class*="location"]',
                '[class*="address"]',
                '[class*="ship"]'
            ]
            
            for selector in location_selectors:
                try:
                    elements = await self.page.query_selector_all(selector)
                    for elem in elements:
                        text = await elem.inner_text()
                        if text.strip() and len(text.strip()) < 50:
                            price_info.location = text.strip()
                            return
                except:
                    continue
        except Exception as e:
            logger.debug(f"Error extracting location: {e}")


async def extract_detailed_price(url: str, cookie_file: str = "1688cookie.json") -> Dict[str, Any]:
    """Extract detailed price for a single product URL"""
    async with Enhanced1688Extractor(cookie_file) as extractor:
        price_info = await extractor.extract_price_info(url)
        return price_info.to_dict()


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python enhanced_price_extractor.py <url>")
        sys.exit(1)
    
    url = sys.argv[1]
    result = asyncio.run(extract_detailed_price(url))
    print(json.dumps(result, indent=2, ensure_ascii=False))
