"""Test that the correct updates are performed when a `Trace`'s series is changed.

We also test that the trace is correctly plotted once it has been updated.
"""

import numpy as np
import pandas as pd
import pytest

from tests.unit.autoplot.plotter.image_utils import images_equal, save_expected_plot, save_trace_plot


@pytest.fixture()
def index_1():
    return pd.date_range(start="2020-01-01", periods=10, freq="d")


@pytest.fixture()
def index_2():
    return pd.date_range(start="2020-01-01", periods=10, freq="h")


@pytest.fixture()
def index_long():
    return pd.date_range(start="2020-01-01", periods=10000, freq="h")


@pytest.fixture()
def values_1(index_1):
    return np.random.randn(len(index_1))


@pytest.fixture()
def values_2(index_2):
    return np.random.randn(len(index_2))


@pytest.fixture()
def values_long(index_long):
    return np.random.randn(len(index_long))


def update_trace_and_compare_plots(trace, final):
    # save expected plot
    expected = save_expected_plot(final)

    # update and plot trace
    assert trace.update_series(final)
    actual = save_trace_plot(trace)

    # test actual equals expected
    assert images_equal(expected, actual)


def test_update_series_index_only(trace_from_series, index_1, index_2, values_1):
    # define initial and final series
    initial = pd.Series(values_1, index=index_1)
    final = pd.Series(values_1, index=index_2)

    # initialise trace
    trace = trace_from_series(initial)

    # run test
    update_trace_and_compare_plots(trace, final)


def test_update_series_values_only(trace_from_series, index_1, values_1, values_2):
    # define initial and final series
    initial = pd.Series(values_1, index=index_1)
    final = pd.Series(values_2, index=index_1)

    # initialise trace
    trace = trace_from_series(initial)

    # run test
    update_trace_and_compare_plots(trace, final)


def test_update_series_index_and_values(trace_from_series, index_1, index_2, values_1, values_2):
    # define initial and final series
    initial = pd.Series(values_1, index=index_1)
    final = pd.Series(values_2, index=index_2)

    # initialise trace
    trace = trace_from_series(initial)

    # run test
    update_trace_and_compare_plots(trace, final)


def test_update_series_different_length(trace_from_series, index_1, index_2, values_1, values_2):
    # define initial and final series
    initial = pd.Series(values_1, index=index_1)
    final = pd.Series(values_2[::2], index=index_2[::2])

    # initialise trace
    trace = trace_from_series(initial)

    # run test
    update_trace_and_compare_plots(trace, final)


def test_update_series_downsampled_initial(trace_from_series, index_1, index_long, values_1, values_long):
    # define initial and final series
    initial = pd.Series(values_long, index=index_long)
    final = pd.Series(values_1, index=index_1)

    # initialise trace
    trace = trace_from_series(initial)

    # run test
    update_trace_and_compare_plots(trace, final)


def test_update_series_no_difference(trace_from_series, index_1, values_1):
    # define initial and final series
    initial = pd.Series(values_1, index=index_1)
    final = pd.Series(values_1, index=index_1)

    # initialise trace
    trace = trace_from_series(initial)

    # save initial trace as expected plot
    expected = save_trace_plot(trace)

    # update plot and save
    assert not trace.update_series(final)
    actual = save_trace_plot(trace)

    # test no change
    assert images_equal(expected, actual)
