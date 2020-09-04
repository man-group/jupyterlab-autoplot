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

#### `CellEventHandler`

This class defines the handlers for the [IPython Events](https://ipython.readthedocs.io/en/stable/config/callbacks.htm). When a cell is successfully executed, the class instance will scan the variables in the notebook's namespace, and look for 'plottable' ones. It defines a dictionary of series names to their values, and one of dataframe names to the set of series names that were created from its columns.

When a series is added, modified or deleted, the dictionaries will be updated and the appropriate calls will be made to the `Plotter` instance.

#### `Plotter`

This class manages the collection of `Trace` class instances and handles the graph plotting. It has a number of public methods like `update_trace_series()`, `update_trace_colour()` etc. which are used by the `CellEventHandler` or `AutoplotMagic` classes to modify the plot and/or traces.

The final action in the `post_run_cell()` event handler is to call `plotter.plot()`, which initialises a matplotlib figure and axes, adds the defined traces to it and styles the figure.

The `Trace` class stores a matplotlib `Line2D` instance and some details about how it should be displayed. Like the `Plotter` class, it defines a number of public methods to allow it to be easily updated, like `update_series()` or `update_colour()`. It also handles the downsampling of long series.

#### `AutoplotMagic`

This class extends [`IPython.core.magic.Magics`](https://ipython.readthedocs.io/en/stable/api/generated/IPython.core.magic.html#IPython.core.magic.Magics), and defines the magic commands described [here](../README.md#modifying-the-plot--traces). Via various utility functions, this class makes calls to the `Plotter` to update specific trace properties and/or the style of the plot.

#### `AutoplotDisplay`

This class extends [`ipywidgets.Output`](https://ipywidgets.readthedocs.io/en/latest/examples/Output%20Widget.html), and defines the output area in which the graph is plotted. By matching the attributes `_model_name`, `_model_module_version` etc. with the equivalents in the JupyterLab extension class `AutoplotDisplayModel`, the two become linked and the output captured by the IPython component will be displayed wherever the JupyterLab component is rendered.

#### `Toast`

This class defines some methods to dispatch DOM events that trigger toast notifications in the JupyterLab extension. These toasts change colour depending on their type, which can be one of 'error', 'warning', 'success' or 'info'.
