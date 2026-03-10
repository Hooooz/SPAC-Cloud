---
name: 1688-price-update
description: Update prices in local Excel tracking sheets from existing 1688 product links. Use when user wants to batch refresh an .xlsx workbook such as `相机包价格顶盘.xlsx`, append today's 1688 price columns, update ladder prices in batches, continue a paused run, or compare new 1688 prices against historical columns. Triggers on phrases like "更新 Excel 价格", "分批更新1688", "刷新阶梯价格", "更新相机包价格顶盘", "批量更新1688链接价格".
---

# 1688 Price Update

Use this skill for **existing workbooks with 1688 links already filled in**. Do not use it for finding new suppliers or new products; that belongs to `1688-product-search`.

## Scope

This skill is for:
- Reading an existing `.xlsx` tracking sheet
- Extracting 1688 links already stored in the sheet
- Refreshing prices in batches
- Appending new price columns without overwriting history
- Saving to a new workbook

This skill is not for:
- Feishu Bitable as the default target
- Creating a new catalog from search results
- Overwriting historical price columns in place

## First Step

Always inspect the workbook before doing anything else. Do not assume a generic tabular layout.

For `相机包价格顶盘.xlsx`, the current structure is:
- Single sheet: `Sheet1`
- Row 2 is the real header row
- Historical 1688 price columns already exist through `1688价格12/26` and `PLUS会员95折12/26`
- Link column is `BN` / column 66 with header `链接`
- Most products occupy 3 rows of ladder pricing
- There is one known merged link block `BN147:BN152` spanning 6 rows
- A merged link block can contain more than one product segment; row 147 and row 150 are separate products sharing one link block

## Product Parsing Rules

Do not treat "every 3 rows" as the source of truth.

Use these rules instead:
1. Identify each crawl unit from the merged ranges in the `链接` column.
2. Inside each link block, identify each product segment by rows where `型号` is non-empty.
3. Treat following rows with blank `型号/颜色` but filled `（阶梯式）起订量` as ladder rows belonging to the current segment.
4. If a shared link block contains multiple product segments, do not blindly copy one result to all segments.

## Update Modes

### Mode A: Summary Price Refresh

Use when the user wants a fast refresh of the latest 1688 price range.

Write rules:
- Append 2 columns at the far right
- Header row must be row 2, not row 1
- Recommended headers:
  - `价格更新日期`
  - `最新1688价格`
- Write only on each product segment start row
- Keep ladder sub-rows blank
- Format price as:
  - `¥12.00` for a single price
  - `¥12.00-18.50` for a range

Output file naming:
- `原文件名_价格已更新.xlsx`

### Mode B: Ladder Price Refresh

Use when the user wants prices mapped back to each MOQ row.

Write rules:
- Append 2 columns at the far right
- Header row is row 2
- Headers:
  - `1688价格\nMM/DD`
  - `更新日期`
- Write matched price to each ladder row
- Preserve all historical columns
- Save to a new workbook

Output file naming:
- `原文件名_阶梯价格已更新.xlsx`

## Ladder Matching Rules

Normalize quantity text before matching:
- `1-499`
- `500-2999`
- `≥3000`
- `1`
- `1000个起批`

Matching priority:
1. Exact range match
2. Exact `≥N` match
3. Clear overlap match when the page tiers and Excel tiers obviously refer to the same bracket

Do not:
- Fill unmatched higher tiers with lower-tier prices
- Invent missing tiers
- Copy a shared-link price to multiple product segments unless the page clearly exposes the same spec/price for all of them

## Status Rules

Allowed write-back statuses:
- Numeric price: matched successfully
- `无价格`: page opened successfully but no usable price was exposed
- `无效`: link invalid, redirected, blocked, or the extracted prices could not be mapped reliably to the workbook segment/tier
- Blank: no result should be written yet, or the row is a subordinate row with no matched tier

Date writing rules:
- If writing a numeric price, `无价格`, or `无效`, also write the update date
- If leaving the price cell blank, leave the date blank

## Batch Workflow

Process by **link blocks**, not by raw row count.

Recommended batch size:
- 10-20 link blocks per batch

Required workflow:
1. Read the workbook structure and detect the link column plus merged ranges.
2. Build product segments from each link block.
3. Ask or infer update mode: `summary` or `ladder`.
4. Process only the requested batch range if the user asks for partial updates.
5. Save intermediate JSON results after each batch.
6. Save workbook snapshots after each batch or at safe checkpoints.
7. Support resume from saved progress instead of restarting from row 1.

## Writing Safeguards

- Never overwrite existing historical price columns
- Never destroy merged cells, images, styles, or formulas
- Keep the original workbook untouched
- If today's appended columns already exist, update those columns instead of adding duplicates
- Preserve the `链接` column even when it is part of a merged range
- For shared-link blocks, review whether multiple product segments need separate handling before writing

## Bundled Scripts

Prefer reusing and patching the bundled scripts in this skill directory instead of rewriting from scratch:
- `scripts/batch_update_prices.py`: summary-mode batch collection
- `scripts/update_excel.py`: summary-mode Excel write-back
- `scripts/robust_ladder_price_updater.py`: ladder-mode extraction and write-back
- `scripts/excel_1688_workbook.py`: workbook parser for merged-link blocks and product segments
- `scripts/enhanced_price_extractor.py`: summary-mode 1688 page extractor

Current behavior to rely on:
- The workbook is parsed by link merged blocks plus product segments, not by fixed 3-row chunks
- Shared link blocks such as `BN147:BN152` are kept intact and their product segments are detected separately
- Summary-mode invalid homepage redirects should be treated as `无效`, not as successful price captures

Residual risk:
- Ladder mode still cannot reliably disambiguate SKU-specific prices inside a shared-link page unless the page exposes a clear tier mapping for the target segment; review those rows after batch update

## Execution Notes

Typical commands:
- Summary mode collection: `python scripts/batch_update_prices.py workbook.xlsx --batch-size 20`
- Summary mode write-back: `python scripts/update_excel.py workbook.xlsx`
- Ladder mode full refresh: `python scripts/robust_ladder_price_updater.py workbook.xlsx --cookie-file 1688cookie.json --delay 0.25`

Dependencies:
- `openpyxl`
- `playwright`
- Valid `1688cookie.json` in the working directory or a path passed with `--cookie-file`

## Output Report

Always report:
- Workbook name
- Update mode
- Batch range processed
- Link blocks processed
- Product segments updated
- Numeric prices written
- `无价格` count
- `无效` count
- Rows left blank because no reliable mapping was possible
- Output file path

## Example Requests

- `用1688skill分批更新 相机包价格顶盘.xlsx 的价格`
- `从第4批开始继续更新这个1688价格表`
- `给这个工作簿追加今天的1688阶梯价格，不要覆盖历史列`
- `只更新前20个1688链接，输出新文件`
