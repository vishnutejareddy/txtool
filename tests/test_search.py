import pytest
from click.testing import CliRunner
from txtool.cli import cli


@pytest.fixture
def sample_file(tmp_path):
    f = tmp_path / "sample.txt"
    f.write_text("Hello world\nfoo bar baz\nFOO BAR\nno match here\n")
    return f


def test_basic_search(sample_file):
    runner = CliRunner()
    result = runner.invoke(cli, ["search", "foo", str(sample_file)])
    assert result.exit_code == 0
    assert "foo bar baz" in result.output


def test_search_no_match(sample_file):
    runner = CliRunner()
    result = runner.invoke(cli, ["search", "zzznomatch", str(sample_file)])
    assert result.exit_code == 1


def test_search_ignore_case(sample_file):
    runner = CliRunner()
    result = runner.invoke(cli, ["search", "-i", "foo", str(sample_file)])
    assert result.exit_code == 0
    assert "foo bar baz" in result.output
    assert "FOO BAR" in result.output


def test_search_line_numbers(sample_file):
    runner = CliRunner()
    result = runner.invoke(cli, ["search", "-n", "--no-color", "foo", str(sample_file)])
    assert result.exit_code == 0
    assert ":2:" in result.output


def test_search_regex(sample_file):
    runner = CliRunner()
    result = runner.invoke(cli, ["search", r"fo+", str(sample_file)])
    assert result.exit_code == 0
    assert "foo bar baz" in result.output


def test_search_no_regex(sample_file):
    runner = CliRunner()
    result = runner.invoke(cli, ["search", "--no-regex", "fo+", str(sample_file)])
    assert result.exit_code == 1  # literal "fo+" not in file


def test_search_empty_file(tmp_path):
    f = tmp_path / "empty.txt"
    f.write_text("")
    runner = CliRunner()
    result = runner.invoke(cli, ["search", "anything", str(f)])
    assert result.exit_code == 1


def test_search_binary_file_skipped(tmp_path):
    f = tmp_path / "binary.bin"
    f.write_bytes(b"\x00\x01\x02binary content")
    runner = CliRunner()
    result = runner.invoke(cli, ["search", "binary", str(f)])
    # binary file should be skipped, exit 1 (no matches found)
    assert result.exit_code == 1
