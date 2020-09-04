/**
 * Set the lower limit of the x axis based on the desired width. Only the lower limit is changed
 * (i.e. the axis will be scaled with the anchor at the right hand edge).
 * @param xMin date instance to be used as the lower limit. Will be modified in place.
 * @param xMax date relative to which `xMin` will be calculated. Will not be modified.
 * @param number the desired difference between `xMin` and `xMax`.
 * @param unit the unit of the `number` parameter. Must be one of "s" = seconds, "M" = minutes,
 * "h" = hours, "d" = days, "w" = weeks, "m" = months, "y" = years.
 */
function setLowerLimit(xMin: Date, xMax: Date, number: number, unit: string): void {
	switch (unit) {
		case 's':
			xMin.setSeconds(xMax.getSeconds() - number);
			break;
		case 'M':
			xMin.setMinutes(xMax.getDate() - number);
			break;
		case 'h':
			xMin.setHours(xMax.getHours() - number);
			break;
		case 'd':
			xMin.setDate(xMax.getDate() - number);
			break;
		case 'm':
			xMin.setMonth(xMax.getMonth() - number);
			break;
		case 'y':
			xMin.setFullYear(xMax.getFullYear() - number);
			break;

		default:
			throw new Error(`Unrecognised unit '${unit}'`);
	}
}

/**
 * Return a new date instance corresponding to a matplotlib date value.
 */
function mplToDate(value: number): Date {
	const date = new Date((value - 719163) * 86400000); // 1000 * 60 * 60 * 24
	date.setMinutes(date.getMinutes() + date.getTimezoneOffset());
	return date;
}

/**
 * Return a set of coordinates that define the limits of the given lines. Only visible lines will
 * be considered.
 * @param fig the associated mpld3 Figure.
 * @param lineIds list of line ids.
 * @returns axes limits, of form `[[xMin, xMax], [yMin, yMax]]`
 */
function getVisibleDomain(
	fig: mpld3.Figure,
	lineIds?: string[]
): [[Date, Date] | undefined, [number, number] | undefined] {
	if (!lineIds) {
		throw new Error('"lineIds" must be defined for the "fit" button to work');
	}

	let xMin: Date | undefined;
	let xMax: Date | undefined;

	let yMin: number | undefined;
	let yMax: number | undefined;

	lineIds.forEach((lineId) => {
		const line = mpld3.get_element(lineId, fig);

		// only consider domain of visible lines
		if (!line.props.isHidden) {
			// update x min and max. If undefined, set to line min and max without comparison
			const lineXMin = mplToDate(line.data[0][line.props.xindex]);
			const lineXMax = mplToDate(line.data[line.data.length - 1][line.props.xindex]);

			xMin = xMin ? (lineXMin < xMin ? lineXMin : xMin) : lineXMin;
			xMax = xMax ? (lineXMax > xMax ? lineXMax : xMax) : lineXMax;

			// update y min and max. If undefined, set to line min and max without comparison
			const [lineYMin, lineYMax] = d3.extent(line.data.map((row) => row[line.props.yindex]));

			yMin = yMin ? (lineYMin < yMin ? lineYMin : yMin) : lineYMin;
			yMax = yMax ? (lineYMax > yMax ? lineYMax : yMax) : lineYMax;
		}
	});

	// add some padding to y limits
	if (yMin && yMax) {
		const padding = (yMax - yMin) / 100;
		yMin -= padding;
		yMax += padding;
	}

	return [xMin && xMax ? [xMin, xMax] : undefined, yMin && yMax ? [yMin, yMax] : undefined];
}
