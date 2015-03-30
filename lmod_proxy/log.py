# -*- coding: utf-8 -*-
"""Offers a function to configure python logging with a flask app"""
import logging
from logging.handlers import SysLogHandler
import os
import platform


def configure_logging(app):
    """
    Set the log level for the application
    """
    config_log_level = app.config.get('LMODP_LOG_LEVEL')

    # Set up format for default logging
    hostname = platform.node().split('.')[0]
    formatter = ('%(asctime)s %(levelname)s %(process)d [%(name)s] '
                 '%(filename)s:%(lineno)d - '
                 '{hostname}- %(message)s').format(hostname=hostname)

    config_log_int = None
    set_level = None

    if config_log_level and not set_level:
        config_log_int = getattr(logging, config_log_level.upper(), None)
        if not isinstance(config_log_int, int):
            raise ValueError('Invalid log level: {0}'.format(config_log_level))
        set_level = config_log_int

    # Set to NotSet if we still aren't set yet
    if not set_level:
        set_level = config_log_int = logging.NOTSET

    # Setup basic StreamHandler logging with format and level (do
    # setup in case we are main, or change root logger if we aren't.
    logging.basicConfig(format=formatter)
    root_logger = logging.getLogger()
    root_logger.setLevel(set_level)

    # Get everything ready to setup the syslog handler
    address = None
    if os.path.exists('/dev/log'):
        address = '/dev/log'
    elif os.path.exists('/var/run/syslog'):
        address = '/var/run/syslog'
    else:
        address = ('127.0.0.1', 514)
    # Add syslog handler before adding formatters
    root_logger.addHandler(
        SysLogHandler(address=address, facility=SysLogHandler.LOG_LOCAL0)
    )

    # Add our formatter to all the handlers
    for handler in root_logger.handlers:
        handler.setFormatter(logging.Formatter(formatter))

    return config_log_int
