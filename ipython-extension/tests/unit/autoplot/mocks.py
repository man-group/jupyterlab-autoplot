from typing import Any, Dict

from IPython.core.interactiveshell import ExecutionResult

from autoplot import Plotter
from autoplot.utils.constants import DF_COLUMN_FORMAT_STRING

VAR = "var"
DF = "df"
COL = "col"
COL_ALT = "col alt"
DF_COL = DF_COLUMN_FORMAT_STRING.format(DF, COL)
DF_COL_ALT = DF_COLUMN_FORMAT_STRING.format(DF, COL_ALT)


class MockSuccessfulExecution(ExecutionResult):
    """Class to mock the successful execution of an IPython cell."""

    def __init__(self):
        super().__init__(None)

    @property
    def success(self):
        return True


class MockIPythonShell(object):
    """Class to mock an IPython shell. Only defines `user_ns`."""

    def __init__(self, user_ns: Dict[str, Any]):
        self.user_ns = user_ns


class MockPlotter(Plotter):
    """Class to mock the `Plotter` class. Overwrites the `plot()` method."""

    def __init__(self, mock_toast):
        super().__init__(mock_toast)  # noqa

    def plot(self, force, output):
        self._changed = False
