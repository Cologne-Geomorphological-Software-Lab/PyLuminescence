# Luminescence (Python)

A Python port of the R package
[`Luminescence`](https://github.com/R-Lum/Luminescence) for luminescence dating data
analysis.

[![Python ≥ 3.12](https://img.shields.io/badge/python-%E2%89%A5%203.12-blue)](pyproject.toml)
[![License: GPL-3.0](https://img.shields.io/badge/license-GPL--3.0-green)](LICENSE)

This repository holds a Python port of the original R Luminescence package.

## Status

The port is pre-alpha and proceeds in phases:

| Phase | Scope | Status | Parity |
|---|---|---|---|
| 0 | Scaffolding, tooling, CI; lookup tables still to export | in progress | n/a |
| 1 | Core object model, BIN/BINX reader, SAR CW-OSL analysis chain | in progress | open |
| | `Record`, `Curve` | done | partial |
| | `Analysis`, `Results` | open | open |
| | `RisoeBinFile` container | open | open |
| | `read_bin` (BIN/BINX v3-v8) | open | open |
| | `lxtx_ratio` | open | open |
| | `summary_statistics` | open | open |
| | `fit_dose_response` (LIN/SSE/GOK) | open | open |
| | `analyze_sar_cwosl`, `extract_irradiation_times` | open | open |
| | Live R-oracle harness | open | n/a |
| 2 | Remaining instrument readers (XSYG, SPE, PSL, Daybreak, TIFF, RF, Helios), writers | open | open |
| 3 | Equivalent-dose / age models, dosimetry, DRAC client | open | open |
| 4 | Remaining fitting routines and analysis protocols | open | open |
| 5 | Plotting layer (matplotlib) | open | n/a |
| 6 | Bayesian analyses (PyMC, optional extra) | open | open |
| 7 | Documentation and PyPI release | open | n/a |

*Parity* tracks whether a unit has been checked against the installed CRAN
release, which is a separate question from whether it is ported. `Record` and
`Curve` are `partial`: only the Carter branch of the smoother has been measured
against `Luminescence` 1.3.0. What is still unchecked is listed in
[`PORTING_NOTES.md`](PORTING_NOTES.md). Phase 5 is exempt because the plotting
layer is an idiomatic redesign rather than a faithful port.

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
results = lum.analyze_sar_cwosl(
    aliquot,
    signal_integral=range(1, 3),  # channels, 1-based inclusive (as in R)
    background_integral=range(900, 1001),
)
print(results["data"][["De", "De.Error", "D01", "RC.Status"]])
```

## Numerical validation

Every ported function is verified live against the currently installed CRAN release of `Luminescence`:

- Raw example instrument files (BIN/BINX, XSYG, ...) are never committed here: they
  belong to the R package and we do not redistribute copies of them.
  [`tools/fetch_test_fixtures.py`](tools/fetch_test_fixtures.py) pulls them fresh
  into the gitignored cache `tests/fixtures_cache/`, from the installed CRAN
  package and from a sparse checkout of the R repository. Run it once before any
  test that needs input files.
- `tools/generate_fixtures.R` (not written yet) calls the installed
  `Luminescence` package fresh and writes reference values to
  `tests/oracle_cache/` (gitignored, regenerated on demand — see
  [CONTRIBUTING.md](CONTRIBUTING.md)). Deterministic results must match within
  documented tolerances (arithmetic 1e-9, fitted parameters 1e-4).
- Monte-Carlo error estimates are compared statistically. All stochastic functions take an explicit `rng` argument; there is no global seeding.

[`PORTING_NOTES.md`](PORTING_NOTES.md) lists where the port deviates from R and
where it rests on an approximation nobody has checked against R yet.

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
