import json
import os
import pytest
from click.testing import CliRunner
from txtool.cli import cli


@pytest.fixture
def runner():
    return CliRunner()


# ---------------------------------------------------------------------------
# JSON
# ---------------------------------------------------------------------------

def test_json_pretty(runner, tmp_path):
    f = tmp_path / "t.json"
    f.write_text('{"a":1,"b":2}')
    result = runner.invoke(cli, ["json", "pretty", str(f)])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data == {"a": 1, "b": 2}
    assert "\n" in result.output  # has newlines = pretty printed


def test_json_minify(runner, tmp_path):
    f = tmp_path / "t.json"
    f.write_text('{\n  "a": 1,\n  "b": 2\n}')
    result = runner.invoke(cli, ["json", "minify", str(f)])
    assert result.exit_code == 0
    assert "\n" not in result.output.strip()
    assert '"a":1' in result.output or '"a": 1' not in result.output


def test_json_validate_valid(runner, tmp_path):
    f = tmp_path / "t.json"
    f.write_text('{"valid": true}')
    result = runner.invoke(cli, ["json", "validate", str(f)])
    assert result.exit_code == 0
    assert "Valid" in result.output


def test_json_validate_invalid(runner, tmp_path):
    f = tmp_path / "t.json"
    f.write_text('{invalid json}')
    result = runner.invoke(cli, ["json", "validate", str(f)])
    assert result.exit_code == 1


def test_json_get(runner, tmp_path):
    f = tmp_path / "t.json"
    f.write_text('{"users": [{"name": "Alice"}, {"name": "Bob"}]}')
    result = runner.invoke(cli, ["json", "get", "users[0].name", str(f)])
    assert result.exit_code == 0
    assert "Alice" in result.output


# ---------------------------------------------------------------------------
# CSV
# ---------------------------------------------------------------------------

def test_csv_view(runner, tmp_path):
    f = tmp_path / "t.csv"
    f.write_text("name,age\nAlice,30\nBob,25\n")
    result = runner.invoke(cli, ["csv", "view", str(f)])
    assert result.exit_code == 0
    assert "name" in result.output
    assert "Alice" in result.output


def test_csv_filter_equals(runner, tmp_path):
    f = tmp_path / "t.csv"
    f.write_text("name,status\nAlice,active\nBob,inactive\nCarol,active\n")
    result = runner.invoke(cli, ["csv", "filter", "status=active", str(f)])
    assert result.exit_code == 0
    assert "Alice" in result.output
    assert "Carol" in result.output
    assert "Bob" not in result.output


def test_csv_select(runner, tmp_path):
    f = tmp_path / "t.csv"
    f.write_text("name,age,city\nAlice,30,NYC\nBob,25,LA\n")
    result = runner.invoke(cli, ["csv", "select", "name,city", str(f)])
    assert result.exit_code == 0
    assert "Alice" in result.output
    assert "NYC" in result.output
    assert "30" not in result.output


def test_csv_to_json(runner, tmp_path):
    f = tmp_path / "t.csv"
    f.write_text("name,age\nAlice,30\nBob,25\n")
    result = runner.invoke(cli, ["csv", "to-json", str(f)])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert isinstance(data, list)
    assert data[0]["name"] == "Alice"


# ---------------------------------------------------------------------------
# ENV
# ---------------------------------------------------------------------------

def test_env_show(runner, tmp_path):
    f = tmp_path / ".env"
    f.write_text("DATABASE_URL=postgres://localhost/db\nSECRET_KEY=abc123\n")
    result = runner.invoke(cli, ["env", "show", str(f)])
    assert result.exit_code == 0
    assert "DATABASE_URL" in result.output
    assert "SECRET_KEY" in result.output


def test_env_diff(runner, tmp_path):
    f1 = tmp_path / "a.env"
    f2 = tmp_path / "b.env"
    f1.write_text("KEY1=value1\nKEY2=old\n")
    f2.write_text("KEY2=new\nKEY3=value3\n")
    result = runner.invoke(cli, ["env", "diff", str(f1), str(f2)])
    assert result.exit_code == 0
    assert "KEY1" in result.output or "KEY3" in result.output


def test_env_check(runner, tmp_path):
    tmpl = tmp_path / "template.env"
    target = tmp_path / "actual.env"
    tmpl.write_text("REQUIRED_KEY=\nANOTHER_KEY=\n")
    target.write_text("REQUIRED_KEY=value\n")
    result = runner.invoke(cli, ["env", "check", str(tmpl), str(target)])
    assert result.exit_code == 1
    assert "ANOTHER_KEY" in result.output


# ---------------------------------------------------------------------------
# Template
# ---------------------------------------------------------------------------

def test_template_basic(runner, tmp_path):
    f = tmp_path / "t.txt"
    f.write_text("Hello {{NAME}}!\n")
    result = runner.invoke(cli, ["template", str(f), "NAME=World"])
    assert result.exit_code == 0
    assert "Hello World!" in result.output


def test_template_env(runner, tmp_path):
    f = tmp_path / "t.txt"
    f.write_text("Value: {{MY_TEST_VAR}}\n")
    env = os.environ.copy()
    env["MY_TEST_VAR"] = "from_env"
    # Use mix_stderr=False to capture output cleanly
    result = runner.invoke(cli, ["template", "--env", str(f)], env=env)
    assert result.exit_code == 0
    assert "from_env" in result.output
