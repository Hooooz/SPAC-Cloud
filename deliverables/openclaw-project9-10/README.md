# OpenClaw 项目 9 & 10（可迁移执行包）

> 目标：在另一台电脑/另一套 OpenClaw 环境中，快速复现项目 9/10 的定时任务（cron）与依赖。

## 项目 9：出口管制/合规变化提醒（工作日 2 次）

- Schedule：工作日 `09:30`、`16:30`（Asia/Shanghai）
- 规则：权威源优先（宁少但准）；近 7 天；无命中静默；抓取失败告警；命中按 P0/P1 模板发群。
- 白名单（v0.2）：见 `cron_jobs.json`。

### 依赖
- OpenClaw：需要可用的 `cron` 功能。
- 抓取：使用 OpenClaw 内置 `web_fetch`。

> 注：rss-digest/feed 已在当前机器安装并跑通，但项目 9 的实现并不强依赖 feed；仍建议未来将部分站点切换为 RSS 更稳。

## 项目 10：小红书趋势简报（每周一）

- Schedule：每周一 `10:00`（Asia/Shanghai）
- 输出：TOP5 主题 + 设计元素总结 + 风险提示 + 下周建议动作；只保留来源链接。
- 依赖：需要小红书抓取能力（例如现有 `xiaohongshu` skill/MCP）且账号已登录。

### 已知阻塞（需在新环境解决）
- 小红书可能触发风控（300012）或直连断开（ERR_CONNECTION_CLOSED），与网络出口/代理强相关。
- 可行解法：手机热点干净出口完成一次登录；或 Browser Relay 接管本机已登录 tab。

## 如何在新环境创建 cron

在 OpenClaw 中使用 cron API/工具创建（或用你们已有的管理界面/CLI）。

- 直接复制 `cron_jobs.json` 里的 job 对象。
- 注意：`jobId` 在不同环境会不同；创建时不要带旧 jobId。

