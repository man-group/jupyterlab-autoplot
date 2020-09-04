"""Utility functions used to compare two plots generated with matplotlib."""

import tempfile
from typing import IO

import matplotlib.lines as mpl_lines
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.testing.compare import compare_images

from autoplot.plotter.trace import Trace


def _save_fig(fig: plt.Figure, ax: plt.Axes) -> IO:
    """Save the given figure. The axes will be scaled to the data."""
    ax.autoscale(enable=True, axis="x", tight=True)
    ax.autoscale(enable=True, axis="y")

    file = tempfile.NamedTemporaryFile(mode="w+b", suffix=".png")
    fig.savefig(file)
    plt.close(fig)

    file.seek(0)
    return file


def save_expected_plot(series: pd.Series, colour="C0") -> IO:
    """Return an image of the plot with the given `series` and `colour`."""
    fig, ax = plt.subplots()
    ax.add_line(mpl_lines.Line2D(series.index, series.values, color=colour))

    return _save_fig(fig, ax)


def save_trace_plot(trace: Trace) -> IO:
    """Return an image of the plot generated with the trace's line."""
    fig, ax = plt.subplots()
    ax.add_line(trace.get_line())

    return _save_fig(fig, ax)


def images_equal(expected_image: IO, actual_image: IO) -> bool:
    """Return `True` if `expected_image` and `actual_image` are equal."""
    return compare_images(expected_image.name, actual_image.name, 0.001) is None
