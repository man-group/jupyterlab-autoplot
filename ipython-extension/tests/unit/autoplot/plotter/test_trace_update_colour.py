"""Test that a `Trace`'s colour can be changed and is plotted correctly.

We also test that a warning is shown if an invalid colour is given.
"""

import pytest

from tests.unit.autoplot.plotter.image_utils import images_equal, save_expected_plot, save_trace_plot


@pytest.mark.parametrize("colour", ["C1", "r", "green", "#ff007f"])
def test_update_trace_valid_colour(colour, datetime_series, trace_from_series):
    series = datetime_series(10)
    expected = save_expected_plot(series, colour)

    # initialise and change the colour of a trace
    trace = trace_from_series(series)
    assert trace.update_colour(colour)

    actual = save_trace_plot(trace)

    # test actual equals expected
    assert images_equal(expected, actual)


@pytest.mark.parametrize("colour", ["h", "gren", "#ff07f"])
def test_update_trace_invalid_colour(mock_toast, colour, datetime_series, trace_from_series):
    toast = mock_toast
    series = datetime_series(10)
    trace = trace_from_series(series, toast)

    # save initial trace as expected plot
    expected = save_trace_plot(trace)

    # update plot and save
    assert not trace.update_colour(colour)
    actual = save_trace_plot(trace)

    # test no change
    assert images_equal(expected, actual)

    # test toast shown
    toast.invalid_trace_colour.assert_called_once_with(colour)


def test_update_trace_same_colour(datetime_series, trace_from_series):
    series = datetime_series(10)
    trace = trace_from_series(series)

    # save initial trace as expected plot
    expected = save_trace_plot(trace)

    # update plot and save
    assert not trace.update_colour("C0")
    actual = save_trace_plot(trace)

    # test no change
    assert images_equal(expected, actual)
