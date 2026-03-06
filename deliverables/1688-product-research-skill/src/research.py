import json
import re
import csv
import os
from playwright.sync_api import sync_playwright


def load_cookies(cookie_file='1688cookie.json'):
    """Load cookies from JSON file."""
    with open(cookie_file, 'r') as f:
        cookies = json.load(f)

    # Convert to Playwright format
    playwright_cookies = []
    for cookie in cookies:
        playwright_cookies.append({
            "name": cookie["name"],
            "value": cookie["value"],
            "domain": cookie["domain"],
            "path": cookie["path"],
            "secure": cookie.get("secure", True),
            "httpOnly": cookie.get("httpOnly", False),
        })
    return playwright_cookies


def extract_product_info(page_text, product_url):
    """Extract product information from page text."""
    product_info = {}

    # Extract colors
    color_pattern = r'([\u767d\u8272\u84dd\u8272\u9ed1\u7c89\u7ea2\u9ec4\u7eff\u7d2b]+翅膀[^\n\u300a]*)'
    color_matches = re.findall(color_pattern, page_text)
    colors = list(set([c.strip() for c in color_matches[:5]]))
    product_info['colors'] = colors if colors else ['N/A']

    # Extract sales
    sale_match = re.search(r'\u5df2\u552e(\d+\.?\d*\u4e07?\+?)', page_text)
    product_info['sales'] = sale_match.group(1) if sale_match else 'N/A'

    # Extract tiered prices
    tiered_prices = []
    sale_pos = page_text.find('\u5df2\u552e')
    if sale_pos > 0:
        price_section = page_text[:sale_pos]
        prices = re.findall(r'\uffe5\s*(\d+\.?\d*)', price_section)
        if prices:
            if len(prices) > 0:
                tiered_prices.append({"min_qty": 1, "max_qty": 49, "price": prices[0]})
            if len(prices) > 1:
                tiered_prices.append({"min_qty": 50, "max_qty": 199, "price": prices[1]})
            if len(prices) > 2:
                tiered_prices.append({"min_qty": 200, "max_qty": "", "price": prices[2]})

    product_info['tiered_prices'] = tiered_prices if tiered_prices else [{"min_qty": 1, "max_qty": "", "price": "N/A"}]
    product_info['url'] = product_url

    return product_info


def get_product_image(page):
    """Extract product image URL."""
    img_url = ""
    try:
        imgs = page.locator("img").all()
        for img in imgs[:10]:
            src = img.get_attribute("src") or ""
            if "alicdn.com" in src and "ibank" in src:
                img_url = src
                break
    except:
        pass
    return img_url


def save_to_csv(product_name, product_info, output_file='output/1688_product_detail.csv'):
    """Save product information to CSV file."""
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    with open(output_file, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f)

        # Write header
        header = ["\u578b\u53f7", "\u989c\u8272", "\u4e00\u5e74\u5185\u9500\u91cf", "\u56fe\u7247", "\u8d77\u8bae\u91cf", "1688\u4ef7\u683c", "PLUS\u4f1a\u545895\u6298", "\u94fe\u63a5"]
        writer.writerow(header)

        colors = product_info.get('colors', [])
        tiered_prices = product_info.get('tiered_prices', [])
        sales = product_info.get('sales', 'N/A')
        img_url = product_info.get('image', '')

        # Write data rows
        for tier in tiered_prices:
            for color in colors:
                if tier.get("max_qty"):
                    qty_range = f"{tier['min_qty']}-{tier['max_qty']}\u4e2a"
                else:
                    qty_range = f"\u2265{tier['min_qty']}\u4e2a"

                row = [
                    product_name,
                    color,
                    f"\u5df2\u552e{sales}\u4e2a",
                    img_url,
                    qty_range,
                    f"\uffe5{tier['price']}",
                    "",
                    product_info.get('url', '')
                ]
                writer.writerow(row)

    print(f"\u5df2\u4fdd\u5b58\u5230: {output_file}")


def run_research(product_url, product_name, cookie_file='1688cookie.json', headless=False):
    """Main research function."""
    print(f"\u52a0\u8f7d\u4e86 {len(load_cookies(cookie_file))} \u4e2aCookie")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        context = browser.new_context()
        context.add_cookies(load_cookies(cookie_file))

        print(f"\u8bbf\u95ee\u5546\u54c1\u8be6\u60c5\u9875...")

        page = context.new_page()
        page.goto(product_url)
        page.wait_for_timeout(15000)

        page_text = page.inner_text("body")

        # Extract product information
        product_info = extract_product_info(page_text, product_url)
        product_info['image'] = get_product_image(page)

        # Print results
        print("\n" + "="*80)
        print("\u5546\u54c1\u4fe1\u606f")
        print("="*80)
        print(f"\u578b\u53f7: {product_name}")
        print(f"\u989c\u8272: {product_info['colors']}")
        print(f"\u9500\u91cf: \u5df2\u552e{product_info['sales']}\u4e2a")
        print(f"\u9644\u8fb9\u4ef7\u683c: {product_info['tiered_prices']}")
        print("="*80)

        # Save to CSV
        save_to_csv(product_name, product_info)

        if not headless:
            print("\n\u6309\u56de\u8f66\u5173\u95ed\u6d4f\u89c8\u5668...")
            input()

        browser.close()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='1688商品调研工具')
    parser.add_argument('--url', type=str, default='http://detail.m.1688.com/page/index.html?offerId=1018923549617', help='1688商品URL')
    parser.add_argument('--name', type=str, default='\u661f\u661f\u5316\u5986\u5305\u5973\u5916\u51fa\u4fbf\u6469\u7acb\u5f97\u76f8\u673a\u5305', help='\u5546\u54c1\u540d\u79f0')
    parser.add_argument('--cookie', type=str, default='1688cookie.json', help='Cookie\u6587\u4ef6')
    parser.add_argument('--headless', action='store_true', help='\u65e0\u5934\u6a21\u5f0f')

    args = parser.parse_args()

    run_research(args.url, args.name, args.cookie, args.headless)