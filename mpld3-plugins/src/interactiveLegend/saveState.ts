function saveVisible(label: string): void {
	window.sessionStorage.removeItem(`autoplot-legend-${label}`);
}

function saveHidden(label: string): void {
	window.sessionStorage.setItem(`autoplot-legend-${label}`, 'hidden');
}

function isHidden(label: string): boolean {
	return window.sessionStorage.getItem(`autoplot-legend-${label}`) === 'hidden';
}
