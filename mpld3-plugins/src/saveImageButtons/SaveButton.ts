/**
 * A class defining a single save button button.
 */
class SaveButton {
	private fig: mpld3.Figure;
	private ax: mpld3.Axes;
	private label: string;
	private fontsize: number;

	private box: d3.Selection<SVGElement>;
	private text: d3.Selection<SVGElement>;

	public buttonHeight: number;
	public buttonWidth: number;

	private readonly xPadding: number = 6;
	private readonly yPadding: number = 4;

	/**
	 * Initialise a `SaveButton` instance.
	 * @param fig the associated mpld3 Figure.
	 * @param ax the associated mpld3 Axes.
	 * @param label the label of the button as it should be displayed. Must either be one of
	 * ["png"]. Validation of the label value should be done prior to passing it to this constructor.
	 * @param fontsize fontsize of the button label (in pixels).
	 */
	public constructor(fig: mpld3.Figure, ax: mpld3.Axes, label: string, fontsize: number) {
		this.fig = fig;
		this.ax = ax;
		this.label = label;
		this.fontsize = fontsize;

		const bgColour = '#bbdde5';

		this.box = fig.canvas
			.append('rect')
			.style('fill', bgColour)
			.attr('class', 'mpld3-save-button-rect')
			.on('click', this.onClick.bind(this));

		this.text = fig.canvas
			.append('text')
			.style('fontsize', fontsize)
			.attr('class', 'mpld3-save-button-text')
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
	 * @param xLoc the x coordinate (in pixels w.r.t. the canvas) of the right edge.
	 * @param yLoc the y coordinate (in pixels w.r.t. the canvas) of the top edge.
	 */
	public setPosition(xLoc: number, yLoc: number): void {
		this.box.attr('x', xLoc - this.buttonWidth).attr('y', yLoc - this.buttonHeight / 2);
		this.text.attr('x', xLoc - this.buttonWidth / 2).attr('y', yLoc);
	}

	/**
	 * Event handler for the click event.
	 */
	public onClick(): void {
		// convert canvas view to SVG
		const { svgString, svgWidth, svgHeight } = figToSVG(this.fig, this.ax);
		const imgSource = 'data:image/svg+xml;base64,' + btoa(unescape(encodeURIComponent(svgString)));

		const callback = (dataUrl: string) => {
			// save the data url to session storage
			const sessionKey = 'autoplot_image_data_url';
			sessionStorage.setItem(sessionKey, dataUrl);

			// create a DOM event to trigger JupyterLab extension actions
			const event = new CustomEvent('autoplot-embed-image', { detail: { sessionKey } });
			document.dispatchEvent(event);
		};

		switch (this.label.toLowerCase()) {
			case 'svg':
				callback(imgSource);
				break;
			case 'png':
				svgToPNG(imgSource, svgWidth, svgHeight, callback);
				break;
			default:
				throw new Error(`Unrecognised save button label ${this.label}`);
		}
	}
}
