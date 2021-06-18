from sqlalchemy import create_engine
import pandas as pd
from collections import defaultdict
from copy import deepcopy
from pyparsing import Literal, White, Word, alphanums, CharsNotIn
from pyparsing import Forward, Group, Optional, OneOrMore, ZeroOrMore
from pyparsing import pythonStyleComment, Empty, Combine
from glob import iglob

from urllib.parse import quote_plus as urlquote

from sqlalchemy.orm import sessionmaker

from src.core import injection

from sqlalchemy import Column
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.types import String, JSON, SMALLINT
from sqlalchemy.ext.declarative import declarative_base

class DatabaseFileConfigParser(object):
    key = Word(alphanums + "_-")
    space = White().suppress()
    value = CharsNotIn("\n")
    filename = Literal("!includedir") + Word(alphanums + " /.")
    comment = ("#")
    config_entry = (key + Optional(space)
                    + Optional(
                Literal("=").suppress() + Optional(space)
                + Optional(value) + Optional(space)
                + Optional("#")
            )
                    )
    single_value = key
    client_block = Forward()
    client_block << Group((Literal("[").suppress()
                           + key
                           + Literal("]").suppress())
                          + Group(ZeroOrMore(Group(config_entry)))
                          )

    include_block = Forward()
    include_block << Group(Combine(filename) +
                           Group(Group(Empty())))

    # The file consists of client_blocks and include_files
    client_file = OneOrMore(include_block | client_block).ignore(
        pythonStyleComment)

    file_header = """# File parsed and saved by privacyidea.\n\n"""

    def __init__(self, infile="/etc/mysql/my.cnf",
                 content=None,
                 opener=open):
        self.file = None
        self.opener = opener
        if content:
            self.content = content
        else:
            if '~' in infile:
                infile = infile.replace('~', '')
                from pathlib import Path
                home = str(Path.home())
                infile = home + infile
                print("infile = " + infile)
            self.file = infile
            self._read()

    def _read(self):
        """
        Reread the contents from the disk
        """
        with self.opener(self.file, 'rb') as f:
            self.content = f.read().decode('utf-8')

    def get(self):
        """
        return the grouped config
        """
        if self.file:
            self._read()
        config = self.client_file.parseString(self.content)
        return config

    def format(self, dict_config):
        '''
        :return: The formatted data as it would be written to a file
        '''
        output = ""
        output += self.file_header
        for section, attributes in dict_config.items():
            if section.startswith("!includedir"):
                output += "{0}\n".format(section)
            else:
                output += "[{0}]\n".format(section)
                for k, v in attributes.iteritems():
                    if v:
                        output += "{k} = {v}\n".format(k=k, v=v)
                    else:
                        output += "{k}\n".format(k=k)

            output += "\n"

        return output

    def get_dict(self, section=None, key=None):
        '''
        return the client config as a dictionary.
        '''
        ret = {}
        config = self.get()
        for client in config:
            client_config = {}
            for attribute in client[1]:
                if len(attribute) > 1:
                    client_config[attribute[0]] = attribute[1].rstrip()
                elif len(attribute) == 1:
                    client_config[attribute[0]] = None
            ret[client[0]] = client_config
        if section:
            ret = ret.get(section, {})
            if key:
                ret = ret.get(key)
        return ret

    def save(self, dict_config=None, outfile=None):
        if dict_config:
            output = self.format(dict_config)
            with self.opener(outfile, 'wb') as f:
                for line in output.splitlines():
                    f.write(line.encode('utf-8') + "\n")

class DatabaseManagerFactory(object):

    @staticmethod
    def create_mysql_database_manager(host, port, database, user, password):
        engine_info = 'mysql+pymysql://{0}:{1}@{2}:{3}/{4}'.format(user, password, host, port, database)
        return DatabaseManager(engine_info)

    @staticmethod
    def create_sqlite_database_manager(sqlite_file_path):
        engine_infor = f'sqlite:///{sqlite_file_path}'
        dm = DatabaseManager(engine_infor)
        Base = declarative_base()
        Base.metadata.create_all(dm.engine)
        return dm

