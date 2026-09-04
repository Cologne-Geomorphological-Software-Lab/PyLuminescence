"""Tests for the core Record and Curve dataclasses."""

from __future__ import annotations

import uuid
from dataclasses import replace

import numpy as np
import pandas as pd
import pytest

from luminescence.core.base import Record
from luminescence.core.curve import Curve


class TestRecord:
    def test_requires_originator(self) -> None:
        assert Record(originator="test_fn").originator == "test_fn"

    def test_defaults(self) -> None:
        record = Record(originator="test_fn")
        assert record.info == {}
        assert record.pids == ()

    def test_uid_is_valid_uuid4(self) -> None:
        record = Record(originator="test_fn")
        assert str(uuid.UUID(record.uid, version=4)) == record.uid

    def test_each_instance_gets_a_fresh_uid(self) -> None:
        assert Record(originator="test_fn").uid != Record(originator="test_fn").uid

    def test_replicate_returns_same_reference_n_times(self) -> None:
        record = Record(originator="test_fn")
        copies = record.replicate(3)
        assert len(copies) == 3
        assert all(c is record for c in copies)

    def test_replicate_rejects_non_positive(self) -> None:
        with pytest.raises(ValueError, match="positive integer"):
            Record(originator="test_fn").replicate(0)


class TestCurve:
    def _make(self, **overrides: object) -> Curve:
        defaults: dict[str, object] = {
            "originator": "test_fn",
            "record_type": "OSL",
            "data": np.array([[1.0, 10.0], [2.0, 20.0], [3.0, 30.0]]),
        }
        defaults.update(overrides)
        return Curve(**defaults)  # type: ignore[arg-type]

    def test_defaults(self) -> None:
        curve = self._make()
        assert curve.curve_type == ""
        assert curve.pids == ()

    def test_len_is_point_count_not_max_x(self) -> None:
        curve = self._make()  # x max is 3.0, but 3 points
        assert len(curve) == 3
        assert curve.duration == 3.0

    def test_x_y_properties(self) -> None:
        curve = self._make()
        np.testing.assert_array_equal(curve.x, [1.0, 2.0, 3.0])
        np.testing.assert_array_equal(curve.y, [10.0, 20.0, 30.0])

    def test_array_coercion(self) -> None:
        curve = self._make()
        np.testing.assert_array_equal(np.asarray(curve), curve.data)

    def test_replace_preserves_uid_and_unrelated_fields(self) -> None:
        original = self._make()
        updated = replace(original, curve_type="measured")
        assert updated.curve_type == "measured"
        assert updated.uid == original.uid
        assert np.array_equal(updated.data, original.data)

    def test_equality_ignores_uid_and_pids(self) -> None:
        a, b = self._make(), self._make()
        assert a.uid != b.uid
        assert a == b

    def test_equality_compares_data(self) -> None:
        a = self._make(data=np.array([[1.0, 10.0]]))
        b = self._make(data=np.array([[1.0, 99.0]]))
        assert a != b

    def test_inequality_with_other_types(self) -> None:
        assert self._make() != "not a curve"

    def test_get_info_without_key_returns_data(self) -> None:
        curve = self._make()
        assert curve.get_info() is curve.data

    def test_get_info_with_key(self) -> None:
        curve = self._make(info={"position": 1})
        assert curve.get_info("position") == 1

    def test_get_info_warns_on_empty_info(self) -> None:
        with pytest.warns(UserWarning, match="empty"):
            assert self._make(info={}).get_info("x") is None

    def test_get_info_warns_on_unknown_key(self) -> None:
        with pytest.warns(UserWarning, match="Invalid 'key'"):
            assert self._make(info={"a": 1}).get_info("b") is None

    def test_info_names(self) -> None:
        assert self._make(info={"a": 1, "b": 2}).info_names() == ["a", "b"]

    def test_to_dict_and_to_dataframe(self) -> None:
        curve = self._make()
        assert set(curve.to_dict()) == {"x", "y"}
        pd.testing.assert_frame_equal(
            curve.to_dataframe(), pd.DataFrame({"x": curve.x, "y": curve.y})
        )

    def test_from_matrix(self) -> None:
        curve = Curve.from_matrix(np.array([[1.0, 2.0]]), originator="test_fn")
        assert curve.record_type == "unknown curve type"

    def test_repr_reports_ranges_and_counts(self) -> None:
        text = repr(self._make(info={"position": 1}))
        assert "record_type='OSL'" in text
        assert "measured values: 3" in text
        assert "x range: 1.0 .. 3.0" in text
        assert "info elements: 1" in text
        assert "contains NaN" not in text

    def test_repr_flags_nan_values(self) -> None:
        curve = self._make(data=np.array([[1.0, np.nan], [2.0, 20.0]]))
        assert "contains NaN values" in repr(curve)

    def test_repr_handles_all_nan_y(self) -> None:
        curve = self._make(data=np.array([[1.0, np.nan]]))
        assert "y range: nan .. nan" in repr(curve)

    def test_binned_sums_channels(self) -> None:
        curve = self._make(data=np.array([[1.0, 1.0], [2.0, 2.0], [3.0, 3.0], [4.0, 4.0]]))
        binned = curve.binned(bin_size=2)
        np.testing.assert_array_equal(binned.y, [3.0, 7.0])  # (1+2), (3+4)
        np.testing.assert_array_equal(binned.x, [1.0, 3.0])

    def test_binned_zero_pads_trailing_partial_bin(self) -> None:
        curve = self._make(data=np.array([[1.0, 1.0], [2.0, 2.0], [3.0, 3.0]]))
        binned = curve.binned(bin_size=2)
        np.testing.assert_array_equal(binned.y, [3.0, 3.0])  # (1+2), (3+0)
        np.testing.assert_array_equal(binned.x, [1.0, 3.0])

    def test_binned_rejects_non_positive(self) -> None:
        with pytest.raises(ValueError, match="positive integer"):
            self._make().binned(0)

    def test_transformations_record_their_originator(self) -> None:
        curve = self._make()
        assert curve.binned().originator == "binned"
        assert curve.smoothed().originator == "smoothed"

    def test_smoothed_mean_right_aligned(self) -> None:
        curve = self._make(
            data=np.column_stack([np.arange(5.0), np.array([1.0, 2.0, 3.0, 4.0, 5.0])])
        )
        smoothed = curve.smoothed(k=2, method="mean", fill=0.0)
        assert smoothed.y[0] == 0.0  # incomplete window filled
        assert smoothed.y[1] == pytest.approx(1.5)

    @pytest.mark.parametrize(
        ("align", "expected"),
        [
            ("right", [0.0, 0.0, 2.0, 3.0, 4.0]),
            ("center", [0.0, 2.0, 3.0, 4.0, 0.0]),
            ("left", [2.0, 3.0, 4.0, 0.0, 0.0]),
        ],
    )
    def test_smoothed_alignment_shifts_the_window(self, align: str, expected: list[float]) -> None:
        curve = self._make(
            data=np.column_stack([np.arange(5.0), np.array([1.0, 2.0, 3.0, 4.0, 5.0])])
        )
        smoothed = curve.smoothed(k=3, align=align, fill=0.0)
        np.testing.assert_array_equal(smoothed.y, expected)
        np.testing.assert_array_equal(smoothed.x, curve.x)

    def test_smoothed_median_ignores_the_outlier(self) -> None:
        curve = self._make(data=np.column_stack([np.arange(4.0), np.array([1.0, 100.0, 2.0, 3.0])]))
        smoothed = curve.smoothed(k=3, method="median", fill=0.0)
        np.testing.assert_array_equal(smoothed.y, [0.0, 0.0, 2.0, 3.0])

    def test_smoothed_default_k_is_one_percent_of_the_points(self) -> None:
        curve = self._make(
            data=np.column_stack([np.arange(5.0), np.array([1.0, 2.0, 3.0, 4.0, 5.0])])
        )
        np.testing.assert_array_equal(curve.smoothed().y, curve.y)  # ceil(5 / 100) == 1

    def test_smoothed_carter_replaces_improbable_counts(self) -> None:
        counts = 100.0 + np.arange(20.0)
        counts[12] = 113.0  # makes the neighbour mean 110.25, so rounding is observable
        counts[10] = 400.0  # far outside the Poisson spread of the rest
        curve = self._make(data=np.column_stack([np.arange(20.0), counts]))
        smoothed = curve.smoothed(method="carter_etal_2018")
        # mean of the four neighbours 108, 109, 111, 113, rounded
        assert smoothed.y[10] == 110.0
        np.testing.assert_array_equal(np.delete(smoothed.y, 10), np.delete(counts, 10))

    def test_smoothed_carter_rejects_p_acceptance_that_drops_everything(self) -> None:
        with pytest.raises(ValueError, match="rejects all counts"):
            self._make().smoothed(method="carter_etal_2018", p_acceptance=1.0)

    def test_smoothed_rejects_bad_method(self) -> None:
        with pytest.raises(ValueError, match="method"):
            self._make().smoothed(method="bogus")

    def test_smoothed_rejects_bad_align(self) -> None:
        with pytest.raises(ValueError, match="align"):
            self._make().smoothed(align="bogus")

    def test_smoothed_rejects_non_positive_k(self) -> None:
        with pytest.raises(ValueError, match="positive integer"):
            self._make().smoothed(k=0)

    @pytest.mark.parametrize(
        ("norm", "expected"),
        [
            ("max", [0.5, 1.0]),
            (True, [0.5, 1.0]),
            ("min", [1.0, 2.0]),
            ("first", [1.0, 2.0]),
            ("last", [0.5, 1.0]),
            (2.0, [2.0, 4.0]),
        ],
    )
    def test_normalised_references(self, norm: float | str | bool, expected: list[float]) -> None:
        curve = self._make(data=np.array([[1.0, 4.0], [2.0, 8.0]]))
        np.testing.assert_array_equal(curve.normalised(norm).y, expected)

    def test_normalised_by_array_divides_channelwise(self) -> None:
        curve = self._make(data=np.array([[1.0, 4.0], [2.0, 8.0]]))
        np.testing.assert_array_equal(curve.normalised(np.array([2.0, 4.0])).y, [2.0, 2.0])

    def test_normalised_false_leaves_the_values_alone(self) -> None:
        curve = self._make()
        np.testing.assert_array_equal(curve.normalised(False).y, curve.y)

    def test_normalised_huot_subtracts_background_then_scales(self) -> None:
        # background is the median of the last 20%, i.e. of [2.0, 4.0] alone
        y = np.array([10.0] * 8 + [2.0, 4.0])
        curve = self._make(data=np.column_stack([np.arange(10.0), y]))
        np.testing.assert_allclose(curve.normalised("huot").y, [1.0] * 8 + [-1 / 7, 1 / 7])

    def test_normalised_intensity_divides_by_channel_width(self) -> None:
        curve = self._make(data=np.array([[2.0, 4.0], [4.0, 8.0]]))
        np.testing.assert_array_equal(curve.normalised("intensity").y, [2.0, 4.0])

    def test_normalised_warns_and_zeroes_non_finite_results(self) -> None:
        curve = self._make(data=np.array([[1.0, 0.0], [2.0, 0.0]]))
        with pytest.warns(UserWarning, match="Inf/NaN"):
            normalised = curve.normalised("max")
        np.testing.assert_array_equal(normalised.y, [0.0, 0.0])

    def test_normalised_keeps_the_x_values(self) -> None:
        curve = self._make()
        np.testing.assert_array_equal(curve.normalised("max").x, curve.x)

    def test_normalised_unknown_raises(self) -> None:
        with pytest.raises(ValueError, match="Unknown 'norm'"):
            self._make().normalised("bogus")

    def test_melt_long_format(self) -> None:
        curve = self._make()
        melted = curve.melt()
        assert list(melted.columns) == ["x", "y", "type", "uid"]
        assert (melted["type"] == "OSL").all()
