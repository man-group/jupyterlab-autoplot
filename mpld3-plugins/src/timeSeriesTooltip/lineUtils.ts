/**
 * Get the `mpld3.Line` instance associated with an id.
 */
function getLine(lineId: string, fig: mpld3.Figure): mpld3.Line {
	return mpld3.get_element(lineId, fig);
}

/**
 * Return the value of a line at the given indices. If it is outside the range, return `null`.
 */
function getValue(line: mpld3.Line, i: number, j: number): number | null {
	return 0 <= i && i < line.data.length ? line.data[i][j] : null;
}

/**
 * Get the x value of a line at the given index. This simplifies the process of extracting
 * the value from the 2D array in which it is stored. If it is outside the range, return `null`.
 */
function getX(line: mpld3.Line, index: number): number | null {
	return getValue(line, index, line.props.xindex);
}

/**
 * Get the y value of a line at the given index. This simplifies the process of extracting
 * the value from the 2D array in which it is stored. If it is outside the range, return `null`.
 */
function getY(line: mpld3.Line, index: number): number | null {
	return getValue(line, index, line.props.yindex);
}
