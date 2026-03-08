---
name: china-trade-policy-weekly
description: "Collect and analyze China's foreign trade policies, international trade events, and policy-driven trade changes, generating comprehensive weekly reports. Use when: (1) User wants to track China's trade policy updates, (2) User needs analysis of international trade events impact, (3) User mentions '贸易政策', '贸易周报', '国际贸易动态', '外贸政策', '贸易壁垒', (4) User wants to understand trade regulation changes. NOT for: domestic trade policies only, non-China related trade, or general economic news without trade focus."
---

# China Trade Policy Weekly - 中国对外贸易政策周报

## Overview

This skill automates the collection and analysis of China's foreign trade policies, international trade events, and policy-driven changes, generating comprehensive weekly reports for trade professionals and businesses.

## Core Coverage Areas

### 1. 政策法规 (Policies & Regulations)
- **关税政策**: 关税调整、税率变化、减免政策
- **贸易协定**: 自由贸易协定(FTA)、区域贸易协定(RCEP等)
- **进出口管制**: 许可证管理、配额制度、禁限令
- **检验检疫**: 海关检验、质量标准、认证要求
- **外汇管理**: 结售汇政策、跨境支付规定

### 2. 时事动态 (Current Events)
- **贸易摩擦**: 反倾销、反补贴、贸易救济措施
- **贸易谈判**: 双边/多边谈判进展、协议签署
- **国际组织**: WTO动态、G20贸易议题、APEC成果
- **地缘政治**: 贸易制裁、出口管制、技术封锁

### 3. 行业影响 (Industry Impact)
- **重点行业**: 电子信息、纺织服装、机械设备、农产品
- **新兴领域**: 跨境电商、数字贸易、绿色贸易
- **供应链**: 产业链转移、供应链安全、多元化布局

### 4. 数据统计 (Trade Statistics)
- **进出口数据**: 月度/季度贸易数据
- **国别分析**: 主要贸易伙伴数据
- **商品结构**: 重点商品进出口情况

## Core Workflow

### Step 1: Define Report Scope

Ask user to clarify:
1. **时间范围**: 本周/上周/特定时间段
2. **关注重点**: 
   - 政策法规更新
   - 贸易摩擦动态
   - 行业影响分析
   - 全部内容
3. **目标市场**: 
   - 全球视角
   - 特定区域（如欧美、东盟、RCEP国家）
   - 特定国家
4. **行业聚焦**: 
   - 全行业
   - 特定行业（如电子、纺织、机械）
5. **报告深度**: 
   - 快速概览（mini）
   - 深度分析（pro）

### Step 2: Multi-Source Data Collection

Execute parallel searches using Tavily API:

#### 2.1 政策法规搜索
```bash
# 中国贸易政策更新
./scripts/search.sh '{
  "query": "中国对外贸易政策 最新政策 关税调整 进出口管理",
  "max_results": 10,
  "search_depth": "advanced",
  "time_range": "week",
  "include_domains": ["mofcom.gov.cn", "customs.gov.cn", "gov.cn"]
}'
```

#### 2.2 贸易时事搜索
```bash
# 国际贸易动态
./scripts/search.sh '{
  "query": "中国国际贸易 贸易摩擦 贸易谈判 最新动态",
  "max_results": 10,
  "search_depth": "advanced",
  "time_range": "week"
}'
```

#### 2.3 贸易数据搜索
```bash
# 贸易统计数据
./scripts/search.sh '{
  "query": "中国进出口数据 贸易统计 最新数据",
  "max_results": 8,
  "search_depth": "advanced",
  "time_range": "month"
}'
```

#### 2.4 行业影响搜索
```bash
# 行业贸易影响
./scripts/search.sh '{
  "query": "中国贸易政策影响 行业分析 供应链变化",
  "max_results": 8,
  "search_depth": "advanced",
  "time_range": "week"
}'
```

### Step 3: Deep Research (Optional - Pro Mode)

For comprehensive analysis, use research skill:

```bash
./scripts/research.sh '{
  "input": "China trade policy changes impact analysis weekly report international trade regulations",
  "model": "pro"
}'
```

### Step 4: Content Analysis & Categorization

Analyze and categorize collected information:

#### 政策分类
- **新出台政策**: 近期发布的新政策
- **政策调整**: 现有政策的修改和完善
- **政策解读**: 官方解读和专家分析
- **实施细则**: 具体执行措施

#### 影响评估
- **正面影响**: 促进贸易便利化、降低成本
- **负面影响**: 增加贸易壁垒、提高合规成本
- **中性调整**: 程序性变化、管理优化

#### 紧急程度
- 🔴 **高**: 立即生效、重大影响
- 🟡 **中**: 近期生效、中等影响
- 🟢 **低**: 长期规划、影响有限

