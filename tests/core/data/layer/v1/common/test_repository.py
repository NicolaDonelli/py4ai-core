"""
Test config files
"""

import unittest

from py4ai.core.data.layer.v1.common.repository import QueryOptions


class TestConfig(unittest.TestCase):
    query = QueryOptions(0, 10)

    def test_query_options_copy(self) -> None:
        self.assertEqual(5, self.query.copy(page_start=5).page_start)
