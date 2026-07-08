---
id: T2
title: store — SQLite 历史与去重
status: done
depends: []
---

## 内容

- 表 `sightings(full_name, date, stars, stars_today)`,主键 (full_name, date)
- `filter_new(repos, lookback_days=14)`:近 N 天未上过榜的才算"新上榜"
- `record(repos, date)` 幂等

## 验收

- 同日重复运行结果一致;昨日已报项目今日不再入选
