from unittest import TestCase

from src.core import ROOT
from src.core.database import DatabaseManagerFactory
import pandas as pd

class TestDatabaseManger(TestCase):
    def test_create_sqlite_dm(self):
        sqlite_file_path = ROOT + '/data/' + 'sqlite.db'
        dm = DatabaseManagerFactory.create_sqlite_database_manager(sqlite_file_path)

        assert dm is not None

    def test_create_sqlite_table(self):
        sqlite_file_path = ROOT + '/data/' + 'sqlite.db'
        dm = DatabaseManagerFactory.create_sqlite_database_manager(sqlite_file_path)
        df = pd.read_csv('https://plotly.github.io/datasets/country_indicators.csv')

        dm.insert(df, dm.create_table_from_dataframe(df, "test1"))
        assert dm is not None