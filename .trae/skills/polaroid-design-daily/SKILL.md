---
name: polaroid-design-daily
description: "Collect design elements and inspiration for Polaroid peripheral products (camera bags, photo frames, albums, etc.) and generate daily design reports. Use when: (1) User wants design inspiration for Polaroid products, (2) User asks for design trend analysis, (3) User mentions '拍立得设计', '设计日报', '设计灵感收集', '周边产品设计', (4) User wants to research design elements for instant camera accessories. NOT for: general photography topics, camera technical specs, or unrelated product categories."
---

# Polaroid Design Daily - Design Elements Collection & Report Generation

## Overview

This skill automates the collection of design elements, trends, and inspiration for Polaroid/instant camera peripheral products, generating comprehensive daily design reports.

## Target Product Categories

- **Camera Bags & Cases**: Protective cases, camera bags, straps
- **Photo Display Solutions**: Photo frames, display stands, photo walls
- **Photo Albums & Storage**: Albums, storage boxes, organizers
- **Accessories**: Film holders, lens accessories, decorative items
- **DIY & Customization**: Stickers, templates, creative tools

## Core Workflow

### Step 1: Define Research Scope

Ask user to clarify:
1. **Product focus**: Which category? (or all categories)
2. **Research depth**: Quick overview (mini) or comprehensive analysis (pro)
3. **Time range**: Recent trends (week/month) or broader analysis
4. **Target market**: Global or specific regions (e.g., China, Japan, Europe)
5. **Design aspects**: 
   - Color palettes & materials
   - Form factors & ergonomics
   - Functional features
   - Aesthetic styles (vintage, modern, minimalist, etc.)

### Step 2: Multi-Source Data Collection

Execute parallel searches using Tavily API:

#### 2.1 Design Trend Analysis
```bash
# Search for current design trends
./scripts/search.sh '{
  "query": "Polaroid instant camera accessories design trends 2025",
  "max_results": 10,
  "search_depth": "advanced",
  "time_range": "month"
}'
```

#### 2.2 Product Innovation Research
```bash
# Search for innovative products
./scripts/search.sh '{
  "query": "creative instant camera bag case design ideas",
  "max_results": 10,
  "search_depth": "advanced"
}'
```

#### 2.3 Material & Color Research
```bash
# Search for material trends
./scripts/search.sh '{
  "query": "camera accessories materials colors 2025 trends",
  "max_results": 8,
  "search_depth": "advanced"
}'
```

#### 2.4 User Preference Analysis
```bash
# Search for user reviews and preferences
./scripts/search.sh '{
  "query": "best instant camera accessories user reviews recommendations",
  "max_results": 8,
  "search_depth": "advanced"
}'
```

### Step 3: Deep Research (Optional - Pro Mode)

For comprehensive analysis, use research skill:

```bash
./scripts/research.sh '{
  "input": "Polaroid instant camera accessories market analysis design trends consumer preferences 2025",
  "model": "pro"
}'
```

### Step 4: Design Element Extraction

Extract and categorize design elements from collected data:

#### Color Palettes
- Trending colors (Pantone, design blogs)
- Material-specific colors (leather tones, fabric colors)
- Seasonal color trends

#### Materials
- Sustainable materials (recycled fabrics, vegan leather)
- Premium materials (genuine leather, canvas, nylon)
- Innovative materials (waterproof, shock-absorbent)

#### Form Factors
- Size variations (compact, medium, large)
- Shape trends (retro, modern, minimalist)
- Ergonomic considerations

#### Functional Features
- Storage capacity
- Protection level (waterproof, shockproof)
- Accessibility (quick-draw, modular)
- Multi-functionality

#### Aesthetic Styles
- Vintage/Retro (70s, 80s inspired)
- Modern Minimalist
- Artistic/Bohemian
- Professional/Sleek

### Step 5: Generate Daily Report

Create a structured markdown report with:

## Report Structure

