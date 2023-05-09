from typing import Union
from unittest.mock import patch

import dtale.global_state
import pandas as pd
import pytest
from IPython.core.display import Image

from autoplot.dtaler import DTaler, VarData
from autoplot.extensions.autoplot_display import AutoplotDisplay
from autoplot.extensions.toast import Toast
from ipywidgets import Output


@patch("autoplot.dtaler.display")
def test_force_draw_no_variable_update(display_mock, dtaler):
    dtaler.draw(True, AutoplotDisplay())

    assert isinstance(_get_parameter(display_mock), Image)


@patch("autoplot.dtaler.display")
def test_force_draw_with_variable_update(display_mock, dtaler):
    dtaler.update_variables({})
    dtaler.draw(True, AutoplotDisplay())

    assert isinstance(_get_parameter(display_mock), Image)


@patch("autoplot.dtaler.display")
def test_force_draw_with_variable_update_and_unexpected_data_id(display_mock, dtaler):
    dtaler.update_variables({})
    output = AutoplotDisplay()
    output.data_id = "1"
    dtaler.draw(True, output)

    assert isinstance(_get_parameter(display_mock), Image)


@patch("autoplot.dtaler.display")
def test_draw_dataframe(display_mock, dtaler):
    df = pd.DataFrame({"a": [1, 2, 3]})
    dtaler.update_variables({"df": df})
    dtaler.draw(False, AutoplotDisplay())

    assert all(_get_parameter(display_mock).data == df)


@patch("autoplot.dtaler.display")
def test_draw_new_dataframe(display_mock, dtaler):
    df1 = pd.DataFrame({"a": [1, 2, 3]})
    df2 = pd.DataFrame({"b": [1, 2, 3]})
    output = AutoplotDisplay()

    vars = {"df1": df1}
    dtaler.update_variables(vars)

    vars["df2"] = df2
    dtaler.update_variables(vars)
    output.data_id = str(dtaler._tracked["df1"].dd._data_id)
    dtaler.draw(False, output)

    assert all(_get_parameter(display_mock).data == df2)
    assert len(dtaler._tracked) == 2


@patch("autoplot.dtaler.display")
def test_draw_reassigned_dataframe(display_mock, dtaler):
    df1 = pd.DataFrame({"a": [1, 2, 3]})
    df2 = pd.DataFrame({"a": [4, 5, 6]})
    output = AutoplotDisplay()

    vars = {"df1": df1, "df2": df2}
    dtaler.update_variables(vars)

    new_df1 = pd.DataFrame({"a": [7, 8, 9]})
    vars["df1"] = new_df1
    dtaler.update_variables(vars)
    output.data_id = str(dtaler._tracked["df1"].dd._data_id)
    dtaler.draw(False, output)

    assert all(_get_parameter(display_mock).data == df1)
    assert len(dtaler._tracked) == 2
    assert dtaler._tracked["df1"].pdf is new_df1


@patch("autoplot.dtaler.display")
def test_draw_does_not_reload_hidden_df(display_mock, dtaler):
    df1 = pd.DataFrame({"a": [1, 2, 3]})
    df2 = pd.DataFrame({"a": [4, 5, 6]})
    output = AutoplotDisplay()

    vars = {"df1": df1, "df2": df2}
    dtaler.update_variables(vars)

    vars["df1"] = pd.DataFrame({"a": [1, 2, 3]})
    dtaler.update_variables(vars)
    output.data_id = str(dtaler._tracked["df2"].dd._data_id)
    dtaler.draw(False, output)

    assert not display_mock.called
    assert len(dtaler._tracked) == 2


