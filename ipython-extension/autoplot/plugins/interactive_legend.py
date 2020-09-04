"""Module containing the `InteractiveLegend` mpld3 plugin.

Classes
-------
InteractiveLegend
    Class defining an mpld3 plugin to create an interactive legend.
"""

from typing import List

import matplotlib.lines as mpl_lines
import mpld3
from pkg_resources import resource_filename

from autoplot.plugins.line_utils import get_line_ids

_js_file_path = resource_filename(__name__, "bundles/interactiveLegend.js")

with open(_js_file_path, "r") as f:
    _js = f.read()


class InteractiveLegend(mpld3.plugins.PluginBase):
    """Class defining an mpld3 plugin to create an interactive legend.

    It extends `mpld3.plugins.PluginBase`, and can be connected to an mpld3 figure
    using `mpld3.plugins.connect(fig, <instance>)`.

    Properties
    ----------
    JAVASCRIPT: str
        A string containing the necessary JavaScript code for the plugin.

    css_: str
        A string containing the necessary style definitions for the plugin.

    Examples
    --------
     >>> import numpy as np
     >>> import matplotlib.pyplot as plt
     >>> import mpld3
     >>> %matplotlib inline
     >>> mpld3.enable_notebook()
     >>> fig, ax = plt.subplots()
     >>> fig.subplots_adjust(bottom=0.15)
     >>> x = np.linspace(-1, 1)
     >>> lines = [ax.plot(x, x), ax.plot(x, x**2), ax.plot(x, x**3)]
     >>> labels = ["Linear", "Quadratic", "Cubic"]
     >>> mpld3.plugins.connect(fig, InteractiveLegend(lines, labels))
     >>> plt.show()

    Notes
    -----
    This plugin communicates with the `TimeSeriesTooltip` plugin via the mpld3 Line
    property `.isHidden`.
    """

    JAVASCRIPT = _js
    css_ = """.mpld3-interactive-legend-rect { cursor: pointer; }"""

    def __init__(
        self,
        lines: List[mpl_lines.Line2D],
        labels: List[str],
        alpha_visible: float = 1.0,
        alpha_hidden: float = 0.15,
        fontsize: int = 13,
    ):
        """Initialise an `InteractiveLegend` instance.

        Parameters
        ----------
        lines: List[mpl_lines.Line2D]
            List of Line2D instances. Their ids will be passed to the plugin.

        labels: List[str]
            List of labels to display in the legend. Must be the same length as the
            list of lines.

        alpha_visible: float, optional
            The transparency of the line when it is visible.

        alpha_hidden: float, optional
            The transparency of the line when it is hidden.

        fontsize: int, optional
            The font size of the legend labels.
        """
        assert 0 <= alpha_visible <= 1
        assert 0 <= alpha_hidden <= 1

        assert len(lines) == len(labels)

        self.dict_ = {
            "type": "interactive_legend",
            "line_ids": get_line_ids(lines),
            "labels": labels,
            "alpha_visible": alpha_visible,
            "alpha_hidden": alpha_hidden,
            "fontsize": fontsize,
        }
