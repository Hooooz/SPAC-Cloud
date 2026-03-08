# 1688 Skills 安装说明

## 快速安装

### 1. 安装依赖
```bash
pip install playwright pandas
playwright install chromium
```

### 2. 安装Skills

将以下文件夹复制到 `~/.trae/skills/` 目录:
- `1688-price-update/`
- `1688-product-search/`
- `shared/`

**macOS/Linux**:
```bash
cp -r 1688-price-update ~/.trae/skills/
cp -r 1688-product-search ~/.trae/skills/
cp -r shared ~/.trae/skills/
```

### 3. 配置1688 Cookie

1. 登录 https://www.1688.com
2. 打开开发者工具 (F12)
3. Application → Cookies → 导出所有cookies
4. 保存为 `1688cookie.json` 到项目根目录

### 4. 开始使用

**更新价格**:
```
帮我更新飞书表格里所有产品的最新价格
```

**搜索新产品**:
```
帮我在1688上搜索指甲刀产品
```

## 主要功能

- ✅ 详细价格提取 (SKU、MOQ、促销价)
- ✅ 批量价格更新
- ✅ 新产品搜索
- ✅ 飞书多维表格集成
- ✅ 智能反爬虫处理

## 详细文档

查看完整文档: [README.md](README.md)
