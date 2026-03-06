---
name: "design-inspiration-daily"
description: "拍立得与周边产品设计灵感日报。综合搜索热点资讯，自动提取设计元素（配色、材质、结构），生成适合飞书群投递的热点趋势简报。"
---

# Design Inspiration Daily Monitor Skill

拍立得与周边产品设计灵感日报，自动综合搜索热点资讯，提取设计元素，生成热点趋势简报。

## 功能特性

- **多平台搜索**：支持今日头条、搜狐等综合资讯平台
- **智能分类**：自动识别产品测评、新品速递、DIY教程、设计趋势等类别
- **设计元素提取**：自动提取配色、材质、结构等设计关键词
- **自动摘要**：生成今日要闻总结
- **飞书群投递**：格式化输出可直接投递到飞书群

## 安装

```bash
pip install pyyaml
```

## 使用方法

### 1. 准备搜索数据

将搜索结果保存为JSON文件，格式如下：

```json
[
  {
    "title": "汉印拍立得亮相CP+2026",
    "description": "国产品牌汉印携数款拍立得产品亮相...",
    "url": "https://example.com/article1"
  },
  {
    "title": "富士mini12测评 奶油风配色",
    "description": "富士mini12奶油风配色持续受热捧...",
    "url": "https://example.com/article2"
  }
]
```

### 2. 配置文件

编辑 `config/config.yaml`：

```yaml
search_keywords:
  - "拍立得"
  - "富士相机"
  - "polaroid"
  - "相机包"
  - "相框"
  - "DIY相册"

topic_keywords:
  - "设计"
  - "配色"
  - "材质"
  - "奶油风"
  - "多巴胺"
  - "美拉德"
  - "测评"
  - "新品"

max_results: 20
```

### 3. 运行日报

```bash
cd design-inspiration-daily-skill
PYTHONPATH=src python src/trend.py --config config/config.yaml --input data/search_results.json --out output/日报
```

### 4. 输出

- `output/日报.json` - JSON格式完整数据
- `output/日报.md` - Markdown格式报告

## 输出字段说明

| 字段 | 说明 |
|------|------|
| topic | 热点标题 |
| summary | 摘要描述 |
| category | 类别（产品测评/新品速递/DIY教程/设计趋势）|
| source_urls | 来源链接 |
| heat_level | 热度等级 |

## 设计元素

日报会自动提取以下设计元素：

| 类别 | 关键词 |
|------|--------|
| 配色 | 粉、绿、白、红、黄等 |
| 材质 | 帆布、皮革、毛毡、塑料等 |
| 结构 | 拉链、纽扣、折叠、mini等 |

## 项目结构

```
design-inspiration-daily-skill/
├── SKILL.md                 # 本文件
├── config/
│   └── config.yaml         # 配置文件
├── src/
│   └── trend.py            # 主程序
├── data/
│   └── search_results.json # 搜索数据示例
├── output/
│   └── .gitkeep            # 输出目录
└── README.md               # 使用说明
```

## 注意事项

1. 搜索数据需要通过WebSearch或其他方式获取
2. 可结合小红书MCP获取真实热点数据
3. 建议设置为每日定时任务自动执行
