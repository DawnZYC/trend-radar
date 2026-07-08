"""trend-radar 主流程:抓取 → 去重 → AI 分析 → 邮件。

用法:
    python main.py            # 完整流程
    python main.py --dry-run  # 只跑抓取+去重,打印候选,不调 AI / 不发邮件
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


def run(dry_run: bool = False) -> int:
    today = date_cls.today().isoformat()
    languages = get_languages()

    print(f"[1/4] 抓取 trending: {languages!r}")
    repos = scraper.fetch_all(languages)
    print(f"      共 {len(repos)} 个 repo")

    print("[2/4] 去重(近 14 天未上榜)+ star 暴涨检测")
    new_repos = store.filter_new(repos, today)
    new_names = {r.full_name for r in new_repos}
    old_repos = [r for r in repos if r.full_name not in new_names]
    surges = store.find_surges(old_repos, today)
    store.record(repos, today)

    candidates = sorted(new_repos, key=lambda r: r.stars_today, reverse=True)
    candidates = (candidates + surges)[:MAX_ANALYZE]
    print(f"      新上榜 {len(new_repos)} 个,暴涨 {len(surges)} 个(合计取前 {MAX_ANALYZE})")

    if dry_run:
        for r in candidates:
            tag = " 🚀surge" if r.is_surge else ""
            print(f"  - {r.full_name}  +{r.stars_today}{tag}  {r.description[:60]}")
        print("[dry-run] 跳过 AI 分析与邮件")
        return 0

    if not candidates:
        print("今日无新项目,跳过日报")
        return 0

    print("[3/4] AI 分析(并发补 README 元数据后送 OpenAI)")
    from concurrent.futures import ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=8) as pool:
        enriched = list(pool.map(scraper.enrich, candidates))
    import analyzer
    analyses, overview = analyzer.analyze_all(enriched)
    print(f"      成功分析 {len(analyses)} 个")

    print("[4/4] 渲染并发送邮件")
    import mailer
    html = mailer.render(today, overview, analyses)
    mailer.send(f"GitHub Trend Radar · {today}", html)
    print("完成 ✓")
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    sys.exit(run(dry_run=args.dry_run))