@patch("autoplot.dtaler.display")
def test_draw_external_data_id_does_not_reload(display_mock, dtaler):
    df1 = pd.DataFrame({"a": [1, 2, 3]})
    df2 = pd.DataFrame({"a": [4, 5, 6]})
    df3 = pd.DataFrame({"a": [7, 8, 9]})
    output = AutoplotDisplay()

    vars = {"df1": df1, "df2": df2}
    dtaler.update_variables(vars)

    vars["df1"] = pd.DataFrame({"a": [1, 2, 3]})
    output.data_id = str(dtale.show(df3, ignore_duplicate=True)._data_id)
    dtaler.update_variables(vars)
    dtaler.draw(False, output)

    assert not display_mock.called


def test_do_not_reinsert_externally_removed_frames_when_variable_is_updated(dtaler):
    df1 = pd.DataFrame({"a": [1, 2, 3]})
    df2 = pd.DataFrame({"b": [1, 2, 3]})

    vars = {"df1": df1, "df2": df2}
    dtaler.update_variables(vars)

    dtale.global_state.cleanup(dtaler._tracked["df1"].dd._data_id)

    vars["df1"] = pd.DataFrame({"a": [4, 5, 6]})
    dtaler.update_variables(vars)

    assert len(dtaler._tracked) == 1
    assert dtaler._ignored == {"df1"}
    assert "df1" not in dtaler._tracked


def test_do_not_reinsert_externally_removed_frames_when_variable_is_the_same(dtaler):
    df1 = pd.DataFrame({"a": [1, 2, 3]})
    df2 = pd.DataFrame({"b": [1, 2, 3]})

    vars = {"df1": df1, "df2": df2}
    dtaler.update_variables(vars)

    old_dd = dtaler._tracked["df1"].dd
    dtale.global_state.cleanup(old_dd._data_id)

    dtaler.update_variables(vars)

    assert len(dtaler._tracked) == 1
    assert dtaler._ignored == {"df1"}
    assert "df1" not in dtaler._tracked


@patch("autoplot.dtaler.display")
def test_draw_doesnt_reload_hidden_dfs(display_mock, dtaler):
    df1 = pd.DataFrame({"a": [1, 2, 3]})
    df2 = pd.DataFrame({"a": [4, 5, 6]})
    output = AutoplotDisplay()

    vars = {"df1": df1, "df2": df2}
    dtaler.update_variables(vars)

    output.data_id = str(dtaler._tracked["df1"].dd._data_id)
    vars.pop("df2")
    dtaler.update_variables(vars)
    dtaler.draw(False, output)

    assert not display_mock.called
    assert len(dtaler._tracked) == 1


@patch("autoplot.dtaler.display")
def test_draw_reloads_when_visible_df_deleted(display_mock, dtaler):
    df1 = pd.DataFrame({"a": [1, 2, 3]})
    df2 = pd.DataFrame({"b": [1, 2, 3]})
    output = AutoplotDisplay()

    vars = {"df1": df1, "df2": df2}
    dtaler.update_variables(vars)

    output.data_id = str(dtaler._tracked["df2"].dd._data_id)
    vars.pop("df2")
    dtaler.update_variables(vars)
    dtaler.draw(False, output)

    assert all(_get_parameter(display_mock).data == df1)
    assert len(dtaler._tracked) == 1


@patch("autoplot.dtaler.display")
def test_ignore_new_variables_when_frozen(display_mock, dtaler):
    df1 = pd.DataFrame({"a": [1, 2, 3]})
    output = AutoplotDisplay()

    dtaler.freeze(Toast(Output()))
    dtaler.update_variables({"df1": df1})
    dtaler.draw(True, output)

    assert isinstance(_get_parameter(display_mock), Image)
    assert "df1" not in dtaler._tracked
    assert "df1" in dtaler._ignored


@patch("autoplot.dtaler.display")
def test_update_non_ignored_variables(display_mock, dtaler):
    df1 = pd.DataFrame({"a": [1, 2, 3]})
    output = AutoplotDisplay()

    dtaler.update_variables({"df1": df1})

    dtaler.freeze(Toast(Output()))
    new_df1 = pd.DataFrame({"b": [4, 5, 6]})
    dtaler.update_variables({"df1": new_df1})
    dtaler.draw(True, output)

    assert all(_get_parameter(display_mock).data == new_df1)
    assert dtaler._tracked["df1"].pdf is new_df1
    assert "df1" not in dtaler._ignored


