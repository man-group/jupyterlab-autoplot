mpld3.register_plugin('range_selector_buttons', RangeSelectorButtons);
RangeSelectorButtons.prototype = <mpld3.Plugin['prototype']>Object.create(mpld3.Plugin.prototype);
RangeSelectorButtons.prototype.constructor = RangeSelectorButtons;
RangeSelectorButtons.prototype.requiredProps = ['button_labels', 'line_ids', 'margin_right', 'fontsize'];

function RangeSelectorButtons(fig: mpld3.Figure, props: mpld3.Plugin['prototype']['props']) {
	// @ts-expect-error 'this' explicitly has type 'any'
	mpld3.Plugin.call(this, fig, props);
}

RangeSelectorButtons.prototype.draw = function () {
	// store axis and figure as local variables, needed to avoid binding "this"
	const fig = this.fig;
	const ax = fig.axes[0];

	// extract properties
	const buttonLabels = <string[]>this.props.button_labels;
	const lineIds = <string[]>this.props.line_ids;
	const marginRight = <number>this.props.margin_right;
	const fontsize = <number>this.props.fontsize;

	// create and place the buttons on the figure
	let x = 10;
	const y = 20;

	for (let i = 0; i < buttonLabels.length; i++) {
		// stop if out of space
		if (x >= fig.width - marginRight) {
			break;
		}

		// create button and set its position
		const button = new RangeButton(fig, ax, buttonLabels[i], fontsize, lineIds);
		button.setPosition(x, y);

		// increment x with padding
		x += button.buttonWidth + 3;
	}
};
