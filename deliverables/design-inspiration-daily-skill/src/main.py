from __future__ import annotations

import argparse
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from fetch_search_results import SearchFetcher
from trend import DesignInspirationMonitor
import yaml


def main():
    parser = argparse.ArgumentParser(description="拍立得与周边产品设计灵感日报 - 完整流程")
    parser.add_argument("--keyword", "-k", required=True, help="搜索关键词")
    parser.add_argument("--config", "-c", default="config/config.yaml", help="配置文件路径")
    parser.add_argument("--max-results", "-n", type=int, default=20, help="最大搜索结果数")
    parser.add_argument("--out", "-o", default="output/日报", help="输出文件前缀")
    args = parser.parse_args()

    config_path = Path(args.config)
    if not config_path.exists():
        config_path = project_root / config_path
    
    config = None
    if config_path.exists():
        with open(config_path, encoding="utf-8") as f:
            config = yaml.safe_load(f)

    print("=" * 50)
    print("📡 Step 1: 搜索热点资讯")
    print("=" * 50)
    
    fetcher = SearchFetcher(keyword=args.keyword, max_results=args.max_results)
    search_results = fetcher.run()

    if not search_results:
        print("❌ 未获取到搜索结果，流程终止")
        return

    search_file = project_root / "data" / f"search_results_{args.keyword}.json"
    with open(search_file, "w", encoding="utf-8") as f:
        import json
        json.dump(search_results, f, ensure_ascii=False, indent=2)
    print(f"📁 搜索结果已保存至: {search_file}")

    print("\n" + "=" * 50)
    print("📊 Step 2: 生成设计灵感日报")
    print("=" * 50)
    
    monitor = DesignInspirationMonitor(config=config)
    report = monitor.run(search_results=search_results)

    output_path = Path(args.out)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    import json
    with open(f"{output_path}.json", "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    md_content = monitor.format_for_feishu()
    with open(f"{output_path}.md", "w", encoding="utf-8") as f:
        f.write(md_content)

    print(f"\n✅ 流程完成！")
    print(f"   • 搜索结果: {search_file}")
    print(f"   • JSON报告: {output_path}.json")
    print(f"   • Markdown报告: {output_path}.md")
    
    print("\n" + "=" * 50)
    print("📰 设计灵感日报")
    print("=" * 50)
    print(md_content)


if __name__ == "__main__":
    main()
