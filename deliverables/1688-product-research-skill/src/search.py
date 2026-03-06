import json
import csv
import os
import urllib.parse
import re
import random
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


def clean_title(title):
    """Clean product title, remove extra info."""
    lines = title.split('\n')
    clean_lines = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if any(x in line for x in ['分享', '新人价', '退货包', '先采后付', '回头率', '件', '¥', '热卖', '回购', '热度', '推荐', '综合服务', '采购咨询', '品质体验']):
            continue
        if re.match(r'^[\d\.¥\+]+$', line):
            continue
        clean_lines.append(line)
    
    if clean_lines:
        return clean_lines[0][:80]
    return title[:80]


def extract_search_results(page):
    """Extract product list from search results page."""
    results = []

    try:
        all_links = page.locator("a").all()
        for link in all_links[:300]:
            try:
                href = link.get_attribute("href") or ""
                text = link.inner_text().strip()

                if "offerId=" in href and len(text) > 5:
                    clean_text = clean_title(text)
                    if clean_text:
                        results.append({
                            "title": clean_text,
                            "price": "",
                            "url": href,
                            "image": ""
                        })
            except:
                continue

        seen = {}
        unique_results = []
        for r in results:
            offer_id = re.search(r'offerId=(\d+)', r['url'])
            if offer_id and offer_id.group(1) not in seen:
                seen[offer_id.group(1)] = True
                unique_results.append(r)
        results = unique_results
    except Exception as e:
        print(f"提取失败: {e}")

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

    # 关键修复：1688需要使用GBK编码，而不是UTF-8
    encoded_keyword = urllib.parse.quote(keyword.encode('gbk'))
    spm_value = f"a26{random.randint(10000000, 99999999)}.searchbox.0"
    search_url = f"https://s.1688.com/selloffer/offer_search.htm?keywords={encoded_keyword}&spm={spm_value}"

    print(f"搜索URL: {search_url}")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        context.add_cookies(load_cookies(cookie_file))

        page = context.new_page()

        print("正在打开搜索页面...")
        page.goto(search_url)
        page.wait_for_timeout(20000)

        print(f"页面标题: {page.title()}")

        print("正在提取商品列表...")
        results = extract_search_results(page)

        print(f"\n找到 {len(results)} 个商品")

        if results:
            print("\n" + "="*80)
            print("搜索结果预览 (前10个):")
            print("="*80)
            for idx, item in enumerate(results[:10], 1):
                print(f"{idx}. {item['title']}")
                print(f"   链接: {item['url'][:80]}...")
                print()

            save_search_results(results[:max_results])
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
