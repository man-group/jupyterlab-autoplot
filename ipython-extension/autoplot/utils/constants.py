"""Constants used throughout the package."""

from enum import Enum


class FigSize(Enum):
    """Class storing constants associated with the figure's size."""

    MIN_WIDTH = 6
    """Minimum width of the figure in inches."""

    MAX_WIDTH = 20
    """Maximum width of the figure in inches."""

    DEFAULT_WIDTH = 13
    """Default width of the figure in inches."""

    MIN_HEIGHT = 3
    """Minimum height of the figure in inches."""

    MAX_HEIGHT = 15
    """Maximum height of the figure in inches."""

    DEFAULT_HEIGHT = 4
    """Default height of the figure in inches."""


DEFAULT_MAX_SERIES_LENGTH = 1000
"""Default maximum series length above which series will be resampled."""

DF_COLUMN_FORMAT_STRING = "{} ({})"
"""The format string used to generate the names of dataframe column variables.

Usage: `DF_COLUMN_FORMAT_STRING.format(<df name>, <col name>)`
"""
