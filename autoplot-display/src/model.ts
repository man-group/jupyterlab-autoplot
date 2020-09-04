/* eslint-disable @typescript-eslint/no-explicit-any */

import { ISerializers } from '@jupyter-widgets/base';
import { OutputModel } from '@jupyter-widgets/jupyterlab-manager/lib/output';
import { VERSION } from './version';

/**
 * Class defining the autoplot display output model, which is exported by the widget. This class
 * facilitates interaction with the Python extension, and as such it is important that the
 * `defaults` match those in Python.
 *
 * @extends OutputModel
 */
export class AutoplotDisplayModel extends OutputModel {
	public defaults(): any {
		// eslint-disable-next-line @typescript-eslint/no-unsafe-return
		return {
			...super.defaults(),
			_model_name: AutoplotDisplayModel.model_name,
			_model_module: AutoplotDisplayModel.model_module,
			_model_module_version: AutoplotDisplayModel.model_module_version,
			_view_name: AutoplotDisplayModel.view_name,
			_view_module: AutoplotDisplayModel.view_module,
			_view_module_version: AutoplotDisplayModel.view_module_version,
			title: VERSION.title,
		};
	}

	// eslint-disable-next-line  @typescript-eslint/explicit-module-boundary-types
	public initialize(attributes: any, options: any): void {
		super.initialize(attributes, options);
		void this.widget_manager.display_model(<any>undefined, <any>this, {});
	}

	public static serializers: ISerializers = {
		...OutputModel.serializers,
		// Add any extra serializers here
	};

	public static model_name = VERSION.modelName;
	public static model_module = VERSION.module;
	public static model_module_version = VERSION.version;

	public static view_name = VERSION.viewName; // Set to null if no view
	public static view_module = VERSION.module; // Set to null if no view
	public static view_module_version = VERSION.version;
}
