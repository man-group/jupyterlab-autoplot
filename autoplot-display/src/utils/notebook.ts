import { INotebookTracker, NotebookPanel } from '@jupyterlab/notebook';

import { ErrorWithToast } from '../handlers/toasts';

/**
 * Return the current notebook panel, `tracker.currentWidget`.
 *
 * @throws error with toast if the current notebook is not found.
 */
export function getCurrentNotebookPanel(tracker: INotebookTracker): NotebookPanel {
	const current = tracker.currentWidget;
	if (!current) {
		throw new ErrorWithToast('Could not find current notebook');
	}
	return current;
}
