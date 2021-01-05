import { JupyterFrontEnd, JupyterFrontEndPlugin } from '@jupyterlab/application';
import { INotebookTracker } from '@jupyterlab/notebook';

import { IJupyterWidgetRegistry, WidgetModel, WidgetView } from '@jupyter-widgets/base';
import { OutputView } from '@jupyter-widgets/jupyterlab-manager/lib/output';

import { embedImage } from './handlers/embedImage';
import { toastHandler } from './handlers/toasts';
import { AutoplotDisplayModel } from './model';
import {AutoplotButton, DtaleButton} from './toolbar';
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

		// fix issue where the dtale iframe would prevent panel resizing.
		window.addEventListener(
			'mousedown',
			(evt) => {
				if (['p-SplitPanel-handle', 'p-DockPanel-handle'].includes((<HTMLElement>evt.target).className)) {
					for (const iframe of document.getElementsByTagName('iframe')) {
						iframe.style.pointerEvents = 'none';
					}
				}
			},
			true
		);
		window.addEventListener(
			'mouseup',
			(evt) => {
				for (const iframe of document.getElementsByTagName('iframe')) {
					iframe.style.pointerEvents = 'auto';
				}
			},
			true
		);
		// create the output view
		const AutoplotDisplayView = class extends OutputView {
			public model!: AutoplotDisplayModel;
			private currentIframe: HTMLIFrameElement | undefined;

			public render() {
				super.render();

				const uuid = <string>this.model.get('uuid');
				// we have no control over when the iframe (dtale) will be created, so that's why we need to observe
				// all the mutations contantly.
				const observer = new MutationObserver((mutationList, observer) => {
					const iframe = this._outputView.node.getElementsByTagName('iframe')[0];
					if (iframe && iframe != this.currentIframe) {
						this.currentIframe = iframe;
						window.addEventListener(
							'message',
							(event) => {
								if (event.source == iframe.contentWindow) {
									// eslint-disable-next-line @typescript-eslint/no-unsafe-member-access
									this.model.set('data_id', event.data.data_id);
									this.model.save_changes();
								}
							},
							false
						);
					}
				});
				observer.observe(this._outputView.node, { childList: true, subtree: true });
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
		const dtaleButton = new DtaleButton();
		app.docRegistry.addWidgetExtension('Notebook', dtaleButton);
	},
};

export default extension;
