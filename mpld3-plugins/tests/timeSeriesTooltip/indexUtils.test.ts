import rewire from 'rewire';
import each from 'jest-each';

const tst = rewire('../../bundles_test/timeSeriesTooltip');
const getClosestIndex = tst.__get__('getClosestIndex');

function range(start: number, step: number, count: number): number[] {
	const result = [];

	for (let i = start; i < start + count * step; i += step) {
		result.push(i);
	}

	return result;
}

interface MockLine {
	data: [number][];
	props: { xindex: number };
}

function genMockLine(xData: number[]): MockLine {
	return { data: xData.map((x) => [x]), props: { xindex: 0 } };
}

describe('Test the getClosestIndex() function with daily data', () => {
	each([
		['05-01 00:00:00', 0], // first value
		['05-20 00:00:00', 19], // last value
		['05-10 00:00:00', 9], // arbitrary value
		['05-10 00:00:01', 9], // non-exact values (should be rounded)
		['05-10 00:59:00', 9],
		['05-10 07:00:00', 9],
		['05-10 11:59:59', 9],
		['05-10 23:59:59', 10],
		['04-30 23:50:00', 0], // outside range
		['05-20 00:10:00', 19],
	]).it('expect date "%s" to give index "%d".', (date: string, index: number) => {
		const xValue = new Date('2020-' + date);
		const line = genMockLine(range(737546, 1, 20)); // 737546 = 2020-05-01

		expect(getClosestIndex(xValue, line).closestIndex).toEqual(index);
	});
});

describe('Test the getClosestIndex() function with hourly data', () => {
	each([
		['05-01 00:00:00', 0], // first value
		['05-02 23:00:00', 47], // last value
		['05-01 17:00:00', 17], // arbitrary value
		['05-01 17:00:01', 17], // non-exact values (should be rounded)
		['05-01 17:01:00', 17],
		['05-01 17:15:00', 17],
		['05-01 17:29:59', 17],
		['05-01 17:30:00', 18],
		['05-01 17:30:01', 18],
		['05-01 17:59:59', 18],
		['04-30 23:50:00', 0], // outside range
		['05-02 23:10:00', 47],
	]).it('expect date "%s" to give index "%d".', (date: string, index: number) => {
		const xValue = new Date('2020-' + date);
		const line = genMockLine(range(737546, 1 / 24, 48)); // 737546 = 2020-05-01

		expect(getClosestIndex(xValue, line).closestIndex).toEqual(index);
	});
});

describe('Test the getClosestIndex() function with minutely data', () => {
	each([
		['18:00:00', 0], // first value
		['19:59:00', 119], // last value
		['18:50:00', 50], // arbitrary value
		['18:50:01', 50], // non-exact values (should be rounded)
		['18:50:15', 50],
		['18:50:29', 50],
		['18:50:30', 51],
		['18:50:31', 51],
		['18:50:59', 51],
		['17:59:00', 0], // outside range
		['20:01:00', 120],
	]).it('expect date "%s" to give index "%d".', (date: string, index: number) => {
		const xValue = new Date('2020-05-01 ' + date);
		const line = genMockLine(range(737546.75, 1 / 24 / 60, 120)); // 737546 = 2020-05-01

		expect(getClosestIndex(xValue, line).closestIndex).toEqual(index);
	});
});
