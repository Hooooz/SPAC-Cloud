#!/usr/bin/env python3
"""
1688 upstream supplier discovery for new product scouting.

Searches 1688 result pages by keyword and extracts:
- Product URL
- Product title
- Rough price hint
- MOQ hint
- Supplier/shop hint
- Upstream/new-product signals
"""

from __future__ import annotations

import argparse
import csv
import json
import random
import re
import urllib.parse
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from playwright.sync_api import BrowserContext, Page, sync_playwright


CAPTCHA_MARKERS = [
    "captcha interception",
    "slide to verify",
    "unusual traffic",
    "访问过于频繁",
    "滑动验证",
]

SUPPLIER_SIGNAL_KEYWORDS = [
    "源头工厂",
    "生产厂家",
    "工厂店",
    "实力商家",
    "深度验厂",
    "加工厂",
    "工贸一体",
    "诚信通",
]

NEW_SIGNAL_KEYWORDS = [
    "新品",
    "新款",
    "上新",
    "新品首发",
]


@dataclass
class DiscoveryItem:
    keyword: str
    offer_id: str
    title: str
    product_url: str
    price_hint: str
    price_min: Optional[float]
    price_max: Optional[float]
    moq_hint: str
    supplier_name: str
    supplier_url: str
    supplier_signals: List[str]
    is_new_signal: bool
    raw_snippet: str
    collected_at: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def load_cookies(cookie_file: Path) -> List[Dict[str, Any]]:
    cookies = json.loads(cookie_file.read_text(encoding="utf-8"))
    fixed: List[Dict[str, Any]] = []
    for cookie in cookies:
        item = dict(cookie)
        same_site = item.get("sameSite")
        if same_site == "no_restriction":
            item["sameSite"] = "None"
        elif same_site == "unspecified" or same_site not in {None, "Strict", "Lax", "None"}:
            item["sameSite"] = "Lax"
        fixed.append(item)
    return fixed


def build_search_url(keyword: str, page_no: int) -> str:
    encoded = urllib.parse.quote(keyword.encode("gbk", errors="ignore"))
    spm = f"a26{random.randint(10000000, 99999999)}.searchbox.0"
    url = f"https://s.1688.com/selloffer/offer_search.htm?keywords={encoded}&spm={spm}"
    if page_no > 1:
        url += f"&beginPage={page_no}"
    return url


def normalize_url(raw_url: str, current_origin: str) -> str:
    url = (raw_url or "").strip()
    if not url:
        return ""
    if url.startswith("//"):
        return f"https:{url}"
    if url.startswith("/"):
        return f"{current_origin}{url}"
    return url


def extract_offer_id(url: str) -> Optional[str]:
    match = re.search(r"offerId=(\d{8,})", url)
    if match:
        return match.group(1)
    match = re.search(r"/offer/(\d{8,})\.html", url)
    if match:
        return match.group(1)
    return None


def parse_price_hint(text: str) -> tuple[str, Optional[float], Optional[float]]:
    compact = " ".join((text or "").split())
    range_match = re.search(
        r"[¥￥]?\s*(\d+(?:\.\d+)?)\s*[-~至到]\s*[¥￥]?\s*(\d+(?:\.\d+)?)",
        compact,
    )
    if range_match:
        a = float(range_match.group(1))
        b = float(range_match.group(2))
        low = min(a, b)
        high = max(a, b)
        return (f"¥{low:.2f}-¥{high:.2f}", low, high)

    single_match = re.search(r"[¥￥]\s*(\d+(?:\.\d+)?)", compact)
    if single_match:
        value = float(single_match.group(1))
        return (f"¥{value:.2f}", value, value)

    yuan_match = re.search(r"(\d+(?:\.\d+)?)\s*元", compact)
    if yuan_match:
        value = float(yuan_match.group(1))
        return (f"¥{value:.2f}", value, value)

    return ("", None, None)


def parse_moq_hint(text: str) -> str:
    compact = " ".join((text or "").split())
    patterns = [
        r"\d+\s*[-~]\s*\d+\s*(?:个|件|套|台|只|条|包|本|双|对)?起批",
        r"\d+\s*[-~]\s*\d+\s*(?:个|件|套|台|只|条|包|本|双|对)",
        r"≥\s*\d+\s*(?:个|件|套|台|只|条|包|本|双|对)?",
        r"\d+\s*(?:个|件|套|台|只|条|包|本|双|对)?起批",
    ]
    for pattern in patterns:
        match = re.search(pattern, compact)
        if match:
            return match.group(0).strip()
    return ""


def find_signals(text: str, keywords: List[str]) -> List[str]:
    return [kw for kw in keywords if kw in (text or "")]


def is_captcha_page(page: Page) -> bool:
    title = (page.title() or "").lower()
    body = (page.inner_text("body") or "").lower()
    return any(marker in title or marker in body for marker in CAPTCHA_MARKERS)