```markdown
# 拍立得周边产品设计日报
**日期**: YYYY-MM-DD

## 📊 设计趋势概览

### 核心趋势
- 趋势1: [描述]
- 趋势2: [描述]
- 趋势3: [描述]

## 🎨 设计元素分析

### 1. 色彩趋势
| 色系 | 具体颜色 | 应用场景 | 热度 |
|------|----------|----------|------|
| ... | ... | ... | ⭐⭐⭐⭐⭐ |

### 2. 材质创新
| 材质类型 | 特点 | 优势 | 应用产品 |
|----------|------|------|----------|
| ... | ... | ... | ... |

### 3. 形态设计
- **尺寸趋势**: ...
- **形状特点**: ...
- **人体工学**: ...

### 4. 功能亮点
- **创新功能1**: [描述]
- **创新功能2**: [描述]

### 5. 风格流派
- **复古风格**: [描述 + 案例]
- **现代简约**: [描述 + 案例]
- **艺术风格**: [描述 + 案例]

## 💡 设计灵感

### 灵感案例1: [产品名称]
- **来源**: [品牌/设计师]
- **设计亮点**: ...
- **可借鉴元素**: ...
- **参考链接**: [URL]

### 灵感案例2: [产品名称]
...

## 📈 市场洞察

### 用户偏好
- 偏好1: [描述]
- 偏好2: [描述]

### 价格区间
- 入门级: ¥XX-XX
- 中端: ¥XX-XX
- 高端: ¥XX-XX

### 热门品牌
1. [品牌名] - [特点]
2. [品牌名] - [特点]

## 🔗 参考资源

### 设计网站
- [网站名](URL) - [描述]
- [网站名](URL) - [描述]

### 产品链接
- [产品名](URL) - [描述]

### 灵感图库
- [图库名](URL) - [描述]

## 📝 设计建议

### 短期建议
1. [具体建议]
2. [具体建议]

### 长期方向
1. [具体建议]
2. [具体建议]

---
**数据来源**: Tavily Search API
**生成时间**: YYYY-MM-DD HH:MM:SS
```

## Advanced Features

### Custom Search Queries

Users can specify custom search focus:

```bash
# Focus on specific aspect
./scripts/search.sh '{
  "query": "vintage style Polaroid camera bag leather design",
  "max_results": 10,
  "search_depth": "advanced"
}'
```

### Regional Analysis

```bash
# Region-specific trends
./scripts/search.sh '{
  "query": "拍立得相机包设计 中国市场",
  "max_results": 10,
  "search_depth": "advanced"
}'
```

### Competitor Analysis

```bash
# Analyze specific brands
./scripts/search.sh '{
  "query": "Polaroid Fujifilm Instax accessories design comparison",
  "max_results": 10,
  "search_depth": "advanced"
}'
```

## Output Options

### 1. Markdown Report (Default)
- Comprehensive daily report
- Structured with sections
- Includes all design elements

### 2. JSON Data
- Structured data for integration
- Easy to parse and process
- Suitable for databases

### 3. Summary Brief
- Quick overview (1-2 pages)
- Key highlights only
- Actionable insights

## Best Practices

### Search Strategy
1. **Use multiple queries** - Different angles yield diverse results
2. **Adjust time_range** - Recent trends vs historical analysis
3. **Leverage search_depth** - "advanced" for quality over speed
4. **Include domains** - Focus on design sites (behance.net, pinterest.com, etc.)

### Data Quality
1. **Verify sources** - Cross-reference multiple sources
2. **Filter relevance** - Focus on design-specific content
3. **Update regularly** - Design trends evolve quickly
4. **Archive insights** - Build historical database

### Report Generation
1. **Be specific** - Concrete examples over vague descriptions
2. **Include visuals** - Reference images when possible
3. **Provide context** - Why this trend matters
4. **Actionable insights** - Clear next steps

## Integration Points

- **Tavily Search API**: Primary data collection
- **Tavily Research API**: Deep analysis (pro mode)
- **WebFetch**: Extract detailed content from specific URLs
- **Feishu/Lark**: Optionally save reports to Bitable (optional)

## Example Usage

**User**: "帮我收集拍立得相机包的设计元素，生成今天的设计日报"

**Assistant Actions**:
1. Execute 4-5 parallel searches for design trends
2. Extract and categorize design elements
3. Generate structured markdown report
4. Save to file: `设计日报_YYYY-MM-DD.md`
5. Provide summary to user

**User**: "我想了解照片展示框的设计趋势，重点关注日式风格"

**Assistant Actions**:
1. Search for Japanese-style photo frame designs
2. Focus on aesthetic elements specific to Japanese design
3. Generate targeted report section
4. Include Japanese design principles and examples

## Troubleshooting

### Common Issues

1. **No relevant results**
   - Broaden search terms
   - Use different query phrasings
   - Adjust time_range

2. **Too many results**
   - Narrow search focus
   - Use include_domains for specific sites
   - Increase search_depth to "advanced"

3. **Outdated trends**
   - Use time_range: "week" or "month"
   - Add year to query (e.g., "2025 trends")
   - Search for recent articles/posts

## Configuration

### Environment Variables
```bash
# Required
TAVILY_API_KEY=tvly-your-api-key

# Optional
DESIGN_REPORT_OUTPUT_DIR=./design-reports
DEFAULT_SEARCH_DEPTH=advanced
DEFAULT_MAX_RESULTS=10
```

### Customization
Users can customize:
- Output directory
- Report format
- Search parameters
- Category focus

---

**Note**: This skill combines the power of web search (Tavily) with structured design analysis to provide actionable design insights for Polaroid peripheral products. It learns from the research and search skills while adding domain-specific value for design professionals.
