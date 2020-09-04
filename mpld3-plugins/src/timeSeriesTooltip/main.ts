mpld3.register_plugin('time_series_tooltip', TimeSeriesTooltip);
TimeSeriesTooltip.prototype = <mpld3.Plugin['prototype']>Object.create(mpld3.Plugin.prototype);
TimeSeriesTooltip.prototype.constructor = TimeSeriesTooltip;
TimeSeriesTooltip.prototype.requiredProps = ['line_ids', 'fontsize'];

function TimeSeriesTooltip(fig: mpld3.Figure, props: mpld3.Plugin['prototype']['props']) {
	// @ts-expect-error 'this' explicitly has type 'any'
	mpld3.Plugin.call(this, fig, props);
}

TimeSeriesTooltip.prototype.draw = function () {
	// store axis and figure as local variables, needed to avoid binding "this"
	const fig = this.fig;
	const ax = fig.axes[0];

	// generate tooltip objects, which will be modified as the mouse moves
	const xTooltip = new XTooltip(fig, ax, <number>this.props.fontsize);
	const yTooltips = new YTooltips(fig, ax, <string[]>this.props.line_ids, <number>this.props.fontsize);

	/**
	 * Update the x and y tooltips given a location. If the location is off the axes, will be set
	 * to within the axes.
	 * @param xLoc the x coordinate (in pixels w.r.t. the canvas).
	 */
	function setTooltipLocation(xLoc: number) {
		// limit xLoc to within axes
		xLoc = Math.min(ax.position[0] + ax.width, Math.max(ax.position[0], xLoc));

		// calculate corresponding x value
		const xValue = xLocationToValue(xLoc, ax);

		xTooltip.setValue(xValue);
		xTooltip.setLocation(xLoc);
		yTooltips.setLocationsAndValues(xValue);
	}

	/**
	 * Set the tooltip position to the current mouse location, if it is within axes' vertical range
	 */
	function updateTooltips() {
		const [xLoc, yLoc] = d3.mouse(fig.canvas.node()!);

		if (ax.position[1] <= yLoc && yLoc <= ax.position[1] + ax.height) {
			setTooltipLocation(xLoc);
		}
	}

	// show and initialise the tooltips to the final value(s)
	xTooltip.show();
	setTooltipLocation(Number.MAX_SAFE_INTEGER);

	// set the tooltips to update on click and click-and-drag
	fig.canvas.on('mousedown', () => {
		updateTooltips();
		fig.canvas.on('mousemove', updateTooltips);
		fig.canvas.on('mouseup', () => {
			fig.canvas.on('mousemove', () => null).on('mouseup', () => null);
		});

		// prevent default mousedown behaviour which may select text
		//@ts-expect-error
		// eslint-disable-next-line @typescript-eslint/no-unsafe-call
		d3.event.preventDefault();
	});
};