def extract_raw_candidates(page: Page) -> List[Dict[str, str]]:
    return page.evaluate(
        """() => {
          const normalize = (v) => (v || '').replace(/\\s+/g, ' ').trim();
          const anchors = Array.from(document.querySelectorAll('a[href]')).filter((a) => {
            const href = a.getAttribute('href') || '';
            return /offerId=\\d+|detail\\.1688\\.com\\/offer\\/\\d+\\.html/.test(href);
          });

          const items = [];
          for (const a of anchors) {
            const href = a.getAttribute('href') || '';
            let card = a;
            for (let i = 0; i < 7; i++) {
              if (!card.parentElement) break;
              card = card.parentElement;
              const links = card.querySelectorAll('a[href]').length;
              if (links >= 3 && (card.innerText || '').length > 30) break;
            }

            const rawText = normalize(card && card.innerText ? card.innerText : a.innerText);
            const title = normalize(a.innerText);
            let shopName = '';
            let shopUrl = '';

            if (card) {
              const shopAnchor = Array.from(card.querySelectorAll('a[href]')).find((node) => {
                const t = normalize(node.innerText);
                const h = node.getAttribute('href') || '';
                return t.length >= 2 && /company|shop|wangpu|store|factory/.test(h);
              });
              if (shopAnchor) {
                shopName = normalize(shopAnchor.innerText);
                shopUrl = shopAnchor.getAttribute('href') || '';
              }
            }

            items.push({
              href,
              title,
              rawText,
              shopName,
              shopUrl,
            });
          }
          return items;
        }"""
    )


def dedupe_and_transform(
    keyword: str,
    page: Page,
    raw_candidates: List[Dict[str, str]],
    seen_offer_ids: set[str],
) -> List[DiscoveryItem]:
    output: List[DiscoveryItem] = []
    now = datetime.now().isoformat(timespec="seconds")

    for candidate in raw_candidates:
        href = normalize_url(candidate.get("href", ""), page.url.split("/", 3)[:3][0] + "//" + page.url.split("/", 3)[2])
        offer_id = extract_offer_id(href)
        if not offer_id or offer_id in seen_offer_ids:
            continue

        seen_offer_ids.add(offer_id)
        product_url = f"https://detail.1688.com/offer/{offer_id}.html"

        title = candidate.get("title", "").strip()
        snippet = candidate.get("rawText", "").strip()
        if not title:
            title = snippet[:80]
        if len(title) < 4:
            continue

        price_hint, price_min, price_max = parse_price_hint(snippet)
        moq_hint = parse_moq_hint(snippet)
        signals = find_signals(snippet, SUPPLIER_SIGNAL_KEYWORDS)
        is_new = bool(find_signals(snippet, NEW_SIGNAL_KEYWORDS))

        supplier_name = (candidate.get("shopName") or "").strip()
        supplier_url = normalize_url(candidate.get("shopUrl", ""), "https://www.1688.com")

        output.append(
            DiscoveryItem(
                keyword=keyword,
                offer_id=offer_id,
                title=title,
                product_url=product_url,
                price_hint=price_hint,
                price_min=price_min,
                price_max=price_max,
                moq_hint=moq_hint,
                supplier_name=supplier_name,
                supplier_url=supplier_url,
                supplier_signals=signals,
                is_new_signal=is_new,
                raw_snippet=snippet[:500],
                collected_at=now,
            )
        )

    return output


