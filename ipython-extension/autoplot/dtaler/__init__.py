import time

from pkg_resources import resource_filename
from typing import Dict, Union, List, Tuple, Optional, NamedTuple, Set, Iterable, Sequence

import dtale
import dtale.views
import dtale.global_state
from autoplot.extensions.autoplot_display import AutoplotDisplay
from autoplot.extensions.toast import Toast, ToastType
from IPython.display import clear_output, display, Image
import pandas as pd

from autoplot.view_manager import View

DataId = str
VariableName = str


class VarData(NamedTuple):
    pdf: Union[pd.Series, pd.DataFrame]
    dd: dtale.views.DtaleData


class DTaler(View):
    """
    Implements the dtale backend for this project. This class will call
    dtale.show for each new dataframe, given dtale's implementation that means
    we will have a single dtale server per kernel. This class uses the data_id
    field in AutoplotDisplay, which is populated from the frontend. That tells
    it which table is being shown to the user.
    """

    def __init__(self) -> None:
        # This is the current state of the variables we track. The tracked dict are the active variables, ignored and
        # forced_shown are variables the user wants to either ignore or stop ignoring
        self._tracked: Dict[str, VarData] = {}
        self._ignored: Set[str] = set()
        self._frozen = False

        # These variables are set using magic commands and informs us of the user's intentions before update_variables
        # is called.
        self._ignore_next: List[str] = []
        self._show_next: List[str] = []

        # The following variables are refreshed every time update_variables is called. They represent the difference
        # between what's changed in the cell and the current internal state.
        self._new: List[VariableName] = []
        self._force_show: List[VariableName] = []
        self._updated: List[DataId] = []
        self._deleted: List[DataId] = []

        # This is a helper variable used to check whether it's the first time dtale.show is called. Due to race
        # conditions in the package, we can't call show twice too fast.
        self._first_show = True

    def update_variables(self, pandas_vars: Dict[str, Union[pd.Series, pd.DataFrame]]) -> None:
        # These variables are populated with the difference between the current state and the new variables
        self._updated = []
        self._new = []
        self._deleted = []
        self._force_show = []

        # 1. The first step is to clean up our internal structures, so it matches what is in dtale and what is currently
        #    available in the namespace.

        #   1.a. Remove and ignore variables deleted in dtale
        removed = _removed_in_dtale(self._tracked.items())
        for name in removed:
            self._remove_tracked_var(name)
            self._ignored.add(name)

        #   1.b. Clean up all variables that are not in the namespace anymore. If they were deleted in dtale and from
        #        the namespace, completely forget about the name, rather than keeping it in the ignore list.
        for name in (self._ignored | set(self._tracked.keys())) - set(pandas_vars.keys()):
            self._remove_tracked_var(name)
            if name in self._ignored:
                self._ignored.remove(name)

        # 2. Ignore all new variables when frozen. Add to ignored all variables the user wants to ignore but remove all.
        #    variables they want to show.
        if self._frozen:
            self._ignored |= set(pandas_vars.keys()) - set(self._tracked.keys())
        # TODO: Currently, we do not know the order variables are shown/ignored so show will have precendence over
        #       ignore if they are both executed in the same cell.
        self._ignored |= set(self._ignore_next)
        self._ignored -= set(self._show_next)
        self._force_show = self._show_next

        #   2.a. clean up user intentions now that we've consumed them.
        self._ignore_next, self._show_next = [], []

        # 3. Now that we know which variables to ignore, make sure they are all removed from the tracked dict as needed.
        for name in self._ignored:
            self._remove_tracked_var(name)

        # 4. Start tracking variables which are not ignored
        for name in set(pandas_vars.keys()) - (set(self._tracked.keys()) | self._ignored):
            self._add_tracked_var(name, pandas_vars[name])

        # 5. Update tracked variables which have changed
        updated_variables = _filter_updated(pandas_vars.items(), self._tracked.copy())
        for name, var in updated_variables.items():
            self._update_tracked_var(name, var)

    def draw(self, force: bool, output: AutoplotDisplay) -> None:
        refresh = False
        current = dtale.get_instance(int(output.data_id))
        if current is None:
            current = Image(data=resource_filename(__name__, "assets/imgs/dtale.png"))
        # The conditionals below encode precedence. Whatever the user wants to show takes is the preferred value to
        # display, followed by new values and so on.
        if set(self._force_show) & set(self._tracked.keys()):
            for key in reversed(self._force_show):
                if key in self._tracked:
                    current = self._tracked[key].dd
                    refresh = True
                    break
        elif set(self._new) & set(self._tracked.keys()):
            for key in reversed(self._new):
                if key in self._tracked:
                    current = self._tracked[key].dd
                    refresh = True
                    break
        elif self._updated:
            if output.data_id in self._updated:
                refresh = True
        elif self._deleted:
            if output.data_id in self._deleted:
                # We don't know what the user is seeing, so we have to switch to an arbitrary dataframe, in case
                # they are seeing the deleted one
                current = _next_dtale_data()
                refresh = True

        if refresh or force:
            with output:
                clear_output()
                display(current)

    def freeze(self, toast: Toast) -> None:
        if not self._frozen:
            toast.show(
                "Dtale is 'frozen'. New DFs will not be tracked, but tracked ones will still update.", ToastType.info
            )
        self._frozen = True

    def defrost(self, toast: Toast) -> None:
        if self._frozen:
            toast.show(
                "Dtale is 'defrosted'. DFs defined while it was frozen will not be automatically picked up. Use --show "
                " to get them added.",
                ToastType.info,
            )
        self._frozen = False

    def ignore_variable(self, toast: Toast, var_name: str) -> None:
        self._ignore_next.append(var_name)

    def show_variable(self, toast: Toast, var_name: str) -> None:
        self._show_next.append(var_name)

    def _dtale_show(self, *args, **kwargs) -> dtale.views.DtaleData:
        result = dtale.show(*args, **kwargs)
        if self._first_show:
            # when running show for the first time, if that happens in rapid succession, it can cause race conditions
            # internal to dtale
            time.sleep(0.3)
            self._first_show = False
        return result

    def _remove_tracked_var(self, var_name: str):
        vardata = self._tracked.pop(var_name, None)
        if vardata:
            data_id = vardata.dd._data_id
            dtale.global_state.cleanup(data_id)
            try:
                # this will be fixed in newer version of D-Tale
                del dtale.global_state._default_store._data_names[var_name]
            except KeyError:
                pass
            self._deleted.append(str(vardata.dd._data_id))

    def _add_tracked_var(self, name, var):
        dd = self._dtale_show(data=var, ignore_duplicate=True, reaper_on=False, name=name, hide_shutdown=True)
        self._tracked[name] = VarData(pdf=var, dd=dd)
        self._new.append(name)

    def _update_tracked_var(self, name, var):
        vardata = self._tracked[name]
        vardata.dd.data = var
        self._tracked[name] = VarData(pdf=var, dd=vardata.dd)
        self._updated.append(str(vardata.dd._data_id))


def _removed_in_dtale(tracked: Iterable) -> Set[str]:
    removed: Set[str] = set()
    for name, vardata in tracked:
        if dtale.get_instance(int(vardata.dd._data_id)) is None:
            removed.add(name)
    return removed


def _filter_updated(pandas_vars: Iterable, tracked: Dict[str, VarData]) -> Dict[str, Union[pd.Series, pd.DataFrame]]:
    result: Dict[str, Union[pd.Series, pd.DataFrame]] = {}

    for name, var in pandas_vars:
        vardata = tracked.get(name)
        if vardata is not None and vardata.pdf is not var:
            result[name] = var

    return result


def _next_dtale_data():
    data_id = next(iter(dtale.global_state.keys()), None)
    if data_id is not None:
        return dtale.get_instance(data_id)
    else:
        return Image(data=resource_filename(__name__, "assets/imgs/dtale.png"))
