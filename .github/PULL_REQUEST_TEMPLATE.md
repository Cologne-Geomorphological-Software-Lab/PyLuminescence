## What changed and why

<!-- One short paragraph. What does this PR do, and what problem does it solve?
     Name the R function(s) ported or fixed. Link the issue: Closes #XX -->


## Type of change

- [ ] Port of an R function
- [ ] Bug fix
- [ ] New feature
- [ ] Refactoring (no behaviour change)
- [ ] Tests only
- [ ] Documentation / chore

## How was this tested?

<!-- Describe what you ran. "pytest passed" is not enough — name the relevant test
     classes, and say how the result was validated against the R oracle
     (fixtures, snapshots, or both). -->


## Checklist

- [ ] `PORTING_NOTES.md` entry for every deviation from R
- [ ] Parity checked against the R oracle, or the reason why not stated above
- [ ] README status table updated (if a unit changed status)
- [ ] `CHANGELOG.md` updated
- [ ] New behaviour is covered by tests
- [ ] `uv run pytest` passes (note any pre-existing failures)
- [ ] No new broad `except Exception` clauses
- [ ] No commented-out code left behind
