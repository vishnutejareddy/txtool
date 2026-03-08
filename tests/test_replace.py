import pytest
from click.testing import CliRunner
from txtool.cli import cli


@pytest.fixture
def sample_file(tmp_path):
    f = tmp_path / "sample.txt"
    f.write_text("Hello world\nfoo bar baz\nfoo again\n")
    return f


def test_replace_stdout(sample_file):
    runner = CliRunner()
    result = runner.invoke(cli, ["replace", "foo", "qux", str(sample_file)])
    assert result.exit_code == 0
    assert "qux bar baz" in result.output
    assert "qux again" in result.output
    # original file unchanged
    assert "foo" in sample_file.read_text()


def test_replace_in_place(sample_file):
    runner = CliRunner()
    result = runner.invoke(cli, ["replace", "foo", "qux", "--in-place", str(sample_file)])
    assert result.exit_code == 0
    content = sample_file.read_text()
    assert "qux" in content
    assert "foo" not in content


def test_replace_dry_run(sample_file):
    runner = CliRunner()
    result = runner.invoke(cli, ["replace", "foo", "qux", "--dry-run", str(sample_file)])
    assert result.exit_code == 0
    assert "would change" in result.output
    # file not modified
    assert "foo" in sample_file.read_text()


def test_replace_no_match_dry_run(sample_file):
    runner = CliRunner()
    result = runner.invoke(cli, ["replace", "zzznomatch", "qux", "--dry-run", str(sample_file)])
    assert result.exit_code == 0
    assert "no changes" in result.output


def test_replace_ignore_case(sample_file):
    runner = CliRunner()
    result = runner.invoke(cli, ["replace", "-i", "FOO", "qux", str(sample_file)])
    assert result.exit_code == 0
    assert "qux bar baz" in result.output


def test_replace_regex(sample_file):
    runner = CliRunner()
    result = runner.invoke(cli, ["replace", r"fo+", "REPLACED", str(sample_file)])
    assert result.exit_code == 0
    assert "REPLACED bar baz" in result.output


def test_replace_no_regex(sample_file):
    runner = CliRunner()
    result = runner.invoke(cli, ["replace", "--no-regex", "fo+", "X", str(sample_file)])
    assert result.exit_code == 0
    # literal "fo+" not present, output unchanged
    assert "foo bar baz" in result.output
