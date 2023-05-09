"""Module containing the `AutoplotDisplay` class.

Classes
-------
AutoplotDisplay
    Class defining the autoplot display output area.
"""

import uuid

from ipywidgets import Output
from traitlets import Unicode

# these values must mach those in autoplot-display/version.ts
EXTENSION_TITLE = "Autoplot Display"
EXTENSION_VERSION = "0.4.0"
MODULE_NAME = "@jupyter-widgets/autoplot-display"

MODEL_NAME = "AutoplotDisplayModel"
VIEW_NAME = "AutoplotDisplayView"


class AutoplotDisplay(Output):
    """Class defining the autoplot display output area.

    It extends `ipywidgets.Output`, thus can be used as a context manager to handle the
    redirection of outputs. It communicates with the JupyterLab extension of the same
    name.
    """

    _model_name = Unicode(MODEL_NAME).tag(sync=True)
    _model_module = Unicode(MODULE_NAME).tag(sync=True)
    _model_module_version = Unicode(EXTENSION_VERSION).tag(sync=True)

    _view_name = Unicode(VIEW_NAME).tag(sync=True)
    _view_module = Unicode(MODULE_NAME).tag(sync=True)
    _view_module_version = Unicode(EXTENSION_VERSION).tag(sync=True)

    # custom attributes
    title = Unicode(EXTENSION_TITLE).tag(sync=True)
    uuid = Unicode(uuid.uuid4().hex).tag(sync=True)
    data_id = Unicode("1").tag(sync=True)