### Step 5: Generate Weekly Report

Create a structured markdown report:

## Report Structure

```markdown
# 中国对外贸易政策周报
**报告期**: YYYY年MM月DD日 - MM月DD日（第X周）

## 📋 本周概要

### 核心要点
- 要点1: [政策/事件] - [影响]
- 要点2: [政策/事件] - [影响]
- 要点3: [政策/事件] - [影响]

### 数据快览
- 进出口总额: XX万亿元（同比±X%）
- 出口: XX万亿元（同比±X%）
- 进口: XX万亿元（同比±X%）
- 贸易顺差: XX亿元

## 📜 政策法规动态

### 1. 新出台政策

#### [政策名称]
- **发布机构**: [机构名称]
- **发布日期**: YYYY-MM-DD
- **生效日期**: YYYY-MM-DD
- **政策要点**: 
  - 要点1
  - 要点2
- **影响范围**: [行业/产品/国家]
- **紧急程度**: 🔴高/🟡中/🟢低
- **参考链接**: [URL]

### 2. 政策调整

#### [政策名称]
- **调整内容**: [具体调整]
- **调整原因**: [原因说明]
- **影响分析**: [影响评估]
- **应对建议**: [建议措施]

### 3. 政策解读

#### [解读主题]
- **解读要点**: [核心内容]
- **专家观点**: [专家分析]
- **企业应对**: [应对策略]

## 🌍 国际贸易动态

### 1. 贸易摩擦

#### [摩擦事件]
- **涉及国家**: [国家/地区]
- **涉案产品**: [产品名称]
- **摩擦类型**: 反倾销/反补贴/保障措施
- **最新进展**: [进展描述]
- **影响评估**: [影响分析]
- **应对措施**: [建议措施]

### 2. 贸易谈判

#### [谈判名称]
- **参与方**: [国家/组织]
- **谈判议题**: [议题内容]
- **最新进展**: [进展情况]
- **预期成果**: [预期结果]

### 3. 国际组织动态

#### [组织名称] - [议题]
- **会议时间**: YYYY-MM-DD
- **主要议题**: [议题列表]
- **重要成果**: [成果描述]
- **对中国影响**: [影响分析]

## 📊 贸易数据分析

### 1. 总体情况
- **进出口总额**: XX万亿元
  - 同比: ±X%
  - 环比: ±X%
- **出口**: XX万亿元（同比±X%）
- **进口**: XX万亿元（同比±X%）
- **贸易顺差**: XX亿元

### 2. 国别/地区分析

| 国家/地区 | 进出口额 | 同比 | 主要产品 | 趋势 |
|-----------|----------|------|----------|------|
| 美国 | XX亿元 | ±X% | [产品] | ↑↓→ |
| 欧盟 | XX亿元 | ±X% | [产品] | ↑↓→ |
| 东盟 | XX亿元 | ±X% | [产品] | ↑↓→ |

### 3. 重点商品分析

| 商品类别 | 出口额 | 进口额 | 同比变化 | 政策影响 |
|----------|--------|--------|----------|----------|
| 电子信息 | XX亿元 | XX亿元 | ±X% | [影响] |
| 纺织服装 | XX亿元 | XX亿元 | ±X% | [影响] |

## 🏭 行业影响分析

### 1. [行业名称]

#### 政策影响
- **利好政策**: [政策描述]
- **限制政策**: [政策描述]
- **合规要求**: [要求说明]

#### 市场动态
- **出口情况**: [情况描述]
- **进口情况**: [情况描述]
- **价格走势**: [走势分析]

#### 应对建议
- 建议1: [具体措施]
- 建议2: [具体措施]

### 2. [行业名称]
...

## ⚠️ 风险提示

### 高风险事项
1. **[风险事项]**: [风险描述]
   - 影响程度: ⭐⭐⭐⭐⭐
   - 发生概率: 高/中/低
   - 应对策略: [策略建议]

### 中风险事项
1. **[风险事项]**: [风险描述]

## 💡 专家观点

### [专家姓名] - [机构]
- **观点**: [观点内容]
- **分析**: [分析说明]
- **建议**: [建议措施]

## 📅 下周关注重点

### 政策预期
1. [预期政策1]
2. [预期政策2]

### 重要事件
1. [事件1] - [时间] - [预期影响]
2. [事件2] - [时间] - [预期影响]

### 数据发布
1. [数据名称] - [发布时间]
2. [数据名称] - [发布时间]

## 🔗 参考资源

### 官方网站
- 商务部: http://www.mofcom.gov.cn/
- 海关总署: http://www.customs.gov.cn/
- WTO: https://www.wto.org/

### 政策文件
- [文件名称](URL)
- [文件名称](URL)

### 新闻报道
- [新闻标题](URL)
- [新闻标题](URL)

## 📝 应对建议

### 短期措施
1. [具体建议]
2. [具体建议]

### 长期策略
1. [具体建议]
2. [具体建议]

---
**数据来源**: Tavily Search API, 官方网站
**生成时间**: YYYY-MM-DD HH:MM:SS
**报告周期**: 第X周
```

