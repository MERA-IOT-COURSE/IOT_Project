#!/usr/bin/python3

import os
import logging
import logging.config

sources_dir = os.path.dirname(os.path.abspath(__file__))

loggerConfig = {
    "version": 1,
    "formatters": {
        "standart": {
            "format": "[%(asctime)s] %(levelname)s %(name)s: %(message)s"
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "filters": [],
            "formatter": "standart",
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "DEBUG",
            "filename": os.path.join(sources_dir, 'logs.log'),
            "formatter": "standart"
        }
    },
    "loggers": {
        "root": {
            "handlers": ["console", "file"],
            "level": "DEBUG"
        }
    }
}

logging.config.dictConfig(loggerConfig)
logger = logging.getLogger("root")
