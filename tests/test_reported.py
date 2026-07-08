from scraper import Repo
import store


def _r(name, stars=100, today=50):
    return Repo(name, f"https://github.com/{name}", stars=stars, stars_today=today)


def test_digest_covers_multi_day_collects(tmp_path):
    """周五、周六、周日各采集一次,周一 digest 应取出全部未报新项目。"""
    db = tmp_path / "t.db"
    store.record([_r("o/fri")], "2026-07-03", db_path=db)
    store.record([_r("o/sat")], "2026-07-04", db_path=db)
    store.record([_r("o/sun"), _r("o/fri")], "2026-07-05", db_path=db)

    pending = store.unreported_new("2026-07-06", db_path=db)
    assert {r.full_name for r in pending} == {"o/fri", "o/sat", "o/sun"}


def test_reported_not_repeated(tmp_path):
    db = tmp_path / "t.db"
    store.record([_r("o/a"), _r("o/b")], "2026-07-06", db_path=db)
    store.mark_reported(["o/a"], "2026-07-06", db_path=db)

    pending = store.unreported_new("2026-07-06", db_path=db)
    assert {r.full_name for r in pending} == {"o/b"}, "已报过的不应重复,未报的自动重试"


def test_old_repo_not_treated_as_new(tmp_path):
    """两周前就上过榜的老项目,即使本窗口再次出现也不算新。"""
    db = tmp_path / "t.db"
    store.record([_r("o/old")], "2026-06-28", db_path=db)
    store.record([_r("o/old")], "2026-07-06", db_path=db)

    assert store.unreported_new("2026-07-06", db_path=db) == []


def test_lightweight_repo_fields(tmp_path):
    db = tmp_path / "t.db"
    store.record([_r("o/x", stars=321, today=42)], "2026-07-06", db_path=db)
    (repo,) = store.unreported_new("2026-07-06", db_path=db)
    assert repo.url == "https://github.com/o/x"
    assert repo.stars == 321 and repo.stars_today == 42
