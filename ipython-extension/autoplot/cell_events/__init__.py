"""Module containing the `CellEventHandler` class.

Classes
-------
CellEventHandler
    Class defining handlers for IPython events
"""

from typing import Any, Dict, Set, Union

import IPython
import pandas as pd
from IPython.core.interactiveshell import ExecutionInfo, ExecutionResult

from autoplot.cell_events.variable_utils import is_plottable
from autoplot.plotter import Plotter
from autoplot.utils.constants import DF_COLUMN_FORMAT_STRING


class CellEventHandler(object):
    """Class defining handlers for IPython events.

    Each handler should be registered on the shell using `shell.events.register()`.

    Methods
    -------
    get_plotted_dfs()
        Return the dictionary of series names associated with each dataframe.

    pre_execute()
        Handle the `pre_execute` IPython event. Currently empty.

    pre_run_cell(info)
        Handle the `pre_run_cell` IPython event. Currently empty.

    post_execute()
        Handle the `post_run_cell` IPython event. Currently empty.

    post_run_cell(result)
        Handle the `post_run_cell` IPython event. Updates the plot if no error.
    """

    def __init__(self, shell: IPython.InteractiveShell, plotter: Plotter):
        """Initialise a `CellEventHandler` instance.

        Parameters
        ----------
        shell: IPython.InteractiveShell
            The IPython interactive shell. Used to access namespace variables.

        plotter: Plotter
            The associated `Plotter` instance.
        """
        self._shell = shell
        self._plotter = plotter

        # dictionary of series, with key = name, value = pd.Series instance
        self._series_dict: Dict[str, pd.Series] = {}

        # dictionary with key = dataframe name, value = plotted column names
        self._plotted_dfs: Dict[str, Set[str]] = {}

        # set of variables in namespace, including series extracted from data frames
        self._ns_with_series: Set[str] = set()

        # set of names to be ignored. Not necessary but useful for debugging
        self._reserved: Set[str] = {"In", "Out", "get_ipython", "exit", "quit", "pd"}

    def __getitem__(self, item: str) -> Union[Set[str], pd.Series]:
        try:
            return self._plotted_dfs[item]
        except KeyError:
            return self._series_dict[item]

    def __setitem__(self, key: str, value: Union[Set[str], pd.Series]):
        if isinstance(value, set):
            self._plotted_dfs[key] = value
        elif isinstance(value, pd.Series):
            self._series_dict[key] = value
        else:
            raise TypeError(f"Can only set values of type 'set' or 'pd.Series', not '{type(value)}'")

    def get_plotted_dfs(self) -> Dict[str, Set[str]]:
        """Return the dictionary of series names associated with each dataframe."""
        return self._plotted_dfs

    def _update_trace_if_changed(self, name: str, series: pd.Series, df_name: str = None):
        """Update the named trace with the given series.

        This function does nothing if the variable is not new and the series has
        not been modified.

        Parameters
        ----------
        name: str
            Name of the variable, as it is defined in Python. Assumed to be the key
            for the variable in `self._series_dict`.

        series: pd.Series
            The new or modified series. Assumed to be datetime-indexed and have
            numeric values.

        df_name: str, optional
            The name of the associated dataframe, if the series is a column from one.
        """
        # update the dataframe dictionary
        if df_name is not None:
            try:
                self[df_name].add(name)
            except KeyError:
                self[df_name] = {name}

        # update it if exists and was modified
        if name in self._series_dict:
            self[name] = series
            self._plotter.update_trace_series(name, series)
        # add it if new
        else:
            self[name] = series
            self._plotter.add_trace(name, series, df_name)

    def _delete_trace(self, name: str):
        """Hide the trace(s) associated with the given series or dataframe name.

        Also removes the variable name (and column names, if applicable) from the
        relevant sets / dictionaries.
        """
        if name in self._plotted_dfs:
            for series_name in self._plotted_dfs[name]:
                self._plotter.hide_trace(series_name)
                self._series_dict.pop(series_name)

            self._plotted_dfs.pop(name)
        else:
            self._plotter.hide_trace(name)
            self._series_dict.pop(name)

            # if it is a dataframe column, remove its reference from self._plotted_dfs
            df_name = self._plotter[name].df_name
            if df_name is not None:
                self._plotted_dfs[df_name].remove(name)

                # remove the dataframe set if empty
                if len(self._plotted_dfs[df_name]) == 0:
                    self._plotted_dfs.pop(df_name)

    def _add_trace_for_series(self, name: str, var: Any) -> bool:
        """Plot variable if it is of type pd.Series and is plottable.

        Parameters
        ----------
        name: str
            Name of the variable, as it is defined in Python.

        var: Any
            Variable value. Not necessarily a series.

        Returns
        -------
        bool
            True if the variable was a plottable series and was therefore use to create
            or update a trace. Otherwise False.
        """
        if not (isinstance(var, pd.Series) and is_plottable(var)):
            return False

        # handle series that used to be a dataframe
        if name in self._plotted_dfs:
            self._delete_trace(name)

        self._update_trace_if_changed(name, var, None)
        return True

    def _add_traces_for_dataframe(self, name: str, var: Any) -> bool:
        """Plot variable if it is of type pd.DataFrame and has plottable columns.

        Parameters
        ----------
        name: str
            Name of the variable, as it is defined in Python.

        var: Any
            Variable value. Not necessarily a dataframe.

        Returns
        -------
        bool
            True if the variable was a dataframe and was therefore use to create
            or update one or more traces. Otherwise False.
        """
        if not isinstance(var, pd.DataFrame):
            return False

        # handle dataframe that used to be a plottable series
        if name in self._series_dict:
            self._delete_trace(name)

        columns = {col: var[col] for col in var.columns}

        for col, series in columns.items():
            series_name = DF_COLUMN_FORMAT_STRING.format(name, col)
            self._ns_with_series.add(series_name)

            # plot column if plottable
            if is_plottable(series):
                self._update_trace_if_changed(series_name, series, name)
            # delete columns that used to be plottable
            elif series_name in self._series_dict:
                self._delete_trace(series_name)

        return True

    def _add_traces_for_namespace_vars(self):
        """Iterate through all variables in namespace, and plot them when appropriate.

        If a variable name starts with "_", or it is in the set `self._reserved`, it
        is skipped. Otherwise, if it is new or has been modified, it is passed to
        `self._update_trace_if_changed()`.
        """
        self._ns_with_series.clear()

        for name, var in self._shell.user_ns.items():
            if name[0] == "_" or name in self._reserved:
                # skip private variables. This excludes a bunch of uninteresting ones
                # like _i1, _i2 etc., and gives the user an easy way to avoid plotting
                # certain variables
                continue

            self._ns_with_series.add(name)

            # plot variables of type pd.Series (if plottable)
            if self._add_trace_for_series(name, var):
                continue

            # convert and store variables of type pd.Dataframe
            if self._add_traces_for_dataframe(name, var):
                continue

            # variable that used to be a plottable series or dataframe
            if name in self._series_dict or name in self._plotted_dfs:
                self._delete_trace(name)

    def _hide_traces_for_deleted_vars(self):
        """Hide the traces of deleted variables, unless they were forcibly shown."""
        deleted_names = self._plotter.get_visible() - self._ns_with_series - self._plotter.force_shown

        for name in deleted_names:
            self._delete_trace(name)

    def pre_execute(self):
        """Handle the `pre_execute` IPython event. Currently empty.

        Notes
        -----
        `pre_execute` is like `pre_run_cell`, but is triggered prior to any execution.
        Sometimes code can be executed by libraries, etc. which skipping the
        history/display mechanisms, in which cases pre_run_cell will not fire [1]_.

        References
        ----------
        [1] https://ipython.readthedocs.io/en/stable/config/callbacks.html#pre-execute
        """
        pass

    def pre_run_cell(self, info: ExecutionInfo):
        """Handle the `pre_run_cell` IPython event. Currently empty.

        Notes
        -----
        `pre_run_cell` fires prior to interactive execution (e.g. a cell in a notebook).
        It can be used to note the state prior to execution, and keep track of changes.
        An object containing information used for the code execution is provided as an
        argument [1]_.

        References
        ----------
        [1] https://ipython.readthedocs.io/en/stable/config/callbacks.html#pre-run-cell
        """
        pass

    def post_execute(self):
        """Handle the `post_run_cell` IPython event. Currently empty.

        Notes
        -----
        The same as `pre_execute`, `post_execute` is like `post_run_cell`, but fires
        for all executions, not just interactive ones [1]_.

        References
        ----------
        [1] https://ipython.readthedocs.io/en/stable/config/callbacks.html#post-execute
        """
        pass

    def post_run_cell(self, result: ExecutionResult):
        """Handle the `post_run_cell` IPython event. Updates the plot if no error.

        Notes
        -----
        `post_run_cell` runs after interactive execution (e.g. a cell in a notebook).
        It can be used to cleanup or notify or perform operations on any side effects
        produced during execution. For instance, the inline matplotlib backend uses
        this event to display any figures created but not explicitly displayed during
        the course of the cell. The object which will be returned as the execution
        result is provided as an argument [1]_.

        References
        ----------
        [1] https://ipython.readthedocs.io/en/stable/config/callbacks.html#post-run-cell
        """
        if result.success:
            self._add_traces_for_namespace_vars()
            self._hide_traces_for_deleted_vars()

            self._plotter.plot()
