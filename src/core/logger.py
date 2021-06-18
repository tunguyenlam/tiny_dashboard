import os
import logging
import threading
from _datetime import datetime
from src.configuration import settings

_loggers = {}
_lock = threading.RLock()


def _acquire_lock():
    if _lock:
        _lock.acquire()


def _release_lock():
    if _lock:
        _lock.release()


class Logger(object):
    LEVELS = {
        'debug': logging.DEBUG,
        'info': logging.INFO,
        'warning': logging.WARNING,
        'error': logging.ERROR,
        'critical': logging.CRITICAL
    }
    MODES = {
        'override': 'w+',
        'appending': 'a'
    }

    def __init__(self, name, log_date = None, mode='a', console=True):
        self.name = name
        self.log_date = log_date
        self.own_logger = self.get_logger(name, log_date, mode, console)
        self.step_check_start_time = datetime.now()
        self.current_step = 1
        self.summary = []

    def summary_and_clear(self):
        for msg in self.summary:
            self.own_logger.info(msg)
        self.summary = []

    @staticmethod
    def get_logger(name, log_date = None, mode='a', console=True):
        logger = _loggers.get(name, None)
        if not logger:
            _acquire_lock()
            try:
                logger = logging.getLogger(name)
                logger.setLevel(logging.INFO)

                formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

                # create file handler which logs even debug messages
                # if is_logging:
                if log_date is None:
                    log_date = datetime.now().date().strftime('%Y-%m-%d')

                fh = logging.FileHandler(Logger.get_logger_path(name, log_date), mode=mode)
                fh.setFormatter(formatter)
                logger.addHandler(fh)

                # create console handler with a higher log level
                # if console:
                #     ch = logging.StreamHandler()
                #     ch.setFormatter(formatter)
                #     logger.addHandler(ch)

                _loggers[name] = logger
            finally:
                _release_lock()

        return logger

    def info(self, msg):
        self.summary.append(msg)
        self.own_logger.info(msg)

    def warn(self, msg):
        self.summary.append(msg)
        self.own_logger.warning(msg)

    def error(self, msg):
        self.summary.append(msg)
        self.own_logger.error(msg)

    def step_check(self, msg):
        self.summary.append(msg)
        start = self.step_check_start_time
        self.step_check_start_time = datetime.now()
        self.info("{0} || STEP-{1}: {2}  || {3}".format(start, self.current_step, msg, self.step_check_start_time))
        self.current_step +=1

    @staticmethod
    def get_logger_path(name, log_date):
        """
            :param name: e.g. FX_SMILE_STALE_REPORT_MODE_0_ (report_name and report_mode)
            :param log_date: e.g. 2019-08-07
            :return: e.g. {RAD_ROOT_FOLDER}/Logs/FX_SMILE_STALE_REPORT_MODE_0_2019-08-07.log
        """
        # create log folder if it does not exist
        os.makedirs(f'{settings.BASE_DIR}/logs/', exist_ok=True)

        return f'{settings.BASE_DIR}/logs/{name}_{log_date}.log'

    @staticmethod
    def delete_logger_path(name, log_date):
        log_file_path = Logger.get_logger_path(name, log_date)
        if os.path.exists(log_file_path):
            os.remove(log_file_path)

    @classmethod
    def log(cls, log_name, log_date, msg):
        if not isinstance(log_date, str):
            log_date = log_date.strftime('%Y-%m-%d')
        logger = Logger.get_logger(log_name, log_date)
        logger.info(msg)

        def inner_function(function):
            def wrapper(*args, **kwargs):
                function(*args, **kwargs)

            return wrapper

        return inner_function
