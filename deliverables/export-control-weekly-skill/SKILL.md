---
name: "export-control-weekly"
description: "国际出口管制周报监控。监控美国 OFAC、BIS 等官方出口管制动态，支持按品类关键词过滤，默认生成详细版周报并可投递到飞书，适合供应链合规团队使用。"
---

# Export Control Weekly Monitor Skill

国际出口管制周报监控工具，自动抓取美国 OFAC、BIS 等官方出口管制动态，按品类关键词过滤生成默认详细版周报。

## 功能特性

- **多数据源监控**：美国OFAC、BIS、中国商务部、中国海关、新加坡海关等
- **智能过滤**：按品类关键词（拍立得、相机包、相框等）过滤，只显示相关内容
- **优先级分类**：P0（出口管制+品类）、P1（纯出口管制）
- **自动生成周报**：支持 JSON 和 Markdown 格式输出
- **详细版默认输出**：默认生成详细版，不做简版压缩，除非用户明确要求
- **飞书群投递**：格式化输出可直接投递到飞书群

## 安装

```bash
pip install httpx pyyaml
```

## 使用方法

### 1. 配置文件

编辑 `config/config.yaml`：

```yaml
source_urls:
  US_BIS: "https://www.bis.gov/"
  US_BIS_EAR: "https://www.bis.gov/regulations/ear"
  OFAC: "https://ofac.treasury.gov/"
  CN_MOFCOM: "https://www.mofcom.gov.cn/fzlm/mrgx/index.html"

category_keywords:
  - "拍立得"
  - "相机包"
  - "相框"
  - "polaroid"
  - "instant camera"

product_keywords:
  - "相机"
  - "胶片"
  - "相册"

topic_keywords:
  - "出口管制"
  - "制裁"
  - "entity list"
  - "OFAC"
  - "BIS"

days_lookback: 30
detail_level: "detailed"
max_alerts: 12
```

### 2. 运行周报

```bash
cd export-control-weekly-skill
PYTHONPATH=src python src/monitor.py --config config/config.yaml --out output/周报
```

默认行为：
- 输出 `detail_level=detailed`
- 每条命中附带命中关键词、业务影响、建议动作、监控备注
- 报告包含抓取失败告警，避免“静默失败”

### 3. 输出

- `output/周报.json` - JSON格式完整数据
- `output/周报.md` - Markdown格式报告

## 详细版输出结构

默认输出以下结构：

1. 管理层摘要
2. 命中概览（P0/P1/P2、命中类型、抓取异常）
3. 重点事项逐条拆解
4. 每条事项的命中关键词、业务影响、建议动作、监控备注
5. 抓取失败告警

## 输出字段说明

| 字段 | 说明 |
|------|------|
| match_type | 匹配类型：出口管制+品类 / 纯出口管制 |
| priority | 优先级：P0 / P1 |
| country | 国家/地区 |
| category | 类别（OFAC制裁、出口管制等）|
| title | 标题 |
| summary | 结论性描述 |
| matched_topic_keywords | 命中的出口管制主题词 |
| matched_product_keywords | 命中的品类/产品关键词 |
| business_impacts | 业务影响判断 |
| recommended_actions | 建议动作 |
| source_url | 来源链接 |

## 数据源

| 数据源 | 说明 |
|--------|------|
| OFAC | 美国财政部海外资产控制办公室制裁名单 |
| BIS | 美国商务部工业与安全局出口管制 |
| 中国商务部 | 中国贸易政策 |
| 中国海关 | 海关动态 |
| 新加坡海关 | 新加坡进出口管制 |

## 项目结构

```
export-control-weekly-skill/
├── SKILL.md                 # 本文件
├── config/
│   └── config.yaml         # 配置文件
├── src/
│   └── monitor.py          # 主程序
├── output/
│   └── .gitkeep            # 输出目录
└── README.md               # 使用说明
```

## 注意事项

1. 默认输出是详细版，若只需要简版，需在调用时明确说明
2. 部分政府网站可能存在反爬机制，建议添加代理
3. 中国海关数据源可能返回 412 错误，需排查网络
4. 建议设置为每周定时任务自动执行
