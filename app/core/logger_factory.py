import http.client as http_client
import logging
from logging import LogRecord

import structlog
from orjson import orjson
from structlog.typing import EventDict

from core.settings import settings, Environment


class OneLineExceptionFormatter(logging.Formatter):
    _spacer: str = '|'

    def set_spacer(self, spacer: str):
        self._spacer = spacer

    def formatException(self, ei) -> str:
        return repr(super().formatException(ei))

    def format(self, record: LogRecord) -> str:
        result = super().format(record)

        if record.exc_text:
            result = result.replace('\n', self._spacer)
        return result


def logger_factory():
    # Set logging level
    logging_level_interpreter = {
        Environment.PROD: 'INFO',
        Environment.TEST: 'INFO',
        Environment.DEV: 'DEBUG' if settings.DEBUG else 'INFO'
    }

    name_to_level = {
        'CRITICAL': logging.CRITICAL,
        'ERROR': logging.ERROR,
        'WARNING': logging.WARNING,
        'INFO': logging.INFO,
        'DEBUG': logging.DEBUG,
        'NOTSET': logging.NOTSET,
    }

    logging_level = logging_level_interpreter[settings.ENVIRONMENT]

    def add_api_name(
            logger: logging.Logger, method_name: str, event_dict: EventDict
    ) -> EventDict:
        """ Add api name to logger """
        event_dict['api'] = settings.API_NAME
        return event_dict

    structlog.configure(
        cache_logger_on_first_use=True,
        wrapper_class=structlog.make_filtering_bound_logger(name_to_level[logging_level]),
        processors=[
            add_api_name,
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.format_exc_info,
            structlog.processors.TimeStamper(fmt="iso", utc=True),
            structlog.processors.JSONRenderer(serializer=orjson.dumps),
        ],
        logger_factory=structlog.BytesLoggerFactory(),
    )

    # Create root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging_level)

    # Create logger
    logger = logging.getLogger('_api_')
    logger.setLevel(logging_level)
    logger.propagate = False

    # Create console handler and set level to debug
    ch = logging.StreamHandler()
    ch.setLevel(logging_level)

    # Create formatter
    formatter_format = '%(asctime)s - %(levelname)s - %(module)s - line:%(lineno)d - %(message)s'
    if settings.ENVIRONMENT == Environment.PROD:
        formatter = OneLineExceptionFormatter(formatter_format)
        formatter.set_spacer(' - ')
    else:
        formatter = logging.Formatter(formatter_format)

    # Add formatter to ch
    ch.setFormatter(formatter)

    # Add ch to logger
    logger.addHandler(ch)
    # Add ch to root logger
    root_logger.addHandler(ch)

    if settings.DEBUG:
        http_client.HTTPConnection.debuglevel = 1
        requests_log = logging.getLogger("requests.packages.urllib3")
        requests_log.setLevel(logging.DEBUG)
        requests_log.propagate = True
