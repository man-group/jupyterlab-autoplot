/**
 * A class defining an x axis tool tip.
 */
class XTooltip {
	private fig: mpld3.Figure;
	private ax: mpld3.Axes;

	private background: d3.Selection<SVGElement>;
	private label: d3.Selection<SVGElement>;

	private formatter: d3.time.Format;
	private xRange: number;

	private fontsize: number;
	private boxWidth: number;
	private readonly xPadding: number = 4;
	private readonly yPadding: number = 2;

	/**
	 * Create an `XTooltip` instance.
	 * @param fig the associated mpld3 Figure.
	 * @param ax the associated mpld3 Axes.
	 * @param fontsize fontsize of the tooltip label (in pixels).
	 */
	public constructor(fig: mpld3.Figure, ax: mpld3.Axes, fontsize: number) {
		this.fig = fig;
		this.ax = ax;

		this.fontsize = fontsize;
		const boxHeight = this.fontsize + this.yPadding * 2;
		this.boxWidth = 0;

		const yLoc = ax.position[1] + ax.height + boxHeight;

		this.background = this.fig.canvas
			.insert('rect')
			.attr('class', 'mpld3-time-series-tooltip-rect')
			.style('visibility', 'hidden')
			.attr('y', yLoc - boxHeight / 2)
			.attr('height', boxHeight)
			.style('fill', 'gray');

		this.label = this.fig.canvas
			.insert('text')
			.attr('class', 'mpld3-time-series-tooltip-text')
			.style('visibility', 'hidden')
			.style('text-anchor', 'middle')
			.attr('dominant-baseline', 'central')
			.style('font-size', this.fontsize)
			.style('fill', 'white')
			.attr('y', yLoc);

		this.xRange = getXRange(this.ax);
		this.formatter = getDateFormatter(this.xRange);
	}
	/**
	 * Update the formatter if the x range has changed. This function should be called before
	 * the formatter is used.
	 */
	private updateFormatter(): void {
		const newXRange = getXRange(this.ax);
		if (this.xRange !== newXRange) {
			this.xRange = newXRange;
			this.formatter = getDateFormatter(this.xRange);
		}
	}

	/**
	 * Set the 'visibility' of all the tooltip components to 'visible'.
	 */
	public show(): void {
		this.background.style('visibility', 'visible');
		this.label.style('visibility', 'visible');
	}

	/**
	 * Update the tooltip label text.
	 * @param value the value to display as the tooltip label.
	 */
	public setValue(value: Date): void {
		this.updateFormatter();
		this.label.text(this.formatter(value));

		// @ts-expect-error property 'getBBox' does not exist on type 'Node'
		// eslint-disable-next-line
		const textWidth: number = this.label.node().getBBox().width;

		this.boxWidth = textWidth + this.xPadding * 2;
		this.background.attr('width', this.boxWidth);
	}

	/**
	 * Update the tooltip location.
	 * @param xLoc the x coordinate (in pixels w.r.t. the canvas).
	 */
	public setLocation(xLoc: number): void {
		this.background.attr('x', xLoc - this.boxWidth / 2);
		this.label.attr('x', xLoc);
	}
}
