import os
from abc import ABC, abstractmethod
from src.core.database import DatabaseManager
from src.core.injection import add_to_context
from src.configuration import settings

from src.core import logger



class PipeLine(ABC):
    def __init__(self, *args, **kwargs):
        self.transformers = []
        self.task_name = args[0] if len(args) > 0 else "UNKNOWN_TASK"
        self.mode = kwargs['mode'] if 'mode' in kwargs else 0
        self.report_date = kwargs['task_date'] if 'task_date' in kwargs else ""
        self.logger = logger.Logger(f'{self.task_name}_MODE_{self.mode}_', self.report_date)
        self.check_existence = []

    def validate_input(self):
        for data in self.check_existence:
            assert os.path.exists(data), f"Input data: {data} does not exist"

    def decorator(self):
        def wrapper(self, *args, **kwargs):
            """
            Params must be in tuple, dict.
            :param args:
            :param kwargs:
            :return:
            """

            def get_parameters(*args, **kwargs):
                if result is not None and isinstance(result, tuple) and isinstance(result[-1], dict):  # args, kwargs
                    kwargs = result[-1]
                    args = result[:-1]
                elif result is not None and isinstance(result, dict):  # ,kwargs
                    args = []
                    kwargs = result
                elif result is not None and isinstance(result, tuple):  # args,
                    kwargs = {}
                    args = result
                else:
                    kwargs = {}
                    if not isinstance(result, tuple):
                        args = (result,)
                    else:
                        args = result

                return args, kwargs

            self.validate_input()
            result = self.open(*args, **kwargs)
            args, kwargs = get_parameters(*args, **kwargs)

            result = self.forward(*args, **kwargs)
            args, kwargs = get_parameters(*args, **kwargs)

            return self.close(*args, **kwargs)




        return wrapper

    @abstractmethod
    def open(self, *args, **kwargs):
        """
        Params must be in tuple, dict.
        :param args:
        :param kwargs:
        :return:
        """
        pass
    @abstractmethod
    def close(self, *args, **kwargs):
        """
        Params must be in tuple, dict.
        :param args:
        :param kwargs:
        :return:
        """
        pass

    @decorator
    def __call__(self, *args, **kwargs):
        """
        Params must be in tuple, dict.
        :param args:
        :param kwargs:
        :return:
        """
        pass

    def forward(self, *args, **kwargs):
        """
        Params must be in tuple, dict.
        :param args:
        :param kwargs:
        :return:
        """
        for transformer in self.transformers[:-1]:
            result = transformer(*args, **kwargs)
            if result is not None and isinstance(result, tuple) and isinstance(result[-1], dict): # args, kwargs
                kwargs = result[-1]
                args = result[:-1]
            elif result is not None and isinstance(result, dict): # ,kwargs
                args = []
                kwargs = result
            elif result is not None and isinstance(result, tuple): # args,
                kwargs = {}
                args = result
            else:
                kwargs = {}
                if not isinstance(result, tuple):
                    args = (result,)
                else:
                    args = result

        return self.transformers[-1](*args, **kwargs) if self.transformers else None

    def get_first_transformer(self):
        return self.transformers[0]

    def get_final_transformer(self):
        return self.transformers[-1]

    def add_transformer(self, transformer):
        self.transformers.append(transformer)

    def remove_transformer(self, transformer):
        self.transformers.remove(transformer)

    def is_empty_pipeline(self):
        return (self.transformers is None or len(self.transformers) == 0)

class Transformer(ABC):
    def __init__(self, *args, **kwargs):
        self.is_done = False

    def __call__(self, *args, **kwargs):
        """
        Params must be in tuple, dict.
        :param args:
        :param kwargs:
        :return:
        """
        return self.transform(*args, **kwargs)

    @abstractmethod
    def transform(self, *args, **kwargs):
        """
        Params must be in tuple, dict.
        :param args:
        :param kwargs:
        :return:
        """
        pass

class PipeLineExecutorBase(ABC):
    def __init__(self):
        if settings.data_store == 'file':
            from src.tests.database_mock import database_manager as mock_database_manager
            database_manager = mock_database_manager
        else:
            database_manager = DatabaseManager(host=settings.host, port=settings.port, database=settings.database,
                                               user=settings.user,
                                               password=settings.password)
        add_to_context(database_manager, 'database_manager')

    @abstractmethod
    def execute(self, *args, **kwargs):
        pass


class PipeLineExecutor(PipeLineExecutorBase):
    def __init__(self):
        super(PipeLineExecutor, self).__init__()

    def execute(self, *args, **kwargs):
        instance = PipeLineFactory.create_pipeline(*args, **kwargs)
        instance(*args, **kwargs)

import importlib


class PipeLineFactory(object):
    TASK_REGISTRY = {
        "STALE_VALUE_REPORT": {
                "module_name": 'business_logic.ir.stale_view_report',
                "class": "StaleViewReportGenerator"
          },
    }

    @staticmethod
    def create_pipeline(*args, **kwargs):
        task_name = args[0]
        executed_entry = PipeLineFactory.TASK_REGISTRY[task_name]
        module_name = executed_entry['module_name']
        class_name = executed_entry['class']
        module = importlib.import_module(module_name)
        class_ = getattr(module, class_name)

        instance = class_(*args, **kwargs)
        return instance