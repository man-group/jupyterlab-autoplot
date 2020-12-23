# JupyterLab Autoplot

![Autoplot demo](/images/demo.gif)

The JupyterLab Autoplot extension facilitates the quick and easy generation of interactive time series visualisations in JupyterLab. When loaded, the extension will watch a notebook's namespace for datetime-indexed, real-valued pandas series or dataframes and update the plot in real time as these variables are modified.

- [Installation](#installation)
- [Usage](#usage)
  - [Getting started](#getting-started)
  - [Interacting with the plot](#interacting-with-the-plot)
  - [Saving or exporting the plot](#saving-or-exporting-the-plot)
  - [Modifying the plot / traces](#modifying-the-plot--traces)
  - [Interacting with dtale](#interacting-with-dtale)
- [Development](#development)
- [Dependencies](#dependencies)
- [Acknowledgements](#acknowledgements)
- [License](#license)

## Installation

Both the IPython extension and the Jupyterlab extension need to be installed:

```sh
pip install jupyterlab-autoplot
jupyter labextension install @jupyter-widgets/jupyterlab-manager
jupyter labextension install @jupyter-widgets/autoplot-display
```

## Usage

### Getting started

To load the IPython component of the extension, run the magic command `%reload_ext autoplot` in a cell. It is possible to insert a cell at the top of the notebook containing this command (and a few instructions) by pressing the <img src="/images/button.png" alt="Autoplot Button" width=17> button in the notebook toolbar.

By default, the plotting backend will be selected. In order to switch to the dtale backend, you will need to run the following magic command: `%autoplot -v dtale`. Dtale gives you a tabular view over pandas dataframes and series. Furthermore, when you have many rows, dtale will allow you to scroll down through all of them, which is not usually possible with the usual pandas dataframe view in jupyter.

When the extension is loaded, any **pandas dataframe** and **pandas series** will be processed after the execution of each cell. The visualisation backend will be updated when variables are added, modified or deleted, which is achieved by watching changes in the shell namespace and updating the view accordingly. Besides non-pandas variables, any variable prefixed with **_** will also be ignored.

The **graph** view will only display **datetime-indexed, real-valued pandas series or dataframes**, whereas the **dtale** view will display any **dataframe and series**.

It is possible to change the properties of the graph and dtale and manage how / which traces and dataframes are displayed with [magic commands](#modifying-the-plot--traces).

To quickly see how the extension works, run the following in a new notebook in JupyterLab (make sure you choose a kernel that supports Python 3.6 or later).

```py
%reload_ext autoplot

import pandas as pd

dti = pd.date_range("2020-01-01", periods=50, freq="d")
ts = pd.Series(range(len(dti)), index=dti)
```

### Interacting with the plot

The plots are generated using [matplotlib](https://matplotlib.org/) and are made interactive with [mpld3](https://mpld3.github.io/). A collection of custom mpld3 plugins have been created specifically for this project:

- **Interactive Legend** - adds an interactive legend below the figure. Each legend item can be clicked to show/hide the associated line.
- **Range Selector Buttons** - adds x axis range selector buttons. Only buttons relevant to the data will be shown.
- **Save Image Buttons** - adds buttons to save the plot as an image (see [below](#saving-or-exporting-the-plot)).
- **Time Series Tooltip** - adds hover information, which can be controlled by clicking and dragging.

These plugins are documented in more detail [here](mpld3-plugins/README.md). Apart from the save image buttons, these plugins can be used with any mpld3 plot, not just the ones created in this extension.

### Saving or exporting the plot

The `svg` and `png` buttons in the top right of the plot window can be used to embed a static copy of the plot in the *current* notebook. A new markdown cell containing the image data will be added below the active cell. This cell can be moved around or deleted like any other notebook cell. Once the image has been embedded, it becomes part of the notebook, and will be saved, printed or exported with it. Just remember to update it if you change the plot!

It is easy to download or copy the embedded image by right-clicking it (you may need to hold SHIFT when you do) then selecting the suitable option.

### Modifying the plot / traces

It is possible to change the properties of the plot and manage how / which traces are displayed with the magic command `%autoplot`. This command takes a number of optional arguments, which are detailed below.

If an invalid value is given to one of the parameters, an error message will be displayed and that change will not be applied. However, other changes with valid parameters may still be applied.

The same argument can be used multiple times in a line, although if the same property is modified more than once the last value will be used (e.g. if setting plot width):

```py
%autoplot --rename series_1 A --rename series_2 B             # -> Legend with names "A", "B"
%autoplot --show series_1 --show series_2 --ignore series_1   # -> series_2 shown, series_1 hidden
%autoplot --width 7 --width 10                                # -> plot width set to 10
```

### Interacting with dtale

Use `%autoplot -v dtale` to switch to dtale view. From that point on, any **pandas dataframes and series** you have in your notebook will be automatically displayed. You can open the dtale menu and switch dataframes by clicking in instances, that is how dtale calls each table.

When in dtale mode, the display will only be refreshed if you make a change to the dataframe that is currently selected. Changes to other dataframes will be reflected in dtale, but the view will not change. When a new dataframe is created, the view will automatically change to that.

You can control what is going to be displayed by naming convention &ndash; variables with a leading **_** will not be displayed. Alternatively, there are a few magic commands that can help:

After running

```py
%autoplot --freeze
```

all new variables will be ignored. Running

```py
%autoplot --defrost
```

will revert it, but variables defined during the frozen period will still be ignored, unless

```py
%autoplot --show <variable name>
```

is called. If you want to ignore a single variable, then

```py
%autoplot --ignore <variable name>
```

can be used. That can also be reverted with `--show`.

Further documentation on all dtale features can be found in [dtale's github readme](https://github.com/man-group/dtale/blob/master/README.md).

#### Magic commands

##### `-w <float>`, `--width <float>`

Set the width of the plot in inches. If a number outside the range of valid values is given, the width will be set to the nearest boundary. The default is 13.

This has no effect when in dtale mode.

##### `-h <float>`, `--height <float>`

Set the height of the plot in inches. If a number outside the range of valid values is given, the height will be set to the nearest boundary. The default is 4.

This has no effect when in dtale mode.

##### `-f`, `--freeze`

Temporarily prevent new series being added to the plot, while continuing to update existing ones. This can be turned off with `--defrost`,

It is possible to override this for any particular variable with `--show`. Using these two commands together can be useful if you want to define a lot of time series variables, but only plot a few of them.

##### `-d`, `--defrost`

Start adding new series to the plot again, undoing `--freeze`. Series defined while the plotter was 'frozen' need to be manually shown with `--show`.

##### `-r <str> <str>`, `--rename <str> <str>`

Change the legend label of the given variable. The first parameter is the variable name *as it is defined in Python* (even if the label has previously been changed), and the second is the new label. If the legend label does not contain any whitespace or special characters, it is not necessary to surround it in quotes. E.g.:

```py
%autoplot -r my_series Prices
%autoplot -r my_series "A nice name!"
```

It is also possible to rename dataframes / dataframe columns like this. If a dataframe name is given, all associated traces will be renamed to contain the new dataframe name. E.g.:

```py
df = pd.DataFrame(..., columns=["A", "B"])

%autoplot -r "df (A)" Prices   # -> 'Prices', 'df (B)'
%autoplot -r df Prices         # -> 'Prices (A)', 'Prices (B)'
```

This has no effect when in dtale mode.

##### `-i <str> ...`, `--ignore <str> ...`

Ignore the named variable(s) and hide them from the plot. If a dataframe name is given, all the associated columns will be hidden. E.g.:

```py
%autoplot -i series_1
%autoplot -i series_1 series_2 df
```

Can be undone with `--show`.

##### `-s <str> ...`, `--show <str> ...`

Show the named variable(s) on the plot. If a dataframe name is given, all the associated columns will be shown. E.g.:

```py
%autoplot -i series_1
%autoplot -i series_1 series_2 df
```

This can be used to undo `--ignore`, or to show the traces of deleted series, dataframes or dataframe columns (note that they are not actually restored to the notebook's namespace). It cannot be used to show variables with names prefixed with a "_", which are hidden by default.

##### `-c <str> <str>`, `--colour <str> <str>`

Change the colour of the named variable on the plot. The first parameter is the variable name *as it is defined in Python*, and the second is a [valid matplotlib colour](https://matplotlib.org/3.1.0/gallery/color/named_colors.html) or hex code. E.g.:

```py
%autoplot -c my_series "tab:blue"
%autoplot -c my_series "#ff0000"
%autoplot -c "df (A)" forestgreen
```

Note that the first argument cannot be a dataframe name, but must be the name of a series or the full name of a dataframe column.

This has no effect when in dtale mode.

##### `-y <str>`, `--ylabel <str>`

Set the y axis label. Set to `""` to remove.

##### `--sample <int>`

Set the maximum length of all the series, above which they will be downsampled (i.e. only this many evenly spaced points will be plotted). The first and last points will always be plotted. By default, series are downsampled to 1000 points, which increases the speed of plotting and the performance of the tooltips.

Set to `0` to disable this feature.

This has no effect when in dtale mode.

#### `-v (graph|dtale)`, `--view (graph|dtale)`

Switches between graph and dtale views. Once a view is selected, all the variables that were already defined (that is, variables that were set during the execution of a cell) will be processed at once. Future switches will not reset the view's state. If you want to completely reset a view, the kernel will need to be restarted.

Some of the magic commands may not be implemented by all views.

## Development

This project is comprised of three components:

- [JupyterLab extension](autoplot-display#jupyterlab-autoplot---jupyterlab-component) - handles the display of the plot window and adds some features to the Jupyter GUI;
- [IPython extension](ipython-extension#jupyterlab-autoplot---ipython-component) - handles the logic controlling which variable to plot, manages how the plot is created and displayed, and defines the magic commands;
- [Custom mpld3 plugins](mpld3-plugins#mpld3-plugins) - extends the interactivity of the plots.

A diagram showing roughly how the different components interact is shown below. The 'communication chain' is started by a notebook cell being executed, and finishes with the plot being displayed and/or updated. Detailed information about how these components function and interact can be found in their READMEs, as can development instructions.

<p align="center">
    <img src="/images/interaction.png" alt="Autoplot interaction" width=650>
</p>

## Dependencies

JupyterLab Component:

- [JupyterLab](https://jupyter.org/) (v1.0.0 or compatible) - *BSD 3-Clause*
- [jupyterlab_toastify](https://www.npmjs.com/package/jupyterlab_toastify) - *BSD 3-Clause*

IPython Component:

- [IPython](https://ipython.org/) - *BSD 3-Clause*
- [numpy](https://numpy.org/) - *BSD 3-Clause*
- [pandas](https://pandas.pydata.org/) - *BSD 3-Clause*
- [matplotlib](https://matplotlib.org/) - *PSF-based License*
- [mpld3](https://mpld3.github.io/) (also the plugins component) - *BSD 3-Clause*
- [dtale](https://github.com/man-group/dtale) - *LGPLv2*

## Acknowledgements

Contributors:

- [Matt Moore](https://github.com/m-c-moore)
- [Rafael Cunha de Almeida](https://github.com/aflag)

## License

JupyterLab Autoplot is licensed under the BSD 3-Clause License, a copy of which is included in [LICENSE](LICENSE).
