# trend-radar 🛰

每天自动抓取 GitHub Trending,筛出新上榜项目,用 OpenAI 分析后生成 HTML 日报发到邮箱。
零服务器,跑在 GitHub Actions 上。

## 本地试跑

```bash
pip install -r requirements.txt
python main.py --dry-run        # 只抓取+去重,不调 AI 不发邮件
cp .env.example .env            # 填好后:
set -a && source .env && set +a
python main.py                  # 完整流程
```

## 部署(GitHub Actions)

1. 推送本仓库到 GitHub
2. Settings → Secrets and variables → Actions,添加 Secrets:
   `OPENAI_API_KEY`、`SMTP_HOST`、`SMTP_PORT`、`SMTP_USER`、`SMTP_PASS`、`MAIL_TO`
3. (可选)Variables:`OPENAI_MODEL`、`TRENDING_LANGUAGES`
4. Actions 页面手动 Run workflow 验证,之后每天 UTC 00:00 自动运行

Gmail 发件需在 Google 账号开启两步验证后创建「应用专用密码」填入 `SMTP_PASS`。

## 项目结构

```
scraper.py    抓 trending HTML + GitHub API 补元数据/README
store.py      SQLite 快照,近 14 天去重
analyzer.py   OpenAI 两轮分析:逐 repo 结构化 JSON + 当日综述
mailer.py     Jinja2 渲染 HTML + SMTP 发送
main.py       流程编排,支持 --dry-run
.trellis/     spec 与任务卡片(任务拆解)
```
