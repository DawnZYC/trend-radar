---
id: T5
title: star 增速追踪 — 暴涨项目重新入选
status: done
depends: [T2]
---

## 内容

- `store.find_surges(repos, date, lookback_days=7, ratio=1.5)`:
  已上过榜的 repo,若当前 star ≥ 上次记录 × ratio,标记 `is_surge` 重新入选
- `Repo` 增加 `is_surge` 字段;分析 prompt 注明"star 近日暴涨"
- 邮件卡片加 🚀 标记

## 验收

- 模拟旧快照(低 star)后,当前高 star 的老项目被识别为 surge
- 未暴涨的老项目仍被去重排除
