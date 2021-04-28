import { NotebookActions, INotebookTracker } from '@jupyterlab/notebook';

import { ErrorWithToast } from './toasts';
import { getCurrentNotebookPanel } from '../utils/notebook';

/**
 * Embed the most recently saved image in the given `notebook`.
 *
 * It will be placed below the first code cell containing the command to load the autoplot extension,
 * or at the top if no such cell can be found. The image data is written to a new markdown cell, which
 * will be immediately rendered.
 *
 * @param tracker the associated `INotebookTracker` instance.
 * @param event the custom event that triggered the embed image function. `event.detail.sessionKey`
 * defines the session storage key for the image data.
 *
 * @throws error with toast if the saved image data could not be found.
 */
export function embedImage(tracker: INotebookTracker, event: CustomEventInit<{ sessionKey: string }>): void {
	// get the current notebook, NOT the associated notebook. This allows the user to embed
	// the graph in any notebook by clicking on it first
	const notebook = getCurrentNotebookPanel(tracker).content;

	// retrieve the image data url from storage
	const dataUrl = sessionStorage.getItem(event.detail!.sessionKey);

	if (!dataUrl) {
		throw new ErrorWithToast(`Could not find image data at '${event.detail!.sessionKey}'`);
	}

	const imageAlt = `Autoplot for ${notebook.title.label}`;

	// add image cell below the active cell and set its content
	NotebookActions.insertBelow(notebook);
	NotebookActions.changeCellType(notebook, 'markdown');

	const cell = tracker.activeCell;
	cell!.model.value.text = `![${imageAlt}](${dataUrl})`;

	// run the cell to render it
	void NotebookActions.run(notebook);

	// show toast
	document.dispatchEvent(
		new CustomEvent('autoplot-toast', {
			detail: {
				type: 'info',
				message: `Image embedded in '${notebook.title.label}'.`,
			},
		})
	);
}
