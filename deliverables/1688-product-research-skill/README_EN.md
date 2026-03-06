# 1688 Product Research Tool

A 1688 product research tool based on Playwright browser automation with cookie-based authentication.

## Features

- ✅ Cookie auto-login (no manual login after initial setup)
- ✅ **Keyword Search** - Supports Chinese URL encoding to prevent garbled text
- ✅ **Product Detail Research** - Extract detailed specs, prices, sales from detail pages
- ✅ Extract detailed product information:
  - Product name (used as model)
  - Color variants
  - Sales volume
  - Tiered pricing (MOQ-based pricing)
  - Product images
  - Product URLs
- ✅ Export to CSV format

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium
```

## Quick Start

### 1. Prepare Cookie File

Export 1688 cookies using Chrome browser extension (like "EditThisCookie" or "Cookie-Editor").

Save cookies as JSON format to `1688cookie.json` in the project root.

### 2. Search Products (Keyword Search)

```bash
python -m src.search --keyword "phone stand"
```

The script will automatically:
1. Load cookies and login to 1688
2. Open search page (keywords automatically URL-encoded)
3. Extract top 20 product results
4. Save to CSV file

### 3. Research Product Details

After getting product URLs from search results, research specific products:

```bash
python -m src.research --url "product_url" --name "product_name"
```

## Output Format

### Search Results (`output/1688_search_results.csv`)

| Column | Description |
|--------|-------------|
| 序号 | Row number |
| 商品标题 | Product title |
| 价格 | Price |
| 图片 | Image URL |
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

Each tiered price creates a separate row.

## Command Line Options

### Search Script (`src/search.py`)

| Option | Description |
|--------|-------------|
| `--keyword` | Search keyword (required) |
| `--cookie` | Cookie file path (default: 1688cookie.json) |
| `--headless` | Run in headless mode |
| `--max` | Maximum results (default: 20) |

### Research Script (`src/research.py`)

| Option | Description |
|--------|-------------|
| `--url` | 1688 product detail URL (required) |
| `--name` | Product name for CSV output |
| `--cookie` | Cookie file path (default: 1688cookie.json) |
| `--headless` | Run in headless mode |

## URL Encoding

This tool automatically handles Chinese keyword URL encoding:

- Input: `手机支架`
- Encoded: `%E6%89%8B%E6%9C%BA%E6%94%AF%E6%9E%B6`
- Search URL: `https://s.1688.com/youyuan/index.htm?tab=search&keywords=%E6%89%8B%E6%9C%BA%E6%94%AF%E6%9E%B6`

## Project Structure

```
1688-product-research-skill/
├── SKILL.md                 # Skill definition
├── README.md                # Chinese documentation
├── README_EN.md             # English documentation
├── requirements.txt         # Python dependencies
├── 1688cookie.json         # Cookie file (you need to create)
├── src/
│   ├── search.py           # Search script (new)
│   └── research.py          # Detail research script
└── output/
    ├── 1688_search_results.csv     # Search results
    └── 1688_product_detail.csv     # Detail research results
```

## Important Notes

- ✅ **URL Encoding**: Keywords automatically URL-encoded to prevent search garbling
- Cookie expiration: Cookies expire, need to refresh periodically
- PLUS会员95折: Requires 1688 PLUS membership account
- Rate limiting: Don't make too many requests in short time

## Troubleshooting

### Search Returns No Results
- Check if cookies are valid and not expired
- Try running without headless mode to see if verification is needed

### Login Failed
- Refresh cookie file with latest browser cookies

### Anti-bot Verification
- Script uses headless=False by default for manual verification
- Complete verification manually in browser window if triggered
