"""Module containing the `SaveImageButtons` mpld3 plugin.

Classes
-------
SaveImageButtons
    Class defining an mpld3 plugin to create save as image buttons.
"""

from typing import List

import mpld3
from pkg_resources import resource_filename

_js_file_path = resource_filename(__name__, "bundles/saveImageButtons.js")

with open(_js_file_path, "r") as f:
    _js = f.read()


class SaveImageButtons(mpld3.plugins.PluginBase):
    """Class defining an mpld3 plugin to create the save as image buttons.

    It extends `mpld3.plugins.PluginBase`, and can be connected to an mpld3 figure
    using `mpld3.plugins.connect(fig, <instance>)`.

    Properties
    ----------
    JAVASCRIPT: str
        A string containing the necessary JavaScript code for the plugin.

    css_: str
        A string containing the necessary style definitions for the plugin.

    Notes
    -----
    This plugin automatically hides any SVG elements added by the `RangeSelectorButtons`
    or `TimeSeriesTooltip` plugins.
    """

    JAVASCRIPT = _js
    css_ = """.mpld3-save-button-rect { cursor: pointer; }
              .mpld3-save-button-text { cursor: pointer; }"""

    def __init__(self, button_labels: List[str], fontsize=13):
        """Initialise a `SaveImageButtons` instance.

        Parameters
        ----------
        button_labels: List[str]
            List of button labels. Each label must be one of {"png", "svg"} (case
            insensitive).

        fontsize: int, optional
            The font size of the button labels.
        """
        for label in button_labels:
            if label.lower() not in {"png", "svg"}:
                raise ValueError(f"Invalid save image button label '{label}'")

        self.dict_ = {"type": "save_image_buttons", "button_labels": button_labels, "fontsize": fontsize}
