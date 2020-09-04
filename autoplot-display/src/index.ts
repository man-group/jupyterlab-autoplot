import { JupyterFrontEnd, JupyterFrontEndPlugin } from '@jupyterlab/application';
import { INotebookTracker } from '@jupyterlab/notebook';

import { IJupyterWidgetRegistry, WidgetModel, WidgetView } from '@jupyter-widgets/base';
import { OutputView } from '@jupyter-widgets/jupyterlab-manager/lib/output';

import { embedImage } from './handlers/embedImage';
import { toastHandler } from './handlers/toasts';
import { AutoplotDisplayModel } from './model';
import { AutoplotButton } from './toolbar';
import { WidgetsByNotebook, WidgetManager } from './utils/WidgetManager';
import { VERSION } from './version';

/**
 * Initialization data for the autoplot display extension.
 */
const extension: JupyterFrontEndPlugin<void> = {
	id: 'autoplot-display',
	autoStart: true,
	requires: [INotebookTracker, IJupyterWidgetRegistry],
	activate: (app: JupyterFrontEnd, tracker: INotebookTracker, registry: IJupyterWidgetRegistry) => {
		// key = associated notebook path, value = panel widget instance
		const widgetsByNotebook: WidgetsByNotebook = {};
		const widgetManager = new WidgetManager(tracker, widgetsByNotebook);

		// create the output view
		const AutoplotDisplayView = class extends OutputView {
			public model!: AutoplotDisplayModel;

			public render() {
				super.render();

				const uuid = <string>this.model.get('uuid');
				if (uuid) {
					widgetManager.addWidget(uuid, this._outputView);
				}
			}
		};

		// add event listener for embed image
		const embedImageHandler = (event: CustomEventInit<{ sessionKey: string }>): void => {
			embedImage(tracker, event);
		};
		document.addEventListener('autoplot-embed-image', embedImageHandler, false);

		// add event listener for popups
		document.addEventListener('autoplot-toast', toastHandler, false);

		// register the widget model and view to allow interaction with Python
		registry.registerWidget({
			name: VERSION.module,
			version: VERSION.version,
			exports: {
				AutoplotDisplayModel: <typeof WidgetModel>AutoplotDisplayModel,
				AutoplotDisplayView: <typeof WidgetView>AutoplotDisplayView,
			},
		});

		// register the toolbar button to attach it to notebooks
		const autoplotButton = new AutoplotButton();
		app.docRegistry.addWidgetExtension('Notebook', autoplotButton);
	},
};

export default extension;
