---
name: "design-inspiration-daily"
description: "拍立得与周边产品设计灵感日报。输入关键词，自动搜索热点资讯，提取设计元素（配色、材质、结构），生成适合飞书群投递的热点趋势简报。"
---

# Design Inspiration Daily Monitor Skill

拍立得与周边产品设计灵感日报，输入关键词自动搜索热点资讯，提取设计元素，生成热点趋势简报。

## 功能特性

- **自动搜索**：输入关键词自动抓取全网热点资讯
- **智能分类**：自动识别产品测评、新品速递、DIY教程、设计趋势等类别
- **设计元素提取**：自动提取配色、材质、结构等设计关键词
- **自动摘要**：生成今日要闻总结
- **一键生成**：一条命令完成搜索+分析+报告生成

## 安装

```bash
pip install httpx pyyaml
```

## 使用方法

### 方式一：一键生成（推荐）

```bash
cd design-inspiration-daily-skill
PYTHONPATH=src python src/main.py --keyword "手机支架"
```

参数说明：
- `--keyword, -k`: 搜索关键词（必填）
- `--config, -c`: 配置文件路径（默认 config/config.yaml）
- `--max-results, -n`: 最大搜索结果数（默认20）
- `--out, -o`: 输出文件前缀（默认 output/日报）

### 方式二：分步执行

```bash
# Step 1: 搜索资讯
PYTHONPATH=src python src/fetch_search_results.py --keyword "手机支架" --out data/results.json

# Step 2: 生成日报
PYTHONPATH=src python src/trend.py --config config/config.yaml --input data/results.json --out output/日报
```

## 输出

- `output/日报.json` - JSON格式完整数据
- `output/日报.md` - Markdown格式报告

### 输出示例

```
# 拍立得与周边产品设计灵感日报

2026-03-06 20:00

---

## 📋 今日要闻

**热点话题**：今日共收录10条热点...

| 类别 | 热门元素 |
|------|----------|
| 配色 | 粉, 白, 绿 |
| 材质 | 铝合金, 塑料 |
| 结构 | 折叠, 便携 |

---

## 🔥 热点聚焦 TOP5

| 序号 | 类别 | 标题 | 来源 |
|------|------|------|------|
| 1 | 产品测评 | xxx | [链接](url) |
...
```

## 配置文件

编辑 `config/config.yaml`：

```yaml
search_keywords:
  - "手机支架"
  - "支架"

topic_keywords:
  - "设计"
  - "配色"
  - "材质"
  - "测评"
  - "新品"
  - "推荐"

max_results: 20
```

## 项目结构

```
design-inspiration-daily-skill/
├── SKILL.md                      # 本文件
├── config/
│   └── config.yaml               # 配置文件
├── src/
│   ├── main.py                   # 主入口（一键生成）
│   ├── fetch_search_results.py   # 搜索模块
│   └── trend.py                  # 分析报告模块
├── data/
│   └── .gitkeep
├── output/
│   └── .gitkeep
└── README.md
```

## 注意事项

1. Google搜索可能被限制，建议配合代理使用
2. 可替换搜索源为其他API（如百度搜索API）
3. 建议设置为每日定时任务自动执行
