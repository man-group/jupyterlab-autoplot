/**
 * A class defining a single range selector button.
 */
class RangeButton {
	private fig: mpld3.Figure;
	private ax: mpld3.Axes;
	private label: string;
	private fontsize: number;

	private lineIds?: string[];

	private number?: number;
	private unit?: string;

	private box: d3.Selection<SVGElement>;
	private text: d3.Selection<SVGElement>;

	public buttonHeight: number;
	public buttonWidth: number;

	private readonly xPadding: number = 6;
	private readonly yPadding: number = 4;

	/**
	 * Initialise a `Button` instance.
	 * @param fig the associated mpld3 Figure.
	 * @param ax the associated mpld3 Axes.
	 * @param label the label of the button as it should be displayed. Must either be of the form
	 * "<number><unit>" (e.g. "3m", "10d", "2y"), or one of ["ytd", "fit", "reset"]. Valid units are
	 * "s" = seconds, "M" = minutes, "h" = hours, "d" = days, "w" = weeks, "m" = months, "y" = years.
	 *
	 * Validation of the label value should be done prior to passing it to this constructor.
	 * @param fontsize fontsize of the button label (in pixels).
	 * @param lineIds list of line ids, used by the "fit" button.
	 */
	public constructor(fig: mpld3.Figure, ax: mpld3.Axes, label: string, fontsize: number, lineIds?: string[]) {
		this.fig = fig;
		this.ax = ax;
		this.label = label;
		this.fontsize = fontsize;
		this.lineIds = lineIds;

		// no validation of the label is performed here as it is should all have been done in python.
		this.number = Number.parseInt(label.substr(0, label.length - 1));

		if (this.number) {
			// valid number, so extract unit
			this.unit = label.charAt(label.length - 1);
		} else {
			// invalid number, set unit to label (i.e. 'ytd', 'fit', 'reset')
			this.unit = label;
		}

		// change colour of "fit" and "reset" buttons
		let bgColour: string;
		switch (this.unit) {
			case 'fit':
				bgColour = '#bbe5bb';
				break;
			case 'reset':
				bgColour = '#e5bbbb';
				break;
			default:
				bgColour = '#e5e5e5';
		}

		this.box = fig.canvas
			.append('rect')
			.style('fill', bgColour)
			.attr('class', 'mpld3-range-selector-button-rect')
			.on('click', this.onClick.bind(this));

		this.text = fig.canvas
			.append('text')
			.style('fontsize', fontsize)
			.attr('class', 'mpld3-range-selector-button-text')
			.attr('dominant-baseline', 'central')
			.attr('text-anchor', 'middle')
			.text(this.label)
			.on('click', this.onClick.bind(this));

		// box must be defined before text (so it appears above), but its width
		// can only be calculated once the text has been generated

		// @ts-expect-error property 'getBBox' does not exist on type 'Node'
		// eslint-disable-next-line
		const textWidth: number = this.text.node().getBBox().width;

		this.buttonHeight = this.fontsize + this.yPadding * 2;
		this.buttonWidth = textWidth + this.xPadding * 2;

		this.box
			.attr('height', this.buttonHeight)
			.attr('width', this.buttonWidth)
			.attr('rx', this.buttonHeight / 6);
	}

	/**
	 * Set the location of the button on the figure.
	 * @param xLoc the x coordinate (in pixels w.r.t. the canvas).
	 * @param yLoc the y coordinate (in pixels w.r.t. the canvas).
	 */
	public setPosition(xLoc: number, yLoc: number): void {
		this.box.attr('x', xLoc).attr('y', yLoc - this.buttonHeight / 2);
		this.text.attr('x', xLoc + this.buttonWidth / 2).attr('y', yLoc);
	}

	/**
	 * Event handler for the click event. Sets the x (and maybe y) limits of the axes based on the
	 * button type / values.
	 */
	public onClick(): void {
		let xLim: [Date, Date] | undefined;
		let yLim: [number, number] | undefined;

		const duration = 200; // duration of transition in ms

		switch (this.unit) {
			case 'reset':
				// set the x and y limits to original domain
				this.ax.reset(duration, true);
				return;

			case 'fit':
				// fit the x and y limits to the visible domain
				[xLim, yLim] = getVisibleDomain(this.fig, this.lineIds);
				break;

			default:
				// calculate lower x limit, do not change upper x limit or y limits
				const xMax = this.ax.xdom.invert(this.ax.width);
				const newXMin = new Date(xMax.valueOf());

				if (this.unit === 'ytd') {
					// set lower limit month to January and day of month to 1
					newXMin.setDate(1);
					newXMin.setMonth(0);
				} else {
					// calculate lower limit based on desired width
					setLowerLimit(newXMin, xMax, this.number!, this.unit!);
				}

				xLim = [newXMin, xMax];
		}

		this.ax.set_axlim(xLim, yLim, duration, true);
	}
}
