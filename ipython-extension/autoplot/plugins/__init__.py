"""This module contains custom mpld3 plugins to add useful features to the graph.

The JavaScript in the Python files was built from the TypeScript source files in the
`mpld3-plugins` directory.

Classes
-------
InteractiveLegend
    Class defining an mpld3 plugin to create an interactive legend.

RangeSelectorButtons
    Class defining an mpld3 plugin to create range selector buttons.

SaveImageButtons
    Class defining an mpld3 plugin to create save as image buttons.

TimeSeriesTooltip
    Class defining an mpld3 plugin to create line graph tooltips.
"""

from autoplot.plugins.interactive_legend import InteractiveLegend
from autoplot.plugins.range_selector_buttons import RangeSelectorButtons
from autoplot.plugins.save_image_buttons import SaveImageButtons
from autoplot.plugins.time_series_tooltip import TimeSeriesTooltip
