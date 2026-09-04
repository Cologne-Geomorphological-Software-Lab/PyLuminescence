# Luminescence (Python)

A Python port of the R package
[`Luminescence`](https://github.com/R-Lum/Luminescence) for luminescence dating data
analysis.

[![Python ≥ 3.12](https://img.shields.io/badge/python-%E2%89%A5%203.12-blue)](pyproject.toml)
[![License: GPL-3.0](https://img.shields.io/badge/license-GPL--3.0-green)](LICENSE)

This repository holds a Python port of the original R Luminescence package. 

## Status

The port is pre-alpha and proceeds in phases:

| Phase | Scope | Status |
|---|---|---|
| 0 | Scaffolding, tooling, CI, physical lookup tables | open |
| 1 | Core object model, BIN/BINX reader, SAR CW-OSL analysis chain | open |
| 2 | Remaining instrument readers (XSYG, SPE, PSL, Daybreak, TIFF, RF, Helios), writers | next |
| 3 | Equivalent-dose / age models, dosimetry, DRAC client | open |
| 4 | Remaining fitting routines and analysis protocols | open |
| 5 | Plotting layer (matplotlib) | open |
| 6 | Bayesian analyses (PyMC, optional extra) | open |
| 7 | Documentation and PyPI release | open |

Everything being written in this repository (no code carried over from the 
prior fork-based port) is validated live against the currently installed CRAN release of `Luminescence`. See *Numerical validation* below.

## Installation

Not yet on PyPI. Install from source (Python ≥ 3.12):

```bash
git clone <this-repository>
cd pyluminescence
uv sync            # or: pip install -e .
```

## Quickstart

**Planned API, once Phase 1 lands** — not yet functional in this repository.

```python
import luminescence as lum

# read a Risø BIN/BINX file and group records per aliquot
data = lum.read_bin("measurement.binx")
aliquot = data.to_analysis(pos=1)

# SAR CW-OSL analysis: LxTx table, rejection criteria, De
results = lum.analyse_sar_cwosl(
    aliquot,
    signal_integral=range(1, 3),        # channels, 1-based inclusive (as in R)
    background_integral=range(900, 1001),
)
print(results["data"][["De", "De.Error", "D01", "RC.Status"]])
```

## Numerical validation

Every ported function is verified live against the currently installed CRAN release of `Luminescence`:

- Raw example instrument files (BIN/BINX, XSYG, ...) live in
  [`tests/fixtures/`](tests/fixtures/) as generic, versioned test data.
- [`tools/generate_fixtures.R`](tools/generate_fixtures.R) calls the installed
  `Luminescence` package fresh and writes reference values to
  `tests/oracle_cache/` (gitignored, regenerated on demand — see
  [CONTRIBUTING.md](CONTRIBUTING.md)). Deterministic results must match within
  documented tolerances (arithmetic 1e-9, fitted parameters 1e-4).
- Monte-Carlo error estimates are compared statistically. All stochastic functions take an explicit `rng` argument; there is no global seeding.

Porting specifications extracted from the R sources live in [`tools/specs/`](tools/specs/).

## Development

```bash
uv sync                    # environment incl. dev dependencies
uv run pytest              # test suite
uv run ruff check .        # lint
uv run ruff format .       # format
uv run basedpyright        # type check (strict)
```

The CI workflow [`python-check.yml`](.github/workflows/python-check.yml) runs all of the
above on Linux, Windows, and macOS.

## License

This is a derivative work of the R package Luminescence by the R-Luminescence Group and, like the original, licensed under [GPL-3.0](LICENSE).
