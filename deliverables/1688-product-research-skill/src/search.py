import json
import csv
import os
import urllib.parse
from playwright.sync_api import sync_playwright


def load_cookies(cookie_file='1688cookie.json'):
    """Load cookies from JSON file."""
    with open(cookie_file, 'r') as f:
        cookies = json.load(f)

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


def build_search_url(keyword, page_num=1):
    """Build 1688 search URL with proper URL encoding."""
    encoded_keyword = urllib.parse.quote(keyword)
    search_url = f"https://s.1688.com/youyuan/index.htm?tab=search&beginPage={page_num}&pageSize=60&keywords={encoded_keyword}"
    return search_url


def extract_search_results(page):
    """Extract product list from search results page."""
    results = []

    try:
        offer_items = page.locator(".offer-item").all()
        
        for item in offer_items[:20]:
            try:
                title_elem = item.locator(".title")
                title = title_elem.inner_text().strip() if title_elem.count() > 0 else ""

                price_elem = item.locator(".price")
                price = price_elem.inner_text().strip() if price_elem.count() > 0 else ""

                link_elem = item.locator("a.title-link")
                url = link_elem.get_attribute("href") if link_elem.count() > 0 else ""

                img_elem = item.locator("img")
                img = img_elem.get_attribute("src") if img_elem.count() > 0 else ""

                if title and url:
                    results.append({
                        "title": title,
                        "price": price,
                        "url": url,
                        "image": img
                    })
            except Exception as e:
                continue
    except Exception as e:
        print(f"提取搜索结果时出错: {e}")

    if not results:
        try:
            all_links = page.locator("a").all()
            for link in all_links[:50]:
                try:
                    href = link.get_attribute("href") or ""
                    text = link.inner_text().strip()
                    
                    if "offerId=" in href and text:
                        img_elem = link.locator("..").locator("img").first
                        img = img_elem.get_attribute("src") if img_elem.count() > 0 else ""
                        
                        results.append({
                            "title": text[:100],
                            "price": "",
                            "url": href,
                            "image": img
                        })
                except:
                    continue
        except:
            pass

    return results


def save_search_results(results, output_file='output/1688_search_results.csv'):
    """Save search results to CSV."""
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    with open(output_file, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["序号", "商品标题", "价格", "图片", "链接"])

        for idx, item in enumerate(results, 1):
            writer.writerow([
                idx,
                item.get('title', ''),
                item.get('price', ''),
                item.get('image', ''),
                item.get('url', '')
            ])

    print(f"已保存到: {output_file}")


def run_search(keyword, cookie_file='1688cookie.json', headless=False, max_results=20):
    """Main search function."""
    print(f"加载了 {len(load_cookies(cookie_file))} 个Cookie")
    print(f"搜索关键词: {keyword}")

    encoded_keyword = urllib.parse.quote(keyword)
    search_url = f"https://s.1688.com/youyuan/index.htm?tab=search&beginPage=1&pageSize=60&keywords={encoded_keyword}"
    print(f"搜索URL: {search_url}")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        context = browser.new_context()
        context.add_cookies(load_cookies(cookie_file))

        page = context.new_page()
        
        print("正在打开搜索页面...")
        page.goto(search_url)
        page.wait_for_timeout(15000)

        print("正在提取商品列表...")
        results = extract_search_results(page)

        print(f"\n找到 {len(results)} 个商品")

        if results:
            print("\n" + "="*80)
            print("搜索结果预览 (前10个):")
            print("="*80)
            for idx, item in enumerate(results[:10], 1):
                print(f"{idx}. {item['title'][:50]}...")
                print(f"   价格: {item['price']}")
                print(f"   链接: {item['url'][:80]}...")
                print()

            save_search_results(results)
        else:
            print("未找到任何商品，请尝试更换关键词或检查登录状态")

        if not headless:
            print("\n按回车键关闭浏览器...")
            input()

        browser.close()

    return results


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='1688商品搜索工具')
    parser.add_argument('--keyword', type=str, default='手机支架', help='搜索关键词')
    parser.add_argument('--cookie', type=str, default='1688cookie.json', help='Cookie文件')
    parser.add_argument('--headless', action='store_true', help='无头模式')
    parser.add_argument('--max', type=int, default=20, help='最大结果数')

    args = parser.parse_args()

    run_search(args.keyword, args.cookie, args.headless, args.max)
