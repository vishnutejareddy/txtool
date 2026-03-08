import json
import pytest
from click.testing import CliRunner
from txtool.cli import cli


@pytest.fixture
def sample_file(tmp_path):
    f = tmp_path / "sample.txt"
    f.write_text("the quick brown fox\nthe fox jumped over\nthe lazy dog\n")
    return f


def test_stats_table(sample_file):
    runner = CliRunner()
    result = runner.invoke(cli, ["stats", str(sample_file)])
    assert result.exit_code == 0
    assert "Lines" in result.output
    assert "Words" in result.output
    assert "Chars" in result.output


def test_stats_plain(sample_file):
    runner = CliRunner()
    result = runner.invoke(cli, ["stats", "--format", "plain", str(sample_file)])
    assert result.exit_code == 0
    assert "Lines: 3" in result.output
    assert "Words: 11" in result.output
    assert "the: 3" in result.output


def test_stats_json(sample_file):
    runner = CliRunner()
    result = runner.invoke(cli, ["stats", "--format", "json", str(sample_file)])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert len(data) == 1
    assert data[0]["lines"] == 3
    assert data[0]["words"] == 11
    top_words = {item["word"]: item["count"] for item in data[0]["top_words"]}
    assert top_words["the"] == 3
    assert top_words["fox"] == 2


def test_stats_top_n(sample_file):
    runner = CliRunner()
    result = runner.invoke(cli, ["stats", "--format", "json", "--top", "2", str(sample_file)])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert len(data[0]["top_words"]) == 2


def test_stats_empty_file(tmp_path):
    f = tmp_path / "empty.txt"
    f.write_text("")
    runner = CliRunner()
    result = runner.invoke(cli, ["stats", "--format", "plain", str(f)])
    assert result.exit_code == 0
    assert "Lines: 0" in result.output
    assert "Words: 0" in result.output


def test_stats_multiple_files(tmp_path):
    f1 = tmp_path / "a.txt"
    f2 = tmp_path / "b.txt"
    f1.write_text("hello world\n")
    f2.write_text("foo bar\n")
    runner = CliRunner()
    result = runner.invoke(cli, ["stats", "--format", "json", str(f1), str(f2)])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert len(data) == 2
