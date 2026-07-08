from scraper import Repo
import store


def test_filter_new_and_record(tmp_path):
    db = tmp_path / "t.db"
    a, b = Repo("o/a", "u", stars=100), Repo("o/b", "u", stars=100)
    store.record([a], "2026-07-07", db_path=db)

    new = store.filter_new([a, b], "2026-07-08", db_path=db)
    assert [r.full_name for r in new] == ["o/b"]


def test_record_idempotent(tmp_path):
    db = tmp_path / "t.db"
    a = Repo("o/a", "u", stars=100)
    store.record([a], "2026-07-08", db_path=db)
    store.record([a], "2026-07-08", db_path=db)  # 不应抛错
    assert store.filter_new([a], "2026-07-09", db_path=db) == []


def test_find_surges(tmp_path):
    db = tmp_path / "t.db"
    store.record([Repo("o/x", "u", stars=1000), Repo("o/y", "u", stars=1000)],
                 "2026-07-07", db_path=db)
    x, y = Repo("o/x", "u", stars=2000), Repo("o/y", "u", stars=1100)

    surges = store.find_surges([x, y], "2026-07-08", db_path=db)
    assert [r.full_name for r in surges] == ["o/x"]
    assert x.is_surge and not y.is_surge


def test_surge_outside_lookback_ignored(tmp_path):
    db = tmp_path / "t.db"
    store.record([Repo("o/x", "u", stars=100)], "2026-06-01", db_path=db)
    x = Repo("o/x", "u", stars=10000)
    assert store.find_surges([x], "2026-07-08", lookback_days=7, db_path=db) == []
