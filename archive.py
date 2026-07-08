"""日报 HTML 存档到 docs/,供 GitHub Pages 发布。"""
from __future__ import annotations

import re
from pathlib import Path

DOCS_DIR = Path(__file__).parent / "docs"

INDEX_TEMPLATE = """\
<!DOCTYPE html>
<html lang="zh"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>GitHub Trend Radar 归档</title>
<style>
  body {{ max-width: 680px; margin: 40px auto; padding: 0 16px;
         font-family: -apple-system, 'Segoe UI', Helvetica, Arial, sans-serif; color: #1f2328; }}
  a {{ color: #0969da; text-decoration: none; }}
  li {{ margin: 6px 0; }}
</style></head>
<body>
<h1>🛰 GitHub Trend Radar</h1>
<p>每日 GitHub Trending 新项目 AI 日报归档,共 {count} 期。</p>
<ul>
{items}
</ul>
</body></html>
"""


def save(date: str, html: str, docs_dir: Path = DOCS_DIR) -> Path:
    """保存当日日报并重建索引,返回日报路径。"""
    docs_dir.mkdir(parents=True, exist_ok=True)
    report = docs_dir / f"{date}.html"
    report.write_text(html, encoding="utf-8")
    rebuild_index(docs_dir)
    return report


def rebuild_index(docs_dir: Path = DOCS_DIR) -> None:
    docs_dir.mkdir(parents=True, exist_ok=True)
    dates = sorted(
        (p.stem for p in docs_dir.glob("*.html")
         if re.fullmatch(r"\d{4}-\d{2}-\d{2}", p.stem)),
        reverse=True,
    )
    items = "\n".join(f'<li><a href="{d}.html">{d}</a></li>' for d in dates)
    (docs_dir / "index.html").write_text(
        INDEX_TEMPLATE.format(count=len(dates), items=items), encoding="utf-8")
