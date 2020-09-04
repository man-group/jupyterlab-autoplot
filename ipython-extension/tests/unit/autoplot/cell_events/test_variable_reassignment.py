"""Test that the `CellEventHandler` deals with variable reassignment correctly.

Each test checks that the expected updates are performed when a namespace
variable is changed from one type to another. For example,
`test_plottable_series_to_non_plottable()` tests the behaviour when a datetime
indexed, real valued series is changed to a non-plottable variable (e.g. a string).
"""

import mock
import pytest

from tests.unit.autoplot.mocks import COL, DF, DF_COL, MockSuccessfulExecution, VAR


def test_plottable_series_to_plottable_series(initialised_mocks, num_series, num_series_alt):
    initial = num_series
    final = num_series_alt

    shell, plotter, handler = initialised_mocks({VAR: initial})

    # update namespace and run again
    shell.user_ns = {VAR: final}

    with mock.patch.object(
        plotter, "update_trace_series", wraps=plotter.update_trace_series
    ) as mock_update_trace_series:
        handler.post_run_cell(MockSuccessfulExecution())

    # test expected method calls occurred
    mock_update_trace_series.assert_called_once()
    assert VAR == mock_update_trace_series.call_args[0][0]
    assert final.equals(mock_update_trace_series.call_args[0][1])

    # test expected updates performed
    assert handler[VAR].equals(final), "Series updated in handler"
    assert plotter[VAR].is_visible(), "Trace exists and is visible"


@pytest.mark.parametrize("final", [42, "A string", None, "SERIES"])
def test_plottable_series_to_non_plottable(final, initialised_mocks, num_series, str_series):
    initial = num_series
    final = str_series if final == "SERIES" else final

    shell, plotter, handler = initialised_mocks({VAR: initial})

    # update namespace and run again
    shell.user_ns = {VAR: final}

    with mock.patch.object(
        plotter, "update_trace_series", wraps=plotter.update_trace_series
    ) as mock_update_trace_series:
        handler.post_run_cell(MockSuccessfulExecution())

    # test expected method calls occurred
    mock_update_trace_series.assert_not_called()

    # test expected updates performed
    with pytest.raises(KeyError):
        _ = handler[VAR]  # series removed from handler

    assert not plotter[VAR].is_visible(), "Trace exists but is hidden"


@pytest.mark.parametrize("initial", [42, "A string", None, "SERIES"])
def test_non_plottable_to_plottable_series(initial, initialised_mocks, num_series, str_series):
    initial = str_series if initial == "SERIES" else initial
    final = num_series

    shell, plotter, handler = initialised_mocks({VAR: initial})

    # update namespace and run again
    shell.user_ns = {VAR: final}

    with mock.patch.object(plotter, "add_trace", wraps=plotter.add_trace) as mock_add_trace:
        handler.post_run_cell(MockSuccessfulExecution())

    # test expected method calls occurred
    mock_add_trace.assert_called_once()
    assert VAR == mock_add_trace.call_args[0][0]
    assert final.equals(mock_add_trace.call_args[0][1])

    # test expected updates performed
    assert handler[VAR].equals(final), "Series updated in handler"
    assert plotter[VAR].is_visible(), "Trace exists and is visible"


def test_plottable_column_to_plottable_column(initialised_mocks, num_dataframe, num_dataframe_alt):
    initial = num_dataframe
    final = num_dataframe_alt

    shell, plotter, handler = initialised_mocks({DF: initial})

    # update namespace and run again
    shell.user_ns = {DF: final}

    with mock.patch.object(
        plotter, "update_trace_series", wraps=plotter.update_trace_series
    ) as mock_update_trace_series:
        handler.post_run_cell(MockSuccessfulExecution())

    # test expected method calls occurred
    mock_update_trace_series.assert_called_once()
    assert DF_COL == mock_update_trace_series.call_args[0][0]
    assert final[COL].equals(mock_update_trace_series.call_args[0][1])

    # test expected updates performed
    assert handler[DF] == {DF_COL}, "Dataframe updated in handler"
    assert handler[DF_COL].equals(final[COL]), "Series updated in handler"
    assert plotter[DF_COL].is_visible(), "Trace exists and is visible"


def test_plottable_column_to_non_plottable_column(initialised_mocks, num_dataframe, str_dataframe):
    initial = num_dataframe
    final = str_dataframe

    shell, plotter, handler = initialised_mocks({DF: initial})

    # update namespace and run again
    shell.user_ns = {DF: final}

    with mock.patch.object(
        plotter, "update_trace_series", wraps=plotter.update_trace_series
    ) as mock_update_trace_series:
        handler.post_run_cell(MockSuccessfulExecution())

    # test expected method calls occurred
    mock_update_trace_series.assert_not_called()

    # test expected updates performed
    with pytest.raises(KeyError):
        _ = handler[DF]  # dataframe removed from handler

    with pytest.raises(KeyError):
        _ = handler[DF_COL]  # column series removed from handler

    assert not plotter[DF_COL].is_visible(), "Trace exists but is hidden"


