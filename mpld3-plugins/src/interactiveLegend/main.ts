mpld3.register_plugin('interactive_legend', InteractiveLegend);
InteractiveLegend.prototype = <mpld3.Plugin['prototype']>Object.create(mpld3.Plugin.prototype);
InteractiveLegend.prototype.constructor = InteractiveLegend;
InteractiveLegend.prototype.requiredProps = ['line_ids', 'labels', 'alpha_visible', 'alpha_hidden', 'fontsize'];

function InteractiveLegend(fig: mpld3.Figure, props: mpld3.Plugin['prototype']['props']) {
	// @ts-expect-error 'this' explicitly has type 'any'
	mpld3.Plugin.call(this, fig, props);
}

InteractiveLegend.prototype.draw = function () {
	// store axis and figure as local variables, needed to avoid binding "this"
	const fig = this.fig;
	const ax = fig.axes[0];

	// extract properties
	const alphaVisible = <number>this.props.alpha_visible;
	const alphaHidden = <number>this.props.alpha_hidden;
	const lineIds = <string[]>this.props.line_ids;
	const fontsize = <number>this.props.fontsize;
	const labels = <string[]>this.props.labels;

	// generate legend items
	const legendItems: LegendItem[] = [];

	for (let i = 0; i < labels.length; i++) {
		const label = labels[i];
		const line = mpld3.get_element(lineIds[i], fig);
		const hidden = isHidden(label); // check if variable was previously hidden

		const legendItem = new LegendItem(label, line, hidden, alphaVisible, alphaHidden);
		legendItems.push(legendItem);
	}

	// add a legend to the canvas of the figure
	new Legend(fig, ax, legendItems, fontsize, onClickItem);
};
