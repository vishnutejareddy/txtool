import pytest
from click.testing import CliRunner
from txtool.cli import cli


@pytest.fixture
def log_file(tmp_path):
    f = tmp_path / "app.log"
    f.write_text("INFO: started\nERROR: something failed\nINFO: done\nERROR: another error\n")
    return f


def test_filter_keep_matching(log_file):
    runner = CliRunner()
    result = runner.invoke(cli, ["filter", "ERROR", str(log_file)])
    assert result.exit_code == 0
    assert "ERROR: something failed" in result.output
    assert "ERROR: another error" in result.output
    assert "INFO" not in result.output


def test_filter_invert(log_file):
    runner = CliRunner()
    result = runner.invoke(cli, ["filter", "-v", "ERROR", str(log_file)])
    assert result.exit_code == 0
    assert "INFO: started" in result.output
    assert "INFO: done" in result.output
    assert "ERROR" not in result.output


def test_filter_ignore_case(log_file):
    runner = CliRunner()
    result = runner.invoke(cli, ["filter", "-i", "error", str(log_file)])
    assert result.exit_code == 0
    assert "ERROR: something failed" in result.output


def test_filter_regex(log_file):
    runner = CliRunner()
    result = runner.invoke(cli, ["filter", r"ERROR.*failed", str(log_file)])
    assert result.exit_code == 0
    assert "ERROR: something failed" in result.output
    assert "ERROR: another error" not in result.output


def test_filter_no_matches(log_file):
    runner = CliRunner()
    result = runner.invoke(cli, ["filter", "CRITICAL", str(log_file)])
    assert result.exit_code == 0
    assert result.output == ""


def test_filter_empty_file(tmp_path):
    f = tmp_path / "empty.txt"
    f.write_text("")
    runner = CliRunner()
    result = runner.invoke(cli, ["filter", "pattern", str(f)])
    assert result.exit_code == 0
    assert result.output == ""
