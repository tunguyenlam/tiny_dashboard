from src.core import ROOT
from src.core.database import DatabaseManagerFactory
from src.model.queries import Models


class Controller(object):
    def __init__(self):
        sqlite_file_path = ROOT + '/data/' + 'sqlite.db'
        dm = DatabaseManagerFactory.create_sqlite_database_manager(sqlite_file_path)
        self.df = dm.get_dataframe(Models.test)

