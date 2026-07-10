"""trend-radar 主流程。

用法:
    python main.py            # digest:抓取 + 合并未报候选 + AI 分析 + 邮件(一三五早8点)
    python main.py --collect  # collect:只抓取入库,零成本(每晚8点)
    python main.py --dry-run  # digest 干跑:打印候选,不调 AI / 不发邮件
"""
from __future__ import annotations

import argparse
import os
import sys
from datetime import date as date_cls

import scraper
import store

MAX_ANALYZE = int(os.environ.get("MAX_ANALYZE", "25"))


def get_languages() -> list[str]:
    raw = os.environ.get("TRENDING_LANGUAGES", ",python,typescript")
    return [x.strip() for x in raw.split(",")]  # "" 表示总榜


def scrape_and_record(today: str) -> list[scraper.Repo]:
    languages = get_languages()
    print(f"抓取 trending: {languages!r}")
    repos = scraper.fetch_all(languages)
    print(f"      共 {len(repos)} 个 repo")
    if not repos:
        # 页面结构变了或被反爬:让 workflow 变红触发告警,而不是静默继续
        raise RuntimeError("抓取结果为 0,GitHub Trending 页面可能已改版")
    store.record(repos, today)
    return repos


def collect() -> int:
    """每晚采集:只抓取 + 入库。"""
    today = date_cls.today().isoformat()
    scrape_and_record(today)
    print("[collect] 入库完成 ✓")
    return 0


def digest(dry_run: bool = False) -> int:
    """一三五日报:今晨抓取 + 自上次日报以来攒的未报候选,一起分析发送。"""
    today = date_cls.today().isoformat()

    print("[1/4] 抓取并入库")
    repos = scrape_and_record(today)

    print("[2/4] 取未报候选(近 4 天首次上榜、14 天未报道)+ star 暴涨检测")
    pending = store.unreported_new(today)
    scraped = {r.full_name: r for r in repos}
    # 今晨刚抓到的候选优先用带完整元数据的对象
    pending = [scraped.get(r.full_name, r) for r in pending]
    pending_names = {r.full_name for r in pending}

    old_repos = [r for r in repos if r.full_name not in pending_names]
    surges = store.find_surges(old_repos, today)

    candidates = sorted(pending, key=lambda r: r.stars_today, reverse=True)
    candidates = (candidates + surges)[:MAX_ANALYZE]
    print(f"      未报 {len(pending)} 个,暴涨 {len(surges)} 个(合计取前 {MAX_ANALYZE})")

    if dry_run:
        for r in candidates:
            tag = " 🚀surge" if r.is_surge else ""
            print(f"  - {r.full_name}  +{r.stars_today}{tag}  {r.description[:60]}")
        print("[dry-run] 跳过 AI 分析与邮件")
        return 0

    if not candidates:
        print("无新候选,跳过日报")
        return 0

    print("[3/4] AI 分析(并发补 README 元数据后送 OpenAI)")
    from concurrent.futures import ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=8) as pool:
        enriched = list(pool.map(scraper.enrich, candidates))
    import analyzer
    analyses, overview = analyzer.analyze_all(enriched)
    print(f"      成功分析 {len(analyses)} 个")

    print("[4/4] 渲染、存档并发送邮件")
    import mailer
    import archive
    html = mailer.render(today, overview, analyses)
    archive.save(today, overview, analyses)  # 网页版单独渲染
    mailer.send(f"GitHub Trend Radar · {today}", html)

    # 只标记成功进入日报的;分析失败的下次日报自动重试
    store.mark_reported([a["full_name"] for a in analyses], today)
    print("完成 ✓")
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--collect", action="store_true", help="只抓取入库,不分析不发邮件")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    sys.exit(collect() if args.collect else digest(dry_run=args.dry_run))
