---
id: T3
title: analyzer — OpenAI 两轮分析
status: done
depends: [T1]
---

## 内容

- 第一轮 `analyze_repo`:输入 描述+topics+README 片段,structured output 返回
  {summary, category, problem_solved, score(1-5), reason}
- 第二轮 `write_overview`:汇总所有 JSON,产出当日综述 + Top3 推荐
- 模型可配 `OPENAI_MODEL`,默认 gpt-4o-mini

## 验收

- 输出严格 JSON;单 repo 失败不拖垮整批(跳过并记录)
