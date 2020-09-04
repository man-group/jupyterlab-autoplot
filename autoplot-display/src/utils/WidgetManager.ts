import { MainAreaWidget } from '@jupyterlab/apputils';
import { INotebookTracker } from '@jupyterlab/notebook';
import { NotebookPanel } from '@jupyterlab/notebook';
import { OutputArea } from '@jupyterlab/outputarea';
import { AutoplotPanel } from '../panel';
import { getCurrentNotebookPanel } from './notebook';

export type WidgetsByNotebook = Partial<Record<string, MainAreaWidget<AutoplotPanel>>>;
type Dictionary = Partial<Record<string, string>>;

/**
 * Class to save the current autoplot extension state and restore it between sessions.
 *
 * It is necessary to save and restore state to perform some form of validation on widgets
 * before they are built and added to the app. This prevents multiple display panels being
 * attached to a single notebook and ensures that panels are reconnected ot the correct
 * notebook when the page is refreshed.
 */
class WidgetStateManager {
	private readonly key = 'autoplot-display-state';
	private pathToWidget: Dictionary;

	/**
	 * Initialise a `WidgetStateManager` instance. Where possible, the instance's attributes will
	 * be restored from the previous session.
	 */
	public constructor() {
		const value = window.sessionStorage.getItem(this.key);
		this.pathToWidget = value ? <Dictionary>JSON.parse(value) : {};
	}

	/**
	 * Save the current state to storage. Should be called whenever the current state is changed.
	 */
	private save(): void {
		const value = JSON.stringify(this.pathToWidget);
		window.sessionStorage.setItem(this.key, value);
	}

	/**
	 * Return the path of the notebook associated with the given `modelId`.
	 *
	 * @param modelId the unique id of the widget model, as it was defined in Python.
	 * @returns the associated notebook's path, or `undefined` if not found.
	 */
	public getPath(modelId: string): string | undefined {
		for (const path of Object.keys(this.pathToWidget)) {
			if (this.pathToWidget[path] === modelId) {
				return path;
			}
		}
		return undefined;
	}

	/**
	 * Save the `modelId` with the associated notebook's `path`.
	 */
	public set(modelId: string, path: string): void {
		this.pathToWidget[path] = modelId;
		this.save();
	}

	/**
	 * Delete the state data associated with the given `path`, if it exists.
	 */
	public deleteByPath(path: string): void {
		const widgetId = this.pathToWidget[path];

		if (!widgetId) {
			return;
		}

		delete this.pathToWidget[path];
		this.save();
	}
}

/**
 * Class to manage the initialisation and rendering of new graph display panels.
 *
 * The logic in this class is necessary to ensure that: no more than one display panel exists
 * for a single notebook; the display panels are 'reconnected' to the correct notebook on page
 * refresh; notebooks can be renamed without 'disconnecting' from the display panel.
 *
 * Here 'reconnect' and 'disconnect' refer to how the display panel is labelled and how it
 * behaves when the notebooks are opened / closed. The actual connection between the IPython
 * component output widget and the JupyterLab extension is internal, but without the logic here there
 * would be some counter-intuitive behaviour (e.g. panels labelled with the wrong name).
 *
 * @see WidgetStateManager
 */
export class WidgetManager {
	private tracker: INotebookTracker;
	private widgetsByNotebook: WidgetsByNotebook;

	private state: WidgetStateManager;

	/**
	 * Initialise a `WidgetManager` instance.
	 *
	 * @param tracker the associated `INotebookTracker` instance.
	 * @param widgetsByNotebook an object with key = notebook path, value = `MainAreaWidget` instance.
	 */
	public constructor(tracker: INotebookTracker, widgetsByNotebook: WidgetsByNotebook) {
		this.tracker = tracker;
		this.widgetsByNotebook = widgetsByNotebook;

		this.state = new WidgetStateManager();
	}

	/**
	 * Dispose of the widget stored in `this.widgetsByNotebook` with the given notebook `path`.
	 */
	private disposeWidgetByPath(path: string): void {
		const widget = this.widgetsByNotebook[path];

		if (widget) {
			widget.dispose();
			delete this.widgetsByNotebook[path];
		}
	}

	/**
	 * Build and show a display panel for the given `outputArea`. The panel will be placed at the top of
	 * the main area, and the necessary event handlers will be connected to it.
	 *
	 * @param outputArea the output area to render in the display panel.
	 * @param notebook the current notebook panel.
	 * @param modelId the unique id of the widget model, as it was defined in Python.
	 * @param path the path of the notebook.
	 */
	private buildWidget(outputArea: OutputArea, notebook: NotebookPanel, modelId: string, path: string): void {
		// create the widget, and store the associated notebook's path in the metadata
		const content = new AutoplotPanel({ notebookPanel: notebook, outputArea: outputArea });
		const widget = new MainAreaWidget<AutoplotPanel>({ content });

		// add output widget as sibling
		notebook.context.addSibling(widget, { ref: notebook.id, mode: 'split-top' });

		// save widget
		this.widgetsByNotebook[path] = widget;

		// dispose widget if the parent notebook is closed
		notebook.content.disposed.connect(() => {
			widget.dispose();
			delete this.widgetsByNotebook[path];
			this.state.deleteByPath(path);
		});

		// update state if notebook path changed
		notebook.context.pathChanged.connect(() => {
			// update panel title
			widget.content.updateTitle();

			const newPath = notebook.context.path;
			// add new records
			this.state.set(modelId, newPath);
			this.widgetsByNotebook[newPath] = widget;

			// delete old records
			this.state.deleteByPath(path);
			delete this.widgetsByNotebook[path];
		});
	}

	/**
	 * Attempt to add a new display panel widget for the given `outputArea`
	 *
	 * If it is new, it will be attached to the current notebook and previously attached widgets
	 * will be disposed of. If it is not new (i.e. it is being restored from a previous session),
	 * it will be attached to the original notebook if it is still running.
	 *
	 * @param modelId the unique id of the widget model, as it was defined in Python.
	 * @param outputArea the output area to render in the display panel.
	 *
	 * @throws error with toast if neither an associated path nor the current notebook can be found.
	 */
	public addWidget(modelId: string, outputArea: OutputArea): void {
		const path = this.state.getPath(modelId);

		if (path) {
			// previous notebook path found -> check if running
			const notebook = this.tracker.find((n) => n.context.path == path);

			// dispose of notebook's old widget if exists
			this.disposeWidgetByPath(path);

			if (notebook) {
				// notebook with matching path is running -> test if open

				if (notebook.isAttached) {
					// notebook is open -> build and attach widget
					this.buildWidget(outputArea, notebook, modelId, path);
				} else {
					// notebook is running but not open -> define callback
					notebook.activated.connect(() => this.buildWidget(outputArea, notebook, modelId, path));
				}
			} else {
				// no notebook with matching path open -> dispose widget and delete record
				outputArea.dispose();
				this.state.deleteByPath(path);
				this.disposeWidgetByPath(path);
			}
		} else {
			// previous notebook not found -> consider attaching to current
			const current = getCurrentNotebookPanel(this.tracker);
			const curPath = current.context.path;

			// dispose of current's old widget if exists
			this.disposeWidgetByPath(curPath);

			// build and save new widget
			this.buildWidget(outputArea, current, modelId, curPath);
			this.state.set(modelId, curPath);
		}
	}
}
