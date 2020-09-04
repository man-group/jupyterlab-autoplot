import { ToolbarButton } from '@jupyterlab/apputils';
import { DocumentRegistry } from '@jupyterlab/docregistry';
import { NotebookPanel, NotebookActions, INotebookModel } from '@jupyterlab/notebook';

import { IDisposable } from '@phosphor/disposable';

/**
 * Content of the new cell that will be added to the top of the notebook.
 */
const CELL_TEXT = `# This will load the JupyterLab Autoplot extension. Run '%autoplot?' for more information.
%reload_ext autoplot`;

/**
 * Class defining the 'Add autoplot' button on the notebook toolbar.
 *
 * An instance of this class should be added to the app using
 * `app.docRegistry.addWidgetExtension('Notebook', <instance>);`
 *
 * @extends IWidgetExtension
 */
export class AutoplotButton implements DocumentRegistry.IWidgetExtension<NotebookPanel, INotebookModel> {
	public createNew(notebookPanel: NotebookPanel, context: DocumentRegistry.IContext<INotebookModel>): IDisposable {
		// function to be called when the button is clicked. Adds a new cell to the top of the notebook.
		const onClick = () => {
			const notebook = notebookPanel.content;

			notebook.activeCellIndex = 0;
			NotebookActions.insertAbove(notebook);

			notebook.activeCell!.model.value.text = CELL_TEXT;
		};

		// define the button
		const className = 'autoplotButton';

		const button = new ToolbarButton({
			className,
			iconClassName: 'fa fa-line-chart',
			onClick,
			tooltip: 'Add an autoplot display panel to this notebook',
		});

		// try to insert the button after the 'restart kernel' button. If it is not found, add to the start
		if (!notebookPanel.toolbar.insertAfter('restart', className, button)) {
			notebookPanel.toolbar.insertItem(0, className, button);
		}

		return button;
	}
}
