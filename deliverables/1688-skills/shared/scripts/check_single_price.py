"""
Check single product price
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from browser_1688 import check_price
import json

async def main():
    if len(sys.argv) < 2:
        print("Usage: python check_single_price.py <url>")
        sys.exit(1)
    
    url = sys.argv[1]
    print(f"正在检查产品价格: {url}\n")
    
    result = await check_price(url, cookie_file="1688cookie.json")
    
    print("="*60)
    print("产品信息")
    print("="*60)
    print(f"标题: {result['title']}")
    print(f"价格: {result['price']}")
    if result['price_min'] and result['price_max']:
        print(f"最低价: ¥{result['price_min']}")
        print(f"最高价: ¥{result['price_max']}")
    if result['sales']:
        print(f"销量: {result['sales']}")
    if result['shop_name']:
        print(f"店铺: {result['shop_name']}")
    print(f"\n完整数据:")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    print("="*60)

if __name__ == '__main__':
    asyncio.run(main())
