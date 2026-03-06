from __future__ import annotations

import json
import argparse
import re
from datetime import datetime
from pathlib import Path

import httpx


class SearchFetcher:
    def __init__(self, keyword: str, max_results: int = 20):
        self.keyword = keyword
        self.max_results = max_results
        self.results = []

    def search_web(self) -> list[dict]:
        search_queries = [
            f"{self.keyword} 评测 推荐 2026",
            f"{self.keyword} 测评 热门 2026",
            f"{self.keyword} 新品 设计 趋势"
        ]
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        }
        
        all_results = []
        
        for query in search_queries[:2]:
            try:
                url = f"https://www.google.com/search?q={query}&num={self.max_results // 2}"
                response = httpx.get(url, headers=headers, timeout=15.0, follow_redirects=True)
                
                if response.status_code == 200:
                    html = response.text
                    
                    items = re.findall(
                        r'<a href="(https?://[^"]+)"[^>]*><span[^>]*>([^<]+)</span>',
                        html
                    )
                    
                    for url, title in items[:10]:
                        if any(skip in url for skip in ['google', 'youtube', 'facebook', 'twitter']):
                            continue
                        all_results.append({
                            "title": title.strip(),
                            "url": url,
                            "description": f"搜索关键词: {self.keyword}",
                            "timestamp": datetime.now().strftime("%Y-%m-%d")
                        })
            except Exception as e:
                print(f"搜索 '{query}' 时出错: {e}")
                continue
        
        unique_results = []
        seen_urls = set()
        for r in all_results:
            if r["url"] not in seen_urls:
                seen_urls.add(r["url"])
                unique_results.append(r)
        
        return unique_results[:self.max_results]

    def run(self) -> list[dict]:
        print(f"🔍 正在搜索: {self.keyword}")
        self.results = self.search_web()
        print(f"✅ 获取到 {len(self.results)} 条结果")
        return self.results


def main():
    parser = argparse.ArgumentParser(description="搜索热点资讯")
    parser.add_argument("--keyword", "-k", required=True, help="搜索关键词")
    parser.add_argument("--max-results", "-n", type=int, default=20, help="最大结果数")
    parser.add_argument("--out", "-o", default="data/search_results.json", help="输出文件路径")
    args = parser.parse_args()

    fetcher = SearchFetcher(keyword=args.keyword, max_results=args.max_results)
    results = fetcher.run()

    output_path = Path(args.out)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"📁 结果已保存至: {output_path}")
    return results


if __name__ == "__main__":
    main()
