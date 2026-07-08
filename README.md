# trend-radar 🛰

Daily GitHub Trending digest — 每天自动抓取 GitHub Trending,筛出**新上榜**项目,
用 LLM 逐个分析评分并生成当日综述,以 HTML 日报发送到邮箱。零服务器,跑在 GitHub Actions 上。

## 特性

- **只报新货**:SQLite 记录近 14 天榜单,重复上榜的老项目不再打扰你
- **AI 两轮分析**:逐项目输出一句话总结/分类/解决的问题/关注度评分(1-5),再汇总成当日趋势综述
- **结构化输出**:分析走 OpenAI structured output,严格 JSON,单项目失败不影响整批
- **安全加固**:邮件模板开启 autoescape 防 HTML 注入;第三方 README 内容隔离在
  `<repo_data>` 标签中防提示词注入;repo 名称白名单校验
- **零运维**:GitHub Actions 每日定时运行,history.db 自动 commit 回仓库持久化

## 本地试跑

```bash
conda create -n trend-radar python=3.12 -y && conda activate trend-radar
pip install -r requirements.txt

python main.py --collect        # 只抓取入库(每晚采集模式)
python main.py --dry-run        # 日报干跑:打印候选,不调 AI 不发邮件

cp .env.example .env            # 填好凭据后:
set -a && source .env && set +a
python main.py                  # 完整流程,跑完查收邮件
```

## 部署(GitHub Actions)

1. 推送仓库到 GitHub
2. Settings → Secrets and variables → Actions → 添加 Secrets:
   `OPENAI_API_KEY` `SMTP_HOST` `SMTP_PORT` `SMTP_USER` `SMTP_PASS` `MAIL_TO`
3. Settings → Actions → General → Workflow permissions 选 **Read and write permissions**
   (机器人需要把 history.db commit 回仓库)
4. Actions 页手动 Run workflow 验证(可选 digest / collect 模式)。之后自动运行:
   每晚北京时间 20:00 采集入库(零 AI 成本),周一/三/五早 08:00 发日报,
   覆盖自上次日报以来攒下的全部新项目;分析失败的候选下次日报自动重试

Gmail 发件:开启两步验证后在 myaccount.google.com/apppasswords 创建应用专用密码,
去掉空格填入 `SMTP_PASS`。

可选配置(Variables):`OPENAI_MODEL`(默认 gpt-4o-mini)、
`TRENDING_LANGUAGES`(默认 `,python,typescript`,空串代表总榜)。

## 项目结构

```
scraper.py    抓 trending HTML + GitHub API 补元数据/README
store.py      SQLite 快照,近 14 天去重
analyzer.py   OpenAI 两轮分析:逐 repo 结构化 JSON + 当日综述
mailer.py     Jinja2 渲染 HTML(autoescape)+ SMTP 发送
main.py       流程编排,支持 --dry-run
.trellis/     spec 与任务卡片(任务拆解)
data/         history.db,由 CI 自动更新
```

## 日常开发

机器人每天会往 `main` 提交一次 `data/history.db`,本地 push 前先:

```bash
git pull --rebase origin main
```
