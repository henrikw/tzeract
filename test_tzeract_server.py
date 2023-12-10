#!/usr/bin/python3

import pytest

from tzeract_server import valid_command


@pytest.mark.parametrize("cmd, expected", [
    ('ls', True),
    ('lsx', True),
    ('mkdir', True),
    ('touch', True),
    ('', False),
    ('xx', False)
])
def test_valid_command(cmd, expected):
    assert valid_command(cmd) == expected