def test_non_plottable_column_to_plottable_column(initialised_mocks, num_dataframe, str_dataframe):
    initial = str_dataframe
    final = num_dataframe

    shell, plotter, handler = initialised_mocks({DF: initial})

    # update namespace and run again
    shell.user_ns = {DF: final}

    with mock.patch.object(plotter, "add_trace", wraps=plotter.add_trace) as mock_add_trace:
        handler.post_run_cell(MockSuccessfulExecution())

    # test expected method calls occurred
    mock_add_trace.assert_called_once()
    assert DF_COL == mock_add_trace.call_args[0][0]
    assert final[COL].equals(mock_add_trace.call_args[0][1])
    assert DF == mock_add_trace.call_args[0][2]

    # test expected updates performed
    assert handler[DF] == {DF_COL}, "Dataframe updated in handler"
    assert plotter[DF_COL].is_visible(), "Trace exists and is visible"


def test_plottable_series_to_plottable_df(initialised_mocks, num_series, num_dataframe):
    initial = num_series
    final = num_dataframe

    shell, plotter, handler = initialised_mocks({DF: initial})

    # update namespace and run again
    shell.user_ns = {DF: final}

    with mock.patch.object(plotter, "add_trace", wraps=plotter.add_trace) as mock_add_trace:
        handler.post_run_cell(MockSuccessfulExecution())

    # test expected method calls occurred
    mock_add_trace.assert_called_once()
    assert DF_COL == mock_add_trace.call_args[0][0]
    assert final[COL].equals(mock_add_trace.call_args[0][1])
    assert DF == mock_add_trace.call_args[0][2]

    # test expected updates performed
    assert handler[DF] == {DF_COL}, "Original series replaced by dataframe"
    assert not plotter[DF].is_visible(), "Original trace exists but is hidden"
    assert plotter[DF_COL].is_visible(), "New trace exists and is visible"


def test_plottable_series_to_non_plottable_df(initialised_mocks, num_series, str_dataframe):
    initial = num_series
    final = str_dataframe

    shell, plotter, handler = initialised_mocks({DF: initial})

    # update namespace and run again
    shell.user_ns = {DF: final}

    with mock.patch.object(plotter, "add_trace", wraps=plotter.add_trace) as mock_add_trace:
        handler.post_run_cell(MockSuccessfulExecution())

    # test expected method calls occurred
    mock_add_trace.assert_not_called()

    # test expected updates performed
    with pytest.raises(KeyError):
        _ = handler[DF]  # dataframe removed from handler

    with pytest.raises(KeyError):
        _ = handler[DF_COL]  # column series not added to handler

    assert not plotter[DF].is_visible(), "Original trace exists but is hidden"


def test_plottable_df_to_plottable_series(initialised_mocks, num_dataframe, num_series):
    initial = num_dataframe
    final = num_series

    shell, plotter, handler = initialised_mocks({DF: initial})

    # update namespace and run again
    shell.user_ns = {DF: final}

    with mock.patch.object(plotter, "add_trace", wraps=plotter.add_trace) as mock_add_trace:
        handler.post_run_cell(MockSuccessfulExecution())

    # test expected method calls occurred
    mock_add_trace.assert_called_once()
    assert DF == mock_add_trace.call_args[0][0]
    assert final.equals(mock_add_trace.call_args[0][1])
    assert mock_add_trace.call_args[0][2] is None

    # test expected updates performed
    assert handler[DF].equals(final), "Original dataframe replaced by series"

    with pytest.raises(KeyError):
        _ = handler[DF_COL]  # column series not removed from handler

    assert not plotter[DF_COL].is_visible(), "Original trace exists but is hidden"
    assert plotter[DF].is_visible(), "New trace exists and is visible"


@pytest.mark.parametrize("final", [42, "A string", None, "SERIES"])
def test_plottable_df_to_non_plottable(final, initialised_mocks, num_dataframe, str_series):
    initial = num_dataframe
    final = str_series if final == "SERIES" else final

    shell, plotter, handler = initialised_mocks({DF: initial})

    # update namespace and run again
    shell.user_ns = {DF: final}

    with mock.patch.object(
        plotter, "update_trace_series", wraps=plotter.update_trace_series
    ) as mock_update_trace_series:
        handler.post_run_cell(MockSuccessfulExecution())

    # test expected method calls occurred
    mock_update_trace_series.assert_not_called()

    # test expected updates performed
    with pytest.raises(KeyError):
        _ = handler[DF]  # dataframe removed from handler

    with pytest.raises(KeyError):
        _ = handler[DF_COL]  # column series removed from handler

    assert not plotter[DF_COL].is_visible(), "Original trace exists but is hidden"


@pytest.mark.parametrize("initial", [42, "A string", None, "SERIES"])
def test_non_plottable_to_plottable_df(initial, initialised_mocks, num_dataframe, str_series):
    initial = str_series if initial == "SERIES" else initial
    final = num_dataframe

    shell, plotter, handler = initialised_mocks({DF: initial})

    # update namespace and run again
    shell.user_ns = {DF: final}

    with mock.patch.object(plotter, "add_trace", wraps=plotter.add_trace) as mock_add_trace:
        handler.post_run_cell(MockSuccessfulExecution())

    # test expected method calls occurred
    mock_add_trace.assert_called_once()
    assert DF_COL == mock_add_trace.call_args[0][0]
    assert final[COL].equals(mock_add_trace.call_args[0][1])
    assert DF == mock_add_trace.call_args[0][2]

    # test expected updates performed
    assert handler[DF] == {DF_COL}, "Dataframe added to handler"
    assert plotter[DF_COL].is_visible(), "Trace exists and is visible"
