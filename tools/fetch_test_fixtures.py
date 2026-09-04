from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

CACHE_DIR = Path("tests/fixtures_cache")


def _require(executable: str) -> str:
    path = shutil.which(executable)
    if path is None:
        raise FileNotFoundError(f"'{executable}' not found on PATH")
    return path


def fetch_extdata() -> None:
    rscript = _require("Rscript")
    result = subprocess.run(  # noqa: S603 - fixed args, no untrusted input
        [rscript, "-e", 'cat(system.file("extdata", package="Luminescence"))'],
        capture_output=True,
        text=True,
        check=True,
    )
    src = Path(result.stdout.strip())
    dest = CACHE_DIR / "extdata"
    shutil.rmtree(dest, ignore_errors=True)
    shutil.copytree(src, dest)


def fetch_r_test_data() -> None:
    git = _require("git")
    clone_dir = CACHE_DIR / "_r_lum_clone"
    shutil.rmtree(clone_dir, ignore_errors=True)
    subprocess.run(  # noqa: S603 - fixed args, no untrusted input
        [
            git,
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
    subprocess.run(  # noqa: S603 - fixed args, no untrusted input
        [
            git,
            "-C",
            str(clone_dir),
            "sparse-checkout",
            "set",
            "tests/testthat/_data",
        ],
        check=True,
    )
    dest = CACHE_DIR / "r_test_data"
    shutil.rmtree(dest, ignore_errors=True)
    shutil.copytree(clone_dir / "tests" / "testthat" / "_data", dest)
    shutil.rmtree(clone_dir)
