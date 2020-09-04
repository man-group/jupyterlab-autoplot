/**
 * A class defining a single legend item. It is associated with a single `mpld3.Line` instance.
 */
class LegendItem {
	private label: string;
	private line: mpld3.Line;

	private alphaVisible: number;
	private alphaHidden: number;

	/**
	 * Create a `LegendItem` instance.
	 * @param label the label to display in the legend.
	 * @param line the associated `mpld3.Line` instance.
	 * @param hidden if False, the line will initially be visible.
	 * @param alphaVisible the transparency of the line when it is visible.
	 * @param alphaHidden the transparency of the line when it is hidden.
	 */
	public constructor(label: string, line: mpld3.Line, hidden: boolean, alphaVisible: number, alphaHidden: number) {
		this.label = label;
		this.line = line;

		this.alphaVisible = alphaVisible;
		this.alphaHidden = alphaHidden;

		if (hidden) {
			this.hide();
		} else {
			this.show();
		}
	}

	/**
	 * Set the stroke opacity to `alphaVisible`, and mark the line as visible.
	 */
	public show(): void {
		this.line.props.isHidden = false;
		d3.select(this.line.path[0]![0]).style('stroke-opacity', this.alphaVisible);
		saveVisible(this.label);
	}

	/**
	 * Set the stroke opacity to `alphaHidden`, and mark the line as hidden.
	 */
	public hide(): void {
		this.line.props.isHidden = true;
		d3.select(this.line.path[0]![0]).style('stroke-opacity', this.alphaHidden);
		saveHidden(this.label);
	}

	/**
	 * Return the line label.
	 */
	public getLabel() {
		return this.label;
	}

	/**
	 * Return true if the line is marked as hidden, otherwise false.
	 */
	public isHidden() {
		return this.line.props.isHidden;
	}

	/**
	 * Return the colour of the line.
	 */
	public getColour() {
		return this.line.props.edgecolor;
	}
}
