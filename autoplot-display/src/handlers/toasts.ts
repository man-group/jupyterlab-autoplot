import { INotification } from 'jupyterlab_toastify';

/**
 * Interface defining the required properties of an autoplot toast event.
 *
 * @extends CustomEventInit
 */
export interface AutoplotToastEvent extends CustomEventInit {
	detail?: { message: string; type: string };
}

/**
 * Handle the autoplot toast event. Will show a toast, whose type and content is defined
 * in the event parameter. The duration of the toast depends on its type.
 *
 * @param event custom event containing toast data.
 * @throws if the `event.detail` is missing or invalid.
 */
export function toastHandler(event: AutoplotToastEvent): void {
	if (!event.detail) {
		throw new Error("'detail' is not defined on error toast event.");
	}

	switch (event.detail.type) {
		case 'error':
			void INotification.error(event.detail.message, { autoClose: 60000 });
			break;
		case 'warning':
			void INotification.warning(event.detail.message, { autoClose: 10000 });
			break;
		case 'success':
			void INotification.success(event.detail.message, { autoClose: 10000 });
			break;
		case 'info':
			void INotification.info(event.detail.message, { autoClose: 10000 });
			break;
		default:
			throw new Error(`Unrecognised message type '${event.detail.type}'`);
	}
}

/**
 * Error class that shows a toast message.
 *
 * @extends Error
 */
export class ErrorWithToast extends Error {
	/**
	 * Show an error toast with the given `message`, then throw an E]error.
	 */
	public constructor(message: string) {
		// show error toast
		document.dispatchEvent(
			new CustomEvent('autoplot-toast', {
				detail: {
					type: 'error',
					message,
				},
			})
		);

		// throw error
		super(message);
	}
}
