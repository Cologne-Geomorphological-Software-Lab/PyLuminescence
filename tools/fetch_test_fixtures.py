"""Fetch R-package-derived test inputs into a gitignored cache. Run before any test that needs
these files.
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

CACHE_DIR = Path("tests/fixtures_cache")


def fetch_extdata() -> None:
    result = subprocess.run(
        ["Rscript", "-e", 'cat(system.file("extdata", package="Luminescence"))'],
        capture_output=True,
        text=True,
        check=True,
    )
    src = Path(result.stdout.strip())
    dest = CACHE_DIR / "extdata"
    shutil.rmtree(dest, ignore_errors=True)
    shutil.copytree(src, dest)


def fetch_r_test_data() -> None:
    clone_dir = CACHE_DIR / "_r_lum_clone"
    shutil.rmtree(clone_dir, ignore_errors=True)
    subprocess.run(
        [
            "git",
            "clone",
            "--depth",
            "1",
            "--filter=blob:none",
            "--sparse",
            "https://github.com/R-Lum/Luminescence.git",
            str(clone_dir),
        ],
        check=True,
    )
    subprocess.run(
        ["git", "-C", str(clone_dir), "sparse-checkout", "set", "tests/testthat/_data"],
        check=True,
    )
    dest = CACHE_DIR / "r_test_data"
    shutil.rmtree(dest, ignore_errors=True)
    shutil.copytree(clone_dir / "tests" / "testthat" / "_data", dest)
    shutil.rmtree(clone_dir)


def main() -> None:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    fetch_extdata()
    fetch_r_test_data()


if __name__ == "__main__":
    main()
