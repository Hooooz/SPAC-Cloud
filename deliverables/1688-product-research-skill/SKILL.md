---
name: "1688-product-research"
description: "Research 1688 products using browser with cookie login. Invoke when user wants to search and gather product information from 1688."
---

# 1688 Product Research Skill

A skill for researching products on 1688.com using Playwright browser automation with cookie-based authentication.

## Features

- Cookie-based login (no manual login required after initial setup)
- Product search on 1688 homepage
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

### 2. Configure Product URL

Edit the `product_url` variable in `src/research.py` to specify the 1688 product page you want to research.

### 3. Run the Research

```bash
python -m src.research
```

The script will:
1. Load cookies and login to 1688
2. Navigate to the product detail page
3. Extract product information
4. Save results to CSV file

## Output Format

The research results are saved to `output/1688_product_detail.csv` with the following columns:

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

## Cookie Setup

1. Install a cookie extension in Chrome (e.g., "EditThisCookie")
2. Visit 1688.com and login
3. Export cookies for 1688.com domain
4. Save as JSON format to `1688cookie.json`

## Project Structure

```
1688-product-research-skill/
├── SKILL.md                 # This file
├── README.md                # English documentation
├── requirements.txt         # Python dependencies
├── 1688cookie.json         # Cookie file (you need to create this)
├── src/
│   └── research.py         # Main research script
└── output/
    └── 1688_product_detail.csv  # Research results
```

## Important Notes

- Cookie expiration: Cookies will expire, you may need to refresh them periodically
- PLUS会员95折: Requires a 1688 PLUS membership account to retrieve
- Rate limiting: Don't make too many requests in a short time to avoid being blocked

## Troubleshooting

### Login Failed
- Refresh the cookie file with new cookies from browser

### Anti-bot Verification
- The script uses headless=False by default to allow manual verification
- If verification is triggered, complete it manually in the browser window

### Price Extraction Failed
- Check if the product page structure has changed
- Update the regex patterns in the script accordingly
