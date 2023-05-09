"""Module containing the `Plotter` class.

Classes
-------
Plotter
    Class to manage `Trace` instances and handle the graph plotting.
"""

import datetime
from typing import Any, Dict, Optional, Set, Union

import matplotlib.pyplot as plt
import mpld3
import numpy as np
import pandas as pd
from ipywidgets import widgets
from IPython.display import clear_output

from autoplot.view_manager import is_plottable, View
from autoplot.extensions.toast import Toast, ToastType
from autoplot.plotter.range_selector_utils import gen_range_selector_labels
from autoplot.plotter.trace import Trace
from autoplot.plugins import InteractiveLegend, RangeSelectorButtons, SaveImageButtons, TimeSeriesTooltip
from autoplot.utils.constants import DEFAULT_MAX_SERIES_LENGTH, DF_COLUMN_FORMAT_STRING, FigSize
from autoplot.utils import remove_quotes

OptDatetime = Optional[datetime.datetime]


class Plotter(object):
    """Class to manage `Trace` instances and handle the graph plotting.

    One instance should be initialised per plot / output area.

    Methods
    -------
    add_trace(name, series, df_name)
        Initialise and add a new `Trace` instance to `self._traces`.

    update_trace_series(name, series)
        Update the series of an existing trace.

    update_trace_colour(name, colour)
        Update the colour of an existing trace.

    update_trace_label(name, label)
        Update the legend label of an existing trace.

    update_max_series_length(max_length)
        Update the maximum series length of all traces.

    hide_trace(name)
        Hide an existing trace.

    force_show_trace(name)
        Show a previously hidden or deleted trace.

    set_figure_width(width)
        Set the width of the figure.

    set_figure_height(height)
        Set the height of the figure.

    set_ylabel(ylabel)
        Set the y axis label.

    freeze()
        Set the plotter to frozen, preventing new traces from being added.

    defrost()
        Set the plotter to un-frozen, allowing new traces to be plotted.

    get_visible()
        Return a set of variable names corresponding to visible traces.

    plot()
        Clear the output area and plot all the visible traces.
    """

    def __init__(self, toast: Toast):
        """Initialise a `Plotter` instance.

        Parameters
        ----------
        graph_output: widgets.Output
            The IPython output widget in which to display the graph. This will be
            cleared every time the graph is replotted.

        toast: Toast
            The `Toast` class instance.
        """
        self._toast = toast

        # dictionary of variable names and their associated Trace
        self._traces: Dict[str, Trace] = {}

        # set of variables that have been forcibly shown (i.e. deleted ones that have
        # be made visible using magic commands)
        self.force_shown: Set[str] = set()

        # optional plot parameters
        self._ylabel: Optional[str] = None
        self._width: int = FigSize.DEFAULT_WIDTH.value
        self._height: int = FigSize.DEFAULT_HEIGHT.value

        # flag that is set to True if a change has been made. If it is False when
        # self.plot() is called, nothing will happen. Initialise to True for placeholder
        self._changed = True

        # if True, no new traces will be added to the plot. Existing ones will still
        # be updated
        self._frozen = False

        # if a series is longer than this, it will be downsampled
        self._max_series_length = DEFAULT_MAX_SERIES_LENGTH

    def __getitem__(self, item: str) -> Trace:
        return self._traces[item]

    def __setitem__(self, key: str, value: Trace):
        assert key not in self._traces, "Cannot overwrite existing trace"
        self._traces[key] = value

    def add_trace(self, name: str, series: pd.Series, df_name: Union[str, None]):
        """Initialise and add a new `Trace` instance to `self._traces`.

        Parameters
        ----------
        name: str
            Name of the variable, as it is defined in Python. Used as the key for
            `self._traces`.

        series: pd.Series
            The variable's value. Assumed to be datetime-indexed and have numeric
            values.

        df_name: str, optional
            The name of the associated dataframe, if the series is a column from one.
        """

        if name in self._traces:
            # if it already exists, overwrite it and reset its visibility. This allows
            # deleted traces to be redefined
            self.update_trace_series(name, series)
            self[name].update_visible(not self._frozen)
        else:
            # add new trace
            self[name] = Trace(
                self._toast,
                name,
                series,
                len(self._traces),
                self._max_series_length,
                visible=not self._frozen,
                df_name=df_name,
            )

        self._changed = not self._frozen

    def update_trace_series(self, name: str, series: pd.Series):
        """Update the series of an existing trace.

        If the series is different, set `self._changed` to True.

        Parameters
        ----------
        name: str
            Name of the associated variable. Must exist in `self._traces`.

        series: pd.Series
            The new series.
        """
        tr = self[name]
        if tr.update_series(series) and tr.is_visible():
            self._changed = True

    def update_trace_colour(self, name: str, colour: str):
        """Update the colour of an existing trace.

        If the colour is different, set `self._changed` to True.

        Parameters
        ----------
        name: str
            Name of the associated variable. Must exist in `self._traces`.

        colour: str
            The new colour.
        """
        tr = self[name]
        if tr.update_colour(colour) and tr.is_visible():
            self._changed = True

    def update_trace_label(self, name: str, label: str):
        """Update the legend label of an existing trace.

        If the label is different, set `self._changed` to True.

        Parameters
        ----------
        name: str
            Name of the associated variable. Must exist in `self._traces`.

        label: str
            The new label.
        """
        tr = self[name]
        if tr.update_label(label) and tr.is_visible():
            self._changed = True

    def update_max_series_length(self, max_length: int):
        """Update the maximum series length of all traces.

        If this has an effect on any of the traces, set `self._changed` to `True`.

        Parameters
        ----------
        max_length: int
            The new maximum series length. If 0, the traces will not be downsampled.
        """
        # show error if negative
        if max_length < 0:
            self._toast.invalid_max_length(max_length)
            return

        # exit if not changed
        if self._max_series_length == max_length:
            return

        for _, tr in self._traces.items():
            if tr.update_max_series_length(max_length) and tr.is_visible():
                self._changed = True  # set to true if any trace changes

        self._max_series_length = max_length

    def hide_trace(self, name: str):
        """Hide an existing trace.

        If it was not already hidden, set `self._changed` to True.

        Parameters
        ----------
        name: str
            Name of the associated variable. Must exist in `self._traces`.
        """
        if self[name].update_visible(False):
            try:
                # should exist, but does not matter if it does not
                self.force_shown.remove(name)
            except KeyError:
                pass

            self._changed = True

    def force_show_trace(self, name: str):
        """Show a previously hidden or deleted trace.

        If it was not already visible, set `self._changed` to True. This can be used
        to undo `self.hide_trace()`, or to show deleted traces.

        Parameters
        ----------
        name: str
            Name of the associated variable. Must exist in `self._traces`.
        """
        if self[name].update_visible(True):
            self.force_shown.add(name)
            self._changed = True

    def set_figure_width(self, width: int):
        """Set the width of the figure.

        If the new width is different, set `self._changed` to True.

        Parameters
        ----------
        width: int
            New width of the figure in inches. Should be validated externally.
        """
        if self._width != width:
            self._width = width
            self._changed = True

    def set_figure_height(self, height: int):
        """Set the height of the figure.

        If the new height is different, set `self._changed` to True.

        Parameters
        ----------
        height: int
            New height of the figure in inches. Should be validated externally.
        """
        if self._height != height:
            self._height = height
            self._changed = True

    def set_ylabel(self, ylabel: str):
        """Set the y axis label.

        If the new label is different, set `self._changed` to True.

        Parameters
        ----------
        ylabel: str
            New label for the y axis. If it is an empty string, no label will be used.
        """
        if ylabel == "" and self._ylabel is not None:
            self._ylabel = None
            self._changed = True
        elif self._ylabel != ylabel:
            self._ylabel = ylabel
            self._changed = True

    def freeze(self):
        """Set the plotter to frozen, preventing new traces from being added."""
        if not self._frozen:
            self._toast.show(
                "Plot has been 'frozen'. New series will not be plotted, but old ones will still be updated.",
                ToastType.info,
            )

        self._frozen = True

    def defrost(self):
        """Set the plotter to un-frozen, allowing new traces to be plotted.

        Note that traces defined while it was frozen will need to be added manually.
        """
        if self._frozen:
            self._toast.show(
                "Plot has been 'defrosted'. Series defined while it was frozen must be manually shown with '--show'",
                ToastType.info,
            )

        self._frozen = False

    def get_visible(self) -> Set[str]:
        """Return a set of variable names corresponding to visible traces."""
        return set(name for name in self._traces.keys() if self[name].is_visible())

    def _adjust_fig_margins(self, fig: plt.Figure, y_max: float):
        """Set the figure margins based on its desired width and height.

        Parameters
        ----------
        fig: plt.Figure
            The `Figure` instance. Will be modified in place.

        y_max: float
            The maximum absolute y axis tick value.
        """
        # the appropriate margins for a figure of size 13x4 are known (i.e. 0.06, 0.94,
        # 0.85, 0.23) thus these values can be used to scale the margins for different
        # figure sizes
        default_width = 13
        default_height = 4

        if y_max >= 1e5:
            extra = 0.008 * (np.log10(y_max) - 5)
        else:
            extra = 0

        if self._ylabel is None:
            left = (0.06 + extra) * default_width / self._width
        else:
            left = (0.09 + extra) * default_width / self._width

        right = 1 - (0.06 * default_width / self._width)
        top = 1 - (0.15 * default_height / self._height)
        bottom = 0.23 * default_height / self._height

        # apply to the figure
        fig.subplots_adjust(left=left, right=right, top=top, bottom=bottom)

    def plot(self, force: bool, graph_output: widgets.Output):
        """Clear the output area and plot all the visible traces.

        The previously generated `Line2D` instances will be reused where possible, and
        only visible traces will be plotted.

        This function does nothing if `self._changed` is `False`.
        """
        if not self._changed and not force:
            return

        # reset matplotlib backend. This is necessary if it was changed to a non-interactive one externally
        for backend in ["module://ipykernel.pylab.backend_inline", "nbAgg", "Qt5Agg", "WXAgg"]:
            try:
                changed = plt.get_backend() != backend
                plt.switch_backend(backend)
                if changed:
                    self._toast.show(f"matplotlib backend switched to '{backend}'.", ToastType.warning)
                break
            except ImportError:
                pass

        mpld3.enable_notebook()

        fig: plt.Figure
        ax: plt.Axes
        fig, ax = plt.subplots(figsize=(self._width, self._height))

        lines = []
        labels = []

        # reset min and max x values
        x_min: OptDatetime = None
        x_max: OptDatetime = None
        min_step = 1e9  # arbitrarily large

        # add lines
        for name, tr in self._traces.items():
            if tr.is_visible():
                line = tr.get_line()
                ax.add_line(line)

                x0, x1 = tr.get_x_min_max()
                x_min = x0 if x_min is None else min(x_min, x0)
                x_max = x1 if x_max is None else max(x_max, x1)
                min_step = min(min_step, tr.get_step_size())

                lines.append(line)
                labels.append(tr.get_label())

        # configure layout
        ax.grid()
        ax.tick_params(axis="both", which="major", labelsize=11)

        # add y axis labels
        if self._ylabel is not None:
            ax.set_ylabel(self._ylabel, fontdict=dict(size=13), labelpad=25)

        # add mpld3 plugins if plot is not empty
        save_buttons = ["png", "svg"]
        mpld3.plugins.connect(fig, SaveImageButtons(save_buttons))

        if len(lines) > 0:
            mpld3.plugins.connect(fig, InteractiveLegend(lines, labels))
            mpld3.plugins.connect(fig, TimeSeriesTooltip(lines))

            assert x_min is not None
            assert x_max is not None
            total_range = (x_max - x_min).total_seconds()
            button_labels = gen_range_selector_labels(total_range, min_step, True)
            margin_right = len(save_buttons) * 50
            mpld3.plugins.connect(fig, RangeSelectorButtons(button_labels, lines, margin_right))

        # fit to the data
        ax.autoscale(enable=True, axis="x", tight=True)
        ax.autoscale(enable=True, axis="y")

        # adjust figure layout to ensure legend and hover info fit
        y_max = max(abs(y_loc) for y_loc in plt.yticks()[0])
        self._adjust_fig_margins(fig, y_max)

        # display plot in placeholder
        with graph_output:
            clear_output()
            plt.show()

        self._changed = False


