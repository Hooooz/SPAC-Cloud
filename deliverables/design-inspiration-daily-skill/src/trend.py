from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional


@dataclass
class TrendItem:
    topic: str
    summary: str
    source_urls: list[str]
    heat_level: Optional[str] = None
    category: str = "综合"


@dataclass
class DesignInspirationConfig:
    search_keywords: list = field(default_factory=list)
    topic_keywords: list = field(default_factory=list)
    max_results: int = 20
    output_format: str = "markdown"


class DesignInspirationMonitor:
    DEFAULT_CONFIG = {
        "search_keywords": [
            "拍立得", "富士相机", "polaroid", "instant photo",
            "相机包", "相框", "DIY相册", "照片打印机",
            "胶片", "复古相机", "摄影", "拍照", "相册"
        ],
        "topic_keywords": [
            "设计", "配色", "材质", "工艺", "颜色搭配",
            "ins风", "北欧风", "简约", "复古", "奶油风",
            "多巴胺", "美拉德", "芭比粉", "薄荷绿",
            "测评", "评测", "推荐", "新品"
        ],
        "max_results": 20,
        "output_format": "markdown"
    }

    def __init__(self, config: Optional[dict] = None):
        cfg = config or {}
        self.config = DesignInspirationConfig(
            search_keywords=cfg.get("search_keywords", self.DEFAULT_CONFIG["search_keywords"]),
            topic_keywords=cfg.get("topic_keywords", self.DEFAULT_CONFIG["topic_keywords"]),
            max_results=cfg.get("max_results", self.DEFAULT_CONFIG["max_results"]),
            output_format=cfg.get("output_format", self.DEFAULT_CONFIG["output_format"])
        )
        self.trends: list[TrendItem] = []
        self.errors: list[dict] = []
        self.design_elements = {
            "colors": [],
            "materials": [],
            "structures": []
        }
        self.risk_warnings = []
        self.next_week_suggestions = [
            "关注配色趋势变化，及时调整产品颜色",
            "监测竞品设计动态，避免同质化",
            "结合热点元素进行新品设计"
        ]
        self.daily_summary = ""

    def _categorize_item(self, title: str) -> str:
        title_lower = title.lower()
        if any(kw in title_lower for kw in ["测评", "评测", "对比", "横评"]):
            return "产品测评"
        if any(kw in title_lower for kw in ["新品", "发布", "上市", "新款"]):
            return "新品速递"
        if any(kw in title_lower for kw in ["教程", "diy", "制作", "攻略"]):
            return "DIY教程"
        if any(kw in title_lower for kw in ["配色", "颜色", "风格", "设计"]):
            return "设计趋势"
        return "综合"

    def _generate_daily_summary(self) -> str:
        if not self.trends:
            return "今日暂无相关热点资讯"

        categories = {}
        for t in self.trends:
            cat = t.category
            categories[cat] = categories.get(cat, 0) + 1

        summary_parts = []
        for cat, count in sorted(categories.items(), key=lambda x: -x[1]):
            summary_parts.append(f"{cat}{count}条")

        hot_topics = [t.topic for t in self.trends[:3]]
        
        summary = f"今日共收录{len(self.trends)}条热点，涵盖{', '.join(summary_parts)}。热点话题集中在：{'、'.join(hot_topics[:2])}。"
        
        if self.design_elements["colors"]:
            summary += f"配色方面，{self.design_elements['colors'][0]}色系热度较高。"
        
        return summary

    def _extract_source_name(self, url: str) -> str:
        if not url:
            return "未知来源"
        if "sohu.com" in url or "m.sohu.com" in url:
            return "搜狐"
        if "toutiao.com" in url:
            return "今日头条"
        if "xiaohongshu.com" in url:
            return "小红书"
        if "weibo.com" in url:
            return "微博"
        if "zhihu.com" in url:
            return "知乎"
        if "bilibili.com" in url:
            return "B站"
        if "jd.com" in url:
            return "京东"
        if "taobao.com" in url or "tmall.com" in url:
            return "淘宝"
        if "1688.com" in url:
            return "1688"
        if "douyin.com" in url:
            return "抖音"
        if "example.com" in url:
            return "示例"
        import re
        match = re.search(r'https?://(?:www\.)?([^/]+)', url)
        if match:
            return match.group(1).split('.')[0]
        return "链接"

    def parse_search_results(self, search_results: list) -> list[dict]:
        parsed = []
        for item in search_results:
            title = item.get("title", "")
            url = item.get("url", item.get("link", ""))
            desc = item.get("description", item.get("content", ""))
            
            parsed.append({
                "title": title,
                "url": url,
                "description": desc,
                "timestamp": item.get("time", item.get("created_at", ""))
            })
        return parsed

    def _extract_design_elements(self, texts: list[str]):
        color_keywords = ["色", "粉", "绿", "蓝", "黄", "紫", "黑", "白", "棕", "橘", "米", "咖", "红"]
        material_keywords = ["帆布", "皮革", "毛毡", "塑料", "金属", "木质", "玻璃", "亚克力", "硅胶"]
        structure_keywords = ["拉链", "纽扣", "磁扣", "折叠", "便携", "mini", "轻便", "复古"]

        all_text = " ".join(texts)
        
        for kw in color_keywords:
            if kw in all_text:
                self.design_elements["colors"].append(kw)
        
        for kw in material_keywords:
            if kw in all_text:
                self.design_elements["materials"].append(kw)
        
        for kw in structure_keywords:
            if kw in all_text:
                self.design_elements["structures"].append(kw)

        self.design_elements["colors"] = list(set(self.design_elements["colors"]))[:5]
        self.design_elements["materials"] = list(set(self.design_elements["materials"]))[:5]
        self.design_elements["structures"] = list(set(self.design_elements["structures"]))[:5]

    def _generate_risk_warnings(self, trends: list[dict]):
        if len(trends) > 10:
            self.risk_warnings.append("同质化风险：热门内容高度相似，建议差异化竞争")
        
        for item in trends:
            title = item.get("title", "")
            if any(kw in title for kw in ["爆款", "网红", "跟风"]):
                self.risk_warnings.append("审美泡沫风险：部分内容可能过度跟风")

    def run(self, search_results: Optional[list] = None) -> dict:
        if search_results is None:
            self.errors.append({
                "error": "No search results provided",
                "message": "需要提供搜索结果作为输入",
                "timestamp": datetime.now().isoformat()
            })
            return self.generate_report()

        parsed_results = self.parse_search_results(search_results)
        
        keywords = self.config.search_keywords + self.config.topic_keywords
        relevant_results = []
        for item in parsed_results:
            text = (item.get("title", "") + " " + item.get("description", "")).lower()
            if any(kw.lower() in text for kw in keywords):
                relevant_results.append(item)

        for item in relevant_results[:self.config.max_results]:
            category = self._categorize_item(item.get("title", ""))
            self.trends.append(TrendItem(
                topic=item.get("title", "未知主题"),
                summary=item.get("description", "")[:200],
                source_urls=[item.get("url", "")] if item.get("url") else [],
                heat_level="high" if any(kw in item.get("title", "") for kw in ["爆款", "热门", "新品"]) else "medium",
                category=category
            ))

        texts = [t.topic + " " + t.summary for t in self.trends]
        self._extract_design_elements(texts)
        self._generate_risk_warnings(relevant_results)
        self.daily_summary = self._generate_daily_summary()

        return self.generate_report()

    def generate_report(self) -> dict:
        categories = {}
        for t in self.trends:
            cat = t.category
            categories[cat] = categories.get(cat, 0) + 1

        report = {
            "status": "success" if self.trends else "no_data",
            "report_type": "daily",
            "summary": {
                "total_trends": len(self.trends),
                "categories": categories,
                "error_count": len(self.errors)
            },
            "daily_summary": self.daily_summary,
            "top_trends": [
                {
                    "topic": t.topic,
                    "summary": t.summary,
                    "category": t.category,
                    "source_urls": t.source_urls,
                    "heat_level": t.heat_level
                }
                for t in self.trends[:5]
            ],
            "design_elements": {
                "colors": self.design_elements["colors"],
                "materials": self.design_elements["materials"],
                "structures": self.design_elements["structures"]
            },
            "risk_warnings": self.risk_warnings,
            "next_week_suggestions": self.next_week_suggestions,
            "errors": self.errors,
            "timestamp": datetime.now().isoformat()
        }
        
        return report

    def format_for_feishu(self) -> str:
        if not self.trends:
            return "📭 设计灵感日报：暂无数据"

        lines = ["# 拍立得与周边产品设计灵感日报", ""]
        lines.append(datetime.now().strftime('%Y-%m-%d %H:%M'))
        lines.append("")
        lines.append("---")
        lines.append("")
        lines.append("## 📋 今日要闻")
        lines.append("")
        lines.append(f"**热点话题**：{self.daily_summary}")
        lines.append("")
        
        if self.design_elements["colors"] or self.design_elements["materials"] or self.design_elements["structures"]:
            lines.append("| 类别 | 热门元素 |")
            lines.append("|------|----------|")
            if self.design_elements["colors"]:
                lines.append(f"| 配色 | {', '.join(self.design_elements['colors'])} |")
            else:
                lines.append("| 配色 | - |")
            if self.design_elements["materials"]:
                lines.append(f"| 材质 | {', '.join(self.design_elements['materials'])} |")
            else:
                lines.append("| 材质 | - |")
            if self.design_elements["structures"]:
                lines.append(f"| 结构 | {', '.join(self.design_elements['structures'])} |")
            else:
                lines.append("| 结构 | - |")
            lines.append("")
        
        lines.append("---")
        lines.append("")
        lines.append("## 🔥 热点聚焦 TOP5")
        lines.append("")
        lines.append("| 序号 | 类别 | 标题 | 来源 |")
        lines.append("|------|------|------|------|")
        
        for i, t in enumerate(self.trends[:5], 1):
            source = t.source_urls[0] if t.source_urls else ""
            source_name = self._extract_source_name(source)
            lines.append(f"| {i} | {t.category} | {t.topic[:30]} | [{source_name}]({source[:60]}) |")
        
        lines.append("")
        lines.append("---")
        
        if self.risk_warnings:
            lines.append("")
            lines.append("## ⚠️ 风险提示")
            for warning in self.risk_warnings:
                lines.append(f"- {warning}")
            lines.append("")
        
        lines.append("")
        lines.append("---")
        
        return "\n".join(lines)


def main():
    import argparse
    import yaml
    
    ap = argparse.ArgumentParser(description="拍立得与周边产品设计灵感日报")
    ap.add_argument("--config", default=None, help="配置文件路径")
    ap.add_argument("--input", default=None, help="输入JSON文件路径（搜索结果）")
    ap.add_argument("--out", default="output/design_inspiration_daily", help="输出文件前缀")
    args = ap.parse_args()

    config = None
    if args.config:
        with open(args.config) as f:
            config = yaml.safe_load(f)

    monitor = DesignInspirationMonitor(config=config)

    if args.input:
        with open(args.input) as f:
            search_results = json.load(f)
        report = monitor.run(search_results=search_results)
    else:
        report = monitor.run()

    out_path = Path(args.out)
    with open(f"{out_path}.json", "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    md_content = monitor.format_for_feishu()
    print(md_content)
    print(f"\n报告已保存至: {out_path}.json")
    
    with open(f"{out_path}.md", "w", encoding="utf-8") as f:
        f.write(md_content)
    print(f"Markdown报告已保存至: {out_path}.md")


if __name__ == "__main__":
    main()
