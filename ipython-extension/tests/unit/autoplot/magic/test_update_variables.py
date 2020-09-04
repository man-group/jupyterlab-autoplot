"""Test the magic commands used to update variables and trace properties.

We expect the correct updates to be performed when a valid input is given, and the
correct warnings to be shown when an invalid one is.
"""

import pytest

from tests.unit.autoplot.mocks import COL, DF, DF_COL, DF_COL_ALT, VAR


@pytest.mark.parametrize("initial,final", [(VAR, "new"), (VAR, "my var"), (VAR, "m1 var!"), (DF_COL, "c")])
def test_rename_valid_names(initial, final, full_autoplot_magic):
    magic = full_autoplot_magic()
    magic.autoplot(f"--rename '{initial}' '{final}'")

    # test label set to correct value
    assert magic.plotter[initial].get_label() == final
    assert magic.plotter._changed


def test_rename_dataframe(full_autoplot_magic):
    initial = DF
    final = "new"

    magic = full_autoplot_magic()
    magic.autoplot(f"--rename {initial} {final}")

    # test label set to correct value
    assert magic.plotter[DF_COL].get_label() == DF_COL.replace(initial, final)
    assert magic.plotter[DF_COL_ALT].get_label() == DF_COL_ALT.replace(initial, final)


@pytest.mark.parametrize("initial", ["undef", "", COL])
def test_rename_undefined_variable(mock_toast, initial, full_autoplot_magic):
    toast = mock_toast
    magic = full_autoplot_magic(toast)
    magic.autoplot(f"--rename '{initial}' new")

    # test plotter not changed and toast show
    assert not magic.plotter._changed
    toast.unrecognised_variable.assert_called_once_with(initial)
