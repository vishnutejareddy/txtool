import base64
import hashlib
import json
import pytest
from click.testing import CliRunner
from txtool.cli import cli


@pytest.fixture
def runner():
    return CliRunner()


# ---------------------------------------------------------------------------
# encode / decode
# ---------------------------------------------------------------------------

def test_encode_base64(runner):
    result = runner.invoke(cli, ["encode", "base64", "--text", "hello world"])
    assert result.exit_code == 0
    expected = base64.b64encode(b"hello world").decode("ascii")
    assert expected in result.output


def test_decode_base64(runner):
    encoded = base64.b64encode(b"hello world").decode("ascii")
    result = runner.invoke(cli, ["encode", "base64", "--decode", "--text", encoded])
    assert result.exit_code == 0
    assert "hello world" in result.output


def test_encode_url(runner):
    result = runner.invoke(cli, ["encode", "url", "--text", "hello world & more"])
    assert result.exit_code == 0
    assert "%" in result.output  # URL encoded
    assert "hello" in result.output


def test_decode_url(runner):
    result = runner.invoke(cli, ["encode", "url", "--decode", "--text", "hello%20world"])
    assert result.exit_code == 0
    assert "hello world" in result.output


def test_encode_html(runner):
    result = runner.invoke(cli, ["encode", "html", "--text", '<script>alert("xss")</script>'])
    assert result.exit_code == 0
    assert "&lt;" in result.output
    assert "&gt;" in result.output
    assert "&quot;" in result.output


def test_decode_html(runner):
    result = runner.invoke(cli, ["encode", "html", "--decode", "--text", "&lt;b&gt;bold&lt;/b&gt;"])
    assert result.exit_code == 0
    assert "<b>bold</b>" in result.output


# ---------------------------------------------------------------------------
# hash
# ---------------------------------------------------------------------------

def test_hash_sha256(runner, tmp_path):
    f = tmp_path / "t.txt"
    f.write_bytes(b"hello world\n")
    expected = hashlib.sha256(b"hello world\n").hexdigest()
    result = runner.invoke(cli, ["hash", str(f)])
    assert result.exit_code == 0
    assert expected in result.output


def test_hash_compare_match(runner, tmp_path):
    f1 = tmp_path / "a.txt"
    f2 = tmp_path / "b.txt"
    content = b"identical content\n"
    f1.write_bytes(content)
    f2.write_bytes(content)
    result = runner.invoke(cli, ["hash", "--compare", str(f1), str(f2)])
    assert result.exit_code == 0
    assert "MATCH" in result.output


def test_hash_compare_mismatch(runner, tmp_path):
    f1 = tmp_path / "a.txt"
    f2 = tmp_path / "b.txt"
    f1.write_bytes(b"content a\n")
    f2.write_bytes(b"content b\n")
    result = runner.invoke(cli, ["hash", "--compare", str(f1), str(f2)])
    assert result.exit_code == 0
    assert "MISMATCH" in result.output


# ---------------------------------------------------------------------------
# wc
# ---------------------------------------------------------------------------

def test_wc_table(runner, tmp_path):
    f1 = tmp_path / "a.txt"
    f2 = tmp_path / "b.txt"
    f1.write_text("hello world\nfoo bar\n")
    f2.write_text("one two three\n")
    result = runner.invoke(cli, ["wc", str(f1), str(f2)])
    assert result.exit_code == 0
    assert "TOTAL" in result.output
    assert "2" in result.output  # line count


def test_wc_json(runner, tmp_path):
    f = tmp_path / "t.txt"
    f.write_text("hello world\nfoo bar baz\n")
    result = runner.invoke(cli, ["wc", "--format", "json", str(f)])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert isinstance(data, list)
    assert data[0]["lines"] == 2
    assert data[0]["words"] == 5


# ---------------------------------------------------------------------------
# grep-replace
# ---------------------------------------------------------------------------

def test_grep_replace_dry_run(runner, tmp_path):
    f = tmp_path / "t.txt"
    f.write_text("hello foo\nbar foo\n")
    result = runner.invoke(cli, ["grep-replace", "foo", "baz", "--dry-run", str(f)])
    assert result.exit_code == 0
    # File should NOT be changed
    assert f.read_text() == "hello foo\nbar foo\n"
    # Output should show diff
    assert "baz" in result.output or "foo" in result.output


def test_grep_replace_applies(runner, tmp_path):
    f = tmp_path / "t.txt"
    f.write_text("hello foo\nbar foo\n")
    result = runner.invoke(cli, ["grep-replace", "foo", "baz", str(f)])
    assert result.exit_code == 0
    content = f.read_text()
    assert "baz" in content
    assert "foo" not in content
