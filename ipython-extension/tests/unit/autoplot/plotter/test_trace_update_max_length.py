"""Test that the correct updates are performed when a `Trace`'s max length is changed.

We also test that the correct warning / info toasts are shown when the trace switches
from being shown in full to being downsampled and vice versa.
"""

import numpy as np
import pytest


@pytest.mark.parametrize("series_length,max_length", [(10, 10), (10, 1000), (10, 10000), (10, np.inf), (10, 0)])
def test_update_trace_length_no_downsample(mock_toast, series_length, max_length, datetime_series, trace_from_series):
    # initialise trace
    series = datetime_series(series_length)
    toast = mock_toast
    trace = trace_from_series(series, toast)

    # update max length, test no change
    assert not trace.update_max_series_length(max_length)

    # test correct toasts shown
    toast.no_downsample_info.assert_not_called()
    toast.downsample_warning.assert_not_called()


@pytest.mark.parametrize("series_length,max_length", [(10, 9), (10, 2)])
def test_update_trace_length_new_downsample(mock_toast, series_length, max_length, datetime_series, trace_from_series):
    # initialise trace
    series = datetime_series(series_length)
    toast = mock_toast
    trace = trace_from_series(series, toast)

    # test correct toasts shown
    toast.downsample_warning.assert_not_called()

    # update max length, test updated
    assert trace.update_max_series_length(max_length)

    # test correct toasts shown
    toast.no_downsample_info.assert_not_called()
    toast.downsample_warning.assert_called_once()


@pytest.mark.parametrize("series_length,max_length", [(2000, 10), (2000, 999), (2000, 1000), (2000, 1500)])
def test_update_trace_length_downsample_twice(
    mock_toast, series_length, max_length, datetime_series, trace_from_series
):
    # initialise trace
    series = datetime_series(series_length)
    toast = mock_toast
    trace = trace_from_series(series, toast)

    # test correct toasts shown
    toast.downsample_warning.assert_called_once()

    # update max length, test updated (unless equal)
    assert trace.update_max_series_length(max_length) != (max_length == 1000)

    # test correct toasts shown
    toast.no_downsample_info.assert_not_called()
    toast.downsample_warning.assert_called_once()


@pytest.mark.parametrize("series_length,max_length", [(2000, 2000), (2000, 2001), (2000, 0)])
def test_update_trace_length_undo_downsample(mock_toast, series_length, max_length, datetime_series, trace_from_series):
    # initialise trace
    series = datetime_series(series_length)
    toast = mock_toast
    trace = trace_from_series(series, toast)

    # test correct toasts shown
    toast.downsample_warning.assert_called_once()

    # update max length, test updated
    assert trace.update_max_series_length(max_length)

    # test correct toasts shown
    toast.no_downsample_info.assert_called_once()
    toast.downsample_warning.assert_called_once()
