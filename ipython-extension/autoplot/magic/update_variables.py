"""Module containing functions to update trace / variable attributes.

Methods
-------
remove_quotes(text)
    Return the `text` with any surrounding quotes removed.

rename_variable(plotter, plotted_dfs, toast, var_name, display_name)
   Update the legend label of the given variable.

ignore_variable(plotter, plotted_dfs, toast, var_name)
    Hide the given variable from the plot. Undoes `show_variable`.

show_variable(plotter, plotted_dfs, toast, var_name)
    Show the given variable on the plot. Undoes `ignore_variable`.

change_colour(plotter, toast, var_name, colour)
    Update the colour of the given variable.
"""

from typing import Dict, Set

from autoplot.extensions.toast import Toast
from autoplot.plotter import Plotter


def remove_quotes(text: str) -> str:
    """Return the `text` with any surrounding quotes removed."""
    return text[1:-1] if text[0] + text[-1] in {"''", '""'} else text


def rename_variable(plotter: Plotter, plotted_dfs: Dict[str, Set[str]], toast: Toast, var_name: str, display_name: str):
    """Update the legend label of the given variable.

    If a dataframe name is specified, the legend labels of all the columns are changed
    accordingly.

    Parameters
    ----------
    plotter: Plotter
        The associated `Plotter` instance.

    plotted_dfs: Dict[str, Set[str]]
        Dictionary with key = dataframe name, value = set of plotted column names.

    toast: Toast
        The `Toast` class instance.

    var_name: str
        The name of the variable to change the label of, as it is defined in Python.
        Can be a series or dataframe name.

    display_name: str
        The desired legend label.
    """
    var_name = remove_quotes(var_name)
    display_name = remove_quotes(display_name)

    try:
        # rename all associated traces if dataframe name given
        if var_name in plotted_dfs:
            for trace_name in plotted_dfs[var_name]:
                label = trace_name.replace(var_name, display_name)
                plotter.update_trace_label(trace_name, label)
        # otherwise update label of named trace
        else:
            plotter.update_trace_label(var_name, display_name)

    except KeyError:
        toast.unrecognised_variable(var_name)


def ignore_variable(plotter: Plotter, plotted_dfs: Dict[str, Set[str]], toast: Toast, var_name: str):
    """Hide the given variable from the plot. Undoes `show_variable`.

    If a dataframe name is specified, all of its columns will be hidden.

    Parameters
    ----------
    plotter: Plotter
        The associated `Plotter` instance.

    plotted_dfs: Dict[str, Set[str]]
        Dictionary with key = dataframe name, value = set of plotted column names.

    toast: Toast
        The `Toast` class instance.

    var_name: str
        Name of the variable to hide, as it is defined in Python. Can be a series
        names or dataframe name.
    """
    var_name = remove_quotes(var_name)

    try:
        # hide all associated traces if dataframe name given
        if var_name in plotted_dfs:
            for trace_name in plotted_dfs[var_name]:
                plotter.hide_trace(trace_name)
        # otherwise hide named trace
        else:
            plotter.hide_trace(var_name)

    except KeyError:
        toast.unrecognised_variable(var_name)


def show_variable(plotter: Plotter, plotted_dfs: Dict[str, Set[str]], toast: Toast, var_name: str):
    """Show the given variable on the plot. Undoes `ignore_variable`.

    If a dataframe name is specified, all of its columns will be shown.

    Parameters
    ----------
    plotter: Plotter
        The associated `Plotter` instance.

    plotted_dfs: Dict[str, Set[str]]
        Dictionary with key = dataframe name, value = set of plotted column names.

    toast: Toast
        The `Toast` class instance.

    var_name: str
        Name of the variable to show, as it is defined in Python. Can be a series
        names or dataframe name.
    """
    var_name = remove_quotes(var_name)

    try:
        # show all associated traces if dataframe name given
        if var_name in plotted_dfs:
            for trace_name in plotted_dfs[var_name]:
                plotter.force_show_trace(trace_name)
        # otherwise show named trace
        else:
            plotter.force_show_trace(var_name)

    except KeyError:
        toast.unrecognised_variable(var_name)


def change_colour(plotter: Plotter, toast: Toast, var_name: str, colour: str):
    """Update the colour of the given variable.

    Only series / column names can be specified, not dataframe names.

    Parameters
    ----------
    plotter: Plotter
        The associated `Plotter` instance.

    toast: Toast
        The `Toast` class instance.

    var_name: str
        The name of the variable to change the colour of, as it is defined in Python.

    colour: str
        The desired trace colour. Must be a valid matplotlib colour.
    """
    var_name = remove_quotes(var_name)
    colour = remove_quotes(colour)

    try:
        plotter.update_trace_colour(var_name, colour)
    except KeyError:
        toast.unrecognised_variable(var_name)
