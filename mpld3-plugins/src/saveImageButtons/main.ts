mpld3.register_plugin('save_image_buttons', SaveImageButtons);
SaveImageButtons.prototype = <mpld3.Plugin['prototype']>Object.create(mpld3.Plugin.prototype);
SaveImageButtons.prototype.constructor = SaveImageButtons;
SaveImageButtons.prototype.requiredProps = ['button_labels', 'fontsize'];

function SaveImageButtons(fig: mpld3.Figure, props: mpld3.Plugin['prototype']['props']) {
	// @ts-expect-error 'this' explicitly has type 'any'
	mpld3.Plugin.call(this, fig, props);
}

SaveImageButtons.prototype.draw = function () {
	// store axis and figure as local variables, needed to avoid binding "this"
	const fig = this.fig;
	const ax = fig.axes[0];

	// extract properties
	const buttonLabels = <string[]>this.props.button_labels;
	const fontsize = <number>this.props.fontsize;

	// generate and place the buttons on the figure
	let x = fig.width - 2;
	const y = 20;

	for (let i = 0; i < buttonLabels.length; i++) {
		// create button and set its position
		const button = new SaveButton(fig, ax, buttonLabels[i], fontsize);
		button.setPosition(x, y);

		// decrement x with padding
		x -= button.buttonWidth + 3;
	}
};
