"""Test the magic commands used to set the figure height or width.

We expect the correct updates to be performed when a valid value is given, and the
correct warnings to be shown when an invalid one is.
"""

import pytest

from autoplot.utils.constants import FigSize


@pytest.mark.parametrize("height", [FigSize.MIN_HEIGHT.value, 4.5, 6, "7", "8.9", 22 / 7, FigSize.MAX_HEIGHT.value])
def test_set_valid_height(height, autoplot_magic):
    magic = autoplot_magic()
    magic.autoplot(f"--height {height}")

    # test height set to given value
    assert magic.view_manager.active_view._plotter._height == pytest.approx(float(height))


@pytest.mark.parametrize("width", [FigSize.MIN_WIDTH.value, 6.7, 8, "9", "10.1", 44 / 7, FigSize.MAX_WIDTH.value])
def test_set_valid_width(width, autoplot_magic):
    magic = autoplot_magic()
    magic.autoplot(f"--width {width}")

    # test width set to given value
    assert magic.view_manager.active_view._plotter._width == pytest.approx(float(width))


@pytest.mark.parametrize(
    "height",
    [
        FigSize.MIN_HEIGHT.value - 1e9,
        FigSize.MIN_HEIGHT.value - 2,
        FigSize.MIN_HEIGHT.value - 1 / 7,
        FigSize.MAX_HEIGHT.value + 1e9,
        FigSize.MAX_HEIGHT.value + 2,
        FigSize.MAX_HEIGHT.value + 1 / 7,
    ],
)
def test_set_height_out_of_range(mock_toast, height, autoplot_magic):
    toast = mock_toast
    magic = autoplot_magic()
    magic.autoplot(f"--height {height}")

    # test height set to nearest boundary
    expected = FigSize.MIN_HEIGHT.value if height <= FigSize.MIN_HEIGHT.value else FigSize.MAX_HEIGHT.value
    assert magic.view_manager.active_view._plotter._height == pytest.approx(expected)

    # test that a warning was shown
    toast.show.assert_called_once()


@pytest.mark.parametrize(
    "width",
    [
        FigSize.MIN_WIDTH.value - 1e9,
        FigSize.MIN_WIDTH.value - 2,
        FigSize.MIN_WIDTH.value - 1 / 7,
        FigSize.MAX_WIDTH.value + 1e9,
        FigSize.MAX_WIDTH.value + 2,
        FigSize.MAX_WIDTH.value + 1 / 7,
    ],
)
def test_set_width_out_of_range(mock_toast, width, autoplot_magic):
    toast = mock_toast
    magic = autoplot_magic()
    magic.autoplot(f"--width {width}")

    # test width set to nearest boundary
    expected = FigSize.MIN_WIDTH.value if width <= FigSize.MIN_WIDTH.value else FigSize.MAX_WIDTH.value
    assert magic.view_manager.active_view._plotter._width == pytest.approx(expected)

    # test that a warning was shown
    toast.show.assert_called_once()
