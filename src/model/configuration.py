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



class ConfigurationDefaultValue:
    CONFIG_TYPE_STRING = 1
    CONFIG_STATUS_ACTIVE = 1


class Configuration(declarative_base()):
    __tablename__ = 'configuration'
    CONFIG_NAME = Column(String(128), nullable=False, primary_key=True)
    CONFIG_VALUE = Column(JSON, nullable=False)
    CONFIG_TYPE = Column(SMALLINT, default=ConfigurationDefaultValue.CONFIG_TYPE_STRING)
    CONFIG_STATUS = Column(SMALLINT, default=ConfigurationDefaultValue.CONFIG_STATUS_ACTIVE)
