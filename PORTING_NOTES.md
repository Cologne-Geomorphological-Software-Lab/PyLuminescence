# Porting notes

This file records where the port deviates from the R package, and where it rests
on an approximation nobody has checked against R yet. One entry per affected
symbol.

*Unverified approximations* is the working list for the live-oracle comparison.
Once the oracle has run, an entry there either disappears, moves to *Deliberate
deviations* if the difference is intentional, or moves to *Confirmed divergences*
if the port and R genuinely disagree.

## Deliberate deviations

| Python | R | Deviation |
|---|---|---|
| `Curve.__len__` | `length_RLum()`, `length()` | R returns `max(x)`, the stimulation duration. Python's `__len__` must return a non-negative integer, so it returns the number of data points. The R value is available as `Curve.duration`. |
| `Record.replicate` | `replicate_RLum()` | Returns the same object `times` times rather than copies, mirroring R's `lapply(1:times, function(x) object)`. Mutating one element mutates them all. |
| `Curve.__eq__` | n/a | Compares `record_type`, `curve_type`, `info` and `data`. `originator`, `uid` and `pids` are excluded, so two curves from different sources compare equal on payload. R has no `==` for these classes. |
| `Result.__eq__` | n/a | Compares identity: two results are equal only if they are the same object. `data` can hold arrays and data frames, whose `==` is element-wise, so a payload comparison has no single meaning. Without an override, `Result` would inherit `Record.__eq__`, which compares only `originator` and `info` and treats results with different `data` as equal. R has no `==` for `RLum.Results`. |
| none | `view()` for `RLum.Results` (`RLum.Results-class.R:269-285`) | Not ported, by design. It opens the element in R's spreadsheet viewer (`utils::View()`), a GUI function with no counterpart in a library. Take the element with `Result.get()` and inspect it in the IDE's variable viewer or as a data frame. |

## Unverified approximations

| Python | R | What is unverified |
|---|---|---|
| `Curve.smoothed`, `_rolling` | `smooth_RLum()`, `.smoothing()` | R uses `data.table::froll*`; this port uses `pandas.Series.rolling` with `min_periods=k`. The behaviour at incomplete windows (the leading `k - 1` channels for `align="right"`, both edges for `"center"`) was approximated rather than derived from `data.table`'s implementation. Check the edge values explicitly during the live-oracle comparison. |

## Confirmed divergences, not yet resolved

None currently.

## Not ported yet

| Python | R | Reason |
|---|---|---|
| `Curve` arithmetic (`+`, `-`, `*`, `/`) | `methods_RLum.R:431-468` | Delegates to `merge_RLum()` in R; blocked until `merge_RLum` itself is ported. |

## References

- `Curve.smoothed(method="carter_etal_2018")` ports R's `"Carter_etal_2018"`
  method. R documents it as an implementation of the Poisson smoother of Carter, J., Cresswell, A.J., Kinnaird, T.C., Carmichael, L.A., Murphy, S. and
  Sanderson, D.C.W. (2018): Non-Poisson variations in photomultipliers and
  implications for luminescence dating. Radiation Measurements 120, 267-273.
  <https://doi.org/10.1016/j.radmeas.2018.05.010>

  A count is flagged when its Poisson probability, taken against the mean of the  whole curve, falls below `p_acceptance`; a flagged count is replaced by the
  mean of its four neighbours. The first and last two channels have no full
  window, and both R and this port write `fill` in them.

  The paper ships its implementation as supplementary material
  (`PoissonSmoothing.R`, mmc3). R's `.smoothing()` follows that script on the
  probability itself: the script computes a standard deviation in its lines 9-10 but never uses it, and line 17 is a plain Poisson mass function with λ set to the mean.

  `.smoothing()` and the published script disagree on the divisor of the
  replacement value (line 78 of `PoissonSmoothing.R`) and on the multi-channel
  exemption described in section 4.1 of the paper. Neither is a port bug; the
  port mirrors R in both cases. To be raised with R-Lum after a closer reading of the paper.
