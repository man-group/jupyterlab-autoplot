"""Module containing utility functions used by the `CellEventHandler` class.

Methods
-------
is_plottable(series)
    Return `True` if the series is DateTime indexed and contains only numbers.
"""

import numpy as np
import pandas as pd


def _is_numeric(series: pd.Series) -> bool:
    """Return `True` if the series contains only real numbers.

    Raises
    ------
    AttributeError
        If the input variable does not have attribute `dtype`. Note that dataframes
        will raise an error.
    """
    return np.issubdtype(series.dtype, np.number) and all(np.isreal(series))


def _is_datetime_indexed(series: pd.Series) -> bool:
    """Return `True` if the series is datetime indexed.

    Raises
    ------
    AttributeError
        If the input variable does not have attribute `index`.
    """
    return isinstance(series.index, pd.DatetimeIndex)


def is_plottable(series: pd.Series) -> bool:
    """Return `True` if the series can be plotted.

    This requires all of the following to be `True`:
        - It is a series;
        - It is datetime indexed;
        - Its values are all real numbers;
        - Its length is greater than or equal to 2.
    """
    try:
        return _is_datetime_indexed(series) and _is_numeric(series) and len(series) > 1
    except AttributeError:
        return False
