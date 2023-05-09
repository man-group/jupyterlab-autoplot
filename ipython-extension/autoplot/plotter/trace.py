"""Module containing the `Trace` class.

Classes
-------
Trace
    Class to store a `Line2D` instance, and manage how it is displayed and updated.
"""

import copy
import datetime
from typing import Optional, Tuple

import matplotlib.lines as mpl_lines
import numpy as np
import pandas as pd
from matplotlib.colors import is_color_like

from autoplot.extensions.toast import Toast


class Trace(object):
    """Class to store a `Line2D` instance, and manage how it is displayed and updated.

    Methods
    -------
    update_series(series)
        Update the trace with the given series. Return `True` if it was changed.

    update_max_series_length(max_length)
        Update the maximum length of the series above which it will be downsampled.

    update_colour(colour)
        Update the trace colour. Return `True` if it was changed.

    update_label(label)
        Update the trace legend label. Return `True` if it was changed.

    get_label()
        Return the trace label, as it should appear in the legend.

    update_visible(visible)
        Update the trace visibility. Return `True` if it was changed.

    is_visible()
        Return `True` if the trace is set to be visible, otherwise `False`.

    get_x_min_max()
        Return the min and max x values as datetime objects.

    get_line()
        Return a copy of the trace's `Line2D` instance.

    get_step_size()
        Return the approximate index step size, in seconds.
    """

    def __init__(
        self,
        toast: Toast,
        name: str,
        series: pd.Series,
        index: int,
        max_length: int,
        *,
        visible: bool = True,
        df_name: Optional[str] = None,
    ):
        """Initialise a `Trace` instance.

        Parameters
        ----------
        toast: Toast
            The `Toast` class instance.

        name: str
            Name of the variable, as it is defined in Python.

        series: pd.Series
            The trace data. Assumed to be datetime-indexed and have numeric values.

        index: int
            Equal to how many other traces already exist. Used to set the line colour.

        max_length: int
            The maximum length of the series above which it will be downsampled.

        visible: bool, optional
            If set to False, trace will initially not be visible.

        df_name: str, optional
            The name of the associated dataframe if the series is a dataframe column.
        """
        self._toast = toast
        self._name = name
        self._series = series
        self.df_name = df_name

        self._colour = f"C{index % 10}"
        self._label = name

        self._visible = visible

        # flag that stores whether the user has been warned that this series is too
        # long to be displayed in full
        self._been_warned = False
        self._max_length = np.iinfo(np.int64).max if max_length == 0 else max_length

        # the approximate index step size, in seconds
        self._step_size = 1

        # build the line
        self._line: mpl_lines.Line2D
        self._build_line_with_props()

    def _get_downsampled(self) -> pd.Series:
        """Return a downsampled copy of the series, or the original if it is shorter.

        `downsample_warning_toast()` will be called if the user has not already been
        warned that the series has been downsampled.
        """
        length = len(self._series)

        # downsample the series if it is too long
        if self._max_length < length:
            index = np.round(np.linspace(0, length - 1, self._max_length)).astype(int)

            # warn user if have not already done so
            if not self._been_warned:
                self._toast.downsample_warning(self._name, length, self._max_length)
                self._been_warned = True

            return self._series[index]

        # reset the warning flag, as from now the series will be displayed in full
        self._been_warned = False
        return self._series

    def _build_line_with_props(self):
        """Build the `Line2D` instance and calculate the step size."""
        series = self._get_downsampled()
        self._step_size = (series.index[1] - series.index[0]).total_seconds()

        self._line = mpl_lines.Line2D(series.index, series.values, label=self._label, color=self._colour)

    def update_series(self, series: pd.Series) -> bool:
        """Update the trace with the given series. Return `True` if it was changed.

        Parameters
        ----------
        series: pd.Series
            The new series. Assumed to be datetime-indexed and have numeric values.

        Returns
        -------
        bool
            True if the series was updated (i.e. the new series was different to
            the current one), otherwise False.
        """
        index_equal = series.index.equals(self._series.index)
        values_equal = np.array_equal(series.values, self._series.values)

        # do nothing if equal
        if index_equal and values_equal:
            return False

        self._series = series

        # update y data if x unchanged. Must downsample again to match original
        if index_equal:
            self._line.set_ydata(self._get_downsampled().values)
        # update x data if y unchanged. Must downsample again to match original
        elif values_equal:
            self._line.set_xdata(self._get_downsampled().index)
        else:
            self._build_line_with_props()

        return True

    def update_max_series_length(self, max_length: int) -> bool:
        """Update the maximum length of the series above which it will be downsampled.

        A toast will be shown if the series was previously downsampled and is now
        shown in full.

        Parameters
        ----------
        max_length: int
            The new maximum series length. If 0, the trace will not be downsampled.

        Returns
        -------
        bool
            True if the new maximum length changed how the series should be plotted,
            otherwise False.
        """
        if max_length == 0:
            max_length = np.iinfo(np.int64).max

        # don't replot if max length unchanged
        if self._max_length == max_length:
            return False

        length = len(self._series)

        # don't replot if the series wasn't and still shouldn't be downsampled
        if self._max_length >= length and max_length >= length:
            self._max_length = max_length
            return False

        # show info toast if was previously downsampled
        if self._max_length < length <= max_length:
            self._toast.no_downsample_info(self._name)

        self._max_length = max_length
        self._build_line_with_props()

        return True

    def update_colour(self, colour: str) -> bool:
        """Update the trace colour. Return `True` if it was changed.

        Parameters
        ----------
        colour: str
            The new colour for the trace. Must be a valid matplotlib colour.

        Returns
        -------
        bool
            True if the colour was updated (i.e. the new colour was different to
            the current one), otherwise False.
        """
        # invalid colour
        if not is_color_like(colour):
            self._toast.invalid_trace_colour(colour)
            return False

        # same colour as before
        if self._colour == colour:
            return False

        self._line.set_color(colour)
        self._colour = colour
        return True

    def update_label(self, label: str) -> bool:
        """Update the trace legend label. Return `True` if it was changed.

        Parameters
        ----------
        label: str
            The new label for the trace.

        Returns
        -------
        bool
            True if the label was updated (i.e. the new label was different to
            the current one), otherwise False.
        """
        if self._label == label:
            return False

        self._label = label
        self._line.set_label(self._label)  # currently not visible
        return True

    def get_label(self) -> str:
        """Return the trace label, as it should appear in the legend."""
        return self._label

    def update_visible(self, visible: bool) -> bool:
        """Update the trace visibility. Return `True` if it was changed.

        Parameters
        ----------
        visible: bool
            True if the trace should be visible, False if hidden.

        Returns
        -------
        bool
            True if the visibility was updated (i.e. the new visibility was different to
            the current one), otherwise False.
        """
        if self._visible == visible:
            return False

        self._visible = visible
        return True

    def is_visible(self) -> bool:
        """Return `True` if the trace is set to be visible, otherwise `False`."""
        return self._visible

    def get_x_min_max(self) -> Tuple[datetime.datetime, datetime.datetime]:
        """Return the min and max x values as datetime objects."""
        return self._series.index.min().to_pydatetime(), self._series.index.max().to_pydatetime()

    def get_line(self) -> mpl_lines.Line2D:
        """Return a copy of the trace's `Line2D` instance."""
        return copy.copy(self._line)

    def get_step_size(self) -> float:
        """Return the approximate index step size, in seconds.

        It's value is calculated when the line is built, and is equal to the difference
        between the first and second index values of the downsampled series.
        """
        return self._step_size
