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

    Args:
        session: The nox session.
    """
    session.install(".")
    session.install("pytest", "pytest_cov", "pytest_mock", "pytest-asyncio")
    test_root = THIS_ROOT / "tests"

    # Print debug information
    session.log(f"Python version: {session.python}")
    session.log(f"Test root directory: {test_root}")
    session.log(f"Package name: {PACKAGE_NAME}")
    session.log(f"Python path: {THIS_ROOT.as_posix()}")

    session.run(
        "pytest",
        "-v",  # Verbose output
        "--tb=short",  # Shorter traceback format
        "--showlocals",  # Show local variables in tracebacks
        "-ra",  # Show extra test summary info
        f"--cov={PACKAGE_NAME}",
        "--cov-report=term-missing",  # Show missing lines in terminal
        "--cov-report=xml:coverage.xml",  # Generate XML coverage report
        f"--rootdir={test_root}",
        env={
            "PYTHONPATH": THIS_ROOT.as_posix(),
            "PYTHONDEVMODE": "1",  # Enable development mode
            "PYTHONWARNINGS": "always",  # Show all warnings
        },
    )


@nox.session
def lint(session: nox.Session) -> None:
    """Run linting checks.

    This session runs the following checks:
    1. isort - Check import sorting
    2. black - Check code formatting
    3. ruff - Check common issues
    4. mypy - Check type hints
    5. pre-commit - Run pre-commit hooks

    Args:
        session: The nox session.
    """
    session.install("isort", "ruff", "black", "mypy", "pre-commit")
    session.run("isort", "--check-only", ".")
    session.run("black", "--check", ".")
    session.run("ruff", "check")
    session.run("mypy", PACKAGE_NAME)
    session.run("pre-commit", "run", "--all-files", "--show-diff-on-failure")


@nox.session(name="lint-fix")
def lint_fix(session: nox.Session) -> None:
    """Fix linting issues.

    This session runs the following tools in order:
    1. autoflake - Remove unused imports and variables
    2. isort - Sort imports
    3. black - Format code
    4. ruff - Fix common issues
    5. mypy - Check type hints
    6. pre-commit - Run pre-commit hooks

    Args:
        session: The nox session.
    """
    session.install("isort", "ruff", "pre-commit", "autoflake", "black", "mypy")

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

    # Sort imports
    session.run("isort", ".")

    # Format code with black
    session.run("black", ".")

    # Fix common issues with ruff
    session.run("ruff", "check", "--fix", silent=True)

    # Check type hints
    session.run("mypy", PACKAGE_NAME)

    # Run pre-commit hooks
    session.run("pre-commit", "run", "--all-files")


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
