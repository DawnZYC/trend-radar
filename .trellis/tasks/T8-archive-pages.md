---
id: T8
title: 日报存档 + GitHub Pages
status: done
depends: [T4]
---

## 内容

- `archive.py`:每日日报 HTML 存 `docs/YYYY-MM-DD.html`,并重建 `docs/index.html`(按日期倒序)
- `main.py` 发邮件后调用存档;`daily.yml` 一并 commit `docs/`
- 部署:Settings → Pages → Deploy from a branch → main → /docs

## 验收

- 本地运行后 docs/ 下生成日期页和索引页;索引倒序、链接可点
