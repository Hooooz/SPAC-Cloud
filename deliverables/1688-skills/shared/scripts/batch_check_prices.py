"""
Batch check product prices from URLs
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from browser_1688 import Browser1688
import json
from datetime import datetime

async def batch_check_prices(urls):
    """Check prices for multiple products"""
    
    results = []
    
    async with Browser1688(cookie_file="1688cookie.json") as browser:
        for i, url in enumerate(urls, 1):
            print(f"\n[{i}/{len(urls)}] 正在检查: {url}")
            
            try:
                product = await browser.visit_product(url, wait_time=3000)
                
                result = {
                    'url': url,
                    'title': product.title,
                    'price': product.price,
                    'price_min': product.price_min,
                    'price_max': product.price_max,
                    'sales': product.sales,
                    'shop_name': product.shop_name,
                    'images': product.images,
                    'collected_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                
                results.append(result)
                
                print(f"  ✓ 标题: {product.title[:50]}...")
                print(f"  ✓ 价格: {product.price}")
                if product.sales:
                    print(f"  ✓ 销量: {product.sales}")
                
                # Wait between requests to avoid blocking
                if i < len(urls):
                    await asyncio.sleep(3)
                    
            except Exception as e:
                print(f"  ✗ 错误: {e}")
                results.append({
                    'url': url,
                    'title': 'Error',
                    'price': None,
                    'error': str(e),
                    'collected_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
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
    
    print(f"\n开始检查 {len(urls)} 个产品价格...\n")
    print("="*60)
    
    results = await batch_check_prices(urls)
    
    print("\n" + "="*60)
    print("批量检查完成")
    print("="*60)
    print(f"总数: {len(results)}")
    print(f"成功: {sum(1 for r in results if r.get('price'))}")
    print(f"失败: {sum(1 for r in results if not r.get('price'))}")
    
    # Save results
    output_file = f"price_check_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n结果已保存到: {output_file}")
    
    # Print summary table
    print("\n" + "="*60)
    print("价格汇总")
    print("="*60)
    for i, r in enumerate(results, 1):
        print(f"{i}. {r['title'][:40]}...")
        print(f"   价格: {r['price'] or '未获取'}")
        if r.get('sales'):
            print(f"   销量: {r['sales']}")
        print()

if __name__ == '__main__':
    asyncio.run(main())
