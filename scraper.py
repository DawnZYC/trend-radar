"""抓取 GitHub Trending 并用 REST API 补充元数据。"""
from __future__ import annotations

import base64
import os
import re
import time
from dataclasses import dataclass, field

import requests
from bs4 import BeautifulSoup

UA = "Mozilla/5.0 (compatible; trend-radar/1.0)"
API = "https://api.github.com"
README_MAX_CHARS = 3000


@dataclass
class Repo:
    full_name: str
    url: str
    description: str = ""
    language: str = ""
    stars: int = 0
    stars_today: int = 0
    topics: list[str] = field(default_factory=list)
    created_at: str = ""
    readme_excerpt: str = ""


def _get(url: str, headers: dict | None = None, retries: int = 3) -> requests.Response:
    last_exc: Exception | None = None
    for i in range(retries):
        try:
            resp = requests.get(url, headers=headers, timeout=20)
            if resp.status_code < 500:
                return resp
        except requests.RequestException as exc:
            last_exc = exc
        time.sleep(2 * (i + 1))
    raise RuntimeError(f"GET {url} failed after {retries} retries") from last_exc


def _parse_int(text: str) -> int:
    digits = re.sub(r"[^\d]", "", text)
    return int(digits) if digits else 0


def fetch_trending(language: str = "", since: str = "daily") -> list[Repo]:
    """解析 github.com/trending 页面。language 为空表示总榜。"""
    path = f"/trending/{language}" if language else "/trending"
    resp = _get(f"https://github.com{path}?since={since}", headers={"User-Agent": UA})
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    repos: list[Repo] = []
    for article in soup.select("article.Box-row"):
        a = article.select_one("h2 a")
        if not a or not a.get("href"):
            continue
        full_name = a["href"].strip("/")
        desc_el = article.select_one("p")
        lang_el = article.select_one('[itemprop="programmingLanguage"]')
        star_el = article.select_one('a[href$="/stargazers"]')
        today_el = article.select_one("span.d-inline-block.float-sm-right")

        repos.append(Repo(
            full_name=full_name,
            url=f"https://github.com/{full_name}",
            description=desc_el.get_text(strip=True) if desc_el else "",
            language=lang_el.get_text(strip=True) if lang_el else "",
            stars=_parse_int(star_el.get_text()) if star_el else 0,
            stars_today=_parse_int(today_el.get_text()) if today_el else 0,
        ))
    return repos


def _api_headers() -> dict:
    headers = {"User-Agent": UA, "Accept": "application/vnd.github+json"}
    token = os.environ.get("GH_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def enrich(repo: Repo) -> Repo:
    """补充 topics / created_at / README 摘录。失败时保留已有字段。"""
    headers = _api_headers()
    try:
        r = _get(f"{API}/repos/{repo.full_name}", headers=headers)
        if r.ok:
            data = r.json()
            repo.topics = data.get("topics", [])
            repo.created_at = (data.get("created_at") or "")[:10]
            repo.stars = data.get("stargazers_count", repo.stars)
            repo.description = data.get("description") or repo.description

        r = _get(f"{API}/repos/{repo.full_name}/readme", headers=headers)
        if r.ok:
            content = base64.b64decode(r.json().get("content", "")).decode("utf-8", "ignore")
            repo.readme_excerpt = content[:README_MAX_CHARS]
    except RuntimeError:
        pass
    return repo


def fetch_all(languages: list[str]) -> list[Repo]:
    """抓多个语言榜并按 full_name 去重(保留首个)。"""
    seen: dict[str, Repo] = {}
    for lang in languages:
        for repo in fetch_trending(lang):
            seen.setdefault(repo.full_name, repo)
    return list(seen.values())
