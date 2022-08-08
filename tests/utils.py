# Copyright 2022 (c) Vincent Dutordoir
# SPDX-License-Identifier: Apache-2.0

# move to conftest.py?
from typing import List


class Out:

    def __init__(self):
        self.lines: List[str] = []

    def write(self, s):
        self.lines.append(s)

    def clear(self):
        self.lines.clear()

    def assert_equal(self, str_list: List[str], reset_if_successful: bool = True):

        def _check(expected, given):
            assert (expected == given
                   ), f"Strings don't match. Expected: '{expected}' != Given: '{given}'"

        assert len(self.lines) == len(str_list), f"{len(self.lines)} != {len(str_list)}"
        list(map(lambda t: _check(t[0], t[1]), zip(self.lines, str_list)))

        if reset_if_successful:
            self.clear()
