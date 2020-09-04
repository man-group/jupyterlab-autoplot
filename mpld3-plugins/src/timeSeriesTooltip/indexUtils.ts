/**
 * Calculate the x coordinate (in pixels w.r.t. the canvas) of the given x value.
 * @param yValue x value as read from a column of the data array.
 * @param ax the associated mpld3 Axes.
 */
function xValueToLocation(xValue: number, ax: mpld3.Axes): number {
	// must add the x offset of the plot (in pixels)
	return ax.x(xValue) + ax.position[0];
}

/**
 * Calculate the y coordinate (in pixels w.r.t. the canvas) of the given y value.
 * @param yValue y value as read from a column of the data array.
 * @param ax the associated mpld3 Axes.
 */
function yValueToLocation(yValue: number, ax: mpld3.Axes): number {
	// must add the y offset of the plot (in pixels)
	return ax.y(yValue) + ax.position[1];
}

/**
 * Return the x value associated with a given coordinate, as a `Date` instance.
 * @param xLoc the x coordinate (in pixels w.r.t. the canvas).
 * @param ax the associated mpld3 Axes.
 */
function xLocationToValue(xLoc: number, ax: mpld3.Axes): Date {
	// must subtract the x offset of the plot (in pixels)
	return ax.xdom.invert(xLoc - ax.position[0]);
}

/**
 * Return the size of the visible range of the x axis in days, assuming it is linearly scaled.
 * @param ax the associated mpld3 Axes.
 */
function getXRange(ax: mpld3.Axes): number {
	return Math.abs(ax.xdom.invert(ax.width).getTime() - ax.xdom.invert(0).getTime()) / (24 * 3600 * 1000);
}

/**
 * Return the index and value of the x value that is closest to the given one. If the value is just outside
 * the range, return the nearest boundary values. If it is far outside, return `null`.
 * @param xValue the x value, as a `Date` instance.
 * @param lineId id of the line on which the data array is stored.
 */
function getClosestIndex(xValue: Date, line: mpld3.Line): { closestIndex: number; closestX: number } | null {
	// calculate timezone offset in days
	const offset = xValue.getTimezoneOffset() / (24 * 60);

	// convert x to matplotlib format, which uses days since 0001-01-00
	const x = xValue.getTime() / (1000 * 3600 * 24) + 719163 - offset;
	const traceLength = line.data.length;

	// return boundary indices if outside but less than 1205 pixels away
	let lineWidth = 1000;
	try {
		// @ts-expect-error property 'getBBox' does not exist on type 'Node'
		// eslint-disable-next-line
		lineWidth = d3.select(line.path[0]![0]).node().getBBox().width;
	} catch {}

	const x0 = getX(line, 0)!;
	const x1 = getX(line, traceLength - 1)!;
	const xMin = Math.min(x0, x1);
	const xMax = Math.max(x0, x1);

	const buffer = (20 * (xMax - xMin)) / lineWidth;

	if (x < xMin) {
		if (xMin - x > buffer) {
			return null;
		}
		return { closestX: xMin, closestIndex: 0 };
	} else if (x > xMax) {
		if (x - xMax > buffer) {
			return null;
		}
		return { closestX: xMax, closestIndex: traceLength - 1 };
	}

	// otherwise binary search for closest value
	let precision = Math.floor(traceLength / 2);

	let closestIndex = Math.floor(traceLength / 2);
	let closestX = getX(line, closestIndex)!;
	let bestDistance = Math.abs(x - closestX);

	while (precision >= 1) {
		// update best values if moving left decreases distance
		const i1 = closestIndex - precision;
		const x1 = getX(line, i1);

		if (x1) {
			const d1 = Math.abs(x - x1);
			if (d1 < bestDistance) {
				closestX = x1;
				closestIndex = i1;
				bestDistance = d1;
				continue;
			}
		}

		// update best values if moving right decreases distance
		const i2 = closestIndex + precision;
		const x2 = getX(line, i2);

		if (x2) {
			const d2 = Math.abs(x - x2);
			if (d2 < bestDistance) {
				closestX = x2;
				closestIndex = i2;
				bestDistance = d2;
				continue;
			}
		}

		// otherwise reduce the search window
		precision = Math.floor(precision / 2);
	}

	return { closestIndex, closestX };
}
