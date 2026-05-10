from typer.testing import CliRunner

import synccut
from synccut.cli import app


def test_package_imports() -> None:
    assert synccut.__version__ == "0.1.0"


def test_cli_help_loads() -> None:
    result = CliRunner().invoke(app, ["--help"])

    assert result.exit_code == 0
    assert "build-timeline" in result.output


def test_build_timeline_help_loads() -> None:
    result = CliRunner().invoke(app, ["build-timeline", "--help"])

    assert result.exit_code == 0
    assert "--audio-dir" in result.output
    assert "--alignment-dir" in result.output
