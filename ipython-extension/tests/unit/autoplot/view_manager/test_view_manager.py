from typing import Dict, Union

import pandas as pd
from ipywidgets import Output

from autoplot.view_manager import ViewManager, View
from autoplot.extensions.autoplot_display import AutoplotDisplay
from autoplot.extensions.toast import Toast
from tests.unit.autoplot.mocks import MockIPythonShell


class TestView(View):
    def __init__(self):
        self.plot_width = None
        self.plot_height = None
        self.ylabel = None
        self.max_series_length = None
        self.frozen = False
        self.defrosted = False
        self.rename = ()
        self.colour = ()
        self.variables = {}
        self.force = False
        self.output = None
        self.ignored = ""
        self.showed = ""

    def update_variables(self, pandas_vars: Dict[str, Union[pd.Series, pd.DataFrame]]) -> None:
        """Update pandas variables"""
        self.variables = pandas_vars

    def draw(self, force: bool, output: AutoplotDisplay) -> None:
        """Draw the view"""
        self.force = force
        self.output = output

    def ignore_variable(self, toast: Toast, var_name: str) -> None:
        self.ignored = var_name

    def show_variable(self, toast: Toast, var_name: str) -> None:
        self.showed = var_name

    def change_colour(self, toast: Toast, var_name: str, colour: str) -> None:
        self.colour = (var_name, colour)

    def rename_variable(self, toast: Toast, var_name: str, display_name: str) -> None:
        self.rename = (var_name, display_name)

    def freeze(self, toast: Toast) -> None:
        self.frozen = True

    def defrost(self, toast: Toast) -> None:
        self.defrosted = True

    def update_max_series_length(self, toast: Toast, sample: int) -> None:
        self.max_series_length = sample

    def set_ylabel(self, toast: Toast, ylabel: str) -> None:
        self.ylabel = ylabel

    def set_plot_height(self, toast: Toast, height: float) -> None:
        self.plot_height = height

    def set_plot_width(self, toast: Toast, width: float) -> None:
        self.plot_width = width


def test_active():
    shell = MockIPythonShell({})
    manager = ViewManager(AutoplotDisplay(), shell, {"a": TestView(), "b": TestView()}, "a")
    assert manager.active == "a"

    manager = ViewManager(AutoplotDisplay(), shell, {"a": TestView(), "b": TestView()}, "b")
    assert manager.active == "b"


def test_set_active():
    shell = MockIPythonShell({})
    a = TestView()
    b = TestView()
    manager = ViewManager(AutoplotDisplay(), shell, {"a": a, "b": b}, "a")

    assert manager.active == "a"
    assert manager.active_view is a

    manager.active = "b"

    assert manager.active == "b"
    assert manager.active_view is b


def test_view_names():
    shell = MockIPythonShell({})
    manager = ViewManager(AutoplotDisplay(), shell, {"a": TestView(), "b": TestView()}, "a")

    assert sorted(manager.view_names) == ["a", "b"]


def test_redraw_filter_pandas():
    df = pd.DataFrame({"a": [1, 2, 3]})
    shell = MockIPythonShell({"n": 1, "df": df})
    a = TestView()
    b = TestView()
    manager = ViewManager(AutoplotDisplay(), shell, {"a": a, "b": b}, "a")

    assert manager._changed

    manager.redraw()

    assert not manager._changed

    assert a.variables == {"df": df}
    assert b.variables == {}


def test_ignore_variable():
    shell = MockIPythonShell({})
    a = TestView()
    b = TestView()
    manager = ViewManager(AutoplotDisplay(), shell, {"a": a, "b": b}, "a")

    manager.ignore_variable(Toast(Output()), "df")

    assert manager._changed
    assert a.ignored == "df"
    assert b.ignored == ""


def test_show_variable():
    shell = MockIPythonShell({})
    a = TestView()
    b = TestView()
    manager = ViewManager(AutoplotDisplay(), shell, {"a": a, "b": b}, "a")

    manager.show_variable(Toast(Output()), "df")

    assert manager._changed
    assert a.showed == "df"
    assert b.showed == ""


def test_change_colour():
    shell = MockIPythonShell({})
    a = TestView()
    b = TestView()
    manager = ViewManager(AutoplotDisplay(), shell, {"a": a, "b": b}, "a")

    manager.change_colour(Toast(Output()), "df", "red")

    assert manager._changed
    assert a.colour == ("df", "red")
    assert b.colour == ()


def test_rename_variable():
    shell = MockIPythonShell({})
    a = TestView()
    b = TestView()
    manager = ViewManager(AutoplotDisplay(), shell, {"a": a, "b": b}, "a")

    manager.rename_variable(Toast(Output()), "df", "ddf")

    assert manager._changed
    assert a.rename == ("df", "ddf")
    assert b.rename == ()


def test_freeze():
    shell = MockIPythonShell({})
    a = TestView()
    b = TestView()
    manager = ViewManager(AutoplotDisplay(), shell, {"a": a, "b": b}, "a")

    manager.freeze(Toast(Output()))

    assert manager._changed
    assert a.frozen
    assert not b.frozen


def test_defrost():
    shell = MockIPythonShell({})
    a = TestView()
    b = TestView()
    manager = ViewManager(AutoplotDisplay(), shell, {"a": a, "b": b}, "a")

    manager.defrost(Toast(Output()))

    assert manager._changed
    assert a.defrosted
    assert not b.defrosted


def test_max_series_length():
    shell = MockIPythonShell({})
    a = TestView()
    b = TestView()
    manager = ViewManager(AutoplotDisplay(), shell, {"a": a, "b": b}, "a")

    manager.update_max_series_length(Toast(Output()), 20)

    assert manager._changed
    assert a.max_series_length == 20
    assert b.max_series_length is None


def test_set_ylabel():
    shell = MockIPythonShell({})
    a = TestView()
    b = TestView()
    manager = ViewManager(AutoplotDisplay(), shell, {"a": a, "b": b}, "a")

    manager.set_ylabel(Toast(Output()), "hello")

    assert manager._changed
    assert a.ylabel == "hello"
    assert b.ylabel is None


def test_set_plot_height():
    shell = MockIPythonShell({})
    a = TestView()
    b = TestView()
    manager = ViewManager(AutoplotDisplay(), shell, {"a": a, "b": b}, "a")

    manager.set_plot_height(Toast(Output()), 3)

    assert manager._changed
    assert a.plot_height == 3
    assert b.plot_height is None


def test_set_plot_width():
    shell = MockIPythonShell({})
    a = TestView()
    b = TestView()
    manager = ViewManager(AutoplotDisplay(), shell, {"a": a, "b": b}, "a")

    manager.set_plot_width(Toast(Output()), 3)

    assert manager._changed
    assert a.plot_width == 3
    assert b.plot_width is None
