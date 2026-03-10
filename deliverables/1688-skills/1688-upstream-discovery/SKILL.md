---
name: 1688-upstream-discovery
description: Discover new products and upstream suppliers on 1688 from scratch (0-1 sourcing), with product links and rough price bands. Use whenever the user asks to 搜新品, 找货源, 找上游供应商, 做1688选品, 比较同类配件供应商, or needs “关键词→候选商品+链接+价格参考” instead of updating an existing Excel tracker.
---

# 1688 Upstream Discovery

Use this skill for **new supplier/new product discovery** on 1688.

Do not use this skill for updating prices in an existing workbook with known links; use `1688-price-update` for that.

## What This Skill Produces

Given one or more keywords, this skill returns a candidate list with:
- Product title
- Product detail link (`https://detail.1688.com/offer/<offerId>.html`)
- Rough price hint (single price or range)
- MOQ hint
- Supplier/shop hint
- Upstream/new-product signals (e.g. `源头工厂`, `新品`)

## Input Pattern

Typical user asks:
- `帮我在1688搜拍立得相机包背带相关新品，给链接和大致价格`
- `找上游供应商，关键词是拍立得 背带 配件`
- `先给我20个候选工厂链接和价格区间`

Required input:
- Search keyword(s), preferably 2-6 words

Optional input:
- Result count target (default 30)
- Page count (default 2)
- Preference (low price / upstream factory signal / new arrivals)

## Execution Steps

1. Build 1688 search URL with GBK-encoded keyword.
2. Open search page with cookie-authenticated Playwright browser.
3. If captcha appears:
- Headed mode: ask user to complete slider verification and continue.
- Headless mode: stop and report captcha block clearly.
4. Extract candidate offers from search results page and normalize to detail links.
5. Parse rough price/MOQ/supplier signals from card snippets.
6. Deduplicate by `offerId`.
7. Output JSON + CSV + Markdown summary.

## Script

Primary script:
- `scripts/search_1688_upstream.py`

Typical command:

```bash
python scripts/search_1688_upstream.py \
  --keyword "拍立得 相机包 背带 配件" \
  --cookie-file 1688cookie.json \
  --max-results 30 \
  --pages 2
```

If captcha is frequent, run in headed mode (default, no `--headless`) and complete slider manually.

## Output Contract

Must provide:
- A short summary of keyword and total extracted items
- Top candidates with clickable product links
- Price hints as rough ranges (not guaranteed final transaction price)
- Any upstream/new-product signals found
- Paths to generated files (`.json`, `.csv`, `.md`)

## Quality Rules

- Always include product links in the final answer.
- Never present rough price hints as guaranteed final quote.
- If blocked by captcha, explicitly report it and suggest headed retry.
- Avoid claiming supplier type as absolute truth; treat as `signal` from page text.

## Boundary With Other 1688 Skills

- `1688-upstream-discovery`: find new candidates from keywords (0-1 sourcing).
- `1688-price-update`: refresh prices for existing known links in local Excel.