def test_update_ignored_variables_still_ignored(dtaler):
    df1 = pd.DataFrame({"a": [1, 2, 3]})

    dtaler.freeze(Toast(Output()))
    dtaler.update_variables({"df1": df1})

    new_df1 = pd.DataFrame({"b": [4, 5, 6]})
    dtaler.update_variables({"df1": new_df1})

    assert "df1" not in dtaler._tracked
    assert "df1" in dtaler._ignored


def test_remove_ignored_variables(dtaler):
    df1 = pd.DataFrame({"a": [1, 2, 3]})

    dtaler.freeze(Toast(Output()))
    dtaler.update_variables({"df1": df1})

    dtaler.update_variables({})

    assert len(dtaler._tracked) == 0
    assert len(dtaler._ignored) == 0


@patch("autoplot.dtaler.display")
def test_continue_to_ignore_after_defrost(display_mock, dtaler):
    df1 = pd.DataFrame({"a": [1, 2, 3]})
    output = AutoplotDisplay()

    dtaler.freeze(Toast(Output()))
    dtaler.update_variables({"df1": df1})

    dtaler.defrost(Toast(Output()))

    dtaler.update_variables({"df1": df1})
    dtaler.draw(True, output)

    assert isinstance(_get_parameter(display_mock), Image)
    assert "df1" not in dtaler._tracked
    assert "df1" in dtaler._ignored


@patch("autoplot.dtaler.display")
def test_accept_new_variables_after_defrost(display_mock, dtaler):
    df1 = pd.DataFrame({"a": [1, 2, 3]})
    df2 = pd.DataFrame({"b": [4, 5, 6]})
    output = AutoplotDisplay()

    dtaler.freeze(Toast(Output()))
    dtaler.update_variables({"df1": df1})

    dtaler.defrost(Toast(Output()))

    dtaler.update_variables({"df1": df1, "df2": df2})
    dtaler.draw(False, output)

    assert all(_get_parameter(display_mock).data == df2)
    assert "df1" not in dtaler._tracked
    assert "df2" in dtaler._tracked
    assert "df1" in dtaler._ignored
    assert "df2" not in dtaler._ignored


@patch("autoplot.dtaler.display")
def test_ignore_current_variable_no_fallback(display_mock, dtaler):
    df1 = pd.DataFrame({"a": [1, 2, 3]})
    output = AutoplotDisplay()

    dtaler.update_variables({"df1": df1})

    output.data_id = str(dtaler._tracked["df1"].dd._data_id)
    dtaler.ignore_variable(Toast(Output()), "df1")
    dtaler.update_variables({"df1": df1})
    dtaler.draw(False, output)

    assert isinstance(_get_parameter(display_mock), Image)
    assert "df1" not in dtaler._tracked
    assert "df1" in dtaler._ignored


@patch("autoplot.dtaler.display")
def test_ignore_current_variable_with_fallback(display_mock, dtaler):
    df1 = pd.DataFrame({"a": [1, 2, 3]})
    df2 = pd.DataFrame({"a": [4, 5, 6]})
    output = AutoplotDisplay()

    dtaler.update_variables({"df1": df1, "df2": df2})

    output.data_id = str(dtaler._tracked["df1"].dd._data_id)
    dtaler.ignore_variable(Toast(Output()), "df1")
    dtaler.update_variables({"df1": df1, "df2": df2})
    dtaler.draw(False, output)

    assert all(_get_parameter(display_mock).data == df2)
    assert "df1" not in dtaler._tracked
    assert "df1" in dtaler._ignored


