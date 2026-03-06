# 1688商品调研工具

基于Playwright浏览器自动化的1688商品调研工具，支持Cookie登录方式自动获取商品详细信息。

## 功能特性

- ✅ Cookie自动登录（首次设置后无需手动登录）
- ✅ **关键词搜索商品** - 支持中文URL编码，避免乱码
- ✅ **商品详情调研** - 从详情页提取详细规格、价格、销量
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

### 2. 搜索商品（关键词搜索）

```bash
python -m src.search --keyword "手机支架"
```

脚本将自动：
1. 加载Cookie并登录1688
2. 打开搜索页面（关键词自动URL编码，避免乱码）
3. 提取前20个商品结果
4. 保存到CSV文件

### 3. 调研商品详情

从搜索结果获取商品URL后，调研具体商品：

```bash
python -m src.research --url "商品URL" --name "商品名"
```

## 输出格式

### 搜索结果 (`output/1688_search_results.csv`)

| 字段 | 说明 |
|------|------|
| 序号 | 行号 |
| 商品标题 | 商品标题 |
| 价格 | 价格 |
| 图片 | 图片URL |
| 链接 | 商品URL |

### 商品详情结果 (`output/1688_product_detail.csv`)

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

## 命令行参数

### 搜索脚本 (`src/search.py`)

| 参数 | 说明 |
|------|------|
| `--keyword` | 搜索关键词（必需） |
| `--cookie` | Cookie文件路径（默认：1688cookie.json） |
| `--headless` | 无头模式运行 |
| `--max` | 最大结果数（默认：20） |

### 详情调研脚本 (`src/research.py`)

| 参数 | 说明 |
|------|------|
| `--url` | 1688商品详情URL（必需） |
| `--name` | 商品名称（用于CSV输出） |
| `--cookie` | Cookie文件路径（默认：1688cookie.json） |
| `--headless` | 无头模式运行 |

## 关键词URL编码说明

本工具自动处理中文关键词的URL编码，确保搜索不会出现乱码：

- 输入：`手机支架`
- 编码后：`%E6%89%8B%E6%9C%BA%E6%94%AF%E6%9E%B6`
- 搜索URL：`https://s.1688.com/youyuan/index.htm?tab=search&keywords=%E6%89%8B%E6%9C%BA%E6%94%AF%E6%9E%B6`

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
│   ├── search.py           # 搜索脚本（新增）
│   └── research.py         # 详情调研脚本
└── output/
    ├── 1688_search_results.csv     # 搜索结果
    └── 1688_product_detail.csv     # 详情调研结果
```

## 注意事项

- ✅ **URL编码**：关键词自动URL编码，避免搜索乱码
- Cookie有效期：Cookie会过期，需要定期刷新
- PLUS会员折扣：需要1688 PLUS会员账号才能获取
- 请求频率：不要在短时间内发送过多请求，以免被封禁

## 常见问题

### 搜索返回0结果
- 检查Cookie是否有效且未过期
- 尝试非无头模式运行，查看是否需要验证

### 登录失败
- 请刷新Cookie文件，使用最新的浏览器Cookie

### 触发反爬虫验证
- 脚本默认使用headless=False模式，方便手动验证
- 如触发验证，请在浏览器窗口中手动完成

## 技术栈

- Python 3.8+
- Playwright（浏览器自动化）
- pandas（数据处理）
- CSV（数据导出）
