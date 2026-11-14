---
name: Bug report
about: Create a report to help us improve
title: ''
labels: ''
assignees: ''

---

**Describe the bug**
A clear and concise description of what the bug is. Name the R function and, if known, the affected Python file and line.

**To Reproduce**
A minimal reproduction on the same input in both languages. Sample files from `tests/fixtures_cache/` are usually available on both sides.

R:
```r
library(Luminescence)
# ...
```

Python:
```python
import luminescence as lum
# ...
```

**Expected behavior**
What the R function returns or does on this input.

**Environment (please complete the following information):**
 - R version: [e.g. 4.6.1]
 - `Luminescence` version: [output of `packageVersion("Luminescence")`]
 - Python version: [e.g. 3.12.7]
 - PyLuminescence version or commit: [e.g. 0.1.0.dev0 or `git rev-parse --short HEAD`]
 - OS: [e.g. Windows 11]

**Additional context**
Add any other context about the problem here.