## Advanced Features

### Custom Search Queries

#### 特定国家/地区
```bash
# 中美贸易
./scripts/search.sh '{
  "query": "中美贸易 贸易战 关税 最新进展",
  "max_results": 10,
  "search_depth": "advanced",
  "time_range": "week"
}'
```

#### 特定行业
```bash
# 电子信息行业
./scripts/search.sh '{
  "query": "电子信息产品 进出口政策 贸易壁垒",
  "max_results": 10,
  "search_depth": "advanced",
  "time_range": "week"
}'
```

#### 特定政策类型
```bash
# 关税政策
./scripts/search.sh '{
  "query": "中国关税政策调整 进出口关税税率",
  "max_results": 10,
  "search_depth": "advanced",
  "time_range": "month"
}'
```

### Regional Focus

#### RCEP区域
```bash
./scripts/search.sh '{
  "query": "RCEP 区域全面经济伙伴关系协定 贸易便利化",
  "max_results": 10,
  "search_depth": "advanced"
}'
```

#### 一带一路
```bash
./scripts/search.sh '{
  "query": "一带一路 贸易合作 投资便利化",
  "max_results": 10,
  "search_depth": "advanced"
}'
```

## Output Options

### 1. 完整周报 (默认)
- 全面的政策分析
- 详细的行业影响
- 数据统计和趋势
- 风险提示和建议

### 2. 简要报告
- 核心要点总结
- 重要政策列表
- 关键数据展示

### 3. 专题报告
- 针对特定主题深度分析
- 如：中美贸易摩擦专题
- 如：RCEP实施进展专题

## Best Practices

### 搜索策略
1. **多维度搜索**: 政策、时事、数据、行业并行搜索
2. **权威来源**: 优先搜索官方网站和权威媒体
3. **时效性**: 使用 time_range 参数获取最新信息
4. **深度分析**: 使用 search_depth: "advanced" 提高质量

### 内容质量
1. **准确性**: 核实政策信息的准确性
2. **完整性**: 涵盖政策要点和影响分析
3. **时效性**: 关注最新动态和变化
4. **实用性**: 提供可操作的应对建议

### 报告生成
1. **结构清晰**: 按类别组织内容
2. **重点突出**: 标注紧急程度和影响级别
3. **数据支撑**: 用数据说话，增强说服力
4. **建议具体**: 提供明确可执行的应对措施

## Integration Points

- **Tavily Search API**: 主要数据收集
- **Tavily Research API**: 深度分析（pro模式）
- **WebFetch**: 提取政策文件详细内容
- **Feishu/Lark**: 可选保存报告到多维表格

## Example Usage

**用户**: "帮我生成本周的中国对外贸易政策周报"

**助手操作**:
1. 执行 4-5 个并行搜索查询
2. 收集政策法规、贸易动态、统计数据
3. 分析政策影响和行业变化
4. 生成结构化周报
5. 保存为: `贸易政策周报_YYYY年第X周.md`
6. 向用户提供摘要

**用户**: "我想了解最近中美贸易摩擦的最新进展"

**助手操作**:
1. 搜索中美贸易相关新闻和政策
2. 分析最新进展和影响
3. 生成专题报告
4. 提供应对建议

## Troubleshooting

### 常见问题

1. **信息过时**
   - 使用 time_range: "week" 或 "month"
   - 添加年份到搜索词
   - 搜索最新新闻和公告

2. **信息不足**
   - 扩大搜索范围
   - 增加搜索关键词
   - 使用多个相关查询

3. **信息不准确**
   - 交叉验证多个来源
   - 优先参考官方网站
   - 标注信息来源

## Configuration

### 环境变量
```bash
# 必需
TAVILY_API_KEY=tvly-your-api-key

# 可选
TRADE_REPORT_OUTPUT_DIR=./trade-reports
DEFAULT_SEARCH_DEPTH=advanced
DEFAULT_MAX_RESULTS=10
```

### 自定义选项
用户可自定义：
- 输出目录
- 报告格式
- 搜索参数
- 关注重点

---

**Note**: 本 skill 结合了网络搜索、政策分析和数据统计，为中国对外贸易从业者提供及时、准确、实用的政策周报。学习自 research 和 search skill 的最佳实践，并针对贸易政策领域进行了专业化优化。
