import pytest
from click.testing import CliRunner
from txtool.cli import cli


@pytest.fixture
def runner():
    return CliRunner()


def test_diff_basic(runner, tmp_path):
    f1 = tmp_path / "a.txt"
    f2 = tmp_path / "b.txt"
    f1.write_text("line1\nline2\nline3\n")
    f2.write_text("line1\nchanged\nline3\n")
    result = runner.invoke(cli, ["diff", str(f1), str(f2)])
    assert result.exit_code == 0
    assert "line2" in result.output or "changed" in result.output


def test_diff_identical(runner, tmp_path):
    f1 = tmp_path / "a.txt"
    f2 = tmp_path / "b.txt"
    content = "line1\nline2\n"
    f1.write_text(content)
    f2.write_text(content)
    result = runner.invoke(cli, ["diff", str(f1), str(f2)])
    assert result.exit_code == 0
    assert "No differences" in result.output


def test_unique_only_in_a(runner, tmp_path):
    f1 = tmp_path / "a.txt"
    f2 = tmp_path / "b.txt"
    f1.write_text("apple\nbanana\ncherry\n")
    f2.write_text("banana\ndate\n")
    result = runner.invoke(cli, ["unique", "--only-in-a", str(f1), str(f2)])
    assert result.exit_code == 0
    assert "apple" in result.output
    assert "cherry" in result.output
    assert "banana" not in result.output


def test_unique_only_in_b(runner, tmp_path):
    f1 = tmp_path / "a.txt"
    f2 = tmp_path / "b.txt"
    f1.write_text("apple\nbanana\n")
    f2.write_text("banana\ndate\n")
    result = runner.invoke(cli, ["unique", "--only-in-b", str(f1), str(f2)])
    assert result.exit_code == 0
    assert "date" in result.output
    assert "apple" not in result.output


def test_unique_common(runner, tmp_path):
    f1 = tmp_path / "a.txt"
    f2 = tmp_path / "b.txt"
    f1.write_text("apple\nbanana\ncherry\n")
    f2.write_text("banana\ndate\ncherry\n")
    result = runner.invoke(cli, ["unique", "--common", str(f1), str(f2)])
    assert result.exit_code == 0
    assert "banana" in result.output
    assert "cherry" in result.output
    assert "apple" not in result.output


def test_concat_basic(runner, tmp_path):
    f1 = tmp_path / "a.txt"
    f2 = tmp_path / "b.txt"
    f1.write_text("file1\n")
    f2.write_text("file2\n")
    result = runner.invoke(cli, ["concat", str(f1), str(f2)])
    assert result.exit_code == 0
    assert "file1" in result.output
    assert "file2" in result.output


def test_concat_with_headers(runner, tmp_path):
    f1 = tmp_path / "a.txt"
    f2 = tmp_path / "b.txt"
    f1.write_text("content1\n")
    f2.write_text("content2\n")
    result = runner.invoke(cli, ["concat", "--with-headers", str(f1), str(f2)])
    assert result.exit_code == 0
    assert "===" in result.output
    assert "content1" in result.output
    assert "content2" in result.output


def test_concat_separator(runner, tmp_path):
    f1 = tmp_path / "a.txt"
    f2 = tmp_path / "b.txt"
    f1.write_text("aaa\n")
    f2.write_text("bbb\n")
    result = runner.invoke(cli, ["concat", "--separator", "---", str(f1), str(f2)])
    assert result.exit_code == 0
    assert "---" in result.output
    assert "aaa" in result.output
    assert "bbb" in result.output
