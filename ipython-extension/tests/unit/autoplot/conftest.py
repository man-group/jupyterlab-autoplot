import sys
import types
import builtins as builtin_mod

import mock
import pandas as pd
import pytest
from IPython import InteractiveShell
from IPython.core import page
from IPython.testing import tools

from autoplot.extensions.toast import Toast


@pytest.fixture()
def datetime_index():
    """Return a new pandas datetime index of the given length."""

    def with_params(length: int):
        return pd.date_range(start="2020-01-01", periods=length, freq="d")

    yield with_params


@pytest.fixture()
def datetime_series(datetime_index):
    """Return a new datetime indexed series with values all equal to `1`."""

    def with_params(length: int):
        return pd.Series([1] * length, index=datetime_index(length))

    yield with_params


@pytest.fixture()
def mock_toast():
    mock.NonCallableMock()
    return mock.MagicMock(spec=Toast)


@pytest.fixture(scope="session")
def session_ip():
    return _start_ipython()


@pytest.fixture(scope="function")
def ip(session_ip):
    yield session_ip
    session_ip.run_line_magic(magic_name="unload_ext", line="autoplot")
    session_ip.run_line_magic(magic_name="reset", line="-f")


def _start_ipython():
    """Start a global IPython shell, which we need for IPython-specific syntax."""

    def xsys(self, cmd):
        """Replace the default system call with a capturing one for doctest."""
        # We use getoutput, but we need to strip it because pexpect captures
        # the trailing newline differently from commands.getoutput
        print(self.getoutput(cmd, split=False, depth=1).rstrip(), end="", file=sys.stdout)
        sys.stdout.flush()

    def _showtraceback(self, etype, evalue, stb):
        """Print the traceback purely on stdout for doctest to capture it."""
        print(self.InteractiveTB.stb2text(stb), file=sys.stdout)

    global get_ipython

    # This function should only ever run once!
    if hasattr(_start_ipython, "already_called"):
        return
    _start_ipython.already_called = True

    # Store certain global objects that IPython modifies
    _displayhook = sys.displayhook
    _excepthook = sys.excepthook
    _main = sys.modules.get("__main__")

    # Create custom argv and namespaces for our IPython to be test-friendly
    config = tools.default_config()
    config.TerminalInteractiveShell.simple_prompt = True

    # Create and initialize our test-friendly IPython instance.
    shell = InteractiveShell.instance(config=config)

    # A few more tweaks needed for playing nicely with doctests...

    # remove history file
    shell.tempfiles.append(config.HistoryManager.hist_file)

    # These traps are normally only active for interactive use, set them
    # permanently since we'll be mocking interactive sessions.
    shell.builtin_trap.activate()

    # Modify the IPython system call with one that uses getoutput, so that we
    # can capture subcommands and print them to Python's stdout, otherwise the
    # doctest machinery would miss them.
    shell.system = types.MethodType(xsys, shell)

    shell._showtraceback = types.MethodType(_showtraceback, shell)

    # IPython is ready, now clean up some global state...

    # Deactivate the various python system hooks added by ipython for
    # interactive convenience so we don't confuse the doctest system
    sys.modules["__main__"] = _main
    sys.displayhook = _displayhook
    sys.excepthook = _excepthook

    # So that ipython magics and aliases can be doctested (they work by making
    # a call into a global _ip object).  Also make the top-level get_ipython
    # now return this without recursively calling here again.
    _ip = shell
    get_ipython = _ip.get_ipython
    builtin_mod._ip = _ip
    builtin_mod.ip = _ip
    builtin_mod.get_ipython = get_ipython

    # Override paging, so we don't require user interaction during the tests.
    def nopage(strng, start=0, screen_lines=0, pager_cmd=None):
        if isinstance(strng, dict):
            strng = strng.get("text/plain", "")
        print(strng)

    page.orig_page = page.pager_page
    page.pager_page = nopage

    return _ip
