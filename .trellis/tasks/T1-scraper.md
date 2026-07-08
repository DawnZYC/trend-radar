---
id: T1
title: scraper — 抓取 Trending + GitHub API 补数据
status: done
depends: []
---

## 内容

- `fetch_trending(language, since="daily")`:解析 github.com/trending HTML,
  返回 [{full_name, description, language, stars, stars_today, url}]
- `enrich(repo)`:GitHub REST API 取 topics、created_at、README 前 3000 字
- 请求带 UA、超时、失败重试;GH_TOKEN 可选

## 验收

- 真实抓取返回 ≥20 个 repo,字段完整
- API 无 token 也能跑(限额内)
