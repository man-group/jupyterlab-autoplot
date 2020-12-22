import pytest


def test_load_extension(ip):
    assert len(ip.events.callbacks["post_run_cell"]) == 0

    ip.run_line_magic(magic_name="load_ext", line="autoplot")
    ip.run_cell("x = 1")

    with pytest.raises(ValueError):
        ex = ip.get_exception_only()
        assert ex is None
    assert len(ip.events.callbacks["post_run_cell"]) == 1
