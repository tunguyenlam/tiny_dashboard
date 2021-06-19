import os
import sys
import logging
from src.configuration.auto_config import AutoConfigImpl

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
# BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_DIR = os.path.abspath(__file__)

BASE_DIR = os.path.abspath(os.path.join(BASE_DIR, os.path.pardir, os.path.pardir,os.path.pardir))
print("BASE_DIR = " + BASE_DIR)

APPS_DIR = '{0}/src'.format(BASE_DIR)
# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
# SECRET_KEY = config('SECRET_KEY')

config = AutoConfigImpl(BASE_DIR + '/.env')
this_module = sys.modules[__name__]
for option, value in config.config.repository.data.items():
    setattr(this_module, option, value)
