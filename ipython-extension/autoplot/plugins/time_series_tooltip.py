"""Module containing the `TimeSeriesTooltip` mpld3 plugin.

Classes
-------
TimeSeriesTooltip
    Class defining an mpld3 plugin to create line graph tooltips.
"""

from typing import List

import matplotlib.lines as mpl_lines
import mpld3
from pkg_resources import resource_filename

from autoplot.plugins.line_utils import get_line_ids

_js_file_path = resource_filename(__name__, "bundles/timeSeriesTooltip.js")

with open(_js_file_path, "r") as f:
    _js = f.read()


class TimeSeriesTooltip(mpld3.plugins.PluginBase):
    """Class defining an mpld3 plugin to create time series line graph tooltips.

    It extends `mpld3.plugins.PluginBase`, and can be connected to an mpld3 figure
    using `mpld3.plugins.connect(fig, <instance>)`.

    Properties
    ----------
    JAVASCRIPT: str
        A string containing the necessary JavaScript code for the plugin.

    Examples
    --------
    >>> import numpy as np
    >>> import pandas as pd
    >>> import matplotlib.pyplot as plt
    >>> import mpld3
    >>> %matplotlib inline
    >>> mpld3.enable_notebook()
    >>> fig, ax = plt.subplots(figsize=(10, 4))
    >>> fig.subplots_adjust(left=0.05, right=0.85)
    >>> x = pd.date_range("2020-01-01", "2020-06-01")
    >>> y1 = np.random.randn(len(x))
    >>> y2 = np.random.randn(len(x)) / 2 + 2
    >>> lines = [ax.plot(x, y1), ax.plot(x, y2)]
    >>> ax.autoscale(enable=True, axis="x", tight=True)
    >>> mpld3.plugins.connect(fig, TimeSeriesTooltip(lines))
    >>> plt.show()

    Notes
    -----
    It may be necessary to adust the right margin of the figure, using
    `fig.subplots_adjust(right=0.8)`.

    This plugin communicates with the `InteractiveLegend` plugin via the mpld3 Line
    property `.isHidden`.
    """

    JAVASCRIPT = _js

    def __init__(self, lines: List[mpl_lines.Line2D], fontsize: int = 12):
        """Initialise a `TimeSeriesTooltip` instance.

        Parameters
        ----------
        lines: List[mpl_lines.Line2D]
            List of Line2D instances. Their ids will be passed to the plugin.

        fontsize: int, optional
            The size of the tooltip font
        """
        self.dict_ = {"type": "time_series_tooltip", "line_ids": get_line_ids(lines), "fontsize": fontsize}