def write_outputs(items: List[DiscoveryItem], output_dir: Path, keyword: str) -> Dict[str, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    slug = re.sub(r"[^0-9A-Za-z_\u4e00-\u9fff]+", "_", keyword).strip("_") or "query"

    json_path = output_dir / f"1688_upstream_{slug}_{ts}.json"
    csv_path = output_dir / f"1688_upstream_{slug}_{ts}.csv"
    md_path = output_dir / f"1688_upstream_{slug}_{ts}.md"

    json_path.write_text(
        json.dumps([item.to_dict() for item in items], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    with csv_path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "关键词",
                "标题",
                "价格参考",
                "MOQ参考",
                "供应商",
                "供应商链接",
                "商品链接",
                "上游信号",
                "新品信号",
                "抓取时间",
            ]
        )
        for item in items:
            writer.writerow(
                [
                    item.keyword,
                    item.title,
                    item.price_hint,
                    item.moq_hint,
                    item.supplier_name,
                    item.supplier_url,
                    item.product_url,
                    " | ".join(item.supplier_signals),
                    "是" if item.is_new_signal else "否",
                    item.collected_at,
                ]
            )

    lines = [
        f"# 1688 新品/上游供应商搜索结果",
        "",
        f"- 关键词: `{keyword}`",
        f"- 结果数: `{len(items)}`",
        "",
        "| 标题 | 价格参考 | MOQ参考 | 供应商 | 商品链接 |",
        "|---|---|---|---|---|",
    ]
    for item in items[:50]:
        lines.append(
            f"| {item.title} | {item.price_hint or '-'} | {item.moq_hint or '-'} | {item.supplier_name or '-'} | {item.product_url} |"
        )
    md_path.write_text("\n".join(lines), encoding="utf-8")

    return {"json": json_path, "csv": csv_path, "markdown": md_path}


def run_search(
    keyword: str,
    cookie_file: Path,
    output_dir: Path,
    max_results: int,
    pages: int,
    headless: bool,
    manual_captcha_wait: int,
) -> List[DiscoveryItem]:
    cookies = load_cookies(cookie_file)
    collected: List[DiscoveryItem] = []
    seen_offer_ids: set[str] = set()

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=headless)
        context: BrowserContext = browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        context.add_cookies(cookies)
        page = context.new_page()

        for page_no in range(1, pages + 1):
            if len(collected) >= max_results:
                break

            url = build_search_url(keyword, page_no)
            print(f"[Page {page_no}] {url}")
            page.goto(url, timeout=45000, wait_until="domcontentloaded")
            page.wait_for_timeout(6000)

            if is_captcha_page(page):
                print("[WARN] 触发验证码页面。")
                if not headless and manual_captcha_wait > 0:
                    print(f"[ACTION] 请在浏览器内完成验证，最长等待 {manual_captcha_wait} 秒...")
                    ok = False
                    for _ in range(max(1, manual_captcha_wait // 2)):
                        page.wait_for_timeout(2000)
                        if not is_captcha_page(page):
                            ok = True
                            break
                    if not ok:
                        print("[WARN] 验证未完成，结束本轮抓取。")
                        break
                else:
                    print("[WARN] 当前为无头模式，无法人工过验证码，结束抓取。")
                    break

            page.mouse.wheel(0, 2500)
            page.wait_for_timeout(1800)
            raw_candidates = extract_raw_candidates(page)
            items = dedupe_and_transform(keyword, page, raw_candidates, seen_offer_ids)
            if not items:
                print(f"[Page {page_no}] 未提取到有效商品。")
                continue

            collected.extend(items)
            print(f"[Page {page_no}] 提取 {len(items)} 条，累计 {len(collected)} 条。")

        browser.close()

    def sort_key(item: DiscoveryItem) -> tuple:
        if item.price_min is None:
            return (1, 10**9, item.offer_id)
        return (0, item.price_min, item.offer_id)

    collected.sort(key=sort_key)
    trimmed = collected[:max_results]
    paths = write_outputs(trimmed, output_dir, keyword)
    print(f"[DONE] 输出 JSON: {paths['json']}")
    print(f"[DONE] 输出 CSV: {paths['csv']}")
    print(f"[DONE] 输出 Markdown: {paths['markdown']}")
    return trimmed


def run_self_test() -> None:
    sample = "源头工厂 新品 ¥21.8-22.5 300-2999个起批"
    price_hint, price_min, price_max = parse_price_hint(sample)
    moq_hint = parse_moq_hint(sample)
    signals = find_signals(sample, SUPPLIER_SIGNAL_KEYWORDS)
    is_new = bool(find_signals(sample, NEW_SIGNAL_KEYWORDS))
    print(
        json.dumps(
            {
                "sample": sample,
                "price_hint": price_hint,
                "price_min": price_min,
                "price_max": price_max,
                "moq_hint": moq_hint,
                "signals": signals,
                "is_new": is_new,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="1688 新品/上游供应商搜索")
    parser.add_argument("--keyword", required=False, default="", help="搜索关键词")
    parser.add_argument("--cookie-file", default="1688cookie.json", help="Cookie 文件路径")
    parser.add_argument("--output-dir", default="search_results", help="输出目录")
    parser.add_argument("--max-results", type=int, default=30, help="最大输出条数")
    parser.add_argument("--pages", type=int, default=2, help="抓取页数")
    parser.add_argument("--headless", action="store_true", help="启用无头模式")
    parser.add_argument("--manual-captcha-wait", type=int, default=120, help="验证码人工处理等待秒数")
    parser.add_argument("--self-test", action="store_true", help="仅运行解析自测")
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return

    keyword = args.keyword.strip()
    if not keyword:
        raise SystemExit("`--keyword` 不能为空")

    cookie_file = Path(args.cookie_file)
    if not cookie_file.exists():
        raise SystemExit(f"找不到 cookie 文件: {cookie_file}")

    run_search(
        keyword=keyword,
        cookie_file=cookie_file,
        output_dir=Path(args.output_dir),
        max_results=max(1, args.max_results),
        pages=max(1, args.pages),
        headless=args.headless,
        manual_captcha_wait=max(0, args.manual_captcha_wait),
    )


if __name__ == "__main__":
    main()
