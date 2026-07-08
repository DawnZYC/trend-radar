---
id: T7
title: 解析测试 + CI
status: done
depends: [T1]
---

## 内容

- scraper 拆出纯函数 `parse_trending(html)`,便于离线测试
- `tests/fixtures/trending.html` 真实页面快照;pytest 覆盖 parse / store 去重与 surge / mailer 转义
- `.github/workflows/ci.yml`:push/PR 跑 pytest
- `main.py`:抓取结果为 0 时抛错退出,让每日 workflow 变红并邮件告警

## 验收

- pytest 全绿;故意破坏 fixture 中的选择器结构时测试能发现
