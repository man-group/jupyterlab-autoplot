from typing import Any, Dict

import pytest

from autoplot.plotter import PlotterModel
from autoplot.extensions.autoplot_display import AutoplotDisplay
from autoplot.extensions.toast import Toast
from autoplot.view_manager import ViewManager
from autoplot import _make_magic
from tests.unit.autoplot.mocks import COL, COL_ALT, DF, MockIPythonShell, MockPlotter, MockSuccessfulExecution, VAR


@pytest.fixture()
def autoplot_magic(mock_toast):
    """Return an `AutoplotMagic` instance initialised with the given namespace."""

    def with_params(user_ns: Dict[str, Any] = None, toast: Toast = None):
        if user_ns is None:
            user_ns = {}

        if toast is None:
            toast = mock_toast

        shell = MockIPythonShell(user_ns)
        plotter = MockPlotter(toast)
        handler = PlotterModel(plotter)
        view_manager = ViewManager(AutoplotDisplay(), shell, {"graph": handler}, "graph")
        magic = _make_magic(shell, toast, view_manager)
        view_manager.redraw()

        return magic

    yield with_params


@pytest.fixture()
def full_autoplot_magic(datetime_series, autoplot_magic, mock_toast):
    """Return an `AutoplotMagic` instance initialised with a 'full' namespace.

    The namespace will contain a datetime indexed series called `VAR` and a datetime
    indexed dataframe `DF` with columns `COL` and `COL_ALT`.
    """

    def with_params(toast: Toast = None):
        if toast is None:
            toast = mock_toast

        df = datetime_series(15).to_frame(name=COL)
        df[COL_ALT] = datetime_series(15).apply(lambda x: x + 1)

        user_ns = {VAR: datetime_series(10), DF: df}

        return autoplot_magic(user_ns, toast)

    yield with_params
