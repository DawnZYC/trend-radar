import archive


def test_save_and_index(tmp_path):
    archive.save("2026-07-08", "<html>day1</html>", docs_dir=tmp_path)
    archive.save("2026-07-09", "<html>day2</html>", docs_dir=tmp_path)

    assert (tmp_path / "2026-07-08.html").read_text() == "<html>day1</html>"
    index = (tmp_path / "index.html").read_text()
    assert index.index("2026-07-09.html") < index.index("2026-07-08.html"), "索引应倒序"
    assert "共 2 期" in index


def test_index_ignores_non_date_files(tmp_path):
    (tmp_path).mkdir(exist_ok=True)
    (tmp_path / "notes.html").write_text("x")
    archive.save("2026-07-08", "<html>d</html>", docs_dir=tmp_path)
    index = (tmp_path / "index.html").read_text()
    assert "notes.html" not in index and "共 1 期" in index


def test_save_idempotent(tmp_path):
    archive.save("2026-07-08", "<html>v1</html>", docs_dir=tmp_path)
    archive.save("2026-07-08", "<html>v2</html>", docs_dir=tmp_path)
    assert (tmp_path / "2026-07-08.html").read_text() == "<html>v2</html>"
    assert "共 1 期" in (tmp_path / "index.html").read_text()
