"""
H2O.ai SumBench - One-shot setup script.

Creates a virtual environment, installs all Python dependencies,
downloads the spaCy language model, and fetches required NLTK data.
Works on macOS, Linux, and Windows.

Usage:
    python setup.py          # or python3 setup.py
"""

import os
import platform
import subprocess
import sys
import venv

MIN_PYTHON = (3, 9)
VENV_DIR = ".venv"


def check_python_version():
    """Exit early if the Python version is too old."""
    if sys.version_info < MIN_PYTHON:
        sys.exit(
            f"ERROR: Python {MIN_PYTHON[0]}.{MIN_PYTHON[1]}+ is required "
            f"(you have {platform.python_version()})."
        )


def venv_python():
    """Return the path to the Python executable inside the venv."""
    if platform.system() == "Windows":
        return os.path.join(VENV_DIR, "Scripts", "python.exe")
    return os.path.join(VENV_DIR, "bin", "python")


def create_venv():
    """Create a virtual environment if it doesn't already exist."""
    py = venv_python()
    if os.path.isfile(py):
        print(f"\n  Virtual environment already exists at {VENV_DIR}/")
        return

    print(f"\n  Creating virtual environment in {VENV_DIR}/ ...")
    venv.create(VENV_DIR, with_pip=True)

    if not os.path.isfile(py):
        sys.exit(f"ERROR: Failed to create virtual environment (expected {py}).")
    print(f"  Created.")


def run(description, cmd):
    """Run a command, printing status and exiting on failure."""
    print(f"\n{'=' * 60}")
    print(f"  {description}")
    print(f"{'=' * 60}\n")
    result = subprocess.run(cmd, check=False)
    if result.returncode != 0:
        print(f"\nERROR: {description} failed (exit code {result.returncode}).")
        sys.exit(result.returncode)
    print(f"\n  Done.\n")


def main():
    project_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(project_dir)

    print("\nH2O.ai SumBench Setup")
    print(f"  Python  : {platform.python_version()}")
    print(f"  Platform: {platform.system()} {platform.machine()}")

    # 0. Version gate
    check_python_version()

    # 1. Create venv
    print(f"\n{'=' * 60}")
    print(f"  Creating virtual environment")
    print(f"{'=' * 60}")
    create_venv()
    py = venv_python()

    # 2. Upgrade pip inside venv
    run(
        "Upgrading pip",
        [py, "-m", "pip", "install", "--upgrade", "pip"],
    )

    # 3. Install dependencies
    run(
        "Installing Python dependencies (requirements.txt)",
        [py, "-m", "pip", "install", "-r", "requirements.txt"],
    )

    # 4. spaCy model
    run(
        "Downloading spaCy model (en_core_web_sm)",
        [py, "-m", "spacy", "download", "en_core_web_sm"],
    )

    # 5. NLTK data
    run(
        "Downloading NLTK data (punkt_tab)",
        [py, "-c", "import nltk; nltk.download('punkt_tab')"],
    )

    # Done
    if platform.system() == "Windows":
        activate = f"{VENV_DIR}\\Scripts\\activate"
    else:
        activate = f"source {VENV_DIR}/bin/activate"

    print("\n" + "=" * 60)
    print("  Setup complete!")
    print("=" * 60)
    print()
    print("Next steps:")
    print(f"  1. Activate the virtual environment:")
    print(f"       {activate}")
    print()
    print("  2. (Optional) Copy .env.example to .env and add your H2OGPTE API key")
    print()
    print("  3. Launch the app:")
    print("       streamlit run ui/app.py")
    print()


if __name__ == "__main__":
    main()
