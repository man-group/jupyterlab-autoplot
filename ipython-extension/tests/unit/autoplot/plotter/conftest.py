import pandas as pd
import pytest

from autoplot.plotter.trace import Trace
from tests.unit.autoplot.mocks import VAR


@pytest.fixture()
def trace_from_series(mock_toast):
    """Return a new `Trace` instance initialised with the given series."""

    def with_params(series: pd.Series, toast=None) -> Trace:
        if toast is None:
            toast = mock_toast

        return Trace(toast, VAR, series, 0, 1000)

    yield with_params
