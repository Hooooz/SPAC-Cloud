---
name: "design-inspiration-daily"
description: "产品/视觉/包装/周边方向的设计灵感日报。输入设计相关关键词，实时搜索热点资讯，提取设计元素（配色、材质、结构、风格、场景），默认生成详细版趋势日报并可直接投递到飞书。只适用于设计灵感类主题；如果关键词明显是社媒运营、账号分析、文案策划等内容运营题目，必须明确拒绝套用本 skill。"
---

# Design Inspiration Daily Monitor Skill

设计灵感日报，输入设计相关关键词自动实时搜索热点资讯，提取设计元素，生成默认详细版热点趋势简报。

## 功能特性

- **自动搜索**：输入关键词自动抓取全网热点资讯
- **智能分类**：自动识别产品测评、新品速递、DIY教程、设计趋势等类别
- **设计元素提取**：自动提取配色、材质、结构等设计关键词
- **自动摘要**：生成今日要闻总结
- **详细版默认输出**：默认输出详细版，不做简版压缩，除非用户明确要求
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

默认行为：
- 输出 `detail_level=detailed`
- 生成 8 条以内热点拆解卡片
- 附带宏观观察、设计元素清单、机会点、风险提示、下周动作

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

## 详细版输出结构

每次默认输出以下结构：

1. 一句话结论 / executive summary
2. 趋势总览（类别分布、来源分布、宏观观察）
3. 设计元素清单（配色、材质、结构、风格、表面处理、场景）
4. 热点拆解卡片（来源、摘要、信号、设计启发、建议动作、链接）
5. 可转化机会
6. 风险提示
7. 下周动作

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
top_n: 8
detail_level: "detailed"
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

1. 默认输出是详细版，若只需要简版，需在调用时明确说明
2. 必须优先使用实时搜索结果，不允许拿本地 mock 样本直接拼接正式报告
3. 如果实时搜索无结果，应明确返回失败原因，而不是硬凑内容
4. 对社媒账号、内容运营、文案选题等非设计类关键词，应拒绝输出并提示改用合适 skill
5. 建议设置为每日定时任务自动执行
