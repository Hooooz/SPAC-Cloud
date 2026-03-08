---
name: 1688-product-search
description: Search for new products on 1688 and add them to Feishu Bitable. Use when user wants to find new products, search for product alternatives, discover suppliers, or expand product catalog. Triggers on phrases like "搜索新产品", "找货源", "搜索1688", "查找商品", "添加新产品", "1688搜索".
---

# 1688 Product Search Workflow

## Overview
This skill searches for new products on 1688, collects detailed product information, and adds them to Feishu Bitable for tracking and comparison.

## Prerequisites
- Valid 1688 cookies for authentication (stored in `1688cookie.json`)
- Browser automation capability (Playwright)
- Feishu Bitable access for storing results

## Workflow

### Step 1: Understand Search Requirements
Ask user to provide:
1. **Product keywords**: Core product name or category
   - Example: "指甲刀", "拍立得相机包", "化妆包"
2. **Related keywords**: Alternative terms or features
   - Example: "指甲剪", "修甲工具", "便携"
3. **Search filters** (optional):
   - Price range
   - Minimum order quantity
   - Shipping location
   - Supplier type (factory/trader)

### Step 2: Prepare Authentication
1. Check for `1688cookie.json` in project root
2. If not found or expired:
   - Open 1688.com in non-headless browser
   - Wait for user to login and complete verification
   - Export cookies to `1688cookie.json`

### Step 3: Execute Search
1. Launch browser with cookies
2. Navigate to https://www.1688.com
3. Enter search keywords in search box
4. Apply any specified filters
5. Wait for results to load
6. Handle anti-crawler challenges:
   - Manual verification prompts
   - Slider CAPTCHA
   - Rate limiting

### Step 4: Collect Product Information
For each product in search results (typically top 20-50):

**Basic Information**:
- Product title (商品标题)
- Product URL (链接)
- Shop name (店铺名称)
- Shop URL (店铺链接)

**Pricing Information**:
- Price range (价格区间)
- Price per MOQ tier (阶梯价格)
- Member price (会员价)
- Promotional price (活动价)

**Product Details**:
- Product images (产品图片)
- Model/SKU variants (型号规格)
- Color options (颜色分类)
- MOQ (起订量)
- Sales volume (销量)
- Ship from location (发货地)

**Supplier Information**:
- Supplier type (工厂/贸易商)
- Years on platform (经营年限)
- Response rate (回复率)

### Step 5: Save to Feishu Bitable
1. Connect to Feishu Bitable using API
2. For each product, create a new record with:
   - All collected information
   - Search timestamp
   - Search keywords used
3. Handle duplicates:
   - Check if product URL already exists
   - If exists, update instead of creating new
   - Flag potential duplicates for review

### Step 6: Generate Summary Report
Provide user with:
- Total products found
- Products saved to Feishu
- Price range summary
- Top suppliers identified
- Potential issues or recommendations

## Data Structure

### Feishu Bitable Fields
| 字段名 | 字段类型 | 说明 |
|--------|----------|------|
| 商品标题 | 文本 | Product title |
| 链接 | 超链接 | 1688 product URL |
| 价格 | 文本 | Price range or single price |
| 店铺名称 | 文本 | Shop name |
| 型号 | 文本 | Model/SKU |
| 颜色 | 文本 | Color variants |
| 起订量 | 文本 | Minimum order quantity |
| 销量 | 文本 | Sales volume |
| 图片 | 附件 | Product images |
| 搜索关键词 | 文本 | Keywords used for search |
| 添加时间 | 日期 | Timestamp |
| 备注 | 文本 | Additional notes |

## Search Strategies

### Strategy 1: Broad Search
- Use general keywords
- Collect diverse products
- Good for market research

### Strategy 2: Targeted Search
- Use specific product names
- Add filters (price, MOQ)
- Good for finding exact matches

### Strategy 3: Competitor Analysis
- Search competitor product names
- Find similar alternatives
- Compare pricing and features

## Anti-Crawler Handling

### Detection Signs
- Frequent CAPTCHA prompts
- "访问过于频繁" messages
- Empty search results
- Redirect to login page

### Mitigation Techniques
1. **Random Delays**: 3-8 seconds between actions
2. **Non-headless Mode**: Allow manual intervention
3. **Cookie Rotation**: Use fresh cookies periodically
4. **Request Throttling**: Limit requests per minute
5. **Human-like Behavior**: Random mouse movements, scrolling

## Error Handling

### Common Errors
1. **Login Required**: Prompt user to re-authenticate
2. **CAPTCHA Blocked**: Switch to non-headless mode
3. **No Results Found**: 
   - Try alternative keywords
   - Broaden search criteria
   - Check keyword spelling
4. **Network Timeout**: Retry with backoff
5. **Feishu API Error**: Validate permissions and token

### Recovery Actions
- Save partial results before failing
- Log error details for debugging
- Provide user with actionable next steps

## Best Practices

1. **Batch Processing**: Process 10-20 products per batch
2. **Progress Updates**: Show real-time progress to user
3. **Data Quality**: Validate and clean data before saving
4. **Duplicate Detection**: Prevent duplicate entries
5. **Image Handling**: Download and attach images to Feishu
6. **Rate Limiting**: Respect platform limits
7. **User Feedback**: Ask for confirmation on ambiguous results

## Example Usage

**User**: "帮我搜索1688上的指甲刀产品,找一些价格便宜的"

**Assistant Actions**:
1. Ask for specific requirements (price range, quantity, etc.)
2. Search "指甲刀" on 1688
3. Apply price filter (low to high)
4. Collect top 30 products
5. Extract detailed information
6. Save to Feishu Bitable
7. Generate summary with recommendations

## Integration Points

- **Browser Automation**: Use shared script at `shared/scripts/browser_1688.py`
- **Feishu MCP**: Use `mcp_lark-mcp_bitable_v1_appTableRecord_create` to add products
- **Feishu MCP**: Use `mcp_lark-mcp_bitable_v1_appTableField_list` to check field structure
- **Cookie Management**: Read from `1688cookie.json`

## Shared Utilities

This skill uses the shared browser automation script located at:
```
shared/scripts/browser_1688.py
```

Key functions:
- `search(keyword, cookie_file, max_results)`: Search for products by keyword
- `Browser1688`: Full browser automation class with search capabilities

Usage example:
```python
from shared.scripts.browser_1688 import search

results = await search("指甲刀", max_results=20)
for product in results:
    print(f"{product['title']}: {product['price']}")
```

## Output Format

```
1688产品搜索报告
==================
搜索关键词: 指甲刀
搜索时间: 2026-03-07 20:00:00

搜索结果:
- 找到产品: 30个
- 已保存: 28个
- 重复跳过: 2个

价格分布:
- 最低价: ¥1.5
- 最高价: ¥25.0
- 平均价: ¥8.3

热门供应商:
1. 阳江市金达刀具有限公司 (5个产品)
2. 揭阳市不锈钢制品厂 (3个产品)
...

推荐产品 (价格最优):
1. [产品名] - ¥1.5 - [店铺名]
2. [产品名] - ¥2.0 - [店铺名]
...

数据已保存到飞书多维表格
```

## Advanced Features

### Price History Tracking
- Save price snapshot with timestamp
- Enable future price trend analysis

### Supplier Quality Scoring
- Calculate supplier score based on:
  - Years on platform
  - Response rate
  - Sales volume
  - Customer reviews

### Product Comparison
- Compare similar products side-by-side
- Highlight key differences
- Recommend best options
