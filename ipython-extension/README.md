# JupyterLab Autoplot - IPython Component

This IPython extension is one of the three components that make up the [JupyterLab Autoplot extension](../README.md).

## Development

First you should follow the instructions [here](../autoplot-display#development) to install the JupyterLab extension component. Then, to apply the changes you have made to the IPython component:

```sh
cd ipython-extension/
python -m pip install -e .
```

You can then reload the extension in your JupyterLab instance with `%reload_ext autoplot` (you may need to restart the kernel first).

### Description of classes

Each of the following classes will be initialised **once** in the `load_ipython_extension()` function, and, where necessary, these instances will be accessible to each other. A diagram showing how these classes interact can be found at the bottom of this section.

#### `ViewManager`

This class is the interface between the ipython interactions and the underlying models. The `redraw` method is expected to be called in the `post_run_cell` IPython hook. All the other methods implement one of the magic commands in autoplot.

This class is a proxy for the actual models, which implement the `View` interface and will perform the actual work needed to integrate with dtale or mpd3.

When `redraw` is called, the class instance will scan the variables in the notebook's namespace, and look for pandas variables. The active view's `update_variables` is called with the filtered variables. Then, the `draw` method is called. Currently, only the active view's `update_variables` is called; however, it may be argued that syncing the `--freeze` and `--ignore` commands regardless of the current view is more natural. In that case, it will be useful to call `update_variables` in all views, rather than just the active one. We need to get more user feedback to decide which is the best approach.

#### `_make_magic` (`AutoplotMagic`)

The function `_make_magic` is a factory for instances of `AutoplotMagic`, in fact, it builds the class itself so that it can easily define the list of possible views in the `-v` argument.

AutoplotMagic extends [`IPython.core.magic.Magics`](https://ipython.readthedocs.io/en/stable/api/generated/IPython.core.magic.html#IPython.core.magic.Magics), and defines the magic commands described [here](../README.md#modifying-the-plot--traces). This class translates the user input into calls to the `ViewManager`.

#### `AutoplotDisplay`

This class extends [`ipywidgets.Output`](https://ipywidgets.readthedocs.io/en/latest/examples/Output%20Widget.html), and defines the output area in which the graph is plotted. By matching the attributes `_model_name`, `_model_module_version` etc. with the equivalents in the JupyterLab extension class `AutoplotDisplayModel`, the two become linked and the output captured by the IPython component will be displayed wherever the JupyterLab component is rendered.

This class also defines the `data_id` property, which is used by dtale to find out which instance (dataframe) is currently active.

#### `Toast`

This class defines some methods to dispatch DOM events that trigger toast notifications in the JupyterLab extension. These toasts change colour depending on their type, which can be one of 'error', 'warning', 'success' or 'info'.

#### Backends

##### `Dtaler`

This is the class that implements the View interface for the dtale integration. It's responsible to keep track of the changed variables and dtale instances.

##### `PlotterModel` and `Plotter`

`PlotterModel` is the class that implements the View interface. It defines a dictionary of series names to their values, and one of dataframe names to the set of series names that were created from its columns. The `draw` method calls `plotter.plot()`, which initialises a matplotlib figure and axes, adds the defined traces to it and styles the figure.

When a series is added, modified or deleted, the dictionaries will be updated and the appropriate calls will be made to the `Plotter` instance.

The `Plotter` class manages the collection of `Trace` class instances and handles the graph plotting. It has a number of public methods like `update_trace_series()`, `update_trace_colour()` etc. which are used by the `PlotterModel` class to modify the plot and/or traces.

The `Trace` class stores a matplotlib `Line2D` instance and some details about how it should be displayed. Like the `Plotter` class, it defines a number of public methods to allow it to be easily updated, like `update_series()` or `update_colour()`. It also handles the downsampling of long series.
