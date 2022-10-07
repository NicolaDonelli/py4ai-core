from py4ai.core.data.model.ml import PandasDataset, PandasTimeIndexedDataset
from py4ai.core.datasets import get_weather_nyc_dataset, get_unbalanced_dataset
from py4ai.core.tests.core import logTest, TestCase


class TestLoadDatasets(TestCase):
    @logTest
    def test_unbalanced_dataset(self):
        self.assertIsInstance(get_unbalanced_dataset(), PandasDataset)

    @logTest
    def test_time_indexed_dataset(self):
        self.assertIsInstance(get_weather_nyc_dataset(), PandasTimeIndexedDataset)