class DatabaseManager(object):
    def __init__(self, engineinfo):
        self.engineinfo = engineinfo
        self.engine = create_engine(self.engineinfo, echo = True)
        session = sessionmaker(bind=self.engine)
        self.session = session()
        # self.config = self.session.query(Configuration)

    def get_dataframe(self, sql_or_table = None, chunksize = None):
        if len(sql_or_table) < 30:
            sql_or_table = 'SELECT * FROM ' + sql_or_table
        data = pd.read_sql_query(sql_or_table, con = self.engine, chunksize = chunksize)
        return data

    def read_table_to_dataframe(self, sql_command, chunksize = None):
        data = pd.read_sql_query(sql_command, con=self.engine, chunksize=chunksize)
        return data

    def excute(self, sql_command):
        with self.engine.begin() as conn:
            conn.execute(sql_command)
        self.engine.dispose()

    def insert(self, df,  data_table, if_exists='append', dtype = None):
        df.to_sql(name=data_table, con=self.engine, if_exists=if_exists, index=False, dtype=dtype)

    def replace_by_recorddate(self, df, data_table, recorddate):
        with self.engine.begin() as conn:
            delete_str = "DELETE FROM " + data_table + " WHERE RECORDDATE = '{0}'".format(recorddate)
            conn.execute(delete_str)
            self.insert(df, data_table)
        self.engine.dispose()

    def update_by_join(self, df, data_table, set_columns = [], inner_join_columns = [], where_columns = {}):
        temp_table = 'temp_dumping_table_for_' + data_table
        set_statement = ""
        if set_columns:
            assign = ['t.' +col + ' = temp.' + col for col in set_columns]
            if len(assign) > 1:
                assign = ' , '.join(assign)
            set_statement = " SET " + assign

        on_statement = ""
        if inner_join_columns:
            on_column = ['t.' + col + ' = temp.' + col for col in inner_join_columns]
            if len(on_column) > 1:
                on_column = ' AND '.join(on_column)
            on_statement = " ON "  +  on_column

        where_statement = ""
        if where_columns:
            where_column = []
            for col, value in where_columns.items():
                where_column.append('t.' + col + ' = ' + value)

            where_column = ' AND '.join(where_column) if len(where_column) > 1 else ''.join(where_column)
            where_statement = " WHERE  " + where_column

        sql = "UPDATE " + temp_table+ " AS temp " +  " INNER JOIN " +  data_table + " AS t " +  on_statement +  set_statement + where_statement

        df.to_sql(temp_table, self.engine, if_exists='replace', index=False)
        with self.engine.begin() as conn:  # TRANSACTION
            conn.read_table_to_dataframe(sql)
        self.engine.dispose()

    def batch_insert(self, data_dict):
        for name, df in data_dict.items():
            df.to_sql(name=name, con=self.engine, if_exists='append', index=False)

    def dispose(self):
        self.engine.dispose()

    def check_existed_date_running(self, table_name,  date, limit = 10):
        sql_query = "SELECT DISTINCT RECORDDATE FROM " + table_name + "  WHERE RECORDDATE = '" + date + "' LIMIT " + str(limit)
        date_df = self.get_dataframe(sql_query)
        return (not date_df.empty)

    def get_config_attribute(self, config_name):
        for item in self.config:
            if item.CONFIG_NAME == config_name:
                return item
        return None

    def create_table_from_dataframe(self, df: pd.DataFrame, table_name:str):
        columns = df.columns
        dtypes = df.dtypes
        query = f"CREATE TABLE IF NOT EXISTS {table_name} ("

        fields = []
        for field, type in zip(columns, dtypes):
            fields.append(f"'{field}' {type}")

        query = query + ", ".join(fields)  + ")"

        self.excute(query)
        return table_name
