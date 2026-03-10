from __future__ import annotations

import json
import re
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime
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
    source_url: str
    published_date: Optional[str] = None
    matched_topic_keywords: list[str] = field(default_factory=list)
    matched_product_keywords: list[str] = field(default_factory=list)
    impacted_products: list[str] = field(default_factory=list)
    business_impacts: list[str] = field(default_factory=list)
    recommended_actions: list[str] = field(default_factory=list)
    monitoring_note: str = ""


@dataclass
class ExportControlConfig:
    source_urls: dict = field(default_factory=dict)
    category_keywords: list = field(default_factory=list)
    product_keywords: list = field(default_factory=list)
    topic_keywords: list = field(default_factory=list)
    days_lookback: int = 30
    detail_level: str = "detailed"
    max_alerts: int = 12


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
            "CN_CUSTOMS": "http://www.customs.gov.cn/customs/302249/ztzl/ztgz/ind",
        },
        "category_keywords": ["拍立得", "相机包", "相框", "polaroid", "instant camera", "photo frame"],
        "product_keywords": ["相机", "胶片", "相册", "照片打印机", "数码相机"],
        "topic_keywords": [
            "出口管制", "export control", "制裁", "sanction",
            "实体清单", "entity list", "许可证", "license",
            "最终用户", "end user", "最终用途", "end use",
            "EAR", "BIS", "OFAC", "embargo", "禁运", "贸易战", "关税",
        ],
        "days_lookback": 30,
        "detail_level": "detailed",
        "max_alerts": 12,
    }

    COUNTRY_MAP = {
        "US_BIS": "美国商务部",
        "US_BIS_EAR": "美国商务部",
        "US_TREASURY": "美国财政部",
        "OFAC": "美国 OFAC",
        "CN_MOFCOM": "中国商务部",
        "CN_CUSTOMS": "中国海关",
        "SG_CUSTOMS": "新加坡海关",
        "CSL": "美国贸易部",
    }

    CATEGORY_MAP = {
        "US_BIS": "出口管制",
        "US_BIS_EAR": "EAR 法规",
        "US_TREASURY": "财政制裁",
        "OFAC": "OFAC 制裁",
        "CN_MOFCOM": "贸易政策",
        "CN_CUSTOMS": "海关动态",
        "SG_CUSTOMS": "海关动态",
        "CSL": "实体筛查",
    }

    def __init__(self, config: Optional[dict] = None):
        cfg = config or {}
        self.config = ExportControlConfig(
            source_urls=cfg.get("source_urls", self.DEFAULT_CONFIG["source_urls"]),
            category_keywords=cfg.get("category_keywords", self.DEFAULT_CONFIG["category_keywords"]),
            product_keywords=cfg.get("product_keywords", self.DEFAULT_CONFIG["product_keywords"]),
            topic_keywords=cfg.get("topic_keywords", self.DEFAULT_CONFIG["topic_keywords"]),
            days_lookback=cfg.get("days_lookback", self.DEFAULT_CONFIG["days_lookback"]),
            detail_level=cfg.get("detail_level", self.DEFAULT_CONFIG["detail_level"]),
            max_alerts=cfg.get("max_alerts", self.DEFAULT_CONFIG["max_alerts"]),
        )
        self.alerts: list[AlertItem] = []
        self.errors: list[dict] = []

    def _match_keywords(self, text: str, keywords: list[str]) -> list[str]:
        text_lower = text.lower()
        return [keyword for keyword in keywords if keyword.lower() in text_lower][:6]

    def _check_match_type(self, text: str) -> tuple[bool, bool, str]:
        text_lower = text.lower()
        has_topic = any(kw.lower() in text_lower for kw in self.config.topic_keywords)
        has_category = any(kw.lower() in text_lower for kw in self.config.category_keywords)
        has_product = any(kw.lower() in text_lower for kw in self.config.product_keywords)

        if has_topic and (has_category or has_product):
            return True, True, self.MATCH_TYPE_BOTH
        if has_topic:
            return True, False, self.MATCH_TYPE_TOPIC
        if has_category or has_product:
            return False, True, self.MATCH_TYPE_PRODUCT
        return False, False, ""

    def _determine_priority(self, match_type: str, text: str) -> str:
        text_lower = text.lower()
        if match_type == self.MATCH_TYPE_BOTH:
            return self.PRIORITY_P0
        if match_type == self.MATCH_TYPE_TOPIC:
            if any(keyword in text_lower for keyword in ["entity list", "制裁", "sanction", "embargo", "禁运"]):
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
                "User-Agent": (
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                )
            }
            response = httpx.get(url, headers=headers, timeout=30.0, follow_redirects=True, verify=False)
            response.raise_for_status()
            return response.text
        except Exception as exc:
            self.errors.append({
                "source": source_name,
                "url": url,
                "error": str(exc),
                "timestamp": datetime.now().isoformat(),
            })
            return None

    def _build_business_impacts(self, priority: str, match_type: str, country: str, category: str) -> list[str]:
        impacts = []
        if priority == self.PRIORITY_P0:
            impacts.append(f"{country} 的 {category} 更新可能直接触发合作方筛查、许可证复核或订单路径调整。")
            impacts.append("若命中终端产品或关键零部件关键词，应立即核查在途订单、历史客户和替代供应链。")
        elif priority == self.PRIORITY_P1:
            impacts.append(f"{country} 有新的 {category} 信号，短期内可能影响合规解释口径和客户沟通节奏。")
            impacts.append("建议先做观察性研判，再决定是否升级为专项合规动作。")
        else:
            impacts.append("当前更像外围品类/市场信号，可作为弱预警保留，不宜单独触发高强度响应。")

        if match_type == self.MATCH_TYPE_BOTH:
            impacts.append("由于同时命中出口管制和品类关键词，需优先判断是否落到实际 SKU 或交易对手。")
        return impacts[:3]

    def _build_recommended_actions(self, priority: str, matched_topic_keywords: list[str], impacted_products: list[str]) -> list[str]:
        actions = [
            f"按关键词 {', '.join(matched_topic_keywords[:3]) or '出口管制'} 回查近 30 天客户、国家和产品流向。",
            f"对 {', '.join(impacted_products[:3]) or '相关品类'} 做一次客户/供应商/物流链路的快速筛查。",
        ]
        if priority == self.PRIORITY_P0:
            actions.append("同步法务或合规负责人，判断是否需要暂停报价、补许可证材料或加强终端用途声明。")
        elif priority == self.PRIORITY_P1:
            actions.append("列入本周合规例会观察项，等待更多权威源或正式规则文件确认。")
        else:
            actions.append("保留为低优先级监测项，继续跟踪是否演变为正式监管动作。")
        return actions[:3]

    def _build_monitoring_note(self, source_name: str, matched_topic_keywords: list[str], matched_product_keywords: list[str]) -> str:
        topic_text = ", ".join(matched_topic_keywords[:3]) or "出口管制"
        product_text = ", ".join(matched_product_keywords[:3]) or "目标品类"
        return f"{source_name} 命中主题词 {topic_text}；关联品类词 {product_text}。建议把该条作为后续规则核验的索引入口。"

    def _parse_generic(self, html: str, base_url: str, source_name: str) -> list[AlertItem]:
        alerts = []
        items = re.findall(r'<a[^>]+href="([^"]+)"[^>]*>([^<]+)</a>', html, re.IGNORECASE)
        country = self.COUNTRY_MAP.get(source_name, "其他")
        category = self.CATEGORY_MAP.get(source_name, "综合")

        for url, title in items[:80]:
            clean_title = re.sub(r"\s+", " ", title).strip()
            full_url = urljoin(base_url, url)
            has_topic, has_product, match_type = self._check_match_type(clean_title)
            if not match_type:
                continue

            priority = self._determine_priority(match_type, clean_title)
            matched_topic_keywords = self._match_keywords(clean_title, self.config.topic_keywords)
            matched_product_keywords = self._match_keywords(clean_title, self.config.category_keywords + self.config.product_keywords)
            impacted_products = matched_product_keywords[:3]
            business_impacts = self._build_business_impacts(priority, match_type, country, category)
            recommended_actions = self._build_recommended_actions(priority, matched_topic_keywords, impacted_products)
            monitoring_note = self._build_monitoring_note(source_name, matched_topic_keywords, matched_product_keywords)

            if match_type == self.MATCH_TYPE_BOTH:
                summary = "同时命中出口管制主题词与目标品类词，建议优先复核是否影响当前业务。"
            elif match_type == self.MATCH_TYPE_TOPIC:
                summary = "命中出口管制主题词，但尚未看到明确品类落点，适合作为规则观察项。"
            else:
                summary = "命中品类词但缺少明确监管词，保留为弱信号，不应单独升级。"

            alerts.append(
                AlertItem(
                    match_type=match_type,
                    priority=priority,
                    country=country,
                    category=category,
                    title=clean_title,
                    summary=summary,
                    source_url=full_url,
                    published_date=self._extract_date(clean_title),
                    matched_topic_keywords=matched_topic_keywords,
                    matched_product_keywords=matched_product_keywords,
                    impacted_products=impacted_products,
                    business_impacts=business_impacts,
                    recommended_actions=recommended_actions,
                    monitoring_note=monitoring_note,
                )
            )

        return alerts

    def run(self) -> dict:
        for source_name, url in self.config.source_urls.items():
            html = self._fetch_page(url, source_name)
            if not html:
                continue
            try:
                self.alerts.extend(self._parse_generic(html, url, source_name))
            except Exception as exc:
                self.errors.append({
                    "source": source_name,
                    "url": url,
                    "error": f"Parse error: {exc}",
                    "timestamp": datetime.now().isoformat(),
                })
        return self.generate_report()

    def generate_report(self) -> dict:
        priority_order = {self.PRIORITY_P0: 0, self.PRIORITY_P1: 1, self.PRIORITY_P2: 2}
        self.alerts.sort(key=lambda item: (priority_order.get(item.priority, 3), item.country, item.category))

        limited_alerts = self.alerts[:self.config.max_alerts]
        summary = {
            "total_alerts": len(self.alerts),
            "p0_count": sum(1 for item in self.alerts if item.priority == self.PRIORITY_P0),
            "p1_count": sum(1 for item in self.alerts if item.priority == self.PRIORITY_P1),
            "p2_count": sum(1 for item in self.alerts if item.priority == self.PRIORITY_P2),
            "match_type_both": sum(1 for item in self.alerts if item.match_type == self.MATCH_TYPE_BOTH),
            "match_type_topic": sum(1 for item in self.alerts if item.match_type == self.MATCH_TYPE_TOPIC),
            "match_type_product": sum(1 for item in self.alerts if item.match_type == self.MATCH_TYPE_PRODUCT),
            "error_count": len(self.errors),
            "source_coverage": dict(Counter(self.COUNTRY_MAP.get(name, name) for name in self.config.source_urls)),
        }

        if summary["total_alerts"]:
            executive_summary = (
                f"近 {self.config.days_lookback} 天共捕获 {summary['total_alerts']} 条相关信号，"
                f"其中 P0 {summary['p0_count']} 条、P1 {summary['p1_count']} 条。"
                f"优先关注同时命中出口管制与品类关键词的事项。"
            )
        else:
            executive_summary = (
                f"近 {self.config.days_lookback} 天未捕获明确命中的出口管制事项。"
                "当前应维持常规监控，并保留抓取失败告警。"
            )

        return {
            "status": "success" if self.alerts else "no_data",
            "report_type": "weekly",
            "detail_level": self.config.detail_level,
            "period": f"近{self.config.days_lookback}天",
            "executive_summary": executive_summary,
            "summary": summary,
            "alerts": [
                {
                    "match_type": item.match_type,
                    "priority": item.priority,
                    "country": item.country,
                    "category": item.category,
                    "title": item.title,
                    "summary": item.summary,
                    "published_date": item.published_date,
                    "matched_topic_keywords": item.matched_topic_keywords,
                    "matched_product_keywords": item.matched_product_keywords,
                    "impacted_products": item.impacted_products,
                    "business_impacts": item.business_impacts,
                    "recommended_actions": item.recommended_actions,
                    "monitoring_note": item.monitoring_note,
                    "source_url": item.source_url,
                }
                for item in limited_alerts
            ],
            "errors": self.errors,
            "timestamp": datetime.now().isoformat(),
        }

    def format_for_feishu(self) -> str:
        lines = [
            "# 国际出口管制详细周报",
            "",
            f"更新时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}",
            f"监控周期：近 {self.config.days_lookback} 天",
            "",
            "---",
            "",
            "## 管理层摘要",
            "",
        ]

        report = self.generate_report()
        summary = report["summary"]
        lines.append(report["executive_summary"])
        lines.append("")
        lines.append(f"- 命中总数：{summary['total_alerts']}（P0 {summary['p0_count']} / P1 {summary['p1_count']} / P2 {summary['p2_count']}）")
        lines.append(f"- 命中结构：出口管制+品类 {summary['match_type_both']} / 仅出口管制 {summary['match_type_topic']} / 仅品类 {summary['match_type_product']}")
        lines.append(f"- 抓取异常：{summary['error_count']} 条")
        lines.append("")

        if report["alerts"]:
            lines.append("## 重点事项")
            lines.append("")
            for index, item in enumerate(report["alerts"], start=1):
                lines.append(f"### {index}. [{item['priority']}][{item['country']}][{item['category']}] {item['title']}")
                lines.append(f"- 结论：{item['summary']}")
                if item["matched_topic_keywords"] or item["matched_product_keywords"]:
                    lines.append(
                        f"- 命中关键词：主题 {', '.join(item['matched_topic_keywords']) or '-'}；品类 {', '.join(item['matched_product_keywords']) or '-'}"
                    )
                for impact in item["business_impacts"]:
                    lines.append(f"- 影响：{impact}")
                for action in item["recommended_actions"]:
                    lines.append(f"- 建议动作：{action}")
                lines.append(f"- 监控备注：{item['monitoring_note']}")
                lines.append(f"- 来源：{item['source_url']}")
                lines.append("")
        else:
            lines.append("## 重点事项")
            lines.append("")
            lines.append("当前无明确命中。若业务涉及敏感国家、终端用途或许可证事项，仍建议保留每周例行复核。")
            lines.append("")

        if self.errors:
            lines.append("## 抓取失败告警")
            lines.append("")
            for error in self.errors[:6]:
                lines.append(f"- {error['source']}：{error['error']}（{error['url']}）")
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
        with open(args.config, encoding="utf-8") as f:
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
