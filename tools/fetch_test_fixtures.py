from __future__ import annotations

import os
import shutil
import stat
import subprocess
from collections.abc import Callable
from pathlib import Path
from typing import Any

CACHE_DIR = Path("tests/fixtures_cache")


def _force_writable(func: Callable[..., Any], path: str, _exc: BaseException) -> None:
    os.chmod(path, stat.S_IWRITE)
    func(path)


def _remove_tree(path: Path) -> None:
    if path.exists():
        shutil.rmtree(path, onexc=_force_writable)


def _registry_r_homes() -> list[Path]:
    try:
        import winreg
    except ImportError:
        return []
    homes: list[Path] = []
    for root in (winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER):
        for key_name in (r"SOFTWARE\R-core\R", r"SOFTWARE\R-core\R64"):
            try:
                with winreg.OpenKey(root, key_name) as key:
                    install_path, _ = winreg.QueryValueEx(key, "InstallPath")
            except OSError:
                continue
            homes.append(Path(str(install_path)))
    return homes


def _extra_search_dirs() -> list[Path]:
    r_home = os.environ.get("R_HOME")
    roots = [Path(r_home)] if r_home else []
    roots.extend(_registry_r_homes())
    return [root / "bin" for root in roots if (root / "bin").is_dir()]


def _require(executable: str) -> str:
    path = shutil.which(executable)
    if path is None:
        search_path = os.pathsep.join(str(directory) for directory in _extra_search_dirs())
        path = shutil.which(executable, path=search_path) if search_path else None
    if path is None:
        raise FileNotFoundError(
            f"'{executable}' not found on PATH or in a registered R installation"
        )
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
    _remove_tree(dest)
    shutil.copytree(src, dest)


def fetch_r_test_data() -> None:
    git = _require("git")
    clone_dir = CACHE_DIR / "_r_lum_clone"
    _remove_tree(clone_dir)
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
    _remove_tree(dest)
    shutil.copytree(clone_dir / "tests" / "testthat" / "_data", dest)
    _remove_tree(clone_dir)


def main() -> None:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    fetch_extdata()
    fetch_r_test_data()


if __name__ == "__main__":
    main()
