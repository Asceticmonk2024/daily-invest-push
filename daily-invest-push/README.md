# 💰 莎总你好 — 每日投资早报自动推送

基于 [Day1Global-Skills](https://github.com/star23/Day1Global-Skills) 的每日投资分析，使用 **DeepSeek API**（超便宜），通过 GitHub Actions 每天自动生成 → 推送到莎总的微信。

**莎总不需要翻墙、不需要装任何东西，只需要微信扫一次码，以后每天早上自动收到投资日报。**

---

## 📋 每天推送什么？

| 模块 | 内容 | 风格 |
|------|------|------|
| 📊 美股市场速览 | 三大指数、市场情绪、行业亮点 | 大白话，零术语 |
| 🌊 资金面分析 | 美联储态度、利率、美元走势 | "钱多不多"翻译版 |
| ₿ 比特币动态 | 价格、情绪、机构动向、周期 | 可选，默认开启 |

---

## 🚀 部署指南（10分钟搞定）

### 第一步：Fork 仓库

点右上角 **Fork**，复制到你自己的 GitHub。

### 第二步：获取 DeepSeek API Key

1. 打开 https://platform.deepseek.com/
2. 注册 → 左侧菜单「API Keys」→ 创建
3. 充值 ¥5（能跑大半年，每天约 ¥0.01）

### 第三步：设置微信推送（三选一）

#### 推荐：Server酱（最简单）

1. 打开 https://sct.ftqq.com/ → 用 GitHub 帐号登录
2. 左侧「通道配置」→ 选「方糖服务号」
3. **让莎总扫页面上的二维码**，关注「方糖」公众号（扫一次就行）
4. 复制你的 **SendKey**（在「Key & API」页面）

#### 备选A：PushPlus

1. 打开 https://www.pushplus.plus/ → 微信扫码登录
2. 获取 **Token**
3. 让莎总也关注 PushPlus 公众号
4. 「一对多推送」中添加她

#### 备选B：企业微信 Webhook

1. 企业微信建一个双人群 → 群设置 → 群机器人 → 获取 **Webhook URL**

### 第四步：配置 GitHub Secrets

仓库 → **Settings → Secrets and variables → Actions → New repository secret**

| Secret 名称 | 值 | 必填 |
|---|---|---|
| `DEEPSEEK_API_KEY` | DeepSeek API Key，形如 `sk-...` | ✅ |
| `PUSH_CHANNEL` | `serverchan` 或 `pushplus` 或 `wecom` | ✅ |
| `PUSH_TOKEN` | 对应渠道的 Token / SendKey / Webhook URL | ✅ |
| `GF_NAME` | 对她的称呼，默认 `莎总` | 选填 |
| `ENABLE_BTC` | `true` 或 `false`，默认 true | 选填 |

### 第五步：启用 Actions

1. 仓库 **Actions** 标签页
2. 点 **I understand my workflows, go ahead and enable them**
3. 搞定！每天北京时间早 8 点自动推送

### 测试一下？

Actions 页 → 左侧 **💰 莎总你好 — 每日投资早报** → **Run workflow** → 确认

约 30 秒后莎总微信就收到了 🎉

---

## ⏰ 改推送时间

编辑 `.github/workflows/daily-push.yml` 的 cron：

```yaml
# 北京时间 = UTC + 8
# 早 7:00 → cron: '0 23 * * *'   (前一天 UTC 23:00)
# 早 8:00 → cron: '0 0 * * *'    ← 默认
# 早 9:00 → cron: '0 1 * * *'
# 中 12:00 → cron: '0 4 * * *'
# 晚 10:00 → cron: '0 14 * * *'  (晚报模式)
# 只推工作日 → cron: '0 0 * * 1-5'
```

---

## 💸 费用

| 项目 | 费用 |
|------|------|
| GitHub Actions | 免费 |
| DeepSeek API | 每天约 ¥0.01（充 ¥5 跑大半年） |
| Server酱/PushPlus | 免费 |
| **总计** | **几乎免费** |

---

## 🎨 莎总收到的效果

```
💰 莎总你好 | 06月05日 周五

莎总早！先看看市场再搞钱💪

---

📊 美股市场速览

昨晚美股整体表现不错 📈 纳斯达克涨了0.8%，
AI概念继续带飞，英伟达又创新高了💎
市场情绪中性偏乐观，还没到过热的程度🟢

💡 建议：正常关注就好，不追高

---

🌊 资金面（钱多不多？）

简单说：市场上的钱还挺充裕💧
美联储最近没那么凶了，降息的预期在升温☀️
美元稍微走弱了一点，对股市是好事～

📊 总结：水位正常偏多，鱼还好抓🐟

---

₿ 比特币动态

BTC 目前在 $108,000 附近晃悠，周涨 3% 📈
大户最近在慢慢买入🐳 散户情绪偏亢奋🔥

💡 判断：偏热，拿着的继续拿，别追高

---

⚠️ 以上分析仅供参考，投资要量力而行哦～
💕 莎总今天也加油！
```

---

## ⚠️ 免责声明

所有分析由 AI 生成，仅供学习参考，不构成投资建议。投资有风险，决策需谨慎。

## 致谢

- [Day1Global-Skills](https://github.com/star23/Day1Global-Skills) — 投资分析框架
- [DeepSeek](https://platform.deepseek.com/) — AI 模型
- [Server酱](https://sct.ftqq.com/) / [PushPlus](https://www.pushplus.plus/) — 微信推送
