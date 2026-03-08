# 1688 Skills 安装说明

## 📦 包含的Skills

本仓库包含两个专门用于1688产品调研的Claude Code Skills:

### 1. 1688-price-update (价格更新)
**功能**: 更新飞书多维表格中已有产品的最新价格

**使用场景**:
- 定期更新产品价格
- 追踪价格变化趋势
- 批量刷新价格数据

**触发词**: "更新价格"、"查最新价格"、"刷新价格"、"价格追踪"

### 2. 1688-product-search (产品搜索)
**功能**: 在1688搜索新产品并添加到飞书多维表格

**使用场景**:
- 寻找新产品供应商
- 发现产品替代方案
- 扩展产品目录

**触发词**: "搜索新产品"、"找货源"、"搜索1688"、"添加新产品"

---

## 🚀 安装步骤

### 前置要求

1. **Python 3.8+**
2. **Playwright** (用于浏览器自动化)
3. **飞书账号** (用于多维表格操作)
4. **1688账号** (用于访问产品页面)

### 步骤1: 安装依赖

```bash
# 安装Python依赖
pip install playwright pandas

# 安装Playwright浏览器
playwright install chromium
```

### 步骤2: 安装Skills

将skills文件夹复制到你的Claude Code配置目录:

**macOS/Linux**:
```bash
# 复制到Claude Code skills目录
cp -r 1688-price-update ~/.trae/skills/
cp -r 1688-product-search ~/.trae/skills/
cp -r shared ~/.trae/skills/
```

**Windows**:
```powershell
# 复制到Claude Code skills目录
Copy-Item -Recurse 1688-price-update $env:USERPROFILE\.trae\skills\
Copy-Item -Recurse 1688-product-search $env:USERPROFILE\.trae\skills\
Copy-Item -Recurse shared $env:USERPROFILE\.trae\skills\
```

### 步骤3: 配置1688 Cookie

1. 打开浏览器访问 https://www.1688.com
2. 登录你的1688账号
3. 完成任何验证(如滑块验证)
4. 打开浏览器开发者工具 (F12)
5. 进入 Application → Cookies → https://www.1688.com
6. 导出所有cookies为JSON格式
7. 保存为 `1688cookie.json` 到项目根目录

**Cookie示例格式**:
```json
[
  {
    "name": "cookie_name",
    "value": "cookie_value",
    "domain": ".1688.com",
    "path": "/",
    "sameSite": "Lax"
  }
]
```

### 步骤4: 配置飞书访问 (可选)

如果需要直接操作飞书多维表格:

1. 创建飞书开放平台应用
2. 获取 App ID 和 App Secret
3. 配置多维表格权限
4. 在Claude Code中配置飞书MCP工具

---

## 📖 使用指南

### 更新产品价格

**方式1: 通过Claude Code对话**
```
用户: 帮我更新飞书表格里所有产品的最新价格
Claude: [自动触发1688-price-update skill]
```

**方式2: 直接运行脚本**
```bash
# 更新CSV文件中的价格
python3 shared/scripts/update_prices.py your_products.csv

# 检查单个产品价格
python3 shared/scripts/enhanced_price_extractor.py "产品链接"

# 批量检查价格
python3 shared/scripts/batch_detailed_prices.py "链接1" "链接2" "链接3"
```

### 搜索新产品

**方式1: 通过Claude Code对话**
```
用户: 帮我在1688上搜索指甲刀产品,找一些价格便宜的
Claude: [自动触发1688-product-search skill]
```

**方式2: 直接运行脚本**
```bash
# 搜索产品
python3 shared/scripts/browser_1688.py search "指甲刀"
```

---

## 🎯 功能特点

### 增强版价格提取器

使用Playwright实现的价格提取器,可以获取:

- ✅ **详细价格区间** - 完整的价格文本信息
- ✅ **SKU价格列表** - 不同规格的价格
- ✅ **MOQ价格** - 阶梯价格信息
- ✅ **促销价格** - 优惠券、折扣信息
- ✅ **会员价格** - PLUS会员专享价
- ✅ **销量信息** - 已售数量
- ✅ **店铺信息** - 店铺名称、评分等
- ✅ **地点信息** - 发货地点
- ✅ **产品图片** - 多张产品图片

