---
id: T4
title: mailer + main + GitHub Actions
status: done
depends: [T2, T3]
---

## 内容

- `mailer.py`:Jinja2 模板渲染 HTML(综述 + 项目卡片),smtplib STARTTLS 发送
- `main.py`:编排全流程,`--dry-run` 跳过 AI 与邮件
- `.github/workflows/daily.yml`:cron 每日运行,跑完 commit history.db

## 验收

- dry-run 本地跑通;yml 语法正确
