/**
 * Handle the event when a legend box is clicked. The line's visibility will be toggled.
 * @param d the associated `LegendItem` instance.
 */
function onClickItem(d: LegendItem): void {
	if (d.isHidden()) {
		// if hidden, make visible and fill box
		d.show();
		// @ts-expect-error 'this' explicitly has type 'any'
		d3.select(this).style('fill', d.getColour());
	} else {
		d.hide();
		// @ts-expect-error 'this' explicitly has type 'any'
		d3.select(this).style('fill', 'white');
	}
}
