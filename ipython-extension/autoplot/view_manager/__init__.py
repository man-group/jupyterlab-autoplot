"""Module containing the `View` and `ViewManager` classes.

Classes
-------
View
    Abstract class that must be implemented by any view that's going to be registered in the ViewManager
ViewManager
    Class that control multiple views and get them displayed
"""
import abc
from typing import Dict, Set, Union, List

import IPython
import pandas as pd
from autoplot.extensions.toast import Toast, ToastType

from autoplot.view_manager.variable_utils import is_plottable
from autoplot.extensions.autoplot_display import AutoplotDisplay


class View(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def update_variables(self, pandas_vars: Dict[str, Union[pd.Series, pd.DataFrame]]) -> None:
        """After each cell execution this function is executed. At this moment the view has the chance to calculate
        any differences between the old state and the current state after the cell execution

        Parameters
        ----------

        pandas_vars: Dict[str, Union[pd.Series, pd.DataFrame]]
            a dictionary where the keys are variable names that are available in the kernel namespace and the
            value is the actual value of those variables. The view manager filters the variables so only pandas
            dataframes and series are received.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def draw(self, force: bool, output: AutoplotDisplay) -> None:
        """After computing update_variables this method may be called. It will usually check the diffs created by
        update_variables to decide what it needs to draw and whether or not a redraw is necessary. Drawing is
        implemented using IPython.display

        Parameters
        ----------

        force: bool
            when True, draw should always redraw the view. Otherwise, the decision is up to the view
        output: AutoplotDisplay
            it's expected that IPython.display is going to be used inside a context created by running
            with output:
               ...
        """
        raise NotImplementedError

    def ignore_variable(self, toast: Toast, var_name: str) -> None:
        """Do not display the variable in the view."""
        raise NotImplementedError

    def show_variable(self, toast: Toast, var_name: str) -> None:
        """Display the variable in the view (used to revert ignore_variable)"""
        raise NotImplementedError

    def change_colour(self, toast: Toast, var_name: str, colour: str) -> None:
        """Change colour of a given trace"""
        raise NotImplementedError

    def rename_variable(self, toast: Toast, var_name: str, display_name: str) -> None:
        """Rename a variable inside the view"""
        raise NotImplementedError

    def freeze(self, toast: Toast) -> None:
        """Set the plotter to frozen, preventing new traces from being added."""
        raise NotImplementedError

    def defrost(self, toast: Toast) -> None:
        """Set the plotter to defrost, allowing new traces to be added."""
        raise NotImplementedError

    def update_max_series_length(self, toast: Toast, sample: int) -> None:
        """Set maximum series length."""
        raise NotImplementedError

    def set_ylabel(self, toast: Toast, ylabel: str) -> None:
        """Set ylabel axis."""
        raise NotImplementedError

    def set_plot_height(self, toast: Toast, height: int) -> None:
        """Set height of the plot"""
        raise NotImplementedError

    def set_plot_width(self, toast: Toast, width: int) -> None:
        """Set width of the plot"""
        raise NotImplementedError


class ViewManager:
    """
    Keeps track of pandas dataframes and series. It takes a dictionary of listeners that will be notified of all
    events. The tracker will always run post cell execution and it will call the draw method of the active view.
    However, events will be passed along to both active and inactive views.

    Parameters
    ----------

    output: AutoplotDisplay
        IPython output object that will be used to show the view
    shell: IPython.InteractiveShell
        the ipython shell. This will be used to inspect the variables defined in the namespace
    views: Dict[str, View]
        all the view implementations available. The active attribute must always be set to match one of the views in
        this directory
    active: str
        currently active view. It must be one  of the keys in the views dictionary
    """

    def __init__(self, output: AutoplotDisplay, shell: IPython.InteractiveShell, views: Dict[str, View], active: str):
        if active not in views:
            raise ValueError(f"view {active} not part of the list of views")
        self._active = active
        self._changed = True  # controls whether the active view has changed

        self._output = output
        self._shell = shell
        self._views = views

        # set of names to be ignored. Not necessary but useful for debugging
        self._reserved: Set[str] = {"In", "Out", "get_ipython", "exit", "quit", "pd"}

    @property
    def active(self) -> str:
        return self._active

    @active.setter
    def active(self, active):
        if active not in self._views:
            raise ValueError(f"view {active} not part of the list of views")
        self._changed = self._active != active
        self._active = active

    @property
    def active_view(self) -> View:
        return self._views[self._active]

    @property
    def view_names(self) -> List[str]:
        return list(self._views.keys())

    def redraw(self) -> None:
        pandas_vars: Dict[str, Union[pd.Series, pd.DataFrame]] = {}
        for name, var in self._shell.user_ns.items():
            if not name.startswith("_") and name not in self._reserved and self._is_pandas(var):
                pandas_vars[name] = var

        self.active_view.update_variables(pandas_vars)
        self.active_view.draw(self._changed, self._output)
        self._changed = False

    def ignore_variable(self, toast: Toast, var_name: str) -> None:
        """Hide the given variable from the plot. Undoes `show_variable`.

        If a dataframe name is specified, all of its columns will be hidden.

        Parameters
        ----------
        toast: Toast
            The `Toast` class instance.

        var_name: str
            Name of the variable to hide, as it is defined in Python. Can be a series
            names or dataframe name.
        """
        try:
            return self.active_view.ignore_variable(toast, var_name)
        except NotImplementedError:
            toast.show(f"{self._active} does not implement ignoring variables", ToastType.warning)

    def show_variable(self, toast: Toast, var_name: str) -> None:
        """Show the given variable on the plot. Undoes `ignore_variable`.

        If a dataframe name is specified, all of its columns will be shown.

        Parameters
        ----------
        plotted_dfs: Dict[str, Set[str]]
            Dictionary with key = dataframe name, value = set of plotted column names.

        toast: Toast
            The `Toast` class instance.

        var_name: str
            Name of the variable to show, as it is defined in Python. Can be a series
            names or dataframe name.
        """
        try:
            return self.active_view.show_variable(toast, var_name)
        except NotImplementedError:
            toast.show(f"{self._active} does not implement showing variables", ToastType.warning)

    def change_colour(self, toast: Toast, var_name: str, colour: str) -> None:
        """Update the colour of the given variable.

        Only series / column names can be specified, not dataframe names.

        Parameters
        ----------
        toast: Toast
            The `Toast` class instance.

        var_name: str
            The name of the variable to change the colour of, as it is defined in Python.

        colour: str
            The desired trace colour. Must be a valid matplotlib colour.
        """
        try:
            return self.active_view.change_colour(toast, var_name, colour)
        except NotImplementedError:
            toast.show(f"{self._active} does not implement changing colours", ToastType.warning)

    def rename_variable(self, toast: Toast, var_name: str, display_name: str) -> None:
        """Update the legend label of the given variable.

        If a dataframe name is specified, the legend labels of all the columns are changed
        accordingly.

        Parameters
        ----------
        toast: Toast
            The `Toast` class instance.

        var_name: str
            The name of the variable to change the label of, as it is defined in Python.
            Can be a series or dataframe name.

        display_name: str
            The desired legend label.
        """
        try:
            return self.active_view.rename_variable(toast, var_name, display_name)
        except NotImplementedError:
            toast.show(f"{self._active} does not implement variable renaming", ToastType.warning)

    def freeze(self, toast: Toast) -> None:
        """Set the plotter to frozen, preventing new traces from being added."""
        try:
            return self.active_view.freeze(toast)
        except NotImplementedError:
            toast.show(f"{self._active} does not implement freeze", ToastType.warning)

    def defrost(self, toast: Toast) -> None:
        """Set the plotter to un-frozen, allowing new traces to be plotted.

        Note that traces defined while it was frozen will need to be added manually.
        """
        try:
            return self.active_view.defrost(toast)
        except NotImplementedError:
            toast.show(f"{self._active} does not implement defrost", ToastType.warning)

    def update_max_series_length(self, toast: Toast, sample: int) -> None:
        """Update the maximum series length of all traces.

        If this has an effect on any of the traces, set `self._changed` to `True`.

        Parameters
        ----------
        max_length: int
            The new maximum series length. If 0, the traces will not be downsampled.
        """
        try:
            return self.active_view.update_max_series_length(toast, sample)
        except NotImplementedError:
            toast.show(f"{self._active} does not implement max series length", ToastType.warning)

    def set_ylabel(self, toast: Toast, ylabel: str) -> None:
        """Set the y axis label.

        If the new label is different, set `self._changed` to True.

        Parameters
        ----------
        toast: Toast
            The `Toast` class instance.

        ylabel: str
            New label for the y axis. If it is an empty string, no label will be used.
        """
        try:
            return self.active_view.set_ylabel(toast, ylabel)
        except NotImplementedError:
            toast.show(f"{self._active} does not implement changing ylabel", ToastType.warning)

    def set_plot_height(self, toast: Toast, height: int) -> None:
        """Validate and set the height of the figure.

        Parameters
        ----------
        toast: Toast
            The `Toast` class instance.

        height: int
            The desired height of the plot in inches. If outside the range `[_MIN_HEIGHT,
            _MAX_HEIGHT]`, will be set to the nearest limit and the user will be notified.
        """
        try:
            return self.active_view.set_plot_height(toast, height)
        except NotImplementedError:
            toast.show(f"{self._active} does not implement setting the plot height", ToastType.warning)

    def set_plot_width(self, toast: Toast, width: int) -> None:
        """Validate and set the width of the figure.

        Parameters
        ----------
        toast: Toast
            The `Toast` class instance.

        width: int
            The desired width of the plot in inches. If outside the range `[_MIN_WIDTH,
            _MAX_WIDTH]`, will be set to the nearest limit and the user will be notified.
        """
        try:
            return self.active_view.set_plot_width(toast, width)
        except NotImplementedError:
            toast.show(f"{self._active} does not implement setting the plot height", ToastType.warning)

    def _is_pandas(self, var):
        return isinstance(var, pd.DataFrame) or isinstance(var, pd.Series)
