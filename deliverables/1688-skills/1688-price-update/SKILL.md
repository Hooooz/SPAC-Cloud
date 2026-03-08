---
name: 1688-price-update
description: Update prices for existing products from 1688 links in Feishu Bitable. Use when user wants to check latest prices for products already in the tracking table, update price information, or refresh product pricing data. Triggers on phrases like "更新价格", "查最新价格", "刷新价格", "价格追踪", "更新1688价格".
---

# 1688 Price Update Workflow

## Overview
This skill updates price information for existing products stored in Feishu Bitable by visiting their 1688 product links and extracting current pricing data.

## Prerequisites
- Feishu Bitable containing product links
- Valid 1688 cookies for authentication (stored in `1688cookie.json`)
- Browser automation capability (Playwright)

## Workflow

### Step 1: Access Feishu Bitable
1. Ask user for the Feishu Bitable link or token
2. Use Feishu API to read the product table
3. Extract product links (column name: "链接" or "URL")
4. Identify the price column to update (column name: "1688价格" or "价格")

### Step 2: Load Authentication
1. Check for `1688cookie.json` in project root
2. If not found, guide user to:
   - Open 1688.com in browser
   - Login and complete any verification
   - Export cookies using browser dev tools
   - Save to `1688cookie.json`

### Step 3: Visit Each Product Link
For each product URL:
1. Launch browser with cookies
2. Navigate to product detail page
3. Wait for page load (handle anti-crawler delays)
4. Extract current price information:
   - Price for different MOQ tiers
   - Member discounts (PLUS会员价格)
   - Promotional prices (券后价)
5. Handle errors gracefully:
   - Product delisted
   - Link expired
   - Anti-crawler blocking

### Step 4: Update Feishu Bitable
1. For each product, update the price column
2. Add timestamp column showing "最后更新时间"
3. If multiple price tiers exist, record:
   - Minimum price
   - Price range (e.g., "¥10-15")
   - MOQ information

### Step 5: Generate Report
Create a summary report including:
- Total products checked
- Successfully updated count
- Failed/Expired links count
- Price changes detected (increase/decrease)
- Timestamp

## Data Structure

### Input (from Feishu)
| 字段名 | 说明 |
|--------|------|
| 产品名称 | Product name |
| 链接 | 1688 product URL |
| 型号 | Model/SKU |
| 颜色 | Color variant |

### Output (to Feishu)
| 字段名 | 说明 |
|--------|------|
| 1688价格 | Current price (updated) |
| 最后更新时间 | Update timestamp |
| 价格变动 | Price change indicator (↑↓→) |
| 备注 | Notes (e.g., "已下架", "链接失效") |

## Error Handling

### Common Issues
1. **Cookie expired**: Prompt user to re-login and export new cookies
2. **Anti-crawler detection**: 
   - Add random delays between requests
   - Use non-headless mode for manual verification
   - Reduce request frequency
3. **Product delisted**: Mark in Feishu with status "已下架"
4. **Network timeout**: Retry with exponential backoff

### Retry Strategy
- Max retries: 3
- Delay between retries: 5-15 seconds (random)
- Skip failed products after max retries

## Best Practices

1. **Rate Limiting**: Wait 3-5 seconds between products to avoid blocking
2. **Batch Processing**: Process in batches of 10-20 products
3. **Progress Tracking**: Show real-time progress to user
4. **Data Validation**: Verify price format before updating
5. **Backup**: Keep previous price data before overwriting

## Example Usage

**User**: "帮我更新飞书表格里所有产品的最新价格"

**Assistant Actions**:
1. Access Feishu Bitable via API
2. Extract all product links
3. For each link:
   - Visit 1688 page with authentication
   - Extract current price
   - Update Feishu record
4. Generate summary report

## Integration Points

- **Feishu MCP**: Use `mcp_lark-mcp_bitable_v1_appTableRecord_search` to read products
- **Feishu MCP**: Use `mcp_lark-mcp_bitable_v1_appTableRecord_update` to update prices
- **Browser Automation**: Use shared script at `shared/scripts/browser_1688.py`
- **Cookie Management**: Read from `1688cookie.json`

## Shared Utilities

This skill uses the shared browser automation script located at:
```
shared/scripts/browser_1688.py
```

Key functions:
- `check_price(url, cookie_file)`: Check price for a single product URL
- `Browser1688`: Full browser automation class with cookie management

Usage example:
```python
from shared.scripts.browser_1688 import check_price

result = await check_price("https://detail.1688.com/offer/123456.html")
print(result['price'])  # "¥10.5-15.0"
```

## Output Format

```
价格更新报告
================
总产品数: 50
成功更新: 45
失败/失效: 5

价格变动:
- 上涨: 3个产品
- 下降: 8个产品
- 不变: 34个产品

失效链接:
1. [产品名] - 链接已失效
2. [产品名] - 商品已下架
...

更新时间: 2026-03-07 20:00:00
```