class PlotterModel(View):
    """Class defining handlers for IPython events.

    Each handler should be registered on the shell using `shell.events.register()`.

    Methods
    -------
    get_plotted_dfs()
        Return the dictionary of series names associated with each dataframe.
    """

    def __init__(self, plotter: Plotter):
        """Initialise a `CellEventHandler` instance.

        Parameters
        ----------
        shell: IPython.InteractiveShell
            The IPython interactive shell. Used to access namespace variables.

        plotter: Plotter
            The associated `Plotter` instance.
        """
        self._plotter = plotter

        # dictionary of series, with key = name, value = pd.Series instance
        self._series_dict: Dict[str, pd.Series] = {}

        # dictionary with key = dataframe name, value = plotted column names
        self._plotted_dfs: Dict[str, Set[str]] = {}

        # set of variables in namespace, including series extracted from data frames
        self._ns_with_series: Set[str] = set()

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

    def _update_trace_if_changed(self, name: str, series: pd.Series, df_name: Optional[str] = None):
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

    def _add_traces_for_namespace_vars(self, pandas_vars: Dict[str, Union[pd.DataFrame, pd.Series]]):
        """Iterate through all variables in namespace, and plot them when appropriate.

        If a variable name starts with "_", or it is in the set `self._reserved`, it
        is skipped. Otherwise, if it is new or has been modified, it is passed to
        `self._update_trace_if_changed()`.
        """
        self._ns_with_series.clear()

        for name, var in pandas_vars.items():
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

    def update_variables(self, pandas_vars: Dict[str, Union[pd.DataFrame, pd.Series]]) -> None:
        self._add_traces_for_namespace_vars(pandas_vars)
        self._hide_traces_for_deleted_vars()

    def draw(self, force, graph_output):
        self._plotter.plot(force, graph_output)

    def ignore_variable(self, toast: Toast, var_name: str) -> None:
        var_name = remove_quotes(var_name)

        try:
            # hide all associated traces if dataframe name given
            if var_name in self._plotted_dfs:
                for trace_name in self._plotted_dfs[var_name]:
                    self._plotter.hide_trace(trace_name)
            # otherwise hide named trace
            else:
                self._plotter.hide_trace(var_name)

        except KeyError:
            toast.unrecognised_variable(var_name)

    def show_variable(self, toast: Toast, var_name: str) -> None:
        var_name = remove_quotes(var_name)

        try:
            # show all associated traces if dataframe name given
            if var_name in self._plotted_dfs:
                for trace_name in self._plotted_dfs[var_name]:
                    self._plotter.force_show_trace(trace_name)
            # otherwise show named trace
            else:
                self._plotter.force_show_trace(var_name)

        except KeyError:
            toast.unrecognised_variable(var_name)

    def change_colour(self, toast: Toast, var_name: str, colour: str) -> None:
        var_name = remove_quotes(var_name)
        colour = remove_quotes(colour)

        try:
            self._plotter.update_trace_colour(var_name, colour)
        except KeyError:
            toast.unrecognised_variable(var_name)

    def rename_variable(self, toast: Toast, var_name: str, display_name: str) -> None:
        var_name = remove_quotes(var_name)
        display_name = remove_quotes(display_name)

        try:
            # rename all associated traces if dataframe name given
            if var_name in self._plotted_dfs:
                for trace_name in self._plotted_dfs[var_name]:
                    label = trace_name.replace(var_name, display_name)
                    self._plotter.update_trace_label(trace_name, label)
            # otherwise update label of named trace
            else:
                self._plotter.update_trace_label(var_name, display_name)

        except KeyError:
            toast.unrecognised_variable(var_name)

    def set_plot_width(self, toast: Toast, width: int) -> None:
        if width < FigSize.MIN_WIDTH.value:
            toast.show(f"Figure width cannot be less than {FigSize.MIN_WIDTH.value}", ToastType.info)
            width = FigSize.MIN_WIDTH.value
        elif width > FigSize.MAX_WIDTH.value:
            toast.show(f"Figure width cannot be greater than {FigSize.MAX_WIDTH.value}", ToastType.info)
            width = FigSize.MAX_WIDTH.value

        self._plotter.set_figure_width(width)

    def set_plot_height(self, toast: Toast, height: int) -> None:
        if height < FigSize.MIN_HEIGHT.value:
            toast.show(f"Figure height cannot be less than {FigSize.MIN_HEIGHT.value}", ToastType.info)
            height = FigSize.MIN_HEIGHT.value
        elif height > FigSize.MAX_HEIGHT.value:
            toast.show(f"Figure height cannot be greater than {FigSize.MAX_HEIGHT.value}", ToastType.info)
            height = FigSize.MAX_HEIGHT.value

        self._plotter.set_figure_height(height)

    def set_ylabel(self, toast: Toast, ylabel: str) -> None:
        self._plotter.set_ylabel(ylabel)

    def update_max_series_length(self, toast: Toast, sample: int) -> None:
        self._plotter.update_max_series_length(sample)

    def freeze(self, toast: Toast) -> None:
        self._plotter.freeze()

    def defrost(self, toast: Toast) -> None:
        self._plotter.defrost()
