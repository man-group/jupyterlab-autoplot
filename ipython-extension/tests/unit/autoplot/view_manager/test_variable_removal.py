"""Test that the `CellEventHandler` deals with variable removal correctly.

Each test checks that the expected updates are performed when a namespace
variable is deleted. In general, we expect the variable to be deleted from the
`handler` but not from the `plotter`, and its trace to be hidden on the graph.
"""

import pytest
from ipywidgets import Output

from tests.unit.autoplot.mocks import COL, COL_ALT, DF, DF_COL, DF_COL_ALT, MockSuccessfulExecution, VAR


def test_deleted_series_removed_and_hidden(initialised_mocks, num_series):
    shell, plotter, handler = initialised_mocks({VAR: num_series})

    handler.update_variables({})

    # test expected updates performed
    with pytest.raises(KeyError):
        _ = handler[VAR]  # series removed from handler

    assert not plotter[VAR].is_visible(), "Original trace exists but is hidden"


def test_deleted_dataframe_removed_and_hidden(initialised_mocks, num_dataframe):
    # initialise mocks with namespace
    shell, plotter, handler = initialised_mocks({DF: num_dataframe})

    # remove the dataframe and rerun
    handler.update_variables({})

    # test expected updates performed
    with pytest.raises(KeyError):
        _ = handler[DF]  # dataframe removed from handler

    with pytest.raises(KeyError):
        _ = handler[DF_COL]  # column series removed from handler

    assert not plotter[DF_COL].is_visible(), "Original trace exists but is hidden"


def test_deleted_column_removed_and_hidden(initialised_mocks, num_dataframe, num_series_alt):
    df = num_dataframe
    df[COL_ALT] = num_series_alt
    shell, plotter, handler = initialised_mocks({DF: df})

    # remove the column and rerun
    df.drop(columns=[COL], inplace=True)
    handler.update_variables({DF: df})

    # test expected updates performed
    assert handler[DF] == {DF_COL_ALT}, "Column removed from dataframe"

    with pytest.raises(KeyError):
        _ = handler[DF_COL]  # column series not added to handler

    assert not plotter[DF_COL].is_visible(), "Original trace exists but is hidden"
