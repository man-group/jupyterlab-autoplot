"""Module containing the `RangeSelectorButtons` mpld3 plugin.

Classes
-------
RangeSelectorButtons
    Class defining an mpld3 plugin to create range selector buttons.
"""

from typing import List, Optional

import matplotlib.lines as mpl_lines
import mpld3
from pkg_resources import resource_filename

from autoplot.plugins.line_utils import get_line_ids

_js_file_path = resource_filename(__name__, "bundles/rangeSelectorButtons.js")

with open(_js_file_path, "r") as f:
    _js = f.read()


class RangeSelectorButtons(mpld3.plugins.PluginBase):
    """Class defining an mpld3 plugin to create range selector buttons.

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
        >>> import matplotlib.pyplot as plt
    import mpld3
    import numpy as np
    import pandas as pd
    %matplotlib inline
        >>> mpld3.enable_notebook()
        >>> fig, ax = plt.subplots(figsize=(10, 4))
        >>> x = pd.date_range("2020-01-01", "2021-06-01")
        >>> y = np.random.randn(len(x))
        >>> lines = [ax.plot(x, y)]
        >>> button_labels = ["fit", "reset", "5d", "14d", "1m", "6m", "ytd", "1y"]
        >>> ax.autoscale(enable=True, axis="x", tight=True)
        >>> mpld3.plugins.connect(fig, RangeSelectorButtons(button_labels, lines))
        >>> plt.show()

        Notes
        -----
        This plugin communicates with the `InteractiveLegend` plugin via the mpld3 Line
        property `.isHidden`.
    """

    JAVASCRIPT = _js
    css_ = """.mpld3-range-selector-button-rect { cursor: pointer; }
              .mpld3-range-selector-button-text { cursor: pointer; }"""

    def __init__(
        self,
        button_labels: List[str],
        lines: Optional[List[mpl_lines.Line2D]] = None,
        margin_right: int = 0,
        fontsize: int = 13,
    ):
        """Initialise a `RangeSelectorButtons` instance.

        Parameters
        ----------
        button_labels: List[str]
            List of button labels. Each label must either be of the form
            "<number><unit>" (e.g. "3m", "10d", "2y"), or one of {"ytd", "fit",
            "reset"}.

            Valid units are "s" = seconds, "M" = minutes, "h" = hours, "d" = days,
            "w" = weeks, "m" = months, "y" = years.

        lines: List[mpl_lines.Line2D], optional
            List of Line2D instances. Their ids will be passed to the plugin. This is
            only required if the "fit" button is used.

        margin_right: int, optional
            The distance in pixels from the right hand edge of the figure right of which
            no new buttons will be added. Default is 0, i.e. buttons will be placed
            until they would be off the edge of the figure.

        fontsize: int, optional
            The font size of the button labels.
        """
        for label in button_labels:
            try:
                int(label[:-1])
                assert label[-1] in {"s", "M", "h", "d", "w", "m", "y"}
            except ValueError:
                assert label in {"ytd", "fit", "reset"}

                if label == "fit" and lines is None:
                    raise ValueError("The 'fit' button requires the 'lines' argument to be defined.")
            except AssertionError:
                raise ValueError(f"Invalid range selector button label '{label}'")

        self.dict_ = {
            "type": "range_selector_buttons",
            "button_labels": button_labels,
            "line_ids": None if lines is None else get_line_ids(lines),
            "margin_right": margin_right,
            "fontsize": fontsize,
        }
