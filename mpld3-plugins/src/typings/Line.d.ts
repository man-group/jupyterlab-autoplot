import Axes = require('./Axes');
import Figure = require('./Figure');

export = Line;

interface LineProps {
	alpha: number;
	coordinates: string;
	data: string;
	edgecolor: string;
	edgewidth: number;
	id: string;
	xindex: number;
	yindex: number;
	zorder: number;

	// added by Interactive Legend, read by Tooltip
	isHidden?: boolean;
}

declare class Line {
	public ax: Axes;
	public data: number[][];
	public fig: Figure;
	public props: LineProps;
	public path: string[][];
}
