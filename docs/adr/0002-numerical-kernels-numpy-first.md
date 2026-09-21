# 0002. Numerical kernels: NumPy first, isolated in _kernels/

* Status: accepted
* Date: 2026-09-21

## Context

The performance-critical routines in the R package are implemented using Rcpp and are contained in seven files in the src/ directory; these routines are bound to R types (NumericVector, List) and therefore cannot be used from Python. 

Three options were considered:

1. Take the C++ code and include Python bindings (using pybind11 or nanobind).
2. Put the routines into a C/C++ library that is used by both R and Python.
3. Reimplement them in NumPy/SciPy.

Options 1 and 2 convert a pure-Python package into a compiled one by providing wheels for all platforms and Python versions, including a compiler for source installations and a different build backend. However, Option 2 only becomes worthwhile if the R package adopts the library. This is currently not planned. In the case of Python, the main reason for using C++ code in R, slow interpreted loops, largely disappears through vectorisation.

## Decision

* Numerical kernels live in luminescence/_kernels/ as pure functions.
* They are implemented in NumPy/SciPy by default
* Numba (optional extra speed) is used only for inherently sequential algorithms where a benchmark shows NumPy is too slow. 
* C/C++ is used only if a shared library alongside R-Lum is required.

## Consequences

* The package is made up entirely of Python; it does not require a compiler to be installed.
* Parity of the kernels is checked via the R oracle, not guaranteed by shared code.
* Replacing _kernels/ with bindings to a shared library later is a local change; callers are unaffected.
