# Changelog

All notable changes to PyLuminescence are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).
What counts as a major, minor or patch release is described under
[Versioning](CONTRIBUTING.md#versioning). Where the port deviates from the R
package `Luminescence`, see [PORTING_NOTES.md](PORTING_NOTES.md).

## [Unreleased]

### Added

- `Record`, the common base of all data objects, with `replicate()`
  (port of `RLum`).
- `Curve` for luminescence curves (port of `RLum.Data.Curve`): access to
  `x`, `y` and `info`, `binned()`, `smoothed()` including the method of
  Carter et al. (2018), `normalised()`, `melt()`, and conversion from and to
  matrices, dictionaries and data frames.
- `tools/fetch_test_fixtures.py`, which fetches the example files of the
  R package into a local, gitignored cache.
- Architecture decision records: ADR 0001 (recording decisions) and ADR 0002
  (numerical kernels in NumPy first).
- CI on Linux, Windows and macOS, pre-commit hooks, mutation testing with
  mutmut.
- Issue and pull request templates, security policy.
