import { NotebookPanel } from '@jupyterlab/notebook';
import { OutputArea } from '@jupyterlab/outputarea';

import { UUID } from '@lumino/coreutils';
import { Signal } from '@lumino/signaling';
import { Panel } from '@lumino/widgets';

/**
 * The namespace for the `AutoplotPanel` class statics.
 */
export namespace AutoplotPanel {
	/**
	 * An options object for creating an autoplot panel.
	 */
	export interface IOptions {
		/**
		 * The notebook panel associated with the autoplot display.
		 */
		notebookPanel: NotebookPanel;
		/**
		 * The `OutputArea` instance to render in the panel.
		 */
		outputArea: OutputArea;
	}
}

/**
 * Class defining the `Panel` in which the autoplot output area is rendered.
 * @extends Panel
 */
export class AutoplotPanel extends Panel {
	private notebookPanel: NotebookPanel | null;
	private outputArea: OutputArea | null;

	/**
	 * Initialise an `AutoplotPanel` instance. This initialises a `Panel` instance and sets
	 * its tab title, caption and icon. Once the `notebookPanel` is loaded, the `outputArea` will
	 * be rendered in the panel.
	 */
	public constructor(options: AutoplotPanel.IOptions) {
		super();

		this.notebookPanel = options.notebookPanel;
		this.outputArea = options.outputArea;

		this.id = `autoplot-display-${UUID.uuid4()}`;

		this.updateTitle();
		this.title.iconClass = 'jp-AutoplotIcon';

		this.addClass('autoplot-panel');

		// wait for the notebook to be loaded before adding the autoplot widget
		void this.notebookPanel.context.ready.then(() => {
			if (this.layout) {
				this.addWidget(this.outputArea!);
			}
		});
	}

	/**
	 * The file path of the associated notebook.
	 */
	public get path(): string {
		return this.notebookPanel!.context.path;
	}

	public dispose(): void {
		Signal.clearData(this);

		this.outputArea = null;
		this.notebookPanel = null;

		super.dispose();
	}

	/**
	 * Set the title of the panel to display some information about the associated notebook.
	 *
	 * Should be called if the notebook's path is changed.
	 */
	public updateTitle(): void {
		const label = this.notebookPanel!.title.label;
		this.title.label = `Autoplot - ${label}`;
		this.title.caption = `Notebook: ${label}\nPath: ${this.notebookPanel!.context.path}`;
	}
}
