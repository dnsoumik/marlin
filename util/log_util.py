#!/usr/bin/env python
# -*- coding: utf-8 -*-

import inspect
import logging
from logging.handlers import TimedRotatingFileHandler
import os
import sys

# from time_util import timeNow
logger = logging.getLogger()
funcFormat = '{} +{} {} '

LOG_FILE_PATH = './log/run.log'


# handler = TimedRotatingFileHandler(LOG_FILE_PATH,
#                                    when="S",
#                                    interval=1, )
# logger.addHandler(handler)

class StreamToLogger(object):
    """
    Fake file-like stream object that redirects writes to a logger instance.
    """

    def __init__(self, logger, log_level=logging.INFO):
        self.logger = logger
        self.log_level = log_level
        self.linebuf = ''

    def write(self, buf):
        temp_linebuf = self.linebuf + buf
        self.linebuf = ''
        for line in temp_linebuf.splitlines(True):
            # From the io.TextIOWrapper docs:
            #   On output, if newline is None, any '\n' characters written
            #   are translated to the system default line separator.
            # By default sys.stdout.write() expects '\n' newlines and then
            # translates them so this is still cross platform.
            if line[-1] == '\n':
                self.logger.log(self.log_level, line.rstrip())
            else:
                self.linebuf += line

    def flush(self):
        if self.linebuf != '':
            self.logger.log(self.log_level, self.linebuf.rstrip())
        self.linebuf = ''


class Log:
    # Adding Log rotation
    # strftime format %Y-%m-%d_%H-%M-%S.
    # Calculate the real rollover interval, which is just the number of
    # seconds between rollovers.  Also set the filename suffix used when
    # a rollover occurs.  Current 'when' events supported:
    # S - Seconds
    # M - Minutes
    # H - Hours
    # D - Days
    # midnight - roll over at midnight
    # W{0-6} - roll over on a certain day; 0 - Monday

    # Rotation set per hour
    rotationHandler = TimedRotatingFileHandler(
        LOG_FILE_PATH,
        when="H",
        interval=1,
    )

    logging.basicConfig(
        # filename=LOG_FILE_PATH,
        # filemode='a',
        # format='[ %(asctime)s, %(msecs)d ] [%(name)s] [%(levelname)s] %(message)s',
        format='| %(asctime)s,%(msecs).3d | %(levelname).1s | %(name)1s | %(message)s',
        # format='[ %(asctime)s, %(msecs)d ] [ ' + '%(levelname).4s' + ' ] %(threadName)s '
        #                                     '[ %(filename)s:%(lineno)s %(funcName)s ] : %(message)s',
        datefmt='%Y:%m:%d %H:%M:%S',
        level=logging.DEBUG,
        handlers=[rotationHandler]
    )
    logging.info('------')
    func = inspect.currentframe().f_back.f_code
    caller = inspect.getframeinfo(inspect.stack()[1][0])
    func = funcFormat.format(
        os.path.relpath(func.co_filename),
        str(caller.lineno),
        func.co_name,
    )
    logging.info(func + 'All Logs written in {}'.format(LOG_FILE_PATH))

    stdout_logger = logging.getLogger('STDOUT')
    sl = StreamToLogger(stdout_logger, logging.INFO)
    sys.stdout = sl

    stderr_logger = logging.getLogger('STDERR')
    sl = StreamToLogger(stderr_logger, logging.ERROR)
    sys.stderr = sl

    # print = logging.info

    # # Output full log
    # logging.FileHandler(LOG_FILE_PATH)

    # For Information py_log
    @staticmethod
    def i(tag='', message=''):
        func = inspect.currentframe().f_back.f_code
        caller = inspect.getframeinfo(inspect.stack()[1][0])
        func = funcFormat.format(
            os.path.relpath(func.co_filename),
            caller.lineno,
            func.co_name,
        )
        logger.info(func + str(tag) + '\t' + str(message))

    # For error py_log
    @staticmethod
    def e(tag='', message=''):
        func = inspect.currentframe().f_back.f_code
        caller = inspect.getframeinfo(inspect.stack()[1][0])
        func = funcFormat.format(
            os.path.relpath(func.co_filename),
            caller.lineno,
            func.co_name,
        )
        logger.error(func + str(tag) + '\t' + str(message))

    # For debug py_log
    @staticmethod
    def d(tag='', message=''):
        func = inspect.currentframe().f_back.f_code
        caller = inspect.getframeinfo(inspect.stack()[1][0])
        func = funcFormat.format(
            os.path.relpath(func.co_filename),
            caller.lineno,
            func.co_name,
        )
        logger.debug(func + str(tag) + '\t' + str(message))

    # For warning py_log
    @staticmethod
    def w(tag='', message=''):
        func = inspect.currentframe().f_back.f_code
        caller = inspect.getframeinfo(inspect.stack()[1][0])
        func = funcFormat.format(
            os.path.relpath(func.co_filename),
            caller.lineno,
            func.co_name,
        )
        logger.warning(func + str(tag) + '\t' + str(message))

    # Showing critical py_log
    @staticmethod
    def c(tag='', message=''):
        func = inspect.currentframe().f_back.f_code
        caller = inspect.getframeinfo(inspect.stack()[1][0])
        func = funcFormat.format(
            os.path.relpath(func.co_filename),
            caller.lineno,
            func.co_name,
        )
        logger.critical(func + str(tag) + '\t' + str(message))
