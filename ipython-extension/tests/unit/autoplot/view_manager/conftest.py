from typing import Any, Dict, Optional, Set, Tuple

import pandas as pd
import pytest

from autoplot.plotter import PlotterModel
from autoplot.extensions.autoplot_display import AutoplotDisplay
from autoplot.extensions.toast import Toast
from autoplot.view_manager import ViewManager
from tests.unit.autoplot.mocks import COL, MockIPythonShell, MockPlotter, MockSuccessfulExecution

LENGTH = 10


@pytest.fixture()
def num_series(datetime_series) -> pd.Series:
    """Return a datetime series with numeric values."""
    return datetime_series(LENGTH)


@pytest.fixture()
def num_series_alt(datetime_series) -> pd.Series:
    """Return a datetime series with numeric values."""
    return datetime_series(LENGTH).apply(lambda x: x + 1)


@pytest.fixture()
def str_series(datetime_series) -> pd.Series:
    """Return a datetime series with string values."""
    return datetime_series(LENGTH).apply(lambda x: "a")


@pytest.fixture()
def num_dataframe(num_series) -> pd.DataFrame:
    """Return a datetime-indexed dataframe with a numeric column, `COL`."""
    return num_series.to_frame(name=COL).apply(lambda x: -x)


@pytest.fixture()
def num_dataframe_alt(num_series_alt) -> pd.DataFrame:
    """Return a datetime-indexed dataframe with a numeric column.

    Note that the column name is still `COL`, not `COL_ALT`.
    """
    return num_series_alt.to_frame(name=COL).apply(lambda x: -x)


@pytest.fixture()
def str_dataframe(str_series) -> pd.DataFrame:
    """Return a datetime-indexed dataframe with a string column, `COL`."""
    return str_series.to_frame(name=COL).apply(lambda x: "b")


@pytest.fixture()
def initialised_mocks(mock_toast):
    """Return a new, initialised mock `Shell`, `Plotter` and `PlotterModel`."""

    def with_params(
        user_ns: Dict[str, Any], reserved: Optional[Set[str]] = None, toast: Toast = None
    ) -> Tuple[MockIPythonShell, MockPlotter, PlotterModel]:
        if toast is None:
            toast = mock_toast

        # initialise mocks with parameters
        shell = MockIPythonShell(user_ns)
        plotter = MockPlotter(toast)

        # initialise cell event handler instance
        handler = PlotterModel(plotter)

        view_manager = ViewManager(AutoplotDisplay(), shell, {"graph": handler}, "graph")
        # optionally add reserved names
        if reserved is not None:
            view_manager._reserved = reserved

        view_manager.redraw()

        return shell, plotter, handler

    yield with_params
