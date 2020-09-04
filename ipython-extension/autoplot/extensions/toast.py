"""Module containing the class used to display JupyterLab toasts.

Communication is achieved via custom DOM events, using the name 'autoplot-toast'.

Classes
-------
ToastType
    Enum class defining different toast types.

Toast
    Class to display JupyterLab toasts via DOM events.
"""

from enum import Enum

from IPython.core.display import Javascript, display
from ipywidgets import widgets


class ToastType(Enum):
    """Enum class defining different toast types."""

    error = "error"
    warning = "warning"
    success = "success"
    info = "info"


class Toast(object):
    """Class to display JupyterLab toasts via DOM events.

    Methods
    -------
    show(message, toast_type)
        Display a generic toast with a given message and type.

    downsample_warning(var_name, old_size, new_size)
        Display a toast warning the user that a trace has been downsampled.

    no_downsample_info(var_name)
        Display a toast notifying the user that a trace is no longer downsampled.

    invalid_trace_colour(colour)
        Display an error toast when an invalid colour is requested.

    invalid_max_length(max_length)
        Display an error toast when an invalid colour sample length is requested.

    unrecognised_variable(var_name)
        Display an error toast when an unrecognised variable name is referenced.
    """

    def __init__(self, js_output: widgets.Output):
        """Initialise a `Toast` instance and display `js_output`.

        Parameters
        ----------
        js_output: widgets.Output
            The IPython output widget in which to display the JavaScript. This will be
            cleared every time new JavaScript is shown to prevent old toasts being
            re-shown on page refresh.
        """
        self._js_output = js_output
        display(self._js_output)

    def show(self, message: str, toast_type: ToastType):
        """Display a generic toast with a given message and type.

        This is achieved by dispatching a custom DOM event with the name
        'autoplot-toast'.

        Parameters
        ----------
        message: str
            The toast message to display. Must not contain the backtick (`) character.

        toast_type: ToastType
            The toast type, used to format the toast. Must be one of the values defined
            in `ToastType`.
        """
        assert "`" not in message, "Message cannot contain '`'"

        js = f"""document.dispatchEvent(new CustomEvent(
                    'autoplot-toast', {{ detail: {{
                        message: `{message}`, type: `{toast_type.value}`,
                    }} }} ))"""

        with self._js_output:
            display(Javascript(js))  # noqa

        self._js_output.clear_output()

    def downsample_warning(self, var_name: str, old_size: int, new_size: int):
        """Display a toast warning the user that a trace has been downsampled.

        Parameters
        ----------
        var_name: str
            The name of the downsampled variable.

        old_size: int
            The variable's original size.

        new_size: int
            The variable's size after downsizing.
        """
        message = (
            f"Time series '{var_name}' has {old_size} data points, thus has been downsampled to {new_size} points."
        )

        self.show(message, ToastType.warning)

    def no_downsample_info(self, var_name: str):
        """Display a toast notifying the user that a trace is no longer downsampled.

        Parameters
        ----------
        var_name: str
            The name of the variable.
        """
        message = f"Time series '{var_name}' is now being displayed in full."
        self.show(message, ToastType.info)

    def invalid_trace_colour(self, colour: str):
        """Display an error toast when an invalid colour is requested.

        Parameters
        ----------
        colour: str
            The invalid colour.
        """
        message = f"'{colour}' is not a valid matplotlib colour."
        self.show(message, ToastType.error)

    def invalid_max_length(self, max_length: int):
        """Display an error toast when an invalid colour sample length is requested.

        Parameters
        ----------
        max_length: int
            The invalid max_length.
        """
        message = (
            f"Maximum series length before downsampling must be >= 0, not '{max_length}'. Set to 0 for no downsampling."
        )

        self.show(message, ToastType.error)

    def unrecognised_variable(self, var_name: str):
        """Display an error toast when an unrecognised variable name is referenced.

        Parameters
        ----------
        var_name: str
            The unrecognised variable name.
        """
        message = f"Cannot find variable '{var_name}'. Make sure you are using its actual name, not its legend label."

        self.show(message, ToastType.error)
