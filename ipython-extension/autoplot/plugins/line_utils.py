"""Module containing the `get_line_ids` function.

Methods
-------
get_line_ids(lines)
    Return a list of mpld3 element ids corresponding to the given list of lines.
"""

import collections
from typing import List

from mpld3.utils import get_id
import matplotlib.lines as mpl_lines


def get_line_ids(lines: List[mpl_lines.Line2D]) -> List[str]:
    """Return a list of mpld3 element ids corresponding to the given list of lines.

    Parameters
    ----------
    lines: List[mpl_lines.Line2D]
        List of matplotlib lines, generated using `ax.plot(...)`, `Line2D(...)` or
        equivalent.
    """
    line_ids: List[str] = []

    # because lines are built slightly differently depending on how they are defined,
    # the exact type of the line must be checked before its id extracted
    for entry in lines:
        if isinstance(entry, collections.Iterable):
            line_ids += [get_id(line) for line in entry]
        else:
            line_ids.append(get_id(entry))

    return line_ids
