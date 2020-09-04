"""Module containing utility functions for Plotter's range selection buttons.

Methods
-------
gen_range_selector_labels(total_range, min_diff, include_standard)
    Return a list of range selector button labels, based on the given information.
"""

from typing import List, Tuple

# list of possible button labels, a selection of which will be chosen
_LABELS: List[Tuple[float, str]] = []

_LABELS += [(n / 86400, f"{n}s") for n in [1, 10, 30]]  # seconds
_LABELS += [(n / 1440, f"{n}M") for n in [1, 10, 30]]  # minutes
_LABELS += [(n / 24, f"{n}h") for n in [1, 6, 12]]  # hours
_LABELS += [(n, f"{n}d") for n in [1, 5, 7]]  # days
_LABELS += [(n * 30.5, f"{n}m") for n in [1, 3, 6]]  # months
_LABELS += [(n * 365.25, f"{n}y") for n in [1, 2, 5]]  # years


def gen_range_selector_labels(total_range: float, min_diff: float, include_standard: bool = True):
    """Return a list of range selector button labels, based on the given information.

    Parameters
    ----------
    total_range: float
        Total range of the data, in seconds.

    min_diff: float
        Minimum difference between consecutive index entries, in seconds.

    include_standard: bool, optional
        If True, will include the "fit" and "reset" buttons.

    Notes
    -----
    The value of the largest button will be chosen to show a range that is at least
    double the range of `total_range` (up to 5 years). The value of the smallest button
    will be chosen to show a range in which at least 10 points with separation
    `min_diff` are visible.

    Returns
    -------
    List[str]
    """
    n = len(_LABELS)
    # get index of first button that shows at least 10 min diff data points. Note that
    # the maximum value is n - 2
    min_diff_10 = min_diff / 86400 * 10  # convert to days
    first = n - 2

    for i, (width, _) in enumerate(_LABELS[:-1]):
        if width > min_diff_10:
            first = i
            break

    # get index of the last button that is at least double the data range. Note that
    # the minimum value is first + 1
    total_range_2 = total_range / 86400 * 2  # convert to days
    last = n - 1

    for i, (width, _) in enumerate(_LABELS[first + 1 :]):
        if width > total_range_2:
            last = first + i
            break

    # get evenly spaced selection of labels between first and last indices
    labels = [_LABELS[i][1] for i in range(first, last + 1)]

    # add special buttons
    if labels[-1][-1] in {"m", "y"}:
        labels.append("ytd")

    if include_standard:
        labels.insert(0, "fit")
        labels.insert(0, "reset")

    return labels