@patch("autoplot.dtaler.display")
def test_ignore_other_variable_with_fallback(display_mock, dtaler):
    df1 = pd.DataFrame({"a": [1, 2, 3]})
    df2 = pd.DataFrame({"a": [4, 5, 6]})
    output = AutoplotDisplay()

    dtaler.update_variables({"df1": df1, "df2": df2})

    output.data_id = str(dtaler._tracked["df1"].dd._data_id)
    dtaler.ignore_variable(Toast(Output()), "df2")
    dtaler.update_variables({"df1": df1, "df2": df2})
    dtaler.draw(False, output)

    assert not display_mock.called
    assert "df2" not in dtaler._tracked
    assert "df2" in dtaler._ignored


@patch("autoplot.dtaler.display")
def test_show_ignored_variable(display_mock, dtaler):
    df1 = pd.DataFrame({"a": [1, 2, 3]})
    df2 = pd.DataFrame({"a": [4, 5, 6]})
    output = AutoplotDisplay()

    dtaler.update_variables({"df1": df1, "df2": df2})

    output.data_id = str(dtaler._tracked["df1"].dd._data_id)
    dtaler.ignore_variable(Toast(Output()), "df2")
    dtaler.update_variables({"df1": df1, "df2": df2})

    dtaler.show_variable(Toast(Output()), "df2")
    dtaler.update_variables({"df1": df1, "df2": df2})
    dtaler.draw(False, output)

    assert all(_get_parameter(display_mock).data == df2)
    assert "df2" in dtaler._tracked
    assert "df2" not in dtaler._ignored


@patch("autoplot.dtaler.display")
def test_show_variable(display_mock, dtaler):
    df1 = pd.DataFrame({"a": [1, 2, 3]})
    df2 = pd.DataFrame({"a": [4, 5, 6]})
    output = AutoplotDisplay()

    dtaler.update_variables({"df1": df1, "df2": df2})

    output.data_id = str(dtaler._tracked["df2"].dd._data_id)
    dtaler.show_variable(Toast(Output()), "df1")
    dtaler.update_variables({"df1": df1, "df2": df2})
    dtaler.draw(False, output)

    assert all(_get_parameter(display_mock).data == df1)
    assert "df2" in dtaler._tracked
    assert "df2" not in dtaler._ignored


@patch("autoplot.dtaler.display")
def test_show_frozen_variable(display_mock, dtaler):
    df1 = pd.DataFrame({"a": [1, 2, 3]})
    df2 = pd.DataFrame({"a": [4, 5, 6]})
    output = AutoplotDisplay()

    dtaler.update_variables({"df1": df1})

    output.data_id = str(dtaler._tracked["df1"].dd._data_id)
    dtaler.freeze(Toast(Output()))

    dtaler.update_variables({"df1": df1, "df2": df2})

    assert "df2" not in dtaler._tracked
    assert "df2" in dtaler._ignored

    dtaler.show_variable(Toast(Output()), "df2")
    dtaler.update_variables({"df1": df1, "df2": df2})
    dtaler.draw(False, output)

    assert all(_get_parameter(display_mock).data == df2)
    assert "df2" in dtaler._tracked
    assert "df2" not in dtaler._ignored


@patch("autoplot.dtaler.display")
def test_delete_from_dtale_and_namespace(display_mock, dtaler):
    df1 = pd.DataFrame({"a": [1, 2, 3]})
    df2 = pd.DataFrame({"a": [4, 5, 6]})
    output = AutoplotDisplay()

    dtaler.update_variables({"df1": df1, "df2": df2})
    output.data_id = str(dtaler._tracked["df1"].dd._data_id)

    dtale.global_state.cleanup(dtaler._tracked["df1"].dd._data_id)
    dtaler.update_variables({"df2": df2})
    dtaler.draw(False, output)

    assert all(_get_parameter(display_mock).data == df2)
    assert "df1" not in dtaler._tracked
    assert "df1" not in dtaler._ignored


def _get_parameter(display_mock) -> Union[Image, VarData]:
    return display_mock.call_args[0][0]


@pytest.fixture
def dtaler():
    dtaler = DTaler()

    yield dtaler

    dtale.global_state.cleanup()
