"""
Update 1688 product prices from CSV file
"""
import asyncio
import pandas as pd
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / 'shared' / 'scripts'))

from browser_1688 import Browser1688, ProductInfo
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def update_prices_from_csv(csv_file: str, output_file: str = None):
    """Update prices for products in CSV file"""
    
    if output_file is None:
        output_file = csv_file.replace('.csv', '_updated.csv')
    
    df = pd.read_csv(csv_file)
    
    logger.info(f"Loaded {len(df)} products from {csv_file}")
    
    if '链接' not in df.columns:
        logger.error("CSV file must have '链接' column")
        return
    
    unique_urls = df['链接'].unique()
    logger.info(f"Found {len(unique_urls)} unique product URLs")
    
    price_cache = {}
    
    async with Browser1688(cookie_file="1688cookie.json") as browser:
        for i, url in enumerate(unique_urls, 1):
            logger.info(f"Processing {i}/{len(unique_urls)}: {url}")
            
            try:
                product = await browser.visit_product(url, wait_time=3000)
                price_cache[url] = {
                    'price': product.price,
                    'price_min': product.price_min,
                    'price_max': product.price_max,
                    'title': product.title,
                    'sales': product.sales
                }
                logger.info(f"  Price: {product.price}")
                
                await asyncio.sleep(3)
                
            except Exception as e:
                logger.error(f"Error processing {url}: {e}")
                price_cache[url] = {
                    'price': None,
                    'price_min': None,
                    'price_max': None,
                    'title': 'Error',
                    'sales': None
                }
    
    logger.info("Updating prices in dataframe...")
    
    if '1688价格_新' not in df.columns:
        df['1688价格_新'] = None
    if '最后更新时间' not in df.columns:
        df['最后更新时间'] = None
    
    from datetime import datetime
    update_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    for idx, row in df.iterrows():
        url = row['链接']
        if url in price_cache:
            cache = price_cache[url]
            df.at[idx, '1688价格_新'] = cache['price']
            df.at[idx, '最后更新时间'] = update_time
    
    df.to_csv(output_file, index=False, encoding='utf-8-sig')
    logger.info(f"Saved updated prices to {output_file}")
    
    print("\n" + "="*60)
    print("价格更新报告")
    print("="*60)
    print(f"总产品数: {len(df)}")
    print(f"唯一链接数: {len(unique_urls)}")
    print(f"成功更新: {sum(1 for v in price_cache.values() if v['price'])}")
    print(f"失败/失效: {sum(1 for v in price_cache.values() if not v['price'])}")
    print(f"\n更新时间: {update_time}")
    print(f"输出文件: {output_file}")
    print("="*60)


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python update_prices.py <csv_file> [output_file]")
        sys.exit(1)
    
    csv_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    asyncio.run(update_prices_from_csv(csv_file, output_file))
