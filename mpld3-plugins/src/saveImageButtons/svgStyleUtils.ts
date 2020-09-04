function addElementCSS(ax: mpld3.Axes, svgElement: SVGElement): void {
	addMissingCSS(ax, svgElement);
	hidePlugins(svgElement);
	addMissingLegendCSS(svgElement);
}

function addAttributesToAll(elements: HTMLCollectionOf<Element>, attributes: Record<string, string>) {
	for (let i = 0; i < elements.length; i++) {
		Object.keys(attributes).forEach((prop) => elements.item(i)!.setAttribute(prop, attributes[prop]));
	}
}

/**
 * Add the mpld3 styles that were inserted as css, e.g.:
 * https://github.com/mpld3/mpld3/blob/674200c8d1044df9f887254b2f684c8a1ea31f28/mpld3/js/mpld3.v0.3.js#L269
 * @param ax associated mpld3 Axes.
 * @param svgElement the svg element to be styled.
 */
function addMissingCSS(ax: mpld3.Axes, svgElement: SVGElement): void {
	ax.elements.forEach((element) => {
		const cssClass = element.cssclass;

		if (!cssClass) {
			return;
		}

		// extract relevant styles
		let tickStyles: Record<string, string> = {};
		let pathStyles: Record<string, string> = {};
		let textStyles: Record<string, string> = {};

		switch (cssClass) {
			case 'mpld3-xaxis':
			case 'mpld3-yaxis':
				pathStyles = {
					'shape-rendering': 'crispEdges',
					stroke: <string>element.props.axiscolor,
					fill: 'none',
				};

				textStyles = {
					'font-family': 'sans-serif',
					'font-size': `${<number>element.props.fontsize}px`,
					fill: <string>element.props.fontcolor,
					stroke: 'none',
				};
				break;

			case 'mpld3-xgrid':
			case 'mpld3-ygrid':
				tickStyles = {
					stroke: <string>element.props.color,
					'stroke-dasharray': <string>element.props.dasharray,
					'stroke-opacity': `${<number>element.props.alpha}`,
				};
				break;
		}

		// apply styles to canvas's children
		const svgElementsByClass = svgElement.getElementsByClassName(cssClass);

		function applyStyles(styles: Record<string, string>, child: { class?: string; tag?: string }): void {
			// add styles directly if no child params given
			if (!child.class && !child.tag) {
				addAttributesToAll(svgElementsByClass, styles);
				return;
			}

			// otherwise find all children and add styles to them
			for (let i = 0; i < svgElementsByClass.length; i++) {
				const children = child.class
					? svgElementsByClass.item(i)!.getElementsByClassName(child.class)
					: svgElementsByClass.item(i)!.getElementsByTagName(child.tag!);

				addAttributesToAll(children, styles);
			}
		}

		applyStyles(pathStyles, {});
		applyStyles(tickStyles, { class: 'tick' });
		applyStyles(textStyles, { tag: 'text' });
	});
}

/**
 * Set the 'display' attribute of unwanted plugins to 'none'. Note that this gives more reliable
 * results than 'visibility' = 'hidden', as this property is modified in the plugin code.
 */
function hidePlugins(svgElement: SVGElement) {
	const pluginClasses = [
		'mpld3-time-series-tooltip-rect',
		'mpld3-time-series-tooltip-text',
		'mpld3-time-series-tooltip-circle',
		'mpld3-range-selector-button-rect',
		'mpld3-range-selector-button-text',
		'mpld3-save-button-text',
		'mpld3-save-button-rect',
		'mpld3-resetbutton',
		'mpld3-zoombutton',
		'mpld3-boxzoombutton',
	];

	pluginClasses.forEach((pluginClass) => {
		const elements = svgElement.getElementsByClassName(pluginClass);
		addAttributesToAll(elements, { display: 'none' });
	});
}

function addMissingLegendCSS(svgElement: SVGElement) {
	const elements = svgElement.getElementsByClassName('mpld3-interactive-legend-text');
	addAttributesToAll(elements, { 'font-family': 'sans-serif' });
}
