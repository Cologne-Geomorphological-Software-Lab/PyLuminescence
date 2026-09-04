# Porting notes

This file records where the port deviates from the R package, and where it rests
on an approximation nobody has checked against R yet. One entry per affected
symbol. The *Unverified approximations* section is the working list for the
live-oracle comparison: delete an entry once the oracle confirms the behaviour,
or move it up to *Deliberate deviations* if the difference turns out to be
intentional.

## Deliberate deviations

| Python | R | Deviation |
|---|---|---|
| `Curve.__len__` | `length_RLum()`, `length()` | R returns `max(x)`, the stimulation duration. Python's `__len__` must return a non-negative integer, so it returns the number of data points. The R value is available as `Curve.duration`. |
| `Record.replicate` | `replicate_RLum()` | Returns the same object `times` times rather than copies, mirroring R's `lapply(1:times, function(x) object)`. Mutating one element mutates them all. |
| `Curve.__eq__` | n/a | Compares `record_type`, `curve_type`, `info` and `data`. `originator`, `uid` and `pids` are excluded, so two curves from different sources compare equal on payload. R has no `==` for these classes. |

## Unverified approximations

| Python | R | What is unverified |
|---|---|---|
| `Curve.smoothed`, `_rolling` | `smooth_RLum()`, `.smoothing()` | R uses `data.table::froll*`; this port uses `pandas.Series.rolling` with `min_periods=k`. The behaviour at incomplete windows (the leading `k - 1` channels for `align="right"`, both edges for `"center"`) was approximated rather than derived from `data.table`'s implementation. Check the edge values explicitly during the live-oracle comparison. |

## Not ported yet

| Python | R | Reason |
|---|---|---|
| `Curve` arithmetic (`+`, `-`, `*`, `/`) | `methods_RLum.R:431-468` | Delegates to `merge_RLum()` in R; blocked until `merge_RLum` itself is ported. |

## References

- `Curve.smoothed(method="carter_etal_2018")` implements Carter et al. (2018),
  <https://doi.org/10.1016/j.radmeas.2018.05.010>: counts whose Poisson
  probability falls below `p_acceptance` are replaced by the mean of up to four
  neighbours.
