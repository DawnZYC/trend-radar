import re
from pathlib import Path

from scraper import parse_trending

FIXTURE = (Path(__file__).parent / "fixtures" / "trending.html").read_text()


def test_parse_returns_enough_repos():
    repos = parse_trending(FIXTURE)
    assert len(repos) >= 10, "解析数量骤降,GitHub 页面结构可能已改版"


def test_parsed_fields_valid():
    repos = parse_trending(FIXTURE)
    for r in repos:
        assert re.fullmatch(r"[\w.-]+/[\w.-]+", r.full_name)
        assert r.url == f"https://github.com/{r.full_name}"
        assert isinstance(r.stars, int) and r.stars >= 0
        assert isinstance(r.stars_today, int) and r.stars_today >= 0
    # trending 榜单至少应有项目带描述和 star 数
    assert any(r.description for r in repos)
    assert any(r.stars > 0 for r in repos)


def test_parse_empty_html_returns_empty():
    assert parse_trending("<html><body></body></html>") == []
