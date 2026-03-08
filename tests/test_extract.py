import pytest
from click.testing import CliRunner
from txtool.cli import cli


@pytest.fixture
def runner():
    return CliRunner()


def test_extract_email(runner, tmp_path):
    f = tmp_path / "t.txt"
    f.write_text("contact us at user@example.com for help\n")
    result = runner.invoke(cli, ["extract", "--type", "email", str(f)])
    assert result.exit_code == 0
    assert "user@example.com" in result.output


def test_extract_url(runner, tmp_path):
    f = tmp_path / "t.txt"
    f.write_text("visit https://example.com for more\n")
    result = runner.invoke(cli, ["extract", "--type", "url", str(f)])
    assert result.exit_code == 0
    assert "https://example.com" in result.output


def test_extract_ip(runner, tmp_path):
    f = tmp_path / "t.txt"
    f.write_text("server at 192.168.1.100 responded\n")
    result = runner.invoke(cli, ["extract", "--type", "ip", str(f)])
    assert result.exit_code == 0
    assert "192.168.1.100" in result.output


def test_extract_number(runner, tmp_path):
    f = tmp_path / "t.txt"
    f.write_text("found 42 items and 3.14 ratio\n")
    result = runner.invoke(cli, ["extract", "--type", "number", str(f)])
    assert result.exit_code == 0
    assert "42" in result.output
    assert "3.14" in result.output


def test_extract_unique(runner, tmp_path):
    f = tmp_path / "t.txt"
    f.write_text("user@example.com\nuser@example.com\nother@example.com\n")
    result = runner.invoke(cli, ["extract", "--type", "email", "--unique", str(f)])
    assert result.exit_code == 0
    lines = result.output.strip().splitlines()
    assert lines.count("user@example.com") == 1


def test_between_basic(runner, tmp_path):
    f = tmp_path / "t.txt"
    f.write_text("before\nSTART\nline1\nline2\nEND\nafter\n")
    result = runner.invoke(cli, ["between", "START", "END", str(f)])
    assert result.exit_code == 0
    assert "line1" in result.output
    assert "line2" in result.output
    assert "before" not in result.output
    assert "after" not in result.output
    assert "START" not in result.output
    assert "END" not in result.output


def test_between_inclusive(runner, tmp_path):
    f = tmp_path / "t.txt"
    f.write_text("before\nSTART\nline1\nEND\nafter\n")
    result = runner.invoke(cli, ["between", "--inclusive", "START", "END", str(f)])
    assert result.exit_code == 0
    assert "START" in result.output
    assert "line1" in result.output
    assert "END" in result.output
    assert "before" not in result.output
    assert "after" not in result.output


def test_columns_by_index(runner, tmp_path):
    f = tmp_path / "t.txt"
    f.write_text("a b c\n1 2 3\n")
    result = runner.invoke(cli, ["columns", "-f", "1,3", str(f)])
    assert result.exit_code == 0
    lines = result.output.strip().splitlines()
    assert "a" in lines[0] and "c" in lines[0]
    assert "1" in lines[1] and "3" in lines[1]


def test_columns_csv_delimiter(runner, tmp_path):
    f = tmp_path / "t.txt"
    f.write_text("a,b,c\n1,2,3\n")
    result = runner.invoke(cli, ["columns", "-d", ",", "-f", "1,3", str(f)])
    assert result.exit_code == 0
    lines = result.output.strip().splitlines()
    assert "a" in lines[0] and "c" in lines[0]
    assert "1" in lines[1] and "3" in lines[1]
