"""Module containing functions to validate and modify the figure size.

Methods
-------
set_plot_width(plotter, toast, width)
    Validate and set the width of the figure.

set_plot_height(plotter, toast, height)
    Validate and set the height of the figure.
"""

from autoplot.extensions.toast import Toast, ToastType
from autoplot.plotter import Plotter
from autoplot.utils.constants import FigSize


def set_plot_width(plotter: Plotter, toast: Toast, width: int):
    """Validate and set the width of the figure.

    Parameters
    ----------
    plotter: Plotter
        The associated `Plotter` instance.

    toast: Toast
        The `Toast` class instance.

    width: int
        The desired width of the plot in inches. If outside the range `[_MIN_WIDTH,
        _MAX_WIDTH]`, will be set to the nearest limit and the user will be notified.
    """
    if width < FigSize.MIN_WIDTH.value:
        toast.show(f"Figure width cannot be less than {FigSize.MIN_WIDTH.value}", ToastType.info)
        width = FigSize.MIN_WIDTH.value
    elif width > FigSize.MAX_WIDTH.value:
        toast.show(f"Figure width cannot be greater than {FigSize.MAX_WIDTH.value}", ToastType.info)
        width = FigSize.MAX_WIDTH.value

    plotter.set_figure_width(width)


def set_plot_height(plotter: Plotter, toast: Toast, height: int):
    """Validate and set the height of the figure.

    Parameters
    ----------
    plotter: Plotter
        The associated `Plotter` instance.

    toast: Toast
        The `Toast` class instance.

    height: int
        The desired height of the plot in inches. If outside the range `[_MIN_HEIGHT,
        _MAX_HEIGHT]`, will be set to the nearest limit and the user will be notified.
    """
    if height < FigSize.MIN_HEIGHT.value:
        toast.show(f"Figure height cannot be less than {FigSize.MIN_HEIGHT.value}", ToastType.info)
        height = FigSize.MIN_HEIGHT.value
    elif height > FigSize.MAX_HEIGHT.value:
        toast.show(f"Figure height cannot be greater than {FigSize.MAX_HEIGHT.value}", ToastType.info)
        height = FigSize.MAX_HEIGHT.value

    plotter.set_figure_height(height)
