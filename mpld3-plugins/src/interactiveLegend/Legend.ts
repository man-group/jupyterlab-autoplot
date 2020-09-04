/**
 * A class defining the interactive legend.
 */
class Legend {
	private fig: mpld3.Figure;
	private ax: mpld3.Axes;
	private items: LegendItem[];
	private fontsize: number;

	private legend: d3.Selection<SVGElement>;
	private boxes: d3.Selection<LegendItem>[];
	private labels: d3.Selection<LegendItem>[];

	private boxWidth: number;
	private boxHeight: number;

	private readonly xPadding: number = 12;
	private readonly yPadding: number = 5;

	/**
	 * Create a `Legend` instance.
	 * @param fig the associated mpld3 Figure.
	 * @param ax the associated mpld3 Axes.
	 * @param items a list of `LegendItem` instances, used to populate the legend.
	 * @param fontsize fontsize of the legend labels (in pixels).
	 * @param onClickItem event handler for the legend box click event.
	 */
	public constructor(
		fig: mpld3.Figure,
		ax: mpld3.Axes,
		items: LegendItem[],
		fontsize: number,
		onClickItem: (d: LegendItem, i?: number) => void
	) {
		this.fig = fig;
		this.ax = ax;
		this.items = items;
		this.fontsize = fontsize;

		this.boxWidth = 1.6 * this.fontsize;
		this.boxHeight = 0.7 * this.fontsize;

		this.legend = fig.canvas.append('svg:g').attr('class', 'legend');

		this.boxes = [];
		this.labels = [];

		for (let i = 0; i < items.length; i++) {
			this.boxes.push(
				this.legend
					.data([items[i]])
					.append('rect')
					.attr('class', 'mpld3-interactive-legend-rect')
					.attr('height', this.boxHeight)
					.attr('width', this.boxWidth)
					.attr('stroke', (d) => d.getColour())
					.style('fill', (d) => (d.isHidden() ? 'white' : d.getColour()))
					.on('click', onClickItem)
			);

			this.labels.push(
				this.legend
					.data([items[i]])
					.append('text')
					.attr('class', 'mpld3-interactive-legend-text')
					.attr('font-size', this.fontsize)
					.attr('dominant-baseline', 'central')
					.text((d) => d.getLabel())
			);
		}

		this.setPositions();
	}

	/**
	 * Set the position of legend boxes and labels. This must be done after they have been added
	 * to the canvas, as the actual display size of the label is used in the calculation.
	 *
	 * The legend will be layed out horizontally below the axes, and will add rows as necessary.
	 * The instance variables `xPadding` and `yPadding` set the size of spaces between items / rows.
	 */
	private setPositions(): void {
		function warnWithToast(message: string): void {
			document.dispatchEvent(new CustomEvent('autoplot-toast', { detail: { type: 'warning', message } }));
			console.warn(message);
		}

		let x = this.ax.position[0];
		let y = this.ax.position[1] + this.ax.height + 35;

		// flag for if just started new line. Needed to prevent infinite loop for very long names
		let newLine = true;
		let notEnoughSpace = false;

		for (let i = 0; i < this.boxes.length; i++) {
			if (notEnoughSpace) {
				this.boxes[i].attr('visibility', 'hidden');
				this.labels[i].attr('visibility', 'hidden');
				continue;
			}

			// set box position and increment
			this.boxes[i].attr('x', x).attr('y', y - this.boxHeight / 2);
			x += this.boxWidth + this.fontsize / 3;

			// set label position and increment
			this.labels[i].attr('x', x).attr('y', y);

			// @ts-expect-error property 'getBBox' does not exist on type 'Node'
			// eslint-disable-next-line
			x += this.labels[i].node().getBBox().width + this.xPadding;

			// move to next row if reached end
			if (x > this.fig.width) {
				if (newLine) {
					// warn if already made a new line for this variable.
					const name = this.items[i].getLabel();
					warnWithToast(`Legend label '${name}' is very long and may cause issues with the layout.`);
					newLine = false;
				} else {
					// otherwise create a new line
					i -= 1;
					y += this.fontsize + this.yPadding;
					x = this.ax.position[0];

					newLine = true;

					// warn and hide legend items if don't fit
					if (y + this.fontsize > this.fig.height) {
						warnWithToast(`The legend labels can't all fit below the figure.`);
						notEnoughSpace = true;
					}
				}
			} else {
				newLine = false;
			}
		}
	}
}
