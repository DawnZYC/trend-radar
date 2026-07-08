---
id: T9
title: 收集/日报分离 — 每晚收集,一三五早上发报
status: done
depends: [T2, T4]
---

## 内容

- `main.py --collect`:只抓取 + 入库,不调 AI 不发邮件
- `store`:新增 `reported` 表;`unreported_new(date, lookback_days=4)` 取
  「近 N 天首次上榜且未进过日报」的 repo;发报成功后 `mark_reported`
- 日报模式:当天抓取 + 历史未报候选合并,分析后发送
- `daily.yml`:双 cron —— 每晚 20:00(北京)collect,一三五 08:00(北京)digest;
  workflow_dispatch 支持手动选模式

## 验收

- collect 不发邮件只入库;digest 覆盖自上次日报以来的所有新项目
- 已报过的项目不会重复出现;分析失败的下次日报自动重试
