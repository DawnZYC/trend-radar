---
id: T6
title: 并发化 enrich 与 AI 分析
status: done
depends: [T1, T3]
---

## 内容

- `main.py`:ThreadPoolExecutor(8) 并发 `scraper.enrich`
- `analyzer.analyze_all`:ThreadPoolExecutor(5) 并发 `analyze_repo`,
  结果仍按 score 降序;OpenAI client 线程安全

## 验收

- dry-run 与完整流程行为不变,仅耗时下降
- 单个 repo 失败仍不影响整批
