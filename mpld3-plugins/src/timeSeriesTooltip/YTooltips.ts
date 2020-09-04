/**
 * A class used to manage a collection of `YTooltip` instances.
 */
class YTooltips {
	private fig: mpld3.Figure;
	private ax: mpld3.Axes;

	private tooltips: Record<string, YTooltip>;
	/**
	 * Create a `YTooltips` instance.
	 * @param fig the associated mpld3 Figure.
	 * @param ax the associated mpld3 Axes.
	 * @param lineIds list of ids for the lines to create tooltips for.
	 * @param fontsize fontsize of the tooltip label (in pixels).
	 */
	public constructor(fig: mpld3.Figure, ax: mpld3.Axes, lineIds: string[], fontsize: number) {
		this.fig = fig;
		this.ax = ax;

		// create map of line ids to YTooltip instances
		this.tooltips = lineIds.reduce(
			(obj, lineId) => ({ ...obj, [lineId]: new YTooltip(fig, ax, lineId, fontsize) }),
			{}
		);
	}

	/**
	 * Update the tooltip locations and label texts.
	 * @param xValue the x value associated with this coordinate. Used to calculate the corresponding
	 *  x and y value for each line.
	 */
	public setLocationsAndValues(xValue: Date) {
		const lineIdLocations: [string, number, number][] = []; // [lineId, xLoc, yLoc]

		Object.keys(this.tooltips).forEach((lineId) => {
			const line = getLine(lineId, this.fig);

			// hide tooltip if line is hidden by legend
			if (line.props.isHidden) {
				this.tooltips[lineId].hide();
				return;
			}

			// recalculate xLoc based on the closest index, causing the dots to snap to defined points
			// note that if the index is just out of range, the first / last value will be returned
			const result = getClosestIndex(xValue, line);

			if (!result) {
				this.tooltips[lineId].hide();
				return;
			}

			const { closestIndex, closestX } = result;

			// hide if the closest x value is off the edge of the graph
			const xLoc = xValueToLocation(closestX, this.ax);

			if (xLoc < 0 + this.ax.position[0] || xLoc > this.ax.width + this.ax.position[0]) {
				this.tooltips[lineId].hide();
				return;
			}

			const yValue = getY(line, closestIndex);

			// hide if yValue is outside vertical range of the axis. Use ydom.invert to get the
			// current y range, as props.ylim only gives the initial
			if (
				!Number.isFinite(yValue) ||
				yValue! < this.ax.ydom.invert(this.ax.height) ||
				yValue! > this.ax.ydom.invert(0)
			) {
				this.tooltips[lineId].hide();
				return;
			}

			// show the tooltip and set its location
			const yLoc = yValueToLocation(yValue!, this.ax);

			this.tooltips[lineId].show();
			this.tooltips[lineId].setValue(yValue!);

			// store the location
			lineIdLocations.push([lineId, xLoc, yLoc]);
		});

		let prevYLoc = Number.MIN_SAFE_INTEGER;

		// loop through line ids again, this time sorted by yLoc (top to bottom). This allows the
		// logic in the // setLocation function to be simplified, as the labels only ever need to
		// be moved below the previous one
		lineIdLocations
			.sort((a, b) => a[2] - b[2])
			.forEach((tup) => {
				prevYLoc = this.tooltips[tup[0]].setLocation(tup[1], tup[2], prevYLoc);
			});
	}
}

/**
 * A class defining a y axis tool tip.
 */
class YTooltip {
	private label: d3.Selection<SVGElement>;
	private circle: d3.Selection<SVGElement>;
	private background: d3.Selection<SVGElement>;

	private fontsize: number;
	private boxHeight: number;
	private readonly xPadding: number = 2;
	private readonly yPadding: number = 2;

	/**
	 * Create a `YTooltip` instance.
	 * @param fig the associated mpld3 Figure.
	 * @param ax the associated mpld3 Axes.
	 * @param lineId id of the line associated with the tooltip.
	 * @param fontsize fontsize of the tooltip label (in pixels).
	 */
	public constructor(fig: mpld3.Figure, ax: mpld3.Axes, lineId: string, fontsize: number) {
		const xLoc = ax.position[0] + ax.width + 3;

		this.fontsize = fontsize;
		this.boxHeight = this.fontsize + this.yPadding * 2;

		this.background = fig.canvas
			.insert('rect')
			.attr('class', 'mpld3-time-series-tooltip-rect')
			.style('visibility', 'hidden')
			.attr('x', xLoc)
			.attr('height', this.boxHeight)
			.style('fill', getLine(lineId, fig).props.edgecolor);

		this.label = fig.canvas
			.insert('text')
			.attr('class', 'mpld3-time-series-tooltip-text')
			.style('visibility', 'hidden')
			.style('text-anchor', 'left')
			.attr('dominant-baseline', 'central')
			.style('font-size', this.fontsize)
			.style('fill', 'white')
			.attr('x', xLoc + this.xPadding);

		this.circle = fig.canvas
			.insert('circle')
			.attr('class', 'mpld3-time-series-tooltip-circle')
			.style('visibility', 'hidden')
			.attr('r', 3)
			.attr('pointer-events', 'none')
			.style('fill', getLine(lineId, fig).props.edgecolor);
	}
	/**
	 * Set the 'visibility' of all the tooltip components to 'visible'.
	 */
	public show(): void {
		this.background.style('visibility', 'visible');
		this.label.style('visibility', 'visible');
		this.circle.style('visibility', 'visible');
	}

	/**
	 * Set the 'visibility' of all the tooltip components to 'hidden'.
	 */
	public hide(): void {
		this.background.style('visibility', 'hidden');
		this.label.style('visibility', 'hidden');
		this.circle.style('visibility', 'hidden');
	}

	/**
	 * Update the tooltip label text.
	 * @param value the value to display as the tooltip label.
	 * @param formatter the d3 formatter used to convert the number to text.
	 */
	public setValue(value: number): void {
		this.label.text(getNumberFormatter(value)(value));

		// @ts-expect-error property 'getBBox' does not exist on type 'Node'
		// eslint-disable-next-line
		const textWidth: number = this.label.node().getBBox().width;
		this.background.attr('width', textWidth + this.xPadding * 2);
	}

	/**
	 * Update the tooltip location.
	 * @param xLoc the desired x coordinate (in pixels w.r.t. the canvas).
	 * @param yLoc the desired y coordinate (in pixels w.r.t. the canvas). This will be the location
	 * of the circle, and the location of the label if there is no overlap.
	 * @param prevYLoc the y coordinate of the previous label. Assumes it is `<= yLoc`.
	 * @returns the final y coordinate of the label.
	 */
	public setLocation(xLoc: number, yLoc: number, prevYLoc: number): number {
		this.circle.attr('cx', xLoc).attr('cy', yLoc);

		// shift label down if there is overlap
		if (yLoc < prevYLoc + this.boxHeight) {
			yLoc = prevYLoc + this.boxHeight;
		}

		this.background.attr('y', yLoc - this.boxHeight / 2);
		this.label.attr('y', yLoc); // as anchor is central

		return yLoc;
	}
}
