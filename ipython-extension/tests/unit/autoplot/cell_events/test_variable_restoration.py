"""Test that the `CellEventHandler` deals with variable restoration correctly.

Each test checks that the expected updates are performed when a namespace
variable is deleted then a new value (or the original one) is assigned to it again.
In general, we expect the series to be updated, and its trace made visible again with
its colour unchanged.
"""

import mock
import pytest

from tests.unit.autoplot.mocks import COL, DF, DF_COL, MockSuccessfulExecution, VAR


def test_deleted_series_restores_correctly(initialised_mocks, num_series, num_series_alt):
    initial = num_series
    final = num_series_alt

    # initialise mocks with namespace
    shell, plotter, handler = initialised_mocks({VAR: initial})
    colour = plotter[VAR].get_line().get_color()

    # remove the variable and rerun
    shell.user_ns.pop(VAR)
    handler.post_run_cell(MockSuccessfulExecution())

    with pytest.raises(KeyError):
        _ = handler[VAR]  # test correctly removed

    # add new series with same name and run
    shell.user_ns[VAR] = final

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
    assert plotter[VAR].get_line().get_color() == colour, "Trace colour unchanged"


def test_deleted_dataframe_restores_correctly(initialised_mocks, num_dataframe, num_dataframe_alt):
    initial = num_dataframe
    final = num_dataframe_alt

    # initialise mocks with namespace
    shell, plotter, handler = initialised_mocks({DF: initial})
    colour = plotter[DF_COL].get_line().get_color()

    # remove the variable and rerun
    shell.user_ns.pop(DF)
    handler.post_run_cell(MockSuccessfulExecution())

    with pytest.raises(KeyError):
        _ = handler[DF]  # test correctly removed

    # add new series with same name and run
    shell.user_ns[DF] = final

    with mock.patch.object(
        plotter, "update_trace_series", wraps=plotter.update_trace_series
    ) as mock_update_trace_series:
        handler.post_run_cell(MockSuccessfulExecution())

    # test expected method calls occurred
    mock_update_trace_series.assert_called_once()
    assert DF_COL == mock_update_trace_series.call_args[0][0]
    assert final[COL].equals(mock_update_trace_series.call_args[0][1])

    # test expected updates performed
    assert handler[DF_COL].equals(final[COL]), "Series updated in handler"
    assert plotter[DF_COL].is_visible(), "Trace exists and is visible"
    assert plotter[DF_COL].get_line().get_color() == colour, "Trace colour unchanged"


def test_deleted_column_restores_correctly(initialised_mocks, num_dataframe, num_series_alt):
    df = num_dataframe
    final_col = num_series_alt

    # initialise mocks with namespace
    shell, plotter, handler = initialised_mocks({DF: df})
    colour = plotter[DF_COL].get_line().get_color()

    # remove the variable and rerun
    df.drop(columns=[COL], inplace=True)
    handler.post_run_cell(MockSuccessfulExecution())

    with pytest.raises(KeyError):
        _ = handler[DF_COL]  # test correctly removed

    # add new series with same name and run
    df[COL] = final_col

    with mock.patch.object(
        plotter, "update_trace_series", wraps=plotter.update_trace_series
    ) as mock_update_trace_series:
        handler.post_run_cell(MockSuccessfulExecution())

    # test expected method calls occurred
    mock_update_trace_series.assert_called_once()
    assert DF_COL == mock_update_trace_series.call_args[0][0]
    assert final_col.equals(mock_update_trace_series.call_args[0][1])

    # test expected updates performed
    assert handler[DF_COL].equals(final_col), "Series updated in handler"
    assert plotter[DF_COL].is_visible(), "Trace exists and is visible"
    assert plotter[DF_COL].get_line().get_color() == colour, "Trace colour unchanged"
