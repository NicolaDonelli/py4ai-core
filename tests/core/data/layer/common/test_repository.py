"""
Test config files
"""

from py4ai.core.data.layer.common.repository import QueryOptions
from py4ai.core.tests.core import TestCase


class TestConfig(TestCase):
    query = QueryOptions(0, 10)

    def test_query_options_copy(self) -> None:
        self.assertEqual(5, self.query.copy(page_start=5).page_start)
