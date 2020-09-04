import Axes = require('./Axes');
import Plugin = require('./Plugin');

export = Figure;

interface FigureProps {
	data: Record<string, number[][]>;
	height: number;
	id: string;
	plugins: Plugin['prototype'][];
	width: number;
}

interface Toolbar {
	fig: Figure;
	parent: Figure;
}

declare class Figure {
	public axes: Axes[];
	public canvas: d3.Selection<SVGElement>;
	public data: Record<string, number[][]>;
	public figid: string;
	public height: number;
	public plugins: Plugin['prototype'][];
	public props: FigureProps;
	public toolbar: Toolbar;
	public width: number;
	public zoom_on: boolean;
}
