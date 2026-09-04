# Contributing to pyluminescence

## Welcome

Welcome to the pyluminescence Contributing Guide. pyluminescence is a Python port of
the R package [`Luminescence`](https://github.com/R-Lum/Luminescence) for luminescence
dating data analysis.

This package was originally developed inside a fork of the R package's own repository,
with the R sources kept alongside the Python port as a reference implementation and
numerical oracle. That coexistence is over: this repository holds only the Python
package now. See [`README.md`](README.md) for the phase plan and current status.

The R original is kept as a local, unversioned reference copy (an `archive/` directory,
excluded via `.gitignore`) on the maintainer's machine, plus the upstream repository
itself at <https://github.com/R-Lum/Luminescence> — used to consult R source when
porting a new function and to regenerate fixtures with `tools/generate_fixtures.R`. It
is not part of this repository and not needed to build, test, or use the package.
Raw test input files derived from the R package are never committed here: they belong
to the R package and we do not redistribute copies of them. `tools/fetch_test_fixtures.py` pulls them fresh into
the gitignored cache `tests/fixtures_cache/`: `extdata/` from the installed CRAN
package, `r_test_data/` from a sparse checkout of the upstream repository (those
dev-only fixtures are not shipped in the CRAN tarball). Run it once before any test
that needs input files:

```bash
uv run python tools/fetch_test_fixtures.py
```

It finds `Rscript` on `PATH`, via `R_HOME`, or via the R installation registered in
the Windows registry, so R does not have to be on `PATH`.

## The porting principle

The single most important rule in this repository: the Python package mirrors the R
package. We are translating, not redesigning.

For every ported function:

* Its behaviour, defaults, argument semantics, edge cases, error/warning conditions,
  and known quirks must match the corresponding R function, unless a quirk is a
  genuine bug that has been discussed and explicitly documented as a deliberate
  deviation.
* Names are chosen for Python developers rather than transliterated from R
  (`analyse_SAR.CWOSL()` becomes `analyze_sar_cwosl()`, `RLum.Data.Curve` becomes
  `Curve`). Function boundaries stay 1:1 with R, one Python function per R function,
  so the oracle comparison needs no mapping layer. The name for a function is fixed
  when its batch is planned; do not invent a different one while implementing.
* Numeric output is validated against the R implementation, not against what "looks
  right"; see *Porting workflow* below.

The one agreed exception is the plotting layer (`luminescence.plot`, Phase 5): it is an
idiomatic matplotlib redesign, not a faithful reproduction of R's base-graphics output.
Every other module mirrors R.

If you're unsure whether something counts as a deviation, open an issue before writing
code.

## Contributions we accept

* **Porting**
  * Implementing an R function in Python. Check the phase table in `README.md` to
    see what's already ported or in progress.
* **Bug reports**
  * Numeric results that don't match the R oracle
  * Crashes or behaviour that silently diverges from R
* **Tests**
  * Parity tests against R fixtures/snapshots
  * Unit tests for edge cases
* **Documentation**
  * Docstrings
  * `PORTING_NOTES.md` entries

At this time, we do not accept:

* Behavioural changes that diverge from the R implementation without a documented,
  discussed reason (see *The porting principle* and *Porting workflow*).
* New third-party runtime dependencies without prior agreement.
* Pull requests targeting the upstream `R-Lum/Luminescence` repository — this project
  is an independent, standalone port, not affiliated with or merging back upstream.
* Swapping the toolchain (uv/hatchling, ruff, basedpyright) for an alternative.

## Ground rules

* Be respectful in all written communication: issues, pull requests, and commit
  messages. You pledge to abide by our [code of conduct][coco].
* Open an issue before starting a port of a non-trivial R function, so scope and
  approach can be agreed on and duplicate work is avoided.
* One logical change per pull request: one function or module per port, in line with
  the granular commit convention below. Do not bundle unrelated ports or fixes.
* All new behaviour must be covered by tests; every ported function needs a parity
  test against the R oracle, not just a unit test of the Python code in isolation.

## AI usage

Using AI tools to help write code is allowed and welcomed. It does not change any of
the standards in this guide: judge the code on its merits, not on how it was produced.

* **Numerical and behavioural choices are not the AI's to decide.** When the R source
  is ambiguous, undocumented, or contains a quirk, go read the R original directly (the
  local `archive/` checkout or upstream) or consult `PORTING_NOTES.md`. Don't let an AI
  tool invent a "cleaner" Pythonic behaviour that
  diverges from R. Any genuine behavioural choice (not already fixed by the R source)
  needs a discussion first, per *The porting principle*.
* **Verify against the R oracle, not by assuming it works.** Run the relevant parity
  test against the values that `tools/generate_fixtures.R` computes from the installed
  CRAN release before calling a port done. A plausible-looking number is not the same
  as a checked one. Anything you could not verify belongs in `PORTING_NOTES.md`.
* Every AI-generated change needs a human to actually read it before it is committed.
  Do not submit code you have not reviewed and understood yourself.
* AI-generated code follows the same rules as any other code, see *Best practices*
  below, especially "no speculative abstractions": prefer the simplest translation of
  the R function over a generated one that handles cases the R source doesn't.
* **AI is well-suited to writing and keeping docstrings up to date**, provided it
  produces this project's actual style (see *Coding style*), not generic filler: no
  filler openers, no `Args:` lines that just restate the type hint, no `Raises:` entry
  for an exception the function doesn't actually raise.
* Install the pre-commit hooks (`uv run pre-commit install`). They run `ruff` (lint
  and format), `basedpyright`, `bandit` (security), and `vulture` (dead code) on
  touched Python files before each commit, plus basic file hygiene (trailing
  whitespace, merge-conflict markers, private-key detection). A complexity gate
  (`xenon`) and a duplicate-code check (`pylint`) are configured but run manually only,
  since several ported functions inherit R's
  branch-heavy logic and would otherwise block unrelated commits; see the comments in
  `.pre-commit-config.yaml`.

## Issue management

Issues are tracked in the GitHub issue tracker.

When filing a bug:

1. State the expected behaviour (what the R function returns/does) and the actual
   Python behaviour.
2. Name the R function and, if known, the affected Python file and line number.
3. Provide a minimal reproduction, ideally comparing R and Python output on the same
   input (sample files under `tests/fixtures_cache/` are usually available on both
   sides).

When filing a port/feature request:

1. Name the R function(s) to be ported and their location in the R original.
2. Note any prerequisites (other unported functions it depends on, new dependencies).

## Environment setup

1. Clone the repository and install [uv](https://docs.astral.sh/uv/):

   ```bash
   git clone <this-repository>
   cd pyluminescence
   uv sync --group dev
   ```

2. Run the test suite:

   ```bash
   uv run pytest
   ```

3. (Only needed for tests that read instrument files or compare against R) Install
   R ≥ 4.6 with the `Luminescence` and `jsonlite` packages, then fetch the inputs and
   regenerate the reference values:

   ```bash
   uv run python tools/fetch_test_fixtures.py
   Rscript tools/generate_fixtures.R
   ```

   R does not need to be on `PATH` for the fetch step. Tests that require these files
   skip themselves when the cache is missing.

## Best practices

* **No unnecessary comments.** Only add a comment when the *why* is non-obvious: a
  hidden constraint, a subtle invariant, or a workaround for a specific bug. Do not
  describe what the code does.
* **No speculative abstractions.** Three similar lines are better than a premature
  helper. Only generalise when there are three or more concrete call sites.
* **No broad exception handling.** Catch only the specific exception types that can
  actually occur. Never use bare `except Exception`.
* **Validate at system boundaries only.** Trust numpy/scipy/pandas guarantees
  internally. Validate user input and data parsed from external files (BIN/BINX, XSYG,
  and the other instrument formats).
* **Mirror R behaviour exactly, including documented quirks.** A deviation from what
  the R source does isn't a local style choice; it needs a discussion first and a
  note in `PORTING_NOTES.md` (see *The porting principle*).

## Coding style

* **Type hints everywhere, clean under `basedpyright` (strict mode).** Every function
  parameter and return type, every dataclass/class field, and every variable whose
  type isn't obvious from the assignment. Modern syntax only: `list[float]`,
  `X | None`, `Literal[...]`.
* **`from __future__ import annotations`** at the top of every module.
* **Module docstrings cite the R source being ported**, e.g. `"""Reader for Risø
  BIN/BINX files (port of ``read_BIN2R``)."""`. Function and method docstrings state
  what the code does, not where it came from; R provenance belongs at module level and
  in `PORTING_NOTES.md`.
* **Google-style docstrings** (`Args:` / `Returns:` / `Raises:`) where a docstring is
  warranted at all, consistent with *Best practices*' "no unnecessary comments" above.
  Most private helpers need none.
* **Private helpers are prefixed with `_`** and not exported from `__init__.py`. Only
  the public API surface, re-exported flat from `luminescence/__init__.py`, is
  unprefixed.
* `ruff check .` and `basedpyright` must both pass clean. Line length is 100 columns.

## Porting workflow

1. Pick an unported R function from the phase table in `README.md`.
2. Read the R source for it directly: signature, behaviour, edge cases, quirks.
3. Implement it in the corresponding `src/luminescence/` module (see *Code
   organisation* below).
4. Validate against the R oracle:
   * Reference values in `tests/oracle_cache/`, computed by
     `tools/generate_fixtures.R` from the installed CRAN release; deterministic
     results must match within the documented tolerances (arithmetic 1e-9, fitted
     parameters 1e-4).
   * Stochastic functions (Monte-Carlo error estimation, resampling) take an explicit
     `rng: np.random.Generator | int | None` argument and are compared statistically,
     not digit for digit.
   * Anything the oracle could not confirm gets an entry in `PORTING_NOTES.md`.
5. Add a parity test under `tests/`.
6. Update the status table in `README.md`, and `PORTING_NOTES.md` if anything
   deviates from R or could not be verified against it.

## Contribution workflow

### Branches

Branches are prefixed by scope, e.g. `dev_<short-description>` for a phase of porting
work or `chore_<short-description>` for tooling/cleanup. Base them on `main` of this
repository. Never push or merge directly to `main`.

### Commit messages

Write commit messages in the imperative mood, present tense:

```
Port read_BIN2R to io/bin.py (BIN/BINX v3-v8)

Add write_bin round-trip test against BINfile_V8.binx
```

* First line: 50 characters max, no trailing period.
* Optional body: explain *why*, not *what*. Reference issue numbers (`Closes #XX`).
* Keep commits granular: one function/module per commit rather than one commit per
  phase. Do not amend published commits.

### Pull requests

* Open against `main` of this repository. Never against `R-Lum/Luminescence` upstream.
* Title mirrors the commit message style.
* Description must state: which R function(s) were ported or fixed, what changed, and
  how it was validated against the R oracle (fixtures, snapshots, or both).
* A series of checks (`python-check.yml`) runs automatically: lint (`ruff`,
  `basedpyright`, `pip-audit`) and the test matrix (Linux/Windows/macOS). They must
  turn green before merging.
* At least one approving review is required before merging.

### Tests

```bash
uv run pytest
uv run ruff check .
uv run ruff format --check .
uv run basedpyright
uv run bandit -r src/luminescence
uv run vulture src/luminescence tests/python --min-confidence 80
uv run pip-audit
```

Pre-commit runs the lint checks automatically on touched files
(`uv run pre-commit install` once, see *AI usage*). The complexity gate and
duplicate-code check are informational for now; run them by hand when touching a
function that might be affected:

```bash
uv run xenon --max-absolute B --max-modules B --max-average A src/luminescence
uv run pylint --disable=all --enable=duplicate-code src/luminescence
```

## Code organisation

| Package | Scope | R counterpart |
|---|---|---|
| `luminescence.core` | Object model: `Record`/`Curve`/`Spectrum`/`ImageData`/`Analysis`/`Results` | `RLum.*` S4 classes |
| `luminescence.io` | Instrument file readers/writers (BIN/BINX, XSYG, SPE, PSL, ...) | `read_*.R`, `write_*.R` |
| `luminescence.analysis` | Analysis protocols (SAR CW-OSL, irradiation handling) | `analyse_*.R` |
| `luminescence.fitting` | Curve fitting (dose-response, ...) | `fit_*.R` |
| `luminescence.models` | Statistics and calculation routines | `calc_*.R` |
| `luminescence.dosimetry` | Equivalent-dose / age models (Phase 3, open) | `calc_*Age*.R`, `calc_*Dose*.R` |
| `luminescence.bayes` | Bayesian analyses, optional `[bayes]` extra (Phase 6, open) | `baSAR`/rjags routines |
| `luminescence.plot` | Matplotlib plotting (idiomatic redesign, not a faithful port) | `plot_*.R` |
| `luminescence.utils` | Shared helpers, exceptions, validation | no direct R counterpart |

## Releases

There is no fixed release cadence. A first PyPI release of `pyluminescence` is planned
for Phase 7, once the migration reaches parity across the phases listed in
`README.md`.

[coco]: CODE_OF_CONDUCT.md
