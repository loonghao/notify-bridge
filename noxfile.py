"""Nox configuration file."""

# Import built-in modules
from pathlib import Path

# Import third-party modules
import nox


# Constants
PACKAGE_NAME = "notify_bridge"
THIS_ROOT = Path(__file__).parent
PROJECT_ROOT = THIS_ROOT.parent


def _assemble_env_paths(*paths):
    """Assemble environment paths separated by a semicolon.

    Args:
        *paths: Paths to be assembled.

    Returns:
        str: Assembled paths separated by a semicolon.
    """
    return ";".join(paths)


@nox.session
def pytest(session: nox.Session) -> None:
    """Run tests with pytest.

    This function allows passing pytest arguments directly.
    Usage examples:
    - Run all tests: nox -s pytest
    - Run specific test file: nox -s pytest -- tests/notify_bridge/test_core.py
    - Run with verbose output: nox -s pytest -- -v
    - Combine options: nox -s pytest -- tests/notify_bridge/test_core.py -v -k "test_specific_function"
    """
    session.install(".")
    session.install("pytest", "pytest-cov", "pytest-mock", "pytest-asyncio")
    test_root = THIS_ROOT / "tests"

    # Print debug information
    session.log(f"Python version: {session.python}")
    session.log(f"Test root directory: {test_root}")
    session.log(f"Package name: {PACKAGE_NAME}")
    session.log(f"Python path: {THIS_ROOT.as_posix()}")

    pytest_args = [
        "--tb=short",  # Shorter traceback format
        "--showlocals",  # Show local variables in tracebacks
        "-ra",  # Show extra test summary info
        f"--cov={PACKAGE_NAME}",
        "--cov-report=term-missing",  # Show missing lines in terminal
        "--cov-report=xml:coverage.xml",  # Generate XML coverage report
        f"--rootdir={test_root}",
    ]

    # Add any additional arguments passed to nox
    pytest_args.extend(session.posargs)

    session.run(
        "pytest",
        *pytest_args,
        env={
            "PYTHONPATH": THIS_ROOT.as_posix(),
            "PYTHONDEVMODE": "1",  # Enable development mode
            "PYTHONWARNINGS": "always",  # Show all warnings
        },
    )


@nox.session
def lint(session: nox.Session) -> None:
    """Run linting checks.

    This session runs the following checks in order:
    1. autoflake - Check unused imports and variables
    2. ruff - Check common issues (including import sorting)
    3. black - Check code formatting
    4. mypy - Check type hints
    5. pre-commit - Run pre-commit hooks

    Args:
        session: The nox session.
    """
    session.install("ruff", "pre-commit", "autoflake", "black", "mypy")

    # Check unused imports and variables
    session.run(
        "autoflake",
        "--check",
        "--remove-all-unused-imports",
        "--remove-unused-variables",
        "--recursive",
        PACKAGE_NAME,
        "tests",
    )

    # Check and fix common issues with ruff
    # Use --fix to auto-fix import sorting issues
    session.run("ruff", "check", "--fix", ".")

    # Check code formatting
    session.run("black", "--check", ".")

    # Check type hints
    session.run("mypy", PACKAGE_NAME)


@nox.session(name="lint-fix")
def lint_fix(session: nox.Session) -> None:
    """Fix linting issues.

    This session runs the following tools in order:
    1. autoflake - Remove unused imports and variables
    2. ruff - Fix common issues (including import sorting)
    3. black - Format code
    4. mypy - Check type hints
    5. pre-commit - Run pre-commit hooks

    Args:
        session: The nox session.
    """
    session.install("ruff", "pre-commit", "autoflake", "black", "mypy")

    # First remove unused imports and variables
    session.run(
        "autoflake",
        "--in-place",
        "--remove-all-unused-imports",
        "--remove-unused-variables",
        "--recursive",
        PACKAGE_NAME,
        "tests",
    )

    # Fix common issues with ruff (including imports)
    session.run("ruff", "check", "--fix", ".", silent=True)

    # Format code with black
    session.run("black", ".")

    # Check type hints
    session.run("mypy", PACKAGE_NAME)


@nox.session(name="docs")
def docs(session: nox.Session) -> None:
    """Build documentation.

    Args:
        session: The nox session.
    """
    session.install(".", "sphinx", "sphinx-rtd-theme", "myst-parser")
    session.run("sphinx-build", "-b", "html", "docs/source", "docs/build/html")


@nox.session(name="clean")
def clean(session: nox.Session) -> None:
    """Clean build artifacts.

    Args:
        session: The nox session.
    """
    for path in [
        "build",
        "dist",
        ".eggs",
        "*.egg-info",
        ".nox",
        ".pytest_cache",
        ".coverage",
        "coverage.xml",
        "htmlcov",
        "docs/build",
    ]:
        session.run("rm", "-rf", path, external=True)
