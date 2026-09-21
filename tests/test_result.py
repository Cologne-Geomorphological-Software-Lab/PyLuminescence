"""Tests for the Result record, after R's test_RLum.Results-class.R."""

from __future__ import annotations

import uuid

import numpy as np
import pandas as pd
import pytest

from luminescence.core.base import Record
from luminescence.core.result import Result


@pytest.fixture
def obj() -> Result:
    # Same element names as R's fixture, calc_FuchsLang2001() output.
    return Result(
        originator="calc_FuchsLang2001",
        data={
            "summary": pd.DataFrame({"de": [2866.11], "de_err": [157.35]}),
            "data": pd.DataFrame({"De": [2800.0, 2900.0], "De.Error": [150.0, 160.0]}),
            "args": {"cvThreshold": 5, "startDeValue": 1},
            "usedDeValues": pd.DataFrame({"De": [2800.0, 2900.0]}),
        },
        info={"call": ["calc_FuchsLang2001", "BT998"]},
    )


@pytest.fixture
def empty() -> Result:
    return Result(originator="test_fn")


class TestConstruction:
    def test_is_a_record(self, obj: Result) -> None:
        assert isinstance(obj, Record)

    def test_empty_defaults(self, empty: Result) -> None:
        assert empty.data == {}
        assert empty.info == {}
        assert empty.pids == ()

    def test_uid_is_fresh_uuid4(self) -> None:
        a, b = Result(originator="test_fn"), Result(originator="test_fn")
        assert a.uid != b.uid
        assert str(uuid.UUID(a.uid, version=4)) == a.uid

    def test_default_data_is_not_shared(self) -> None:
        a, b = Result(originator="test_fn"), Result(originator="test_fn")
        a.data["x"] = 1
        assert b.data == {}


class TestEquality:
    def test_equal_to_itself(self, obj: Result) -> None:
        assert obj == obj

    def test_different_data_is_not_equal(self) -> None:
        # Record.__eq__ would compare only originator and info.
        a = Result(originator="test_fn", data={"a": 1})
        b = Result(originator="test_fn", data={"a": 2})
        assert a != b

    def test_same_payload_is_not_equal(self) -> None:
        a = Result(originator="test_fn", data={"a": np.ones(2)})
        b = Result(originator="test_fn", data={"a": np.ones(2)})
        assert a != b


class TestCoercion:
    def test_to_dict(self, obj: Result) -> None:
        assert list(obj.to_dict()) == ["summary", "data", "args", "usedDeValues"]

    def test_to_dict_does_not_alias(self, obj: Result) -> None:
        obj.to_dict()["extra"] = 1
        assert "extra" not in obj.names()

    def test_from_dict_sets_coercion_originator(self) -> None:
        converted = Result.from_dict({"a": 1})
        assert converted.originator == "coercion"
        assert converted.get("a") == 1

    def test_from_empty_dict(self) -> None:
        assert len(Result.from_dict({})) == 0


class TestLengthAndNames:
    def test_names(self, obj: Result) -> None:
        assert obj.names() == ["summary", "data", "args", "usedDeValues"]

    def test_len_counts_data_not_info(self, obj: Result) -> None:
        assert len(obj) == 4

    def test_empty(self, empty: Result) -> None:
        assert len(empty) == 0
        assert empty.names() == []


class TestGet:
    def test_no_key_returns_first_element(self, obj: Result) -> None:
        assert obj.get() is obj.data["summary"]

    def test_no_key_on_empty_returns_none(self, empty: Result) -> None:
        # R: list()[1][[1]] is NULL, not an error.
        assert empty.get() is None

    def test_by_name(self, obj: Result) -> None:
        assert obj.get("data") is obj.data["data"]

    def test_by_index_is_zero_based(self, obj: Result) -> None:
        assert obj.get(1) is obj.data["data"]

    def test_unknown_name_lists_valid_names(self, obj: Result) -> None:
        with pytest.raises(KeyError, match="summary, data, args, usedDeValues"):
            obj.get("error")

    def test_index_out_of_bounds(self, obj: Result) -> None:
        with pytest.raises(IndexError, match="out of bounds"):
            obj.get(100)

    def test_rejects_bool(self, obj: Result) -> None:
        with pytest.raises(TypeError):
            obj.get(False)  # type: ignore[arg-type]

    def test_rejects_float(self, obj: Result) -> None:
        with pytest.raises(TypeError):
            obj.get(1.5)  # type: ignore[arg-type]

    def test_getitem_matches_get(self, obj: Result) -> None:
        assert obj["args"] is obj.get("args")
        assert obj[0] is obj.get(0)

    def test_numpy_payload(self) -> None:
        arr = np.arange(3.0)
        assert Result(originator="test_fn", data={"a": arr}).get("a") is arr


class TestSubset:
    def test_selected_elements_in_selection_order(self, obj: Result) -> None:
        sub = obj.subset(["data", "summary"])
        assert isinstance(sub, Result)
        assert sub.names() == ["data", "summary"]
        assert sub.get("data") is obj.get("data")

    def test_index_selection_keeps_names(self, obj: Result) -> None:
        assert obj.subset([0, 2]).names() == ["summary", "args"]

    def test_keeps_originator(self, obj: Result) -> None:
        assert obj.subset(["summary"]).originator == "calc_FuchsLang2001"

    def test_new_uid_and_no_info(self, obj: Result) -> None:
        # R builds the subset via set_RLum() without passing info or .uid.
        sub = obj.subset(["summary"])
        assert sub.uid != obj.uid
        assert sub.info == {}

    def test_unknown_name(self, obj: Result) -> None:
        with pytest.raises(KeyError, match="valid names"):
            obj.subset(["summary", "error"])

    def test_index_out_of_bounds(self, obj: Result) -> None:
        with pytest.raises(IndexError, match="out of bounds"):
            obj.subset([0, 100])

    def test_original_unchanged(self, obj: Result) -> None:
        obj.subset(["summary"])
        assert len(obj) == 4


class TestGetInfo:
    def test_value(self, obj: Result) -> None:
        assert obj.get_info("call") == ["calc_FuchsLang2001", "BT998"]

    def test_unknown_name_warns(self, obj: Result) -> None:
        with pytest.warns(UserWarning, match="valid names are: call"):
            assert obj.get_info("error") is None

    def test_empty_info_warns(self, empty: Result) -> None:
        with pytest.warns(UserWarning, match="no info objects"):
            assert empty.get_info("error") is None


class TestRepr:
    def test_content(self, obj: Result) -> None:
        text = repr(obj)
        assert "calc_FuchsLang2001" in text
        for name in obj.names():
            assert f"${name}" in text
        assert "DataFrame" in text

    def test_empty(self, empty: Result) -> None:
        assert "test_fn" in repr(empty)
