"""Test that the `CellEventHandler` deals with variable assignment correctly.

Each test checks that the expected variables are extracted from the namespace
and stored in the handler. We only expect datetime indexed, real valued series
to be stored, unless their names begin with an underscore or are reserved.
"""

import numpy as np
import pandas as pd
import pytest

from tests.unit.autoplot.mocks import VAR


@pytest.mark.parametrize("name,expected", [("var", True), ("_var", False), ("v_ar", True), ("_", False)])
def test_underscore_variables_skipped(name, expected, initialised_mocks, datetime_series):
    # initialise mocks with parameters
    user_ns = {name: datetime_series(5)}
    _, _, handler = initialised_mocks(user_ns)

    # test stored variables are expected ones
    if expected:
        _ = handler[name]
    else:
        with pytest.raises(KeyError):
            _ = handler[name]


def test_reserved_variables_skipped(initialised_mocks, datetime_series):
    # initialise mocks with parameters
    user_ns = {"var": datetime_series(10), "res": datetime_series(5)}
    shell, plotter, handler = initialised_mocks(user_ns, reserved={"res"})

    # test stored variables are expected ones
    _ = handler["var"]

    with pytest.raises(KeyError):
        _ = handler["res"]


@pytest.mark.parametrize(
    "index,expected",
    [
        (pd.date_range("2020-01-01", "2020-02-01", freq="d"), True),  # days
        (pd.date_range("2020-01-01", "2020-01-05", freq="h"), True),  # hours
        (pd.date_range("2020-01-01", "2020-01-02", freq="min"), True),  # minutes
        (range(20), False),  # int
        (["a", "b", "c"], False),  # strings
        (["1", "2", "3"], False),  # number strings
    ],
)
def test_only_datetime_indexed_series_added(index, expected, initialised_mocks):
    # initialise mocks with parameters
    user_ns = {VAR: pd.Series([1] * len(index), index=index)}
    _, _, handler = initialised_mocks(user_ns)

    # test stored variables are expected ones
    if expected:
        _ = handler[VAR]
    else:
        with pytest.raises(KeyError):
            _ = handler[VAR]


@pytest.mark.parametrize(
    "values,expected",
    [
        (range(10), True),  # int
        (np.random.randn(20), True),  # float
        ([1e100, 0, -1e99], True),  # big
        (np.array([1 + 1j, 2 + 2j, 3 + 3j]), False),  # complex
        (np.array([], dtype=int), False),  # empty
        ([1], False),  # short
        (["a", "b", "c"], False),  # string
        (["1", "2", "3"], False),  # number strings
    ],
)
def test_only_numeric_series_added(values, expected, datetime_index, initialised_mocks):
    # initialise mocks with parameters
    user_ns = {VAR: pd.Series(values, index=datetime_index(len(values)))}
    _, _, handler = initialised_mocks(user_ns)

    # test stored variables are expected ones
    if expected:
        _ = handler[VAR]
    else:
        with pytest.raises(KeyError):
            _ = handler[VAR]
