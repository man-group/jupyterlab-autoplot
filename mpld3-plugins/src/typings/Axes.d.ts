import Figure = require('./Figure');

export = Axes;

interface AxesProps {
	xlim: [number, number];
	xscale: string;
	ydomain: [number, number];
	ylim: [number, number];
	yscale: string;
	zoomable: boolean;
}

interface AxesElement {
	ax: Axes;
	cssclass?: string;
	fig: Figure;
	props: Record<string, string | number | boolean>;
}

declare class Axes {
	public baseaxes: d3.Selection<SVGElement>;
	public elements: AxesElement[];
	public fig: Figure;
	public height: number;
	public parent: Figure;
	public position: [number, number];
	public props: AxesProps;
	public width: number;

	/**
	 * Return the x coordinate in pixels (w.r.t. the axes) of the given x value.
	 */
	public x(value: number): number;

	/**
	 * Return the y coordinate in pixels (w.r.t. the axes) of the given y value.
	 * @param value
	 */
	public y(value: number): number;

	public xdom: { invert: (location: number) => Date };
	public ydom: { invert: (location: number) => number };
	public zoom_x: { scale: () => number };
	public zoom_y: { scale: () => number };

	/**
	 * Set the limits of the axis
	 * @param xlim x limits, in form [xMin, xMax].
	 * @param ylim y limits, in form [yMin, yMax].
	 * @param duration duration of the transition in milliseconds (default 750).
	 * @param propagate if true, will also update linked axes (default true).
	 */
	public set_axlim(
		xlim?: [number, number] | [Date, Date],
		ylim?: [number, number],
		duration?: number,
		propagate?: boolean
	): void;

	/**
	 * Reset the axis view. Calls `set_axlim` with original x and y domains.
	 * @param duration duration of the transition in milliseconds (default 750).
	 * @param propagate if true, will also update linked axes (default true).

	 */
	public reset(duration?: number, propagate?: boolean): void;
}
