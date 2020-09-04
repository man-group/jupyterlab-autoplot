import mock
import pandas as pd
import pytest

from autoplot.extensions.toast import Toast


@pytest.fixture()
def datetime_index():
    """Return a new pandas datetime index of the given length."""

    def with_params(length: int):
        return pd.date_range(start="2020-01-01", periods=length, freq="d")

    yield with_params


@pytest.fixture()
def datetime_series(datetime_index):
    """Return a new datetime indexed series with values all equal to `1`."""

    def with_params(length: int):
        return pd.Series([1] * length, index=datetime_index(length))

    yield with_params


@pytest.fixture()
def mock_toast():
    mock.NonCallableMock()
    return mock.MagicMock(spec=Toast)
