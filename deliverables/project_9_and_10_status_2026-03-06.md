# 彩友乐 AI 需求 — 项目 9 & 项目 10 阶段记录（2026-03-06）

> 目的：沉淀“我们做了什么、做到哪、踩了哪些坑、有哪些可复用配置/代码片段”。

## 项目 9：出口政策/合规变化提醒（按品类定向，出口管制优先）

### 1. 需求口径（已确认）
- 覆盖区域：**中国 / 美国 / 新加坡**
- 优先主题：**出口管制**（制裁/实体清单/许可证/最终用户最终用途等）
- 品类定向：主营品类关键词（拍立得周边产品、拍立得相机包、拍立得相框）
- 输出：投递到 **本飞书群**
- 颗粒度：只需要 **信息来源链接（URL）**；不要求截图
- 去噪策略：**权威源优先（宁少但准）**

### 2. 方法论/流程（已沉淀）
统一框架：**数据源抓取 → 过滤归类 → 分级（P0/P1）→ 摘要 → 定时投递 → 可追溯**

- 无命中：允许**静默**（不刷屏）
- 异常（抓取失败/403/404/空结构）：必须**告警**并带失败源 URL 与原因

### 3. 当前实现状态（OpenClaw 配置落地）
已创建 cron 定时任务（工作日 2 次）：
- Job 名称：`信息洞察-9 出口管制预警（工作日2次）`
- Job ID：`8b8e5cd6-579f-4006-a3b7-edc5a1949dc0`
- Schedule：`30 9,16 * * 1-5`（Asia/Shanghai）
- SessionTarget：`isolated`

#### 3.1 cron payload（关键“代码”片段）
> 该段是当前生产逻辑的“可复用代码”；后续主要在“权威源入口白名单”与“过滤词表”迭代。

- 时间范围：**近 7 天**（从原本 24h 扩大）
- 核心规则：
  1) web_fetch 抓取白名单入口页
  2) 提取近 7 天内与“出口管制/制裁/实体清单/许可证/最终用户最终用途”相关更新
  3) 同时需命中：品类/材质关键词（命中其一即可）
  4) 无命中静默；抓取失败必告警
  5) 命中时按模板输出：标题【出口管制预警 P0/P1】【国家/区域】【品类】+ 结论/影响/建议动作/来源 URL

#### 3.2 权威源白名单（v0.2）
- US BIS：
  - https://www.bis.gov/
  - https://www.bis.gov/regulations/ear
- US Treasury press releases：
  - https://home.treasury.gov/news/press-releases
- OFAC：
  - https://ofac.treasury.gov/
- Consolidated Screening List（CSL search）：
  - https://www.trade.gov/data-visualization/csl-search
- SG Customs：
  - https://www.customs.gov.sg/news/
- CN MOFCOM（每日更新摘要，按近 7 天收集）：
  - https://www.mofcom.gov.cn/fzlm/mrgx/index.html

### 4. 本次跑批结果（2026-03-06 手动触发）
- 触发方式：cron `run`（立即运行）
- 现象：
  - 抓取失败告警出现过：
    - `http://english.mofcom.gov.cn/article/policyrelease/` → `web_fetch` 抓取失败（fetch failed）
    - `https://home.treasury.gov/news/press-releases` → 可访问但抽取结果为空结构/只拿到标题（疑似动态渲染/反爬）
  - 命中：在“成功抓取”的入口中，未发现同时满足强主题 + 品类/材质关键词的条目，因此按规则不输出日报正文。

### 5. 待办/下一步迭代
- 把 Treasury / BIS 的信息源换为更“列表友好/RSS友好”的入口，减少空结构。
- 中国源已明确使用 `mrgx`（每日更新摘要），下一步是验证其近 7 天列表结构稳定性。

---


## 项目 10：热点/趋势抓取（设计元素 + 市场热度）每周趋势简报

### 1. 需求口径（已确认）
- 部门：运营 / 设计 / 市场
- 渠道：小红书（MVP），后续可扩抖音/微博
- 投递：本飞书群
- 输出频率：每周趋势简报（每周一 10:00）
- 输出要求：**只保留信息来源链接（URL）**；不作为唯一决策依据

### 2. 当前实现状态（OpenClaw 配置落地）
已创建 cron 定时任务（每周一）：
- Job 名称：`信息洞察-10 小红书趋势简报（每周一）`
- Job ID：`ec3d9975-338a-4493-b364-cd39e26740c3`
- Schedule：`0 10 * * 1`（Asia/Shanghai）
- SessionTarget：`isolated`

#### 2.1 cron 输出结构（模板）
1) TOP5 主题（每条：一句话趋势 + 1-3 个来源链接）
2) 设计元素总结（配色 / 材质工艺 / 结构功能点）
3) 风险提示（同质化 / 侵权 / 审美泡沫等）
4) 下周建议动作（≤3 条）

### 3. 当前阻塞（已定位）
- xiaohongshu MCP 返回 **未登录**，且自动化/隔离浏览器访问小红书触发风控/断连：
  - 风控提示：`300012`（IP 存在风险）
  - 或：`ERR_CONNECTION_CLOSED`
- 根因定位：macOS 系统全局代理指向 `127.0.0.1:7891`（HTTP/HTTPS/SOCKS 均开启），小红书对代理出口敏感。
- 处理尝试：按王子渊授权，做“仅小红书域名绕过代理”（bypass domains 增加 `xiaohongshu.com` / `*.xiaohongshu.com` / `*.xhscdn.com` / `*.xhslink.com`）。
- 结果：绕过后出现直连被断（ERR_CONNECTION_CLOSED），说明当前网络出口对直连小红书不通/被拦。

### 4. 可行解法（下一步）
- 方案 A（推荐）：切换到可直连且不触发风控的网络出口（如手机热点）后完成一次登录。
- 方案 B：Browser Relay 接管用户本机已登录的小红书 tab（不依赖本机网络出口）。

---

## 附：关键工具/安装记录
- skill 安装：`rss-digest`（odysseus0/feed@rss-digest）
- 依赖安装：Homebrew 安装 `feed` CLI（`feed version 0.2.0`）
- cron 已建立：项目 9（工作日2次）；项目 10（每周一）

> 注：项目 10 的 cron 当前会因小红书未登录/网络风控失败而告警；业务已决定先跳过 10，可后续禁用/删除。
