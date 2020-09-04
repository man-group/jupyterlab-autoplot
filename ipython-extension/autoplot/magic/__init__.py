"""Module containing the `AutoplotMagic` class.

Classes
-------
AutoplotMagic
    Class to define and handle IPython magic commands for the autoplot extension.
"""

from argparse import Namespace

import IPython
from IPython.core.magic import Magics, line_magic, magics_class
from IPython.core.magic_arguments import argument, magic_arguments, parse_argstring

from autoplot.cell_events import CellEventHandler
from autoplot.extensions.toast import Toast
from autoplot.magic.resize_figure import set_plot_height, set_plot_width
from autoplot.magic.update_variables import (
    change_colour,
    ignore_variable,
    remove_quotes,
    rename_variable,
    show_variable,
)
from autoplot.plotter import Plotter
from autoplot.utils.constants import DEFAULT_MAX_SERIES_LENGTH, FigSize


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

    def __init__(
        self, shell: IPython.InteractiveShell, plotter: Plotter, cell_events_handler: CellEventHandler, toast: Toast
    ):
        """Initialise an `AutoplotMagic` instance.

        Parameters
        ----------
        shell: IPython.InteractiveShell
            The IPython interactive shell. Used to initialise the super class.

        plotter: Plotter
            The `Plotter` class instance associated with the session.

        cell_events_handler: CellEventHandler
            The `CellEventHandler` class instance associated with the session.

        toast: Toast
            The `Toast` class instance.
        """
        super(AutoplotMagic, self).__init__(shell)
        self.plotter = plotter
        self.plotted_dfs = cell_events_handler.get_plotted_dfs()
        self.toast = toast

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
            set_plot_width(self.plotter, self.toast, args.width)
        if args.height is not None:
            set_plot_height(self.plotter, self.toast, args.height)

        # handle variable arguments
        if args.rename is not None:
            for var, label in args.rename:
                rename_variable(self.plotter, self.plotted_dfs, self.toast, var, label)

        if args.ignore is not None:
            for a in args.ignore:
                for var in a:
                    ignore_variable(self.plotter, self.plotted_dfs, self.toast, var)

        if args.show is not None:
            for a in args.show:
                for var in a:
                    show_variable(self.plotter, self.plotted_dfs, self.toast, var)

        if args.colour is not None:
            for var, colour in args.colour:
                change_colour(self.plotter, self.toast, var, colour)

        # handle axis label arguments
        if args.ylabel is not None:
            self.plotter.set_ylabel(remove_quotes(args.ylabel))

        # handle sample arguments
        if args.sample is not None:
            self.plotter.update_max_series_length(args.sample)

        # handle freeze / defrost arguments
        if args.freeze:
            self.plotter.freeze()

        if args.defrost:
            self.plotter.defrost()

        # no need to re-plot graph here as this will be done on cell execution
