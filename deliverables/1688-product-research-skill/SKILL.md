---
name: "1688-product-research"
description: "Research 1688 products using browser with cookie login. Supports both search by keyword and product detail research. Invoke when user wants to search and gather product information from 1688."
---

# 1688 Product Research Skill

A skill for researching products on 1688.com using Playwright browser automation with cookie-based authentication.

## Features

- Cookie-based login (no manual login required after initial setup)
- **Product Search**: Search products by keyword and get top results with URLs
- **Product Detail Research**: Extract detailed product information from detail pages
- Extract detailed product information including:
  - Product name (used as model)
  - Color variants
  - Sales volume
  - Tiered pricing (MOQ-based pricing)
  - Product images
  - Product URLs
- Export to CSV format

## Installation

```bash
# Install dependencies
pip install playwright pandas

# Install Playwright browsers
playwright install chromium
```

## Usage

### 1. Prepare Cookie File

Export your 1688 cookies from Chrome browser using a cookie extension (like "EditThisCookie" or "Cookie-Editor").

Save the cookies as JSON format to `1688cookie.json` in the project root.

### 2. Search Products by Keyword

```bash
python -m src.search --keyword "手机支架"
```

The search script will:
1. Load cookies and login to 1688
2. Navigate to 1688 search page with properly URL-encoded keyword
3. Extract top 20 product results
4. Save results to CSV file

### 3. Research Product Details

After getting product URLs from search, research individual products:

```bash
python -m src.research --url "商品URL" --name "商品名"
```

## Output Format

### Search Results (`output/1688_search_results.csv`)

| Column | Description |
|--------|-------------|
| 序号 | Row number |
| 商品标题 | Product title |
| 价格 | Product price |
| 图片 | Product image URL |
| 链接 | Product URL |

### Product Detail Results (`output/1688_product_detail.csv`)

| Column | Description |
|--------|-------------|
| 型号 | Product name (used as model) |
| 颜色 | Color variant |
| 一年内销量 | Sales volume |
| 图片 | Product image URL |
| 起订量 | Minimum order quantity |
| 1688价格 | Product price |
| PLUS会员95折 | PLUS member discount (requires PLUS account) |
| 链接 | Product URL |

Each tiered price creates a separate row in the output.

## Command Line Options

### Search Script (`src/search.py`)

| Option | Description |
|--------|-------------|
| `--keyword` | Search keyword (required) |
| `--cookie` | Cookie file path (default: 1688cookie.json) |
| `--headless` | Run in headless mode |
| `--max` | Maximum number of results (default: 20) |

### Research Script (`src/research.py`)

| Option | Description |
|--------|-------------|
| `--url` | 1688 product detail URL (required) |
| `--name` | Product name for CSV output |
| `--cookie` | Cookie file path (default: 1688cookie.json) |
| `--headless` | Run in headless mode |

## Important Notes

- **URL Encoding**: Keywords are automatically URL-encoded to prevent garbled search queries
- Cookie expiration: Cookies will expire, you may need to refresh them periodically
- PLUS会员95折: Requires a 1688 PLUS membership account to retrieve
- Rate limiting: Don't make too many requests in a short time to avoid being blocked

## Troubleshooting

### Search Returns No Results
- Check if cookies are valid and not expired
- Try running without headless mode to see if verification is needed

### Login Failed
- Refresh the cookie file with new cookies from browser

### Anti-bot Verification
- The script uses headless=False by default to allow manual verification
- If verification is triggered, complete it manually in the browser window
