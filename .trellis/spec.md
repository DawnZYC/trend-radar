# trend-radar — Spec

## 目标

每天自动抓取 GitHub Trending,筛出「新上榜/值得关注」的项目,用 OpenAI API 做结构化分析,
生成 HTML 日报发送到邮箱。零服务器,跑在 GitHub Actions 上。

## 数据流

```
GitHub Actions cron (每天 00:00 UTC)
  → scraper: 抓 github.com/trending (总榜 + 指定语言榜)
  → scraper: GitHub REST API 补元数据 + README
  → store:   SQLite 快照,筛出新上榜 repo
  → analyzer: OpenAI 逐 repo 结构化分析(JSON) + 当日综述
  → mailer:  Jinja2 渲染 HTML → SMTP 发送
  → 提交 data/history.db 回仓库(持久化)
```

## 非目标(v1 不做)

- Web 界面 / 数据库服务
- star 增量曲线追踪
- 多收件人订阅管理

## 配置(环境变量 / Actions Secrets)

| 变量 | 说明 |
|---|---|
| `OPENAI_API_KEY` | OpenAI API key |
| `OPENAI_MODEL` | 默认 `gpt-4o-mini` |
| `GH_TOKEN` | GitHub token(提高 API 限额,可选) |
| `SMTP_HOST` / `SMTP_PORT` | 默认 Gmail smtp.gmail.com:587 |
| `SMTP_USER` / `SMTP_PASS` | 发件邮箱 + 应用专用密码 |
| `MAIL_TO` | 收件人 |
| `TRENDING_LANGUAGES` | 逗号分隔,如 `,python,typescript`(空串=总榜) |

## 验收标准

1. 本地 `python main.py --dry-run` 可完整跑通抓取→去重→(跳过 AI/邮件)输出候选列表
2. 重复运行同一天不会把老项目再次判为"新上榜"
3. AI 输出为严格 JSON(structured output),含总结/分类/评分 1-5/理由
4. 邮件为可读性良好的 HTML,含当日综述 + 逐项目卡片
