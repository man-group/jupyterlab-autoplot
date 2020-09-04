# JupyterLab Autoplot - JupyterLab Component

This JupyterLab extension is one of the three components that make up the [JupyterLab Autoplot extension](../README.md).

- [Development](#development)
  - [Description of classes](#description-of-classes)
  - [Additional functionality](#additional-functionality)
- [Known issues](#known-issues)

## Development

```sh
# create a new conda environment
conda create -n jupyterlab-autoplot -c conda-forge jupyterlab ipywidgets nodejs
conda activate jupyterlab-autoplot

# clone the repo
git clone https://github.com/man-group/jupyterlab-autoplot.git

# navigate to the JupyterLab extension's directory
cd jupyterlab-autoplot/autoplot-display

# install dependencies
jlpm install

# build and install the extension
jlpm build
jupyter labextension install . --no-build

# launch JupyterLab, and watch for changes caused by 'jlpm build'
jupyter lab --watch
```

You will also need to install the IPython extension, as described [here](../ipython-extension#development).

### Description of classes

#### `AutoplotDisplayModel`

As described [here](../ipython-extension#autoplotdisplay), this class is linked to the IPython `AutoplotDisplay` class to control where the plot is displayed. This becomes the model for `AutoplotDisplayView`, which is rendered to display the plot tab.

#### `JupyterFrontEndPlugin`

An instance of this class is defined and exported from `index.ts` to register the extension. The `activate` property defines the function to run when JupyterLab is loaded, thus it contains commands to initialise the widget 'dictionaries', add event listeners and register the widgets. It also adds the `AutoplotButton` to the notebook toolbar.

#### `WidgetManager`

The logic in this class is necessary to ensure that:

- No more than one display panel exists for a single notebook;
- The display panels are 'reconnected' to the correct notebook on page refresh;
- Notebooks can be renamed without 'disconnecting' from the display panel.

Here 'reconnect' and 'disconnect' only refer to how the display panel is labelled and how it behaves when the notebooks are opened / closed. The actual connection between the IPython output widget and the JupyterLab extension is internal, but without the logic here there would be some counter-intuitive behaviour (e.g. panels labelled with the wrong name).

This class uses the custom `WidgetStateManager` class to save and restore its state between page refreshes using the browser's session storage.

### Additional functionality

#### Toasts

Custom DOM events with the name `'autoplot-toast'` can be used to display toast messages in JupyterLab. These events can be dispatched by the mpld3 plugins, the IPython extension or the JupyterLab extension itself. This was made possible by [jupyterlab_toastify](https://www.npmjs.com/package/jupyterlab_toastify).

#### Embedding images

As described [here](../README.md#saving-or-exporting-the-plot), it is possible to embed a static copy of the plot in the notebook using the mpld3 save image plugin. This is also triggered by a DOM event: when the `'autoplot-embed-image'` event is dispatched, the JupyterLab extension will look for image data in the session storage at the key `event.detail.sessionKey`. It will then add a markdown cell containing the image data to the current (not necessarily the original) notebook and render it.

## Known issues

- Opening or switching to a different notebook while the IPython extension is loading causes the wrong label to be shown on the display panel tab.
