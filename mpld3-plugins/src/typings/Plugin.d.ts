import Figure = require('./Figure');

export = Plugin;

type PluginProps = Record<string, string | string[] | number | [number, number]>;

declare class PluginPrototype {
	public requiredProps: string[];
	public defaultProps: PluginProps;
	public props: PluginProps;

	public fig: Figure;

	public draw(): void;
}

declare class Plugin {
	public prototype: PluginPrototype;
	public call(self: string, fig: mpld3.Figure, props: PluginProps): void;
}
