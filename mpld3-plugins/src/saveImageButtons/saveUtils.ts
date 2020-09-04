function figToSVG(fig: mpld3.Figure, ax: mpld3.Axes): { svgString: string; svgWidth: number; svgHeight: number } {
	const svgElement = <SVGGraphicsElement>fig.canvas.node().cloneNode(true);

	// add necessary attributes / styles
	svgElement.setAttribute('xlink', 'http://www.w3.org/1999/xlink');
	addElementCSS(ax, svgElement);

	// set the viewbox and viewport
	const viewBox = [0, 0, fig.width, fig.height];
	svgElement.setAttribute('viewBox', viewBox.join(' '));
	svgElement.setAttribute('width', `${viewBox[2]}`);
	svgElement.setAttribute('height', `${viewBox[3]}`);

	// build the svg string
	const serializer = new XMLSerializer();

	let svgString = serializer.serializeToString(svgElement);
	svgString = svgString.replace(/(\w+)?:?xlink=/g, 'xmlns:xlink='); // Fix root xlink without namespace
	svgString = svgString.replace(/NS\d+:href/g, 'xlink:href'); // Safari NS namespace fix

	return { svgString, svgWidth: viewBox[2], svgHeight: viewBox[3] };
}

function svgToPNG(imgSource: string, width: number, height: number, callback: (dataUrl: string) => void): void {
	// define amount by which to scale the image. Larger -> higher quality
	const scaleFactor = 3;
	const scaledWidth = width * scaleFactor;
	const scaledHeight = height * scaleFactor;

	// create the canvas on which to build the image
	const canvas = document.createElement('canvas');
	const context = canvas.getContext('2d');

	canvas.width = scaledWidth;
	canvas.height = scaledHeight;

	const image = new Image();

	// add a callback to run once the image has loaded
	image.onload = function () {
		// draw image with white background
		context!.fillStyle = 'white';
		context!.fillRect(0, 0, scaledWidth, scaledHeight);
		context!.drawImage(image, 0, 0, scaledWidth, scaledHeight);

		// other image types may not be available in all browsers
		callback(canvas.toDataURL('image/png'));
	};

	image.src = imgSource;
}
