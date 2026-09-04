"""Curve record: a two-column (x, y) measurement.

Port of ``RLum.Data.Curve`` (``RLum.Data.Curve-class.R``) and its S3 methods
in ``methods_RLum.R``. Arithmetic operators are NOT ported here yet.
"""

from __future__ import annotations

import warnings
from collections.abc import Callable
from dataclasses import dataclass, replace
from typing import Any, cast

import numpy as np
import pandas as pd
from scipy.special import gammaln

from luminescence.core.base import Record, validate_positive_scalar

_NormaliseArg = float | str | bool | np.ndarray


def _rolling(x: np.ndarray, k: int, *, fill: float, align: str, func: str) -> np.ndarray:
    """Rolling ``mean`` or ``median`` over ``k`` channels, aligned right, center or left."""
    series: pd.Series = pd.Series(x, dtype=float)
    if align == "right":
        rolled = getattr(series.rolling(window=k, min_periods=k), func)()
    elif align == "center":
        rolled = getattr(series.rolling(window=k, min_periods=k, center=True), func)()
    elif align == "left":
        reversed_: pd.Series = series.iloc[::-1].reset_index(drop=True)
        rolled = getattr(reversed_.rolling(window=k, min_periods=k), func)()
        rolled = rolled.iloc[::-1].reset_index(drop=True)
    else:
        raise ValueError("'align' should be one of 'right', 'center', 'left'")
    return rolled.fillna(fill).to_numpy()


_CARTER_WINDOW = 5


def _smoothing(
    x: np.ndarray,
    *,
    k: int | None,
    fill: float,
    align: str,
    p_acceptance: float,
    method: str,
) -> np.ndarray:
    """Smooth counts by a rolling window, or by replacing improbable counts."""
    if k is not None:
        validate_positive_scalar(k, name="k")
    if method not in {"mean", "median", "carter_etal_2018"}:
        raise ValueError("'method' should be one of 'mean', 'median', 'carter_etal_2018'")
    if k is None:
        k = int(np.ceil(len(x) / 100))

    if method in {"mean", "median"}:
        return _rolling(x, k, fill=fill, align=align, func=method)

    mx = np.nanmean(x)
    with np.errstate(divide="ignore", invalid="ignore"):
        log_prob = -mx + x * np.log(mx) - gammaln(x + 1)
    prob = np.exp(log_prob)
    na_idx = prob < p_acceptance
    if np.all(na_idx):
        raise ValueError("'p_acceptance' rejects all counts, set it to a smaller value")
    x = x.astype(float).copy()
    x[na_idx] = np.nan
    x_series: pd.Series = pd.Series(x)
    rolled_series = cast(
        "pd.Series",
        x_series.rolling(window=_CARTER_WINDOW, center=True, min_periods=1).mean(),
    )
    rolled = rolled_series.to_numpy(copy=True)
    edge = (_CARTER_WINDOW - 1) // 2
    rolled[:edge] = fill
    rolled[-edge:] = fill
    x[na_idx] = rolled[na_idx]
    return np.round(x)


_NORM_REFERENCE: dict[str, Callable[[np.ndarray], float]] = {
    "max": np.nanmax,
    "min": np.nanmin,
    "first": lambda data: data[0],
    "last": lambda data: data[-1],
}

_HUOT_BACKGROUND_START = 0.8


def _normalise_huot(data: np.ndarray) -> np.ndarray:
    """Subtract the median of the final 20% as background, then scale to the maximum."""
    bg = np.nanmedian(data[int(np.floor(len(data) * _HUOT_BACKGROUND_START)) :])
    return (data - bg) / np.nanmax(data - bg)


def _normalise_curve(data: np.ndarray, norm: _NormaliseArg) -> np.ndarray:
    """Divide ``data`` by the reference selected by ``norm``.

    Non-finite results are replaced by 0 and a warning is emitted.
    """
    if norm is False:
        return data
    if norm is True:
        norm = "max"

    with np.errstate(divide="ignore", invalid="ignore"):
        if isinstance(norm, int | float | np.ndarray):
            result = data / norm
        elif norm == "huot":
            result = _normalise_huot(data)
        elif norm in _NORM_REFERENCE:
            result = data / _NORM_REFERENCE[norm](data)
        else:
            raise ValueError(f"Unknown 'norm' option: {norm!r}")

    bad = ~np.isfinite(result)
    if np.any(bad):
        result = result.copy()
        result[bad] = 0.0
        warnings.warn(
            "Curve normalisation produced Inf/NaN values, values replaced by 0",
            stacklevel=2,
        )
    return result


