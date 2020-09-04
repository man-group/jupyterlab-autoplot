/**
 * Return a d3 time formatter for the x tooltip, based on the visible range of the x axis.
 * @param xRange current visible range of the x axis (in days).
 */
function getDateFormatter(xRange: number): d3.time.Format {
	if (xRange >= 30) {
		return d3.time.format('%Y-%m-%d');
	}
	if (xRange >= 5) {
		return d3.time.format('%m-%d %H:00');
	}
	if (xRange >= 0.25) {
		return d3.time.format('%m-%d %H:%M');
	}
	return d3.time.format('%d - %H:%M:%S');
}

/**
 * Return a d3 time formatter for the y tooltip, based on its value.
 */
function getNumberFormatter(yValue: number): (n: number) => string {
	const abs = Math.abs(yValue);

	if (abs < 0.001 || abs >= 1000000) {
		return d3.format('.5s'); // SI-prefix with 5 significant digits
	}
	if (abs < 1) {
		return d3.format('.5f'); // 5 decimal places
	} 
	if (abs < 10000) {
		return d3.format('.5r'); // 5 significant digits
	}
	return d3.format(',.0f'); // grouped thousands with 0 decimal places
}
