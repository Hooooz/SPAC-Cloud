# 1688商品调研工具

基于Playwright浏览器自动化的1688商品调研工具，支持Cookie登录方式自动获取商品详细信息。

## 功能特性

- ✅ Cookie自动登录（首次设置后无需手动登录）
- ✅ 1688首页搜索商品
- ✅ 提取详细的商品信息：
  - 产品名称（作为型号）
  - 颜色规格
  - 销量数据
  - 阶梯价格（不同起订量的价格）
  - 商品图片
  - 商品链接
- ✅ 导出CSV格式报表

## 安装

```bash
# 安装依赖
pip install -r requirements.txt

# 安装Playwright浏览器
playwright install chromium
```

## 快速开始

### 1. 准备Cookie文件

使用Chrome浏览器插件（如"EditThisCookie"或"Cookie-Editor"）导出1688的Cookie。

将Cookie保存为JSON格式到项目根目录的`1688cookie.json`文件中。

### 2. 配置商品URL

编辑`src/research.py`中的`product_url`变量，指定要调研的1688商品页面。

### 3. 运行调研

```bash
python -m src.research
```

脚本将自动：
1. 加载Cookie并登录1688
2. 访问商品详情页
3. 提取商品信息
4. 保存到CSV文件

## 输出格式

调研结果保存到`output/1688_product_detail.csv`，包含以下字段：

| 字段 | 说明 |
|------|------|
| 型号 | 产品名称（作为型号） |
| 颜色 | 颜色规格 |
| 一年内销量 | 销量数据 |
| 图片 | 商品图片URL |
| 起订量 | 最小起订量 |
| 1688价格 | 商品价格 |
| PLUS会员95折 | PLUS会员折扣（需要PLUS账号） |
| 链接 | 商品URL |

每个阶梯价格会单独生成一行记录。

## Cookie设置步骤

1. 在Chrome浏览器安装Cookie扩展（如EditThisCookie）
2. 访问1688.com并登录
3. 导出1688.com域名的Cookie
4. 保存为JSON格式到`1688cookie.json`

## 项目结构

```
1688-product-research-skill/
├── SKILL.md                 # 技能定义文件
├── README.md                # 中文说明文档
├── README_EN.md             # English documentation
├── requirements.txt         # Python依赖
├── 1688cookie.json         # Cookie文件（需要自行创建）
├── src/
│   └── research.py         # 主程序
└── output/
    └── 1688_product_detail.csv  # 调研结果
```

## 注意事项

- Cookie有效期：Cookie会过期，需要定期刷新
- PLUS会员折扣：需要1688 PLUS会员账号才能获取
- 请求频率：不要在短时间内发送过多请求，以免被封禁

## 常见问题

### 登录失败
- 请刷新Cookie文件，使用最新的浏览器Cookie

### 触发反爬虫验证
- 脚本默认使用headless=False模式，方便手动验证
- 如触发验证，请在浏览器窗口中手动完成

### 价格提取失败
- 检查商品页面结构是否发生变化
- 相应更新脚本中的正则表达式

## 技术栈

- Python 3.8+
- Playwright（浏览器自动化）
- pandas（数据处理）
- CSV（数据导出）