@dataclass(kw_only=True, eq=False)
class Curve(Record):
    """A single measured curve (e.g. one OSL/TL/IRSL shine-down).

    Attributes:
        record_type: Curve type label, e.g. ``"OSL"``, ``"TL"``.
        curve_type: Measurement stage, e.g. ``"measured"``.
        data: ``(n, 2)`` array; column 0 is x (time/temperature), column 1 is y (counts).
    """

    record_type: str
    curve_type: str = ""
    data: np.ndarray

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Curve):
            return NotImplemented
        return (
            self.record_type == other.record_type
            and self.curve_type == other.curve_type
            and self.info == other.info
            and np.array_equal(self.data, other.data)
        )

    def __repr__(self) -> str:
        y = self.y
        finite_y = y[np.isfinite(y)]
        nan_note = " (contains NaN values)" if finite_y.size < y.size else ""
        y_min = float(finite_y.min()) if finite_y.size else float("nan")
        y_max = float(finite_y.max()) if finite_y.size else float("nan")
        return (
            f"[Curve] record_type={self.record_type!r} curve_type={self.curve_type!r}\n"
            f"  measured values: {len(self)}\n"
            f"  x range: {self.x.min()} .. {self.x.max()}\n"
            f"  y range: {y_min} .. {y_max}{nan_note}\n"
            f"  info elements: {len(self.info)}"
        )

    def __len__(self) -> int:
        """Number of data points."""
        return self.data.shape[0]

    def __array__(self, dtype: Any = None) -> np.ndarray:
        return np.asarray(self.data, dtype=dtype)

    @property
    def duration(self) -> float:
        """Largest x-value: the stimulation time or the maximum temperature."""
        return float(np.max(self.x))

    @property
    def x(self) -> np.ndarray:
        return self.data[:, 0]

    @property
    def y(self) -> np.ndarray:
        return self.data[:, 1]

    def info_names(self) -> list[str]:
        """Names of the ``info`` entries."""
        return list(self.info)

    def get_info(self, key: str | None = None) -> Any:
        """Return the raw ``data`` array, or the ``info`` value stored under ``key``.

        A missing or unknown key yields ``None`` and a warning, not an exception.
        """
        if key is None:
            return self.data
        if not self.info:
            warnings.warn("'info' is empty, None returned", stacklevel=2)
            return None
        if key not in self.info:
            warnings.warn(f"Invalid 'key', valid names are: {', '.join(self.info)}", stacklevel=2)
            return None
        return self.info[key]

    def to_dict(self) -> dict[str, np.ndarray]:
        """Column arrays keyed ``"x"`` and ``"y"``."""
        return {"x": self.x, "y": self.y}

    def to_dataframe(self) -> pd.DataFrame:
        """Two-column frame with ``x`` and ``y`` columns."""
        return pd.DataFrame(self.to_dict())

    @classmethod
    def from_matrix(
        cls,
        data: np.ndarray,
        *,
        originator: str,
        record_type: str = "unknown curve type",
    ) -> Curve:
        """Wrap an ``(n, 2)`` x/y matrix as a curve; an existing array is not copied."""
        return cls(originator=originator, record_type=record_type, data=np.asarray(data))

    def binned(self, bin_size: int = 2) -> Curve:
        """Sum every ``bin_size`` channels into one, keeping each bin's first x-value.

        A trailing partial bin is zero-padded.

        Raises:
            ValueError: If ``bin_size`` is not a positive integer.
        """
        validate_positive_scalar(bin_size, name="bin_size")
        y = self.y
        n_bins = int(np.ceil(len(y) / bin_size))
        padded = np.zeros(n_bins * bin_size, dtype=float)
        padded[: len(y)] = y
        new_y = padded.reshape(n_bins, bin_size).sum(axis=1)
        new_x = self.x[::bin_size][:n_bins]
        return replace(self, data=np.column_stack([new_x, new_y]), originator="binned")

    def smoothed(
        self,
        *,
        k: int | None = None,
        fill: float = np.nan,
        align: str = "right",
        method: str = "mean",
        p_acceptance: float = 1e-7,
    ) -> Curve:
        """Smooth the y-values, leaving the x-values untouched.

        Args:
            k: Window width in channels. Defaults to ``ceil(n_points / 100)``.
            fill: Value used where the window is incomplete.
            align: Window position, one of ``"right"``, ``"center"``, ``"left"``.
            method: One of ``"mean"``, ``"median"``, ``"carter_etal_2018"``.
                The last ignores ``k``, ``fill`` and ``align``.
            p_acceptance: Poisson threshold for ``"carter_etal_2018"``.

        Returns:
            A new curve with ``originator="smoothed"``.

        Raises:
            ValueError: If ``p_acceptance`` rejects every count.
        """
        new_y = _smoothing(
            self.y,
            k=k,
            fill=fill,
            align=align,
            p_acceptance=p_acceptance,
            method=method,
        )
        return replace(self, data=np.column_stack([self.x, new_y]), originator="smoothed")

    def normalised(self, norm: _NormaliseArg = "max") -> Curve:
        """Scale the y-values against the reference selected by ``norm``.

        Args:
            norm: ``"max"`` (or ``True``), ``"min"``, ``"first"`` and ``"last"``
                divide by that y-value. ``"huot"`` subtracts the median of the
                final 20% as background, then scales to the maximum.
                ``"intensity"`` divides by the channel width. ``False`` returns
                the y-values unchanged. A number or array is used as the divisor
                directly.

        Returns:
            A new curve; non-finite results are replaced by 0 with a warning.
        """
        if isinstance(norm, str) and norm == "intensity":
            norm_vec = np.diff(np.concatenate([[0.0], self.x]))
            new_y = _normalise_curve(self.y, norm_vec)
        else:
            new_y = _normalise_curve(self.y, norm)
        return replace(self, data=np.column_stack([self.x, new_y]))

    def melt(self) -> pd.DataFrame:
        """Long-format frame with ``x``, ``y``, ``type`` and ``uid`` columns."""
        return pd.DataFrame(
            {
                "x": self.x,
                "y": self.y,
                "type": self.record_type,
                "uid": self.uid,
            }
        )
