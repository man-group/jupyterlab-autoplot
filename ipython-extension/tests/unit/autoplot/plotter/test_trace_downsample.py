"""Test the `_get_downsampled()` method of the `Trace` class.

In general, we expect the trace to be downsampled if it is longer than the `max_length`,
but unchanged if it shorter. We also expect warning / info toasts to be shown when
the trace switches from being shown in full to being downsampled and vice versa.
"""

import pytest

from autoplot.plotter.trace import Trace
from tests.unit.autoplot.mocks import VAR


@pytest.mark.parametrize("length", [2, 100, 999, 1000])
def test_no_downsample_if_smaller(mock_toast, length, datetime_series):
    toast = mock_toast
    series = datetime_series(length)
    trace = Trace(toast, VAR, series, 1, max_length=1000)

    # test not downsampled
    assert series.equals(trace._get_downsampled()), "Series unchanged"

    # test no warning shown
    toast.downsample_warning.assert_not_called()


@pytest.mark.parametrize("length", [1001, 1002, 2000, 3547, 12345])
def test_correct_downsample_if_larger(mock_toast, length, datetime_series):
    toast = mock_toast
    series = datetime_series(length)
    original = series.copy()
    trace = Trace(toast, VAR, series, 1, max_length=1000)

    # test downsampled correctly
    assert len(trace._get_downsampled()) == 1000, "Length reduced to correct value"
    assert trace._get_downsampled()[0] == series[0], "First value unchanged"
    assert trace._get_downsampled()[-1] == series[-1], "Last value unchanged"
    assert series.equals(original), "Original series unchanged"

    # test warning shown
    toast.downsample_warning.assert_called_once_with(VAR, length, 1000)


@pytest.mark.parametrize(
    "length,new_length", [(2, 1000), (999, 2), (1000, 999), (1001, 500), (2000, 999), (12345, 1000)]
)
def test_no_downsample_for_smaller_updated_trace(mock_toast, length, new_length, datetime_series):
    toast = mock_toast
    series = datetime_series(length)
    trace = Trace(toast, VAR, series, 1, max_length=1000)

    new_series = datetime_series(new_length)
    trace.update_series(new_series)

    # test not downsampled
    assert new_series.equals(trace._get_downsampled()), "Series unchanged"

    # test correct warnings shown
    if length > 1000:
        toast.downsample_warning.assert_called_once_with(VAR, length, 1000)
    else:
        toast.downsample_warning.assert_not_called()


@pytest.mark.parametrize(
    "length,new_length", [(2, 1001), (999, 2000), (1000, 12345), (1001, 1002), (2000, 1500), (12345, 12346)]
)
def test_correct_downsample_for_updated_trace(mock_toast, length, new_length, datetime_series):
    toast = mock_toast
    series = datetime_series(length)
    trace = Trace(toast, VAR, series, 1, max_length=1000)

    new_series = datetime_series(new_length)
    original = new_series.copy()
    trace.update_series(new_series)

    # test updated series downsample correctly
    assert len(trace._get_downsampled()) == 1000, "Length reduced to correct value"
    assert trace._get_downsampled()[0] == new_series[0], "First value unchanged"
    assert trace._get_downsampled()[-1] == new_series[-1], "Last value unchanged"
    assert new_series.equals(original), "Original series unchanged"

    # test correct warnings shown
    if length > 1000:
        toast.downsample_warning.assert_called_once_with(VAR, length, 1000)
    else:
        # only shown if warning has not already been shown for this variable
        toast.downsample_warning.assert_called_once_with(VAR, new_length, 1000)
