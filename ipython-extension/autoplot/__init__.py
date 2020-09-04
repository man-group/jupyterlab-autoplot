"""This is the main python package for the autoplot IPython extension."""

from ipywidgets import widgets

from autoplot.cell_events import CellEventHandler
from autoplot.extensions.autoplot_display import AutoplotDisplay
from autoplot.extensions.toast import Toast
from autoplot.magic import AutoplotMagic
from autoplot.plotter import Plotter


def load_ipython_extension(shell):
    """Load the IPython extension. Called by `%load_ext ...`.

    This function initialises the widget output area, the autoplot display area defined
    in `AutoplotDisplay` and the `Plotter` instance. It also attaches adds
    the IPython event listeners defined in `CellEventHandler` and registers the magic
    commands defined in `AutoplotMagic`.

    Parameters
    ----------
    shell: IPython.InteractiveShell
        The active IPython shell.
    """
    graph_output = AutoplotDisplay()
    js_output = widgets.Output()

    toast = Toast(js_output)
    plotter = Plotter(graph_output, toast)
    cell_event_handler = CellEventHandler(shell, plotter)

    # remove previous listeners
    for name, funcs in shell.events.callbacks.items():
        for func in funcs:
            if cell_event_handler.__class__.__name__ in str(func):
                shell.events.unregister(name, func)

    # register new event listeners
    for name, func in [
        ("pre_execute", cell_event_handler.pre_execute),
        ("pre_run_cell", cell_event_handler.pre_run_cell),
        ("post_execute", cell_event_handler.post_execute),
        ("post_run_cell", cell_event_handler.post_run_cell),
    ]:
        shell.events.register(name, func)

    # register magic commands
    apm = AutoplotMagic(shell, plotter, cell_event_handler, toast)
    shell.register_magics(apm)
