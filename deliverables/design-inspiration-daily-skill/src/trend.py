from __future__ import annotations

import json
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse
import re


@dataclass
class TrendItem:
    topic: str
    summary: str
    source_urls: list[str]
    source_name: str
    heat_level: str = "medium"
    category: str = "综合"
    matched_keywords: list[str] = field(default_factory=list)
    design_takeaway: str = ""
    business_signal: str = ""
    recommended_action: str = ""


@dataclass
class DesignInspirationConfig:
    search_keywords: list = field(default_factory=list)
    topic_keywords: list = field(default_factory=list)
    max_results: int = 20
    top_n: int = 8
    detail_level: str = "detailed"
    output_format: str = "markdown"


class DesignInspirationMonitor:
    OUT_OF_SCOPE_TERMS = ["社媒", "账号", "运营", "投放", "文案", "获客", "引流", "培训", "课程"]
    DESIGN_SCOPE_TERMS = ["设计", "产品", "包装", "周边", "配色", "材质", "结构", "视觉", "风格", "海报", "品牌", "页面", "ui", "ux"]

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
        "top_n": 8,
        "detail_level": "detailed",
        "output_format": "markdown",
    }

    ELEMENT_KEYWORDS = {
        "colors": {
            "米色": ["米色", "米白", "奶油", "卡其"],
            "黑色": ["黑色", "雅黑", "深空灰"],
            "白色": ["白色", "纯白", "珍珠白"],
            "银色": ["银色", "银灰", "金属银"],
            "绿色": ["绿色", "薄荷绿", "橄榄绿"],
            "蓝色": ["蓝色", "湖蓝", "雾霾蓝"],
            "粉色": ["粉色", "樱花粉", "珊瑚粉"],
            "透明": ["透明", "半透明", "冰透"],
        },
        "materials": {
            "铝合金": ["铝合金", "铝材"],
            "金属": ["金属", "不锈钢", "钢制"],
            "硅胶": ["硅胶"],
            "PC/ABS": ["pc", "abs", "pc/abs"],
            "TPU": ["tpu"],
            "亚克力": ["亚克力"],
            "皮革": ["皮革", "pu", "仿皮"],
            "木质": ["木质", "原木"],
            "尼龙": ["尼龙", "织物", "帆布"],
        },
        "structures": {
            "磁吸": ["磁吸", "磁扣", "磁铁"],
            "折叠": ["折叠", "翻折"],
            "伸缩": ["伸缩", "拉伸", "加长"],
            "旋转": ["旋转", "云台", "万向"],
            "夹持": ["夹持", "夹臂", "夹子"],
            "桌面支撑": ["桌面", "底座", "立式"],
            "便携": ["便携", "轻便", "mini"],
            "收纳": ["收纳", "分层", "整理"],
        },
        "styles": {
            "极简": ["极简", "简约", "简洁"],
            "复古": ["复古", "胶片感"],
            "INS": ["ins", "ins风"],
            "通勤": ["通勤", "办公"],
            "奶油风": ["奶油风"],
            "Y2K": ["y2k"],
            "户外感": ["户外", "露营"],
        },
        "finishes": {
            "磨砂": ["磨砂", "喷砂"],
            "亮面": ["亮面", "高光"],
            "透明件": ["透明", "半透明"],
            "涂层": ["涂层", "镀层"],
            "编织感": ["编织", "织纹"],
        },
        "scenarios": {
            "桌搭办公": ["桌搭", "办公", "会议"],
            "通勤": ["通勤", "地铁", "随身"],
            "旅行": ["旅行", "出游", "便携"],
            "直播拍摄": ["直播", "拍摄", "三脚架"],
            "车载": ["车载", "汽车"],
            "家居陈列": ["家居", "展示", "摆件"],
        },
    }

    def __init__(self, config: Optional[dict] = None):
        cfg = config or {}
        self.config = DesignInspirationConfig(
            search_keywords=cfg.get("search_keywords", self.DEFAULT_CONFIG["search_keywords"]),
            topic_keywords=cfg.get("topic_keywords", self.DEFAULT_CONFIG["topic_keywords"]),
            max_results=cfg.get("max_results", self.DEFAULT_CONFIG["max_results"]),
            top_n=cfg.get("top_n", self.DEFAULT_CONFIG["top_n"]),
            detail_level=cfg.get("detail_level", self.DEFAULT_CONFIG["detail_level"]),
            output_format=cfg.get("output_format", self.DEFAULT_CONFIG["output_format"]),
        )
        self.trends: list[TrendItem] = []
        self.errors: list[dict] = []
        self.design_elements = {key: [] for key in self.ELEMENT_KEYWORDS}
        self.risk_warnings: list[str] = []
        self.next_week_suggestions: list[str] = []
        self.opportunity_points: list[str] = []
        self.macro_observations: list[str] = []
        self.daily_summary = ""
        self.focus_keyword = "设计灵感"

    def _is_out_of_scope_keyword(self, keyword: str) -> bool:
        text = (keyword or "").lower()
        content_hits = sum(1 for term in self.OUT_OF_SCOPE_TERMS if term in text)
        design_hits = sum(1 for term in self.DESIGN_SCOPE_TERMS if term in text)
        return content_hits >= 2 and design_hits == 0

    def _extract_focus_terms(self) -> list[str]:
        text = (self.focus_keyword or "").lower().strip()
        terms: list[str] = []
        ascii_terms = re.findall(r"[a-z0-9]+", text)
        chinese_chunks = re.findall(r"[\u4e00-\u9fff]+", text)

        for term in ascii_terms:
            if len(term) >= 2:
                terms.append(term)

        for chunk in chinese_chunks:
            if len(chunk) >= 2:
                terms.append(chunk)
            for size in (2, 3):
                if len(chunk) < size:
                    continue
                for idx in range(len(chunk) - size + 1):
                    terms.append(chunk[idx:idx + size])

        seen: set[str] = set()
        unique_terms: list[str] = []
        for term in terms:
            if term in seen:
                continue
            seen.add(term)
            unique_terms.append(term)
        return unique_terms

    def _score_focus_relevance(self, item: dict) -> int:
        text = f"{item.get('title', '')} {item.get('description', '')}".lower()
        normalized_keyword = self.focus_keyword.lower().strip()
        score = 0

        if normalized_keyword and normalized_keyword in text:
            score += 10

        for term in self._extract_focus_terms():
            if term not in text:
                continue
            if len(term) >= 4:
                score += 4
            elif len(term) == 3:
                score += 3
            else:
                score += 2

        score += int(item.get("relevance_score", 0))
        return score

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

    def _extract_source_name(self, url: str) -> str:
        if not url:
            return "未知来源"
        hostname = urlparse(url).netloc.lower()
        if "sohu.com" in hostname:
            return "搜狐"
        if "toutiao.com" in hostname:
            return "今日头条"
        if "xiaohongshu.com" in hostname:
            return "小红书"
        if "weibo.com" in hostname:
            return "微博"
        if "zhihu.com" in hostname:
            return "知乎"
        if "bilibili.com" in hostname:
            return "B站"
        if "jd.com" in hostname:
            return "京东"
        if "taobao.com" in hostname or "tmall.com" in hostname:
            return "淘宝"
        if "1688.com" in hostname:
            return "1688"
        if "douyin.com" in hostname:
            return "抖音"
        if not hostname:
            return "未知来源"
        return hostname.split(".")[0]

    def _match_keywords(self, text: str) -> list[str]:
        matches = []
        for keyword in self.config.search_keywords + self.config.topic_keywords:
            if keyword.lower() in text.lower():
                matches.append(keyword)
        return matches[:8]

    def parse_search_results(self, search_results: list) -> list[dict]:
        parsed = []
        for item in search_results:
            title = item.get("title", "")
            url = item.get("url", item.get("link", ""))
            desc = item.get("description", item.get("content", ""))
            parsed.append({
                "title": title.strip(),
                "url": url,
                "description": desc.strip(),
                "timestamp": item.get("time", item.get("created_at", "")),
            })
        return parsed

    def _extract_design_elements(self, texts: list[str]) -> None:
        combined = " ".join(texts).lower()
        for bucket, options in self.ELEMENT_KEYWORDS.items():
            found = []
            for label, keywords in options.items():
                if any(keyword.lower() in combined for keyword in keywords):
                    found.append(label)
            self.design_elements[bucket] = found[:6]

    def _build_business_signal(self, category: str, matched_keywords: list[str], source_name: str) -> str:
        if category == "产品测评":
            return f"{source_name} 侧重性能对比，说明用户正在从单一颜值诉求转向参数和体验并重。"
        if category == "新品速递":
            return f"{source_name} 出现新品信号，说明市场仍在用新结构/新卖点拉动关注。"
        if category == "设计趋势":
            return f"{source_name} 的内容更偏审美表达，可直接转译为配色、材质和视觉风格方向。"
        if matched_keywords:
            return f"关键词命中 {', '.join(matched_keywords[:3])}，表明内容与当前选题相关度较高。"
        return f"{source_name} 提供了与 {self.focus_keyword} 相关的外围趋势线索。"

    def _build_design_takeaway(self, title: str, summary: str) -> str:
        text = f"{title} {summary}".lower()
        signals = []
        if any(term in text for term in ["金属", "铝", "喷砂"]):
            signals.append("硬质材料感增强，适合做更强的品质感表达")
        if any(term in text for term in ["便携", "mini", "轻便"]):
            signals.append("便携诉求明显，结构上应优先考虑轻量和收纳")
        if any(term in text for term in ["磁吸", "快拆"]):
            signals.append("快装快拆是高频卖点，可延展为磁吸和模块化方向")
        if any(term in text for term in ["米", "奶油", "白", "透明"]):
            signals.append("浅色与通透感审美仍有市场，适合礼品化和家居化表达")
        if not signals:
            signals.append("建议从用户场景和风格叙事切入，而不是只复刻竞品外观")
        return "；".join(signals[:2]) + "。"

    def _build_recommended_action(self, category: str) -> str:
        if category == "产品测评":
            return "把高频被提及的结构点整理成竞品拆解表，再决定哪些值得进入打样。"
        if category == "新品速递":
            return "跟进新品首发页面和评论区，验证卖点是否真正被用户认可。"
        if category == "设计趋势":
            return "把高频配色和材质组合做成 2-3 组视觉板，用于下一轮方案评审。"
        return "保留为弱信号观察项，等待更多来源交叉验证。"

    def _generate_daily_summary(self) -> str:
        if not self.trends:
            return "今日暂无相关热点资讯。"

        categories = Counter(trend.category for trend in self.trends)
        category_summary = "、".join(f"{name}{count}条" for name, count in categories.most_common(4))
        top_topics = [trend.topic for trend in self.trends[:2]]
        top_color = self.design_elements["colors"][0] if self.design_elements["colors"] else "综合色"
        top_structure = self.design_elements["structures"][0] if self.design_elements["structures"] else "基础支撑结构"
        return (
            f"围绕“{self.focus_keyword}”共收录 {len(self.trends)} 条相关内容，"
            f"以 {category_summary} 为主。当前热点从 {top_topics[0]} 等内容发散，"
            f"视觉上偏向 {top_color}，结构上偏向 {top_structure}。"
        )

    def _generate_risk_warnings(self) -> None:
        warnings = []
        sources = Counter(trend.source_name for trend in self.trends)
        if sources:
            top_source, top_count = sources.most_common(1)[0]
            if top_count / max(len(self.trends), 1) >= 0.6:
                warnings.append(f"来源集中风险：当前样本中过度依赖 {top_source}，需要再补 2-3 个不同平台交叉验证。")

        titles = [trend.topic for trend in self.trends]
        if len(set(titles)) <= max(1, len(titles) // 2):
            warnings.append("内容同质化风险：标题和卖点高度重复，后续选题容易陷入单一结构竞争。")

        if not self.design_elements["styles"]:
            warnings.append("风格标签不足：现有样本偏功能对比，审美和场景表达仍需补样。")

        self.risk_warnings = warnings[:3]

    def _generate_macro_observations(self) -> None:
        observations = []
        if self.design_elements["materials"]:
            observations.append(f"材质趋势偏向 {', '.join(self.design_elements['materials'][:3])}，说明用户愿意为更明确的质感买单。")
        if self.design_elements["structures"]:
            observations.append(f"结构关键词集中在 {', '.join(self.design_elements['structures'][:3])}，说明产品卖点需要直接对应使用效率。")
        if self.design_elements["scenarios"]:
            observations.append(f"应用场景高频落在 {', '.join(self.design_elements['scenarios'][:2])}，适合做更具体的场景化展示。")
        if not observations:
            observations.append("当前样本更像流量词聚合，还需要增加高质量原始案例来支撑设计判断。")
        self.macro_observations = observations[:3]

    def _generate_opportunity_points(self) -> None:
        opportunities = []
        if self.design_elements["colors"] and self.design_elements["materials"]:
            opportunities.append(
                f"可以尝试“{self.design_elements['colors'][0]} + {self.design_elements['materials'][0]}”的组合，做更适合礼品和桌搭场景的版本。"
            )
        if "磁吸" in self.design_elements["structures"] or "旋转" in self.design_elements["structures"]:
            opportunities.append("把磁吸/旋转做成可视化演示卖点，强化开箱即懂的体验差异。")
        if "通勤" in self.design_elements["scenarios"] or "旅行" in self.design_elements["scenarios"]:
            opportunities.append("针对通勤和旅行场景拆成轻便款与稳固款两条产品线，减少单品承担过多诉求。")
        opportunities.append("为下轮调研补充评论区与短视频内容，验证“被讨论”是否等于“被购买”。")
        self.opportunity_points = opportunities[:3]

    def _generate_next_week_suggestions(self) -> None:
        suggestions = [
            "补抓至少 2 个非资讯聚合来源，优先小红书/B站/电商详情页，验证风格与功能是否一致。",
            "把本周高频结构点做成竞品矩阵，标记“可直接采用 / 可改良 / 应避免同质化”三档。",
            "围绕最强场景词做 1 版视觉 moodboard 和 1 版功能草图，压缩从趋势到方案的距离。",
        ]
        self.next_week_suggestions = suggestions

    def run(self, search_results: Optional[list] = None, keyword: Optional[str] = None) -> dict:
        self.focus_keyword = keyword or self.focus_keyword

        if self._is_out_of_scope_keyword(self.focus_keyword):
            self.errors.append({
                "error": "OutOfScopeKeyword",
                "message": f"关键词“{self.focus_keyword}”更像社媒/内容运营选题，不适合当前设计灵感 skill。请改用专门的内容选题或账号分析 skill。",
                "timestamp": datetime.now().isoformat(),
            })
            return self.generate_report()

        if search_results is None:
            self.errors.append({
                "error": "No search results provided",
                "message": "需要提供搜索结果作为输入",
                "timestamp": datetime.now().isoformat(),
            })
            return self.generate_report()

        parsed_results = self.parse_search_results(search_results)
        relevant_results = []
        for item in parsed_results:
            relevance_score = self._score_focus_relevance(item)
            if relevance_score >= 4:
                item["focus_relevance_score"] = relevance_score
                relevant_results.append(item)

        if not relevant_results:
            self.errors.append({
                "error": "NoRelevantRealtimeResults",
                "message": f"没有检索到与“{self.focus_keyword}”足够相关的实时结果。本次不会使用本地样本或 mock 数据拼接报告。",
                "timestamp": datetime.now().isoformat(),
            })
            return self.generate_report()

        for item in relevant_results[:self.config.max_results]:
            title = item.get("title", "未知主题")
            summary = item.get("description", "")[:220]
            url = item.get("url", "")
            source_name = self._extract_source_name(url)
            category = self._categorize_item(title)
            matched_keywords = self._match_keywords(f"{title} {summary}")
            self.trends.append(
                TrendItem(
                    topic=title,
                    summary=summary,
                    source_urls=[url] if url else [],
                    source_name=source_name,
                    heat_level="high" if any(keyword in title for keyword in ["爆款", "热门", "新品"]) else "medium",
                    category=category,
                    matched_keywords=matched_keywords,
                    design_takeaway=self._build_design_takeaway(title, summary),
                    business_signal=self._build_business_signal(category, matched_keywords, source_name),
                    recommended_action=self._build_recommended_action(category),
                )
            )

        texts = [f"{trend.topic} {trend.summary}" for trend in self.trends]
        self._extract_design_elements(texts)
        self.daily_summary = self._generate_daily_summary()
        self._generate_risk_warnings()
        self._generate_macro_observations()
        self._generate_opportunity_points()
        self._generate_next_week_suggestions()
        return self.generate_report()

    def generate_report(self) -> dict:
        categories = Counter(trend.category for trend in self.trends)
        sources = Counter(trend.source_name for trend in self.trends)
        report = {
            "status": "success" if self.trends else "no_data",
            "report_type": "daily",
            "detail_level": self.config.detail_level,
            "focus_keyword": self.focus_keyword,
            "summary": {
                "total_trends": len(self.trends),
                "categories": dict(categories),
                "source_breakdown": dict(sources),
                "error_count": len(self.errors),
            },
            "executive_summary": self.daily_summary,
            "macro_observations": self.macro_observations,
            "trend_cards": [
                {
                    "topic": trend.topic,
                    "summary": trend.summary,
                    "category": trend.category,
                    "source_name": trend.source_name,
                    "source_urls": trend.source_urls,
                    "heat_level": trend.heat_level,
                    "matched_keywords": trend.matched_keywords,
                    "business_signal": trend.business_signal,
                    "design_takeaway": trend.design_takeaway,
                    "recommended_action": trend.recommended_action,
                }
                for trend in self.trends[:self.config.top_n]
            ],
            "design_elements": self.design_elements,
            "opportunity_points": self.opportunity_points,
            "risk_warnings": self.risk_warnings,
            "next_week_suggestions": self.next_week_suggestions,
            "errors": self.errors,
            "timestamp": datetime.now().isoformat(),
        }
        return report

    def format_for_feishu(self) -> str:
        header = f"# 设计灵感详细日报｜{self.focus_keyword}"
        if not self.trends:
            reason = self.errors[-1]["message"] if self.errors else "暂无可用样本，建议先补充搜索结果后再生成日报。"
            return "\n".join([
                header,
                "",
                datetime.now().strftime("%Y-%m-%d %H:%M"),
                "",
                reason,
            ])

        lines = [header, "", datetime.now().strftime("%Y-%m-%d %H:%M"), "", "---", ""]
        lines.append("## 一句话结论")
        lines.append("")
        lines.append(self.daily_summary)
        lines.append("")
        lines.append("## 趋势总览")
        lines.append("")
        category_summary = "、".join(
            f"{name}{count}条" for name, count in Counter(trend.category for trend in self.trends).most_common(4)
        )
        source_summary = "、".join(
            f"{name}{count}" for name, count in Counter(trend.source_name for trend in self.trends).most_common(4)
        )
        lines.append(f"- 内容结构：{category_summary}")
        lines.append(f"- 来源结构：{source_summary}")
        for observation in self.macro_observations:
            lines.append(f"- 观察：{observation}")
        lines.append("")
        lines.append("## 设计元素清单")
        lines.append("")
        lines.append("| 维度 | 高频元素 |")
        lines.append("|------|----------|")
        lines.append(f"| 配色 | {', '.join(self.design_elements['colors']) or '-'} |")
        lines.append(f"| 材质 | {', '.join(self.design_elements['materials']) or '-'} |")
        lines.append(f"| 结构 | {', '.join(self.design_elements['structures']) or '-'} |")
        lines.append(f"| 风格 | {', '.join(self.design_elements['styles']) or '-'} |")
        lines.append(f"| 表面处理 | {', '.join(self.design_elements['finishes']) or '-'} |")
        lines.append(f"| 场景 | {', '.join(self.design_elements['scenarios']) or '-'} |")
        lines.append("")
        lines.append("## 热点拆解")
        lines.append("")
        for index, trend in enumerate(self.trends[:self.config.top_n], start=1):
            lines.append(f"### {index}. [{trend.category}] {trend.topic}")
            lines.append(f"- 来源：{trend.source_name}")
            lines.append(f"- 摘要：{trend.summary}")
            lines.append(f"- 信号：{trend.business_signal}")
            lines.append(f"- 设计启发：{trend.design_takeaway}")
            lines.append(f"- 建议动作：{trend.recommended_action}")
            if trend.matched_keywords:
                lines.append(f"- 关键词：{', '.join(trend.matched_keywords)}")
            if trend.source_urls:
                lines.append(f"- 链接：{trend.source_urls[0]}")
            lines.append("")
        if self.opportunity_points:
            lines.append("## 可转化机会")
            lines.append("")
            for item in self.opportunity_points:
                lines.append(f"- {item}")
            lines.append("")
        if self.risk_warnings:
            lines.append("## 风险提示")
            lines.append("")
            for warning in self.risk_warnings:
                lines.append(f"- {warning}")
            lines.append("")
        lines.append("## 下周动作")
        lines.append("")
        for action in self.next_week_suggestions:
            lines.append(f"- {action}")
        lines.append("")
        return "\n".join(lines)


def main():
    import argparse
    import yaml

    ap = argparse.ArgumentParser(description="拍立得与周边产品设计灵感日报")
    ap.add_argument("--config", default=None, help="配置文件路径")
    ap.add_argument("--input", default=None, help="输入 JSON 文件路径（搜索结果）")
    ap.add_argument("--out", default="output/design_inspiration_daily", help="输出文件前缀")
    ap.add_argument("--keyword", default="设计灵感", help="选题关键词")
    args = ap.parse_args()

    config = None
    if args.config:
        with open(args.config, encoding="utf-8") as f:
            config = yaml.safe_load(f)

    monitor = DesignInspirationMonitor(config=config)

    if args.input:
        with open(args.input, encoding="utf-8") as f:
            search_results = json.load(f)
        report = monitor.run(search_results=search_results, keyword=args.keyword)
    else:
        report = monitor.run(keyword=args.keyword)

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
