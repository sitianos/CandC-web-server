import os

from .common import *

SECRET_KEY = os.getenv('SECRET_KEY')

DEBUG = False

ALLOWED_HOSTS = ['localhost', '.onion', os.getenv('SERVER_NAME')]

LINE_TOKEN = os.getenv('LINE_TOKEN')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME':  os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST'),
        'PORT': os.getenv('DB_PORT'),
    }
}
