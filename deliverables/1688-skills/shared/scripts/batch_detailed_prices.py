"""
Batch extract detailed prices using enhanced extractor
"""
import asyncio
import json
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))

from enhanced_price_extractor import Enhanced1688Extractor
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def batch_extract_prices(urls):
    """Batch extract detailed prices"""
    
    results = []
    
    async with Enhanced1688Extractor(cookie_file="1688cookie.json") as extractor:
        for i, url in enumerate(urls, 1):
            print(f"\n{'='*60}")
            print(f"[{i}/{len(urls)}] 正在提取: {url}")
            print('='*60)
            
            try:
                price_info = await extractor.extract_price_info(url)
                result = price_info.to_dict()
                results.append(result)
                
                # Print summary
                print(f"✓ 标题: {price_info.title[:50]}...")
                print(f"✓ 价格区间: {price_info.price_range[:100] if price_info.price_range else '未获取'}...")
                if price_info.sku_prices:
                    print(f"✓ SKU价格: {len(price_info.sku_prices)} 个")
                if price_info.promotion_price:
                    print(f"✓ 促销: {price_info.promotion_price[:50]}...")
                if price_info.shop_name:
                    print(f"✓ 店铺: {price_info.shop_name[:30]}...")
                if price_info.location:
                    print(f"✓ 地点: {price_info.location}")
                
                # Wait between requests
                if i < len(urls):
                    await asyncio.sleep(3)
                    
            except Exception as e:
                logger.error(f"Error processing {url}: {e}")
                results.append({
                    'url': url,
                    'title': 'Error',
                    'error': str(e),
                    'collected_at': datetime.now().isoformat()
                })
    
    return results


async def main():
    # Read URLs from command line or file
    if len(sys.argv) > 1:
        urls = sys.argv[1:]
    else:
        print("请输入产品链接(每行一个,空行结束):")
        urls = []
        while True:
            url = input().strip()
            if not url:
                break
            urls.append(url)
    
    if not urls:
        print("未提供任何链接")
        sys.exit(1)
    
    print(f"\n开始提取 {len(urls)} 个产品的详细价格信息...\n")
    
    results = await batch_extract_prices(urls)
    
    # Save results
    output_file = f"detailed_prices_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    # Generate summary
    print("\n" + "="*60)
    print("提取完成 - 汇总报告")
    print("="*60)
    print(f"总数: {len(results)}")
    print(f"成功: {sum(1 for r in results if r.get('price_range'))}")
    print(f"失败: {sum(1 for r in results if not r.get('price_range'))}")
    print(f"\n结果已保存到: {output_file}")
    
    # Print price summary table
    print("\n" + "="*60)
    print("价格汇总表")
    print("="*60)
    for i, r in enumerate(results, 1):
        print(f"\n{i}. {r.get('title', 'Unknown')[:50]}...")
        if r.get('price_range'):
            # Extract first line of price range
            price_first_line = r['price_range'].split('\n')[0:3]
            print(f"   价格: {' '.join(price_first_line)}")
        if r.get('promotion_price'):
            print(f"   促销: {r['promotion_price'][:50]}")
        if r.get('location'):
            print(f"   地点: {r['location']}")


if __name__ == '__main__':
    asyncio.run(main())