### 智能反爬虫处理

- 随机延迟避免检测
- Cookie认证绕过登录
- 非headless模式处理验证
- 请求频率控制

### 飞书集成

- 自动读取飞书多维表格
- 批量更新价格信息
- 添加新产品记录
- 字段自动映射

---

## 📂 文件结构

```
1688-skills/
├── 1688-price-update/          # 价格更新skill
│   ├── SKILL.md                # Skill说明文档
│   └── evals/                  # 测试用例
│       └── evals.json
├── 1688-product-search/        # 产品搜索skill
│   ├── SKILL.md                # Skill说明文档
│   └── evals/                  # 测试用例
│       └── evals.json
├── shared/                     # 共享组件
│   └── scripts/                # Python脚本
│       ├── browser_1688.py              # 基础浏览器自动化
│       ├── enhanced_price_extractor.py  # 增强版价格提取器
│       ├── update_prices.py             # 批量更新价格
│       ├── batch_detailed_prices.py     # 批量详细价格提取
│       └── check_single_price.py        # 单个产品价格检查
└── README.md                   # 本文档
```

---

## 🔧 高级配置

### 自定义等待时间

编辑 `enhanced_price_extractor.py`:

```python
# 修改页面加载等待时间(毫秒)
await self.page.wait_for_timeout(5000)  # 默认5秒

# 修改请求间隔时间
await asyncio.sleep(3)  # 默认3秒
```

### 添加自定义选择器

如果1688页面结构变化,可以在 `enhanced_price_extractor.py` 中更新选择器:

```python
price_selectors = [
    '.price-text',
    '.price-value',
    # 添加新的选择器
    '.new-price-class'
]
```

---

## 🐛 故障排除

### 问题1: Cookie过期

**症状**: 无法访问产品页面,提示登录

**解决**:
1. 重新登录1688.com
2. 导出新的cookies
3. 更新 `1688cookie.json`

### 问题2: 价格提取失败

**症状**: 价格显示为None或错误

**解决**:
1. 检查页面是否完全加载
2. 增加等待时间
3. 更新CSS选择器
4. 使用非headless模式调试

### 问题3: 反爬虫拦截

**症状**: 频繁出现验证码

**解决**:
1. 增加请求间隔时间
2. 使用非headless模式
3. 手动完成验证后继续
4. 更换IP或使用代理

### 问题4: 飞书API错误

**症状**: 无法访问多维表格

**解决**:
1. 检查飞书应用权限
2. 验证access token
3. 确认多维表格ID正确
4. 检查网络连接

---

## 📊 输出示例

### 价格更新报告

```
价格更新报告
================
总产品数: 50
成功更新: 45
失败/失效: 5

价格变动:
- 上涨: 3个产品
- 下降: 8个产品
- 不变: 34个产品

失效链接:
1. [产品名] - 链接已失效
2. [产品名] - 商品已下架

更新时间: 2026-03-08 12:00:00
```

### 详细价格数据 (JSON)

```json
{
  "url": "https://detail.1688.com/offer/123456.html",
  "title": "产品名称",
  "price_range": "¥10.5-15.0",
  "sku_prices": [
    {"text": "¥10.5"},
    {"text": "¥12.0"}
  ],
  "promotion_price": "限时5折",
  "sales": "已售1000+个",
  "shop_name": "店铺名称",
  "location": "浙江金华"
}
```

---

## 🤝 贡献指南

欢迎贡献代码和建议!

1. Fork本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启Pull Request

---

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

---

## 📞 联系方式

如有问题或建议,请通过以下方式联系:

- GitHub Issues: https://github.com/Hooooz/SPAC-Cloud/issues
- Email: your-email@example.com

---

## 🙏 致谢

感谢以下技术和工具:

- [Playwright](https://playwright.dev/) - 浏览器自动化
- [Claude Code](https://www.anthropic.com/) - AI助手
- [飞书](https://www.feishu.cn/) - 协作平台
- [1688](https://www.1688.com/) - B2B电商平台

---

**最后更新**: 2026-03-08  
**版本**: 1.0.0
