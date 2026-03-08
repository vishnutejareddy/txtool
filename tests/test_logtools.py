import json
import pytest
from click.testing import CliRunner
from txtool.cli import cli


@pytest.fixture
def runner():
    return CliRunner()


def test_tail_lines(runner, tmp_path):
    f = tmp_path / "t.log"
    f.write_text("line1\nline2\nline3\nline4\nline5\n")
    result = runner.invoke(cli, ["tail", "-n", "2", str(f)])
    assert result.exit_code == 0
    assert "line4" in result.output
    assert "line5" in result.output
    assert "line1" not in result.output


def test_tail_filter(runner, tmp_path):
    f = tmp_path / "t.log"
    f.write_text("ERROR: bad thing\nINFO: good thing\nERROR: another bad\n")
    result = runner.invoke(cli, ["tail", "-n", "10", "--filter", "ERROR", str(f)])
    assert result.exit_code == 0
    assert "ERROR" in result.output
    assert "good thing" not in result.output


def test_parse_log_counts(runner, tmp_path):
    f = tmp_path / "t.log"
    f.write_text(
        "2024-01-01 INFO: started\n"
        "2024-01-01 ERROR: failed\n"
        "2024-01-01 WARN: low memory\n"
        "2024-01-01 INFO: done\n"
        "2024-01-01 ERROR: crash\n"
    )
    result = runner.invoke(cli, ["parse-log", str(f)])
    assert result.exit_code == 0
    assert "INFO" in result.output
    assert "ERROR" in result.output
    assert "WARN" in result.output


def test_parse_log_json(runner, tmp_path):
    f = tmp_path / "t.log"
    f.write_text(
        "INFO: starting\n"
        "ERROR: oops\n"
        "DEBUG: verbose\n"
    )
    result = runner.invoke(cli, ["parse-log", "--format", "json", str(f)])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert isinstance(data, list)
    assert data[0]["levels"]["INFO"] == 1
    assert data[0]["levels"]["ERROR"] == 1


def test_timestamp_normalize(runner, tmp_path):
    f = tmp_path / "t.log"
    f.write_text("2024-01-15T10:30:00 some event happened\n")
    result = runner.invoke(cli, ["timestamp", str(f)])
    assert result.exit_code == 0
    # Original ISO format should be replaced with normalized format
    assert "2024-01-15 10:30:00" in result.output
