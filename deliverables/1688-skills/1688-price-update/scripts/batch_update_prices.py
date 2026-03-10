"""
批量更新1688产品价格
分批处理Excel中的产品链接，获取最新价格信息
"""
import asyncio
import json
from collections import OrderedDict
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

from enhanced_price_extractor import Enhanced1688Extractor, DetailedPriceInfo
from excel_1688_workbook import extract_product_segments


class BatchPriceUpdater:
    """批量价格更新器"""
    
    def __init__(self, excel_file: str, cookie_file: str = "1688cookie.json"):
        self.excel_file = Path(excel_file)
        self.cookie_file = Path(cookie_file)
        self.output_dir = Path("price_update_results")
        self.output_dir.mkdir(exist_ok=True)
        
    def extract_links_from_excel(self) -> List[Dict[str, Any]]:
        """从Excel提取所有商品段和1688链接"""
        segments = extract_product_segments(self.excel_file)
        return [
            {
                'excel_row': segment.excel_start_row,
                'model': segment.model,
                'color': segment.color,
                'link': segment.link,
                'link_block_start': segment.link_block_start,
                'link_block_end': segment.link_block_end,
                'shared_link_segment_count': segment.shared_link_segment_count,
            }
            for segment in segments
            if segment.link
        ]

    @staticmethod
    def _is_valid_price_info(price_info: DetailedPriceInfo) -> bool:
        title = (price_info.title or "").strip()
        final_url = (price_info.final_url or "").strip()
        has_price_signal = any(
            [
                price_info.price_range,
                price_info.price_min,
                price_info.price_max,
                price_info.sku_prices,
                price_info.moq_prices,
            ]
        )

        if not has_price_signal:
            return False
        if title in {"", "Error", "阿里1688首页"}:
            return False
        if "阿里1688首页" in title:
            return False
        if final_url and "/offer/" not in final_url:
            return False
        return True

    @staticmethod
    def _classify_result(price_info: DetailedPriceInfo) -> str:
        if not BatchPriceUpdater._is_valid_price_info(price_info):
            return 'invalid'
        if price_info.price_min is None and price_info.price_max is None and not price_info.price_range:
            return 'no_price'
        return 'success'

    async def update_batch(
        self, 
        links: List[Dict[str, Any]], 
        batch_num: int,
        delay: float = 3.0
    ) -> List[Dict[str, Any]]:
        """更新一批产品的价格"""
        results = []
        grouped_links: "OrderedDict[str, List[Dict[str, Any]]]" = OrderedDict()
        for item in links:
            grouped_links.setdefault(item['link'], []).append(item)
        
        async with Enhanced1688Extractor(str(self.cookie_file)) as extractor:
            total_links = len(grouped_links)
            for i, (link, group_items) in enumerate(grouped_links.items(), 1):
                item = group_items[0]
                print(f"\n批次{batch_num} - 进度 {i}/{total_links}")
                print(f"产品: {item['model']} - {item['color']}")
                print(f"链接: {link}")
                if len(group_items) > 1:
                    print(f"共享链接商品段: {len(group_items)}")
                
                try:
                    price_info = await extractor.extract_price_info(link, wait_time=5000)
                    status = self._classify_result(price_info)

                    if status == 'success':
                        print(f"✓ 价格: {price_info.price_range or '未找到'}")
                        if price_info.price_min and price_info.price_max:
                            print(f"  最低价: ¥{price_info.price_min}, 最高价: ¥{price_info.price_max}")
                    elif status == 'no_price':
                        print("✗ 页面可访问，但未提取到价格")
                    else:
                        print(f"✗ 页面无效: {price_info.title or '未知标题'}")

                    for group_item in group_items:
                        results.append({
                            'excel_row': group_item['excel_row'],
                            'model': group_item['model'],
                            'color': group_item['color'],
                            'link': group_item['link'],
                            'title': price_info.title,
                            'final_url': price_info.final_url,
                            'price_range': price_info.price_range,
                            'price_min': price_info.price_min,
                            'price_max': price_info.price_max,
                            'sku_prices': price_info.sku_prices,
                            'moq_prices': price_info.moq_prices,
                            'member_price': price_info.member_price,
                            'promotion_price': price_info.promotion_price,
                            'sales': price_info.sales,
                            'shop_name': price_info.shop_name,
                            'status': status,
                            'collected_at': datetime.now().isoformat()
                        })
                    
                except Exception as e:
                    print(f"✗ 错误: {e}")
                    for group_item in group_items:
                        results.append({
                            'excel_row': group_item['excel_row'],
                            'model': group_item['model'],
                            'color': group_item['color'],
                            'link': group_item['link'],
                            'status': 'error',
                            'error': str(e),
                            'collected_at': datetime.now().isoformat()
                        })
                
                if i < total_links:
                    await asyncio.sleep(delay)
        
        return results
    
    async def run_batch_update(
        self, 
        batch_size: int = 20,
        start_batch: int = 0,
        max_batches: int = None
    ):
        """运行批量更新"""
        all_links = self.extract_links_from_excel()
        total_products = len(all_links)
        
        print(f"\n{'='*60}")
        print(f"批量价格更新任务")
        print(f"{'='*60}")
        print(f"Excel文件: {self.excel_file}")
        print(f"总产品数: {total_products}")
        print(f"批次大小: {batch_size}")
        print(f"{'='*60}\n")
        
        all_results = []
        
        total_batches = (total_products + batch_size - 1) // batch_size
        remaining_batches = max(0, total_batches - start_batch)
        planned_batches = remaining_batches if max_batches is None else min(remaining_batches, max_batches)

        for batch_idx in range(start_batch, start_batch + planned_batches):
            start_idx = batch_idx * batch_size
            end_idx = min(start_idx + batch_size, total_products)
            
            if start_idx >= total_products:
                break
            
            batch_links = all_links[start_idx:end_idx]
            
            print(f"\n{'='*60}")
            print(f"开始处理批次 {batch_idx + 1}/{start_batch + planned_batches}")
            print(f"产品范围: {start_idx + 1} - {end_idx}")
            print(f"{'='*60}\n")
            
            batch_results = await self.update_batch(batch_links, batch_idx + 1)
            all_results.extend(batch_results)
            
            batch_file = self.output_dir / f"batch_{batch_idx + 1}_results.json"
            with open(batch_file, 'w', encoding='utf-8') as f:
                json.dump(batch_results, f, ensure_ascii=False, indent=2)
            print(f"\n✓ 批次{batch_idx + 1}结果已保存: {batch_file}")
            
            success_count = sum(1 for r in batch_results if r['status'] == 'success')
            print(f"成功: {success_count}/{len(batch_results)}")
            
            if batch_idx < start_batch + planned_batches - 1:
                wait_time = 10
                print(f"\n等待 {wait_time} 秒后继续下一批...")
                await asyncio.sleep(wait_time)
        
        all_results_file = self.output_dir / "all_results.json"
        with open(all_results_file, 'w', encoding='utf-8') as f:
            json.dump(all_results, f, ensure_ascii=False, indent=2)
        print(f"\n✓ 所有结果已保存: {all_results_file}")
        
        self.generate_report(all_results)
        
        return all_results
    
    def generate_report(self, results: List[Dict[str, Any]]):
        """生成更新报告"""
        total = len(results)
        success = sum(1 for r in results if r['status'] == 'success')
        invalid = sum(1 for r in results if r['status'] == 'invalid')
        no_price = sum(1 for r in results if r['status'] == 'no_price')
        errors = sum(1 for r in results if r['status'] == 'error')
        
        report = f"""
价格更新报告
{'='*60}
更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
总产品数: {total}
成功更新: {success}
无价格: {no_price}
无效页面: {invalid}
失败/错误: {errors}
成功率: {success/total*100:.1f}%
{'='*60}

异常产品列表:
"""
        
        for r in results:
            if r['status'] != 'success':
                report += f"\n- 行{r['excel_row']}: {r['model']} - {r['color']}"
                if r['status'] == 'error':
                    report += f"\n  错误: {r.get('error', 'Unknown')}"
                elif r['status'] == 'invalid':
                    report += f"\n  状态: 无效页面"
                    report += f"\n  标题: {r.get('title', '')}"
                elif r['status'] == 'no_price':
                    report += f"\n  状态: 页面无价格"
        
        report_file = self.output_dir / "update_report.txt"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(report)
        print(f"\n报告已保存: {report_file}")


async def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='批量更新1688产品价格')
    parser.add_argument('excel_file', help='Excel文件路径')
    parser.add_argument('--batch-size', type=int, default=20, help='每批处理的产品数量')
    parser.add_argument('--start-batch', type=int, default=0, help='起始批次编号')
    parser.add_argument('--max-batches', type=int, help='最大批次数量')
    parser.add_argument('--cookie-file', default='1688cookie.json', help='Cookie文件路径')
    
    args = parser.parse_args()
    
    updater = BatchPriceUpdater(args.excel_file, args.cookie_file)
    await updater.run_batch_update(
        batch_size=args.batch_size,
        start_batch=args.start_batch,
        max_batches=args.max_batches
    )


if __name__ == '__main__':
    asyncio.run(main())
