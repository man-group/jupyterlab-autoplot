"""This is the main python package for the autoplot IPython extension."""
from argparse import Namespace

import IPython
from IPython.core.magic import magics_class, Magics, line_magic
from IPython.core.magic_arguments import magic_arguments, argument, parse_argstring
from autoplot.utils import remove_quotes
from autoplot.utils.constants import FigSize, DEFAULT_MAX_SERIES_LENGTH

from ipywidgets import widgets
from IPython.core.interactiveshell import ExecutionResult

from autoplot.view_manager import ViewManager
from autoplot.dtaler import DTaler
from autoplot.extensions.autoplot_display import AutoplotDisplay
from autoplot.extensions.toast import Toast
from autoplot.plotter import Plotter, PlotterModel


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
    js_output = widgets.Output()

    toast = Toast(js_output)
    plotter_model = PlotterModel(Plotter(toast))
    dtaler = DTaler()
    view_manager = ViewManager(AutoplotDisplay(), shell, {"graph": plotter_model, "dtale": dtaler}, "graph")

    def _autoplot_post_run_cell(*args):
        if args:
            success = args[0].success
        else:
            # IPython 5.x didn't use to pass the result as a parameter of post_run_cell
            success = IPython.get_ipython().last_execution_succeeded
        if success:
            view_manager.redraw()

    # Unregister previous events registered with this class (eg.: when the plugin reloads)
    for name, funcs in shell.events.callbacks.items():
        for func in funcs:
            if _autoplot_post_run_cell.__name__ == func.__name__:
                shell.events.unregister(name, func)
    shell.events.register("post_run_cell", _autoplot_post_run_cell)

    apm = _make_magic(shell, toast, view_manager)
    shell.register_magics(apm)


def _make_magic(shell, toast, view_manager):
    @magics_class
    class AutoplotMagic(Magics):
        """Class to define and handle IPython magic commands for the autoplot extension.

        It extends `IPython.core.magic.Magics`, and be registered on an
        `IPython.InteractiveShell` using `shell.register_magics(<instance>).

        Methods
        -------
        autoplot(arg_string)
            Define the `%autoplot <arg_string>` line magic.
        """

        def __init__(self, shell: IPython.InteractiveShell, toast: Toast, view_manager: ViewManager):
            """Initialise an `AutoplotMagic` instance.

            Parameters
            ----------
            shell: IPython.InteractiveShell
                The IPython interactive shell. Used to initialise the super class.

            toast: Toast
                The `Toast` class instance.
            """
            super(AutoplotMagic, self).__init__(shell)
            self.toast = toast
            self.view_manager = view_manager

        @line_magic
        @magic_arguments()
        @argument(
            "-w",
            "--width",
            type=float,
            help=f"Set the width of the plot in inches. Must be in range {FigSize.MIN_WIDTH.value}-"
            f"{FigSize.MAX_WIDTH.value}. The default is {FigSize.DEFAULT_WIDTH.value}.",
        )
        @argument(
            "-h",
            "--height",
            type=float,
            help=f"Set the height of the plot in inches. Must be in range {FigSize.MIN_HEIGHT.value}-"
            f"{FigSize.MAX_HEIGHT.value}. The default is {FigSize.DEFAULT_HEIGHT.value}.",
        )
        @argument(
            "-r",
            "--rename",
            type=str,
            nargs=2,
            action="append",  # allows "-r A a -r B b" to work
            help="Change the legend label of the given variable. The first argument should be the variable name as it is "
            "defined, and the second is the label. E.g. `-r my_series 'A nice name'`.",
        )
        @argument(
            "-i",
            "--ignore",
            nargs="+",
            type=str,
            action="append",  # means "-i A -i B C D" => "[[A], [B, C, D]]"
            help="Remove the given variable(s) from the plot. Can be undone with '--show'.",
        )
        @argument(
            "-s",
            "--show",
            type=str,
            nargs="+",
            action="append",  # means "-s A -s B C D" => "[[A], [B, C, D]]"
            help="Show the given variable(s) on the plot. Can be used to undo '--ignore', or to display deleted variables. "
            "Cannot be used to plot variables prefixed with a '_', which are hidden by default.",
        )
        @argument(
            "-c",
            "--colour",
            type=str,
            nargs=2,
            action="append",  # allows "-c A red -r B blue" to work
            help="Change the colour of the given variable. The first argument should be the variable name as it is "
            "defined, and the second is the colour (as a valid matplotlib colour). E.g. `-c my_series gold`.",
        )
        @argument("-y", "--ylabel", type=str, help="Set the y axis label. Set to '' to remove.")
        @argument(
            "--sample",
            type=int,
            help="Set the maximum length of all the series above which they will be downsampled, (i.e. only this many "
            f"evenly spaced points will be plotted). The default value is {DEFAULT_MAX_SERIES_LENGTH}, which is "
            "recommended for good performance. Set to 0 to disable this feature.",
        )
        @argument(
            "-f",
            "--freeze",
            action="store_true",
            help="Prevent new series being added to the plot. Existing traces will continue to be updated. Reset "
            "with '--defrost'.",
        )
        @argument(
            "-d",
            "--defrost",
            action="store_true",
            help="Start adding new series to the plot again. Series defined while the plotter was 'frozen' need to be "
            "manually shown with '--show'.",
        )
        @argument(
            "-v", "--view", default=None, choices=view_manager.view_names, help="Switch variable visualization method"
        )
        def autoplot(self, arg_string: str):
            """You have successfully loaded the JupyterLab Autoplot extension!

            This extension will watch the notebook's namespace for datetime indexed, real
            valued pandas series or dataframes and update the plot in real time as these
            variables are modified.

            To modify the plot or traces, use the command `%autoplot` with one of more of
            the optional arguments.:
            """
            args: Namespace = parse_argstring(self.autoplot, arg_string)

            # handle resize arguments
            if args.width is not None:
                self.view_manager.set_plot_width(self.toast, args.width)
            if args.height is not None:
                self.view_manager.set_plot_height(self.toast, args.height)

            # handle variable arguments
            if args.rename is not None:
                for var, label in args.rename:
                    self.view_manager.rename_variable(self.toast, var, label)

            if args.ignore is not None:
                for a in args.ignore:
                    for var in a:
                        self.view_manager.ignore_variable(self.toast, var)

            if args.show is not None:
                for a in args.show:
                    for var in a:
                        self.view_manager.show_variable(self.toast, var)

            if args.colour is not None:
                for var, colour in args.colour:
                    self.view_manager.change_colour(self.toast, var, colour)

            # handle axis label arguments
            if args.ylabel is not None:
                self.view_manager.set_ylabel(self.toast, remove_quotes(args.ylabel))

            # handle sample arguments
            if args.sample is not None:
                self.view_manager.update_max_series_length(self.toast, args.sample)

            # handle freeze / defrost arguments
            if args.freeze:
                self.view_manager.freeze(self.toast)

            if args.defrost:
                self.view_manager.defrost(self.toast)

            self.view_manager.active = args.view if args.view is not None else self.view_manager.active

    return AutoplotMagic(shell, toast, view_manager)


__all__ = ["load_ipython_extension"]
