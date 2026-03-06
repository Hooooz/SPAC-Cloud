from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional
from urllib.parse import urljoin

import httpx


@dataclass
class AlertItem:
    match_type: str
    priority: str
    country: str
    category: str
    title: str
    summary: str
    impact: str
    recommendation: str
    source_url: str
    published_date: Optional[str] = None


@dataclass
class ExportControlConfig:
    source_urls: dict = field(default_factory=dict)
    category_keywords: list = field(default_factory=list)
    product_keywords: list = field(default_factory=list)
    topic_keywords: list = field(default_factory=list)
    days_lookback: int = 30


class ExportControlMonitor:
    PRIORITY_P0 = "P0"
    PRIORITY_P1 = "P1"
    PRIORITY_P2 = "P2"

    MATCH_TYPE_BOTH = "出口管制+品类"
    MATCH_TYPE_TOPIC = "出口管制"
    MATCH_TYPE_PRODUCT = "品类销售"

    DEFAULT_CONFIG = {
        "source_urls": {
            "US_BIS": "https://www.bis.gov/",
            "US_BIS_EAR": "https://www.bis.gov/regulations/ear",
            "US_TREASURY": "https://home.treasury.gov/news/press-releases",
            "OFAC": "https://ofac.treasury.gov/",
            "CSL": "https://www.trade.gov/data-visualization/csl-search",
            "SG_CUSTOMS": "https://www.customs.gov.sg/news/",
            "CN_MOFCOM": "https://www.mofcom.gov.cn/fzlm/mrgx/index.html",
            "CN_CUSTOMs": "http://www.customs.gov.cn/customs/302249/ztzl/ztgz/ind",
        },
        "category_keywords": ["拍立得", "相机包", "相框", "polaroid", "instant camera", "photo frame"],
        "product_keywords": ["相机", "胶片", "相册", "照片打印机", "数码相机"],
        "topic_keywords": [
            "出口管制", "export control", "制裁", "sanction",
            "实体清单", "entity list", "许可证", "license",
            "最终用户", "end user", "最终用途", "end use",
            "EAR", "BIS", "OFAC", "embargo", "禁运", "贸易战", "关税"
        ],
        "days_lookback": 30
    }

    def __init__(self, config: Optional[dict] = None):
        cfg = config or {}
        self.config = ExportControlConfig(
            source_urls=cfg.get("source_urls", self.DEFAULT_CONFIG["source_urls"]),
            category_keywords=cfg.get("category_keywords", self.DEFAULT_CONFIG["category_keywords"]),
            product_keywords=cfg.get("product_keywords", self.DEFAULT_CONFIG["product_keywords"]),
            topic_keywords=cfg.get("topic_keywords", self.DEFAULT_CONFIG["topic_keywords"]),
            days_lookback=cfg.get("days_lookback", self.DEFAULT_CONFIG["days_lookback"])
        )
        self.alerts: list[AlertItem] = []
        self.errors: list[dict] = []
        self._all_fetched_items: list[tuple[str, str]] = []

    def _check_match_type(self, text: str) -> tuple[bool, bool, str]:
        text_lower = text.lower()
        has_topic = any(kw.lower() in text_lower for kw in self.config.topic_keywords)
        has_category = any(kw.lower() in text_lower for kw in self.config.category_keywords)
        has_product = any(kw.lower() in text_lower for kw in self.config.product_keywords)
        
        if has_topic and (has_category or has_product):
            return True, True, self.MATCH_TYPE_BOTH
        elif has_topic:
            return True, False, self.MATCH_TYPE_TOPIC
        elif has_category or has_product:
            return False, True, self.MATCH_TYPE_PRODUCT
        return False, False, ""

    def _determine_priority(self, match_type: str, text: str) -> str:
        text_lower = text.lower()
        if match_type == self.MATCH_TYPE_BOTH:
            return self.PRIORITY_P0
        if match_type == self.MATCH_TYPE_TOPIC:
            if any(kw in text_lower for kw in ["entity list", "制裁", "sanction", "embargo", "禁运"]):
                return self.PRIORITY_P0
            return self.PRIORITY_P1
        return self.PRIORITY_P2

    def _extract_date(self, text: str) -> Optional[str]:
        date_patterns = [
            r"(\d{4}-\d{2}-\d{2})",
            r"(\d{4}/\d{2}/\d{2})",
            r"(\d{4}年\d{1,2}月\d{1,2}日)",
        ]
        for pattern in date_patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1)
        return None

    def _fetch_page(self, url: str, source_name: str) -> Optional[str]:
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            }
            response = httpx.get(url, headers=headers, timeout=30.0, follow_redirects=True, verify=False)
            response.raise_for_status()
            return response.text
        except Exception as e:
            self.errors.append({
                "source": source_name,
                "url": url,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            })
            return None

    def _parse_generic(self, html: str, base_url: str, source_name: str) -> list[AlertItem]:
        alerts = []
        items = re.findall(r'<a[^>]+href="([^"]+)"[^>]*>([^<]+)</a>', html, re.IGNORECASE)
        
        country_map = {
            "US_BIS": "美国商务部", "US_BIS_EAR": "美国商务部", "US_TREASURY": "美国财政部", "OFAC": "美国OFAC",
            "CN_MOFCOM": "中国商务部", "CN_CUSTOMS": "中国海关", "SG_CUSTOMS": "新加坡海关"
        }
        country = country_map.get(source_name, "OTHER")
        
        category_map = {
            "US_BIS": "出口管制", "US_BIS_EAR": "EAR法规", "US_TREASURY": "财政制裁",
            "OFAC": "OFAC制裁", "CN_MOFCOM": "贸易政策", "CN_CUSTOMS": "海关", "SG_CUSTOMS": "海关"
        }
        category = category_map.get(source_name, "综合")
        
        for url, title in items[:50]:
            full_url = urljoin(base_url, url)
            has_topic, has_product, match_type = self._check_match_type(title)
            
            if not match_type:
                continue
                
            priority = self._determine_priority(match_type, title)
            date = self._extract_date(title)
            
            if match_type == self.MATCH_TYPE_BOTH:
                summary = "出口管制+品类关键词命中"
                impact = "需立即评估对拍立得品类出口的影响"
                recommendation = "建议审查许可证要求并评估业务风险"
            elif match_type == self.MATCH_TYPE_TOPIC:
                summary = "出口管制政策更新"
                impact = "可能影响出口业务"
                recommendation = "关注政策变化，必要时咨询合规部门"
            else:
                summary = "品类销售/市场动态"
                impact = "市场趋势参考"
                recommendation = "关注竞品动态，把握市场机会"
            
            alerts.append(AlertItem(
                match_type=match_type,
                priority=priority,
                country=country,
                category=category,
                title=title.strip(),
                summary=summary,
                impact=impact,
                recommendation=recommendation,
                source_url=full_url,
                published_date=date
            ))
            
            self._all_fetched_items.append((title.strip(), full_url))
        
        return alerts

    def run(self) -> dict:
        for source_name, url in self.config.source_urls.items():
            html = self._fetch_page(url, source_name)
            if not html:
                continue
            
            try:
                alerts = self._parse_generic(html, url, source_name)
                self.alerts.extend(alerts)
            except Exception as e:
                self.errors.append({
                    "source": source_name,
                    "url": url,
                    "error": f"Parse error: {str(e)}",
                    "timestamp": datetime.now().isoformat()
                })

        return self.generate_report()

    def generate_report(self) -> dict:
        priority_order = {self.PRIORITY_P0: 0, self.PRIORITY_P1: 1, self.PRIORITY_P2: 2}
        self.alerts.sort(key=lambda x: (priority_order.get(x.priority, 3), x.match_type))

        match_type_order = {self.MATCH_TYPE_BOTH: 0, self.MATCH_TYPE_TOPIC: 1, self.MATCH_TYPE_PRODUCT: 2}
        
        p0_alerts = [a for a in self.alerts if a.priority == self.PRIORITY_P0]
        p1_alerts = [a for a in self.alerts if a.priority == self.PRIORITY_P1]
        p2_alerts = [a for a in self.alerts if a.priority == self.PRIORITY_P2]
        
        both_count = len([a for a in self.alerts if a.match_type == self.MATCH_TYPE_BOTH])
        topic_count = len([a for a in self.alerts if a.match_type == self.MATCH_TYPE_TOPIC])
        product_count = len([a for a in self.alerts if a.match_type == self.MATCH_TYPE_PRODUCT])

        report = {
            "status": "success",
            "report_type": "weekly",
            "period": f"近{self.config.days_lookback}天",
            "summary": {
                "total_alerts": len(self.alerts),
                "p0_count": len(p0_alerts),
                "p1_count": len(p1_alerts),
                "p2_count": len(p2_alerts),
                "match_type_both": both_count,
                "match_type_topic": topic_count,
                "match_type_product": product_count,
                "error_count": len(self.errors)
            },
            "alerts": [
                {
                    "match_type": a.match_type,
                    "priority": a.priority,
                    "country": a.country,
                    "category": a.category,
                    "title": a.title,
                    "summary": a.summary,
                    "impact": a.impact,
                    "recommendation": a.recommendation,
                    "source_url": a.source_url,
                    "published_date": a.published_date
                }
                for a in self.alerts
            ],
            "errors": self.errors,
            "timestamp": datetime.now().isoformat()
        }

        return report

    def format_for_feishu(self) -> str:
        lines = ["# 国际出口周报", ""]
        lines.append(f"**周期**: 近{self.config.days_lookback}天，**更新时间**: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        lines.append("")
        lines.append("---")
        lines.append("")
        lines.append("## 📊 合规建议")
        lines.append("")
        lines.append("1. **持续关注美国OFAC制裁名单更新**，特别是俄罗斯、伊朗、朝鲜等国家的制裁动态")
        lines.append("2. **核查业务合作伙伴**是否在制裁名单上")
        lines.append("3. **出口许可证申请**需关注BIS最新法规变化")
        lines.append("")
        lines.append("---")
        
        if not self.alerts:
            lines.append("## 拍立得相关出口管制（0）")
            lines.append("> 出口管制关键词+拍立得品类")
            lines.append("**当前无命中**")
            lines.append("")
            lines.append("---")
            lines.append("\n*报告时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}*")
            return "\n".join(lines)

        priority_order = {self.PRIORITY_P0: 0, self.PRIORITY_P1: 1, self.PRIORITY_P2: 2}
        self.alerts.sort(key=lambda x: (priority_order.get(x.priority, 3), x.match_type))

        both_count = len([a for a in self.alerts if a.match_type == self.MATCH_TYPE_BOTH])
        topic_count = len([a for a in self.alerts if a.match_type == self.MATCH_TYPE_TOPIC])
        
        lines.append(f"## 拍立得相关出口管制（{both_count}）")
        lines.append("")
        lines.append("> 出口管制关键词+拍立得品类")
        
        p0_alerts = [a for a in self.alerts if a.match_type == self.MATCH_TYPE_BOTH]
        if p0_alerts:
            for a in p0_alerts[:10]:
                lines.append(f"• [{a.country}] {a.title}")
        else:
            lines.append("**当前无命中**")
        
        lines.append("")
        lines.append("---")
        lines.append("")
        lines.append(f"## 所有出口管制（{len(self.alerts[:10])}）")
        lines.append("")
        lines.append("> 出口管制政策相关")
        lines.append("")
        lines.append("| 序号 | 标题 | 关键词 | 大致描述 | 来源 |")
        lines.append("| ---- | ---------------------------- | ---------------------------- | ---------------------------- | ----------------------------------------------------------------------------------------------------------------- |")
        
        p1_alerts = [a for a in self.alerts if a.priority in [self.PRIORITY_P0, self.PRIORITY_P1]]
        for i, a in enumerate(p1_alerts[:10], 1):
            keywords = a.category
            desc = a.summary
            lines.append(f"| {i} | {a.title[:25]} | {keywords[:25]} | {desc[:25]} | [{a.country}]({a.source_url[:50]}) |")
        
        lines.append("")
        lines.append("---")
        
        if self.errors:
            lines.append("")
            lines.append("## ⚠️ 抓取异常")
            lines.append("")
            for e in self.errors[:3]:
                lines.append(f"| {e['source']} | {e['error'][:50]} |")
            lines.append("")

        return "\n".join(lines)


def main():
    import argparse
    import yaml
    
    ap = argparse.ArgumentParser(description="出口政策/合规变化周报")
    ap.add_argument("--config", default=None, help="配置文件路径")
    ap.add_argument("--out", default="output/export_weekly_report", help="输出文件前缀")
    args = ap.parse_args()

    config = None
    if args.config:
        with open(args.config) as f:
            config = yaml.safe_load(f)

    monitor = ExportControlMonitor(config=config)
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
