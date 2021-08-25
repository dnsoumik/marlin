import json
import sys

from util.log_util import Log

try:
    # SERVER CONFIGURATION FILE
    CONFIG_FILE_PATH = './configuration.json'
    CONFIG_FILE = open(CONFIG_FILE_PATH)
    CONFIG = json.loads(CONFIG_FILE.read())
    CONFIG_FILE.close()

    # Project Code
    PROJECT_NAME = CONFIG['name']

    timeOffsetIST = CONFIG['timeOffsetIST']
    # Project Code
    PROJECT_CODE = CONFIG['projectCode']

    # WEB SERVER CONFIGURATION
    WEB_SERVER_PORT = CONFIG["instance"][0]['port']

except Exception as e:
    status = False
    template = 'Exception: {0}. Argument: {1!r}'
    code = 5011
    iMessage = template.format(type(e).__name__, e.args)
    message = 'Internal Error Please Contact the Support Team.'
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = exc_tb.tb_frame.f_code.co_filename
    Log.c('BUILD-EXC', iMessage)
    Log.c('BUILD-EX2', 'FILE: ' + str(fname) + ' LINE: ' + str(exc_tb.tb_lineno) + ' TYPE: ' + str(exc_type))