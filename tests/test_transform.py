import pytest
from click.testing import CliRunner
from txtool.cli import cli


@pytest.fixture
def runner():
    return CliRunner()


def test_fmt_trim(runner, tmp_path):
    f = tmp_path / "t.txt"
    f.write_text("hello   \nworld  \n")
    result = runner.invoke(cli, ["fmt", "--trim", str(f)])
    assert result.exit_code == 0
    assert "hello   " not in result.output
    assert "hello\n" in result.output


def test_fmt_wrap(runner, tmp_path):
    f = tmp_path / "t.txt"
    f.write_text("this is a very long line that should be wrapped\n")
    result = runner.invoke(cli, ["fmt", "--wrap", "20", str(f)])
    assert result.exit_code == 0
    for line in result.output.splitlines():
        assert len(line) <= 20


def test_fmt_indent(runner, tmp_path):
    f = tmp_path / "t.txt"
    f.write_text("line1\nline2\n")
    result = runner.invoke(cli, ["fmt", "--indent", "2", str(f)])
    assert result.exit_code == 0
    assert "  line1" in result.output
    assert "  line2" in result.output


def test_fmt_dedent(runner, tmp_path):
    f = tmp_path / "t.txt"
    f.write_text("  line1\n  line2\n")
    result = runner.invoke(cli, ["fmt", "--dedent", str(f)])
    assert result.exit_code == 0
    assert "line1" in result.output
    assert result.output.startswith("line1") or "line1\n" in result.output


def test_fmt_line_endings_lf(runner, tmp_path):
    f = tmp_path / "t.txt"
    f.write_bytes(b"hello\r\nworld\r\n")
    result = runner.invoke(cli, ["fmt", "--line-endings", "lf", str(f)])
    assert result.exit_code == 0
    assert b"\r\n" not in result.output.encode()


def test_case_snake(runner, tmp_path):
    f = tmp_path / "t.txt"
    f.write_text("helloWorld\n")
    result = runner.invoke(cli, ["case", "snake", str(f)])
    assert result.exit_code == 0
    assert "hello_world" in result.output


def test_case_camel(runner, tmp_path):
    f = tmp_path / "t.txt"
    f.write_text("hello_world\n")
    result = runner.invoke(cli, ["case", "camel", str(f)])
    assert result.exit_code == 0
    assert "helloWorld" in result.output


def test_case_pascal(runner, tmp_path):
    f = tmp_path / "t.txt"
    f.write_text("hello_world\n")
    result = runner.invoke(cli, ["case", "pascal", str(f)])
    assert result.exit_code == 0
    assert "HelloWorld" in result.output


def test_case_kebab(runner, tmp_path):
    f = tmp_path / "t.txt"
    f.write_text("hello_world\n")
    result = runner.invoke(cli, ["case", "kebab", str(f)])
    assert result.exit_code == 0
    assert "hello-world" in result.output


def test_case_upper(runner, tmp_path):
    f = tmp_path / "t.txt"
    f.write_text("hello world\n")
    result = runner.invoke(cli, ["case", "upper", str(f)])
    assert result.exit_code == 0
    assert "HELLO WORLD" in result.output


def test_case_lower(runner, tmp_path):
    f = tmp_path / "t.txt"
    f.write_text("HELLO WORLD\n")
    result = runner.invoke(cli, ["case", "lower", str(f)])
    assert result.exit_code == 0
    assert "hello world" in result.output


def test_sort_alpha(runner, tmp_path):
    f = tmp_path / "t.txt"
    f.write_text("banana\napple\ncherry\n")
    result = runner.invoke(cli, ["sort", str(f)])
    assert result.exit_code == 0
    lines = result.output.splitlines()
    assert lines == sorted(lines)


def test_sort_reverse(runner, tmp_path):
    f = tmp_path / "t.txt"
    f.write_text("apple\nbanana\ncherry\n")
    result = runner.invoke(cli, ["sort", "-r", str(f)])
    assert result.exit_code == 0
    lines = result.output.splitlines()
    assert lines == sorted(lines, reverse=True)


def test_sort_numeric(runner, tmp_path):
    f = tmp_path / "t.txt"
    f.write_text("10\n2\n30\n1\n")
    result = runner.invoke(cli, ["sort", "--numeric", str(f)])
    assert result.exit_code == 0
    lines = result.output.splitlines()
    assert lines == ["1", "2", "10", "30"]


def test_sort_unique(runner, tmp_path):
    f = tmp_path / "t.txt"
    f.write_text("apple\nbanana\napple\ncherry\n")
    result = runner.invoke(cli, ["sort", "-u", str(f)])
    assert result.exit_code == 0
    lines = result.output.splitlines()
    assert len(lines) == 3
    assert len(set(lines)) == 3


def test_dedup(runner, tmp_path):
    f = tmp_path / "t.txt"
    f.write_text("apple\nbanana\napple\ncherry\nbanana\n")
    result = runner.invoke(cli, ["dedup", str(f)])
    assert result.exit_code == 0
    lines = result.output.splitlines()
    assert lines == ["apple", "banana", "cherry"]


def test_truncate_head(runner, tmp_path):
    f = tmp_path / "t.txt"
    f.write_text("line1\nline2\nline3\nline4\n")
    result = runner.invoke(cli, ["truncate", "--head", "2", str(f)])
    assert result.exit_code == 0
    lines = result.output.splitlines()
    assert lines == ["line1", "line2"]


def test_truncate_tail(runner, tmp_path):
    f = tmp_path / "t.txt"
    f.write_text("line1\nline2\nline3\nline4\n")
    result = runner.invoke(cli, ["truncate", "--tail", "2", str(f)])
    assert result.exit_code == 0
    lines = result.output.splitlines()
    assert lines == ["line3", "line4"]
