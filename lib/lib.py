#!/usr/bin/env python
# -*- coding: utf-8 -*-
import random
import re
import string
import sys

import phonenumbers
from bson import ObjectId

from build_config import CONFIG
from util.conn_util import MongoMixin
from util.log_util import Log


class Validate:

    @staticmethod
    def i(arg=str, name='N/A', **kwargs):
        code = 4100
        message = ''
        try:
            regexSp = re.compile('[@_`+!#$%^&*()<>?/\-|}{~:,.]')
            regexSp2 = re.compile('[@_`!#$%^&*()<>?/\|}{~:,.]')
            regexNp = re.compile('[1234567890]')
            name = str(name)
            for key, value in kwargs.items():
                # TODO: need to fix
                if key == 'notNull' and value:
                    if arg is None:
                        code = 4510
                        message = 'Missing Argument - [ ' + name + ' ].'
                        return code, message
                if key == 'dataType':
                    if type(arg) != value:
                        code = 4511
                        message = 'Invalid Argument - [ ' + name + ' ].'
                        return code, message
                if key == 'notEmpty' and value:
                    if not len(str(arg)):
                        code = 4512
                        message = 'Please enter the ' + name + '.'
                        return code, message
                if key == 'minLength':
                    if (type(arg) == str or type(arg) == str) and len(arg) < value:
                        code = 4513
                        message = name + ' should be at least ' + str(value) + ' characters.'
                        return code, message
                    elif (type(arg) == int or type(arg) == float) and len(str(arg)) < value:
                        code = 4523
                        message = name + ' should be at least ' + str(value) + ' .'
                        return code, message
                    elif (type(arg) == list or type(arg) == dict) and len(arg) < value:
                        code = 4529
                        message = name + ' should be at least ' + str(value) + ' .'
                        return code, message
                if key == 'maxLength':
                    if (type(arg) == str or type(arg) == str) and len(arg) > value:
                        code = 4514
                        message = name + ' should be less than ' + str(value) + ' characters.'
                        return code, message
                    elif (type(arg) == int or type(arg) == float) and len(str(arg)) > value:
                        code = 4545
                        message = name + ' should be less than ' + str(value) + ' .'
                        return code, message
                    elif (type(arg) == dict or type(arg) == list) and len(arg) > value:
                        code = 4546
                        message = name + ' should be less than ' + str(value + 1) + ' .'
                        return code, message
                if key == 'minNumber':
                    if type(arg) == list and len(arg) < value:
                        code = 4525
                        message = name + ' should be at least ' + str(value) + '.'
                        return code, message
                    elif type(arg) != list and arg < value:
                        code = 4515
                        message = name + ' should be at least ' + str(value) + '.'
                        return code, message
                if key == 'maxNumber':
                    if type(arg) == list and len(arg) > value:
                        code = 4526
                        message = name + ' should be less than ' + str(value) + '.'
                        return code, message
                    elif type(arg) != list and arg > value:
                        code = 4516
                        message = name + ' should be less than ' + str(value) + '.'
                        return code, message
                if key == 'noSpecial' and value:
                    if arg != None and regexSp.search(arg) != None:
                        code = 4517
                        message = name + ' should not contain any special character.'
                        return code, message
                if key == 'noSpecial2' and value:
                    if arg != None and regexSp2.search(arg) != None:
                        code = 4517
                        message = name + ' should not contain any special character.'
                        return code, message
                if key == 'noNumber' and value:
                    if arg != None and regexNp.search(str(arg)) != None:
                        code = 4518
                        message = name + ' should not contain any number.'
                        return code, message
                if key == 'noSpace':
                    if ' ' in arg:
                        code = 4519
                        message = name + ' should not contain any white space.'
                        return code, message
                if key == 'inputType' and value == 'email':
                    arg = str(arg)
                    if len(arg) < 7 or \
                            not re.match('^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$', arg):
                        code = 4610
                        message = 'Please enter a valid Email.'
                        return code, message
                if key == 'exception':
                    if arg == value:
                        code = 4611
                        message = 'Invalid Argument - [ ' + name + ' ].'
                        return code, message
        except Exception as e:
            if code == 4100:
                template = 'Exception: {0}. Argument: {1!r}'
                code = 5010
                iMessage = template.format(type(e).__name__, e.args)
                message = 'Internal Error, Please Contact the Support Team.'
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = exc_tb.tb_frame.f_code.co_filename
                Log.w('[LIB] EXC', iMessage)
                Log.d('[LIB] EX2',
                      'FILE: ' + str(fname) + ' LINE: ' + str(exc_tb.tb_lineno) + ' TYPE: ' + str(exc_type))
                code = 4200
                return code, message
        return code, message

    @staticmethod
    def p(dialNum=int, countryCode=str, prefix=str):

        code = 4100
        message = ''

        if dialNum == None or str(dialNum) == '' or prefix == None or str(prefix) == '':
            message = 'Format execption.'
            code = 4220

        else:
            Log.i('DialCode', countryCode)
            Log.i('Prefix', prefix)
            dN = prefix + str(dialNum)
            z = phonenumbers.parse(dN, countryCode)
            x = phonenumbers.is_valid_number(z)
            if not x:
                message = 'Please enter a valid phone number.'
                code = 4221

        return code, message


def randomString(stringLength=6):
    """Generate a random string of letters and digits """
    lettersAndDigits = string.ascii_letters + string.digits
    return ''.join(random.choice(lettersAndDigits) for i in range(stringLength))


async def initSession(self):
    code = 4000
    status = False
    message = ''
    result = []

    if self.sessionId is None:
        return

    signedSession = MongoMixin.userDb[
        CONFIG['database'][0]['table'][10]['name']
    ]
    signedSession = await signedSession.find_one(
        {
            '_id': ObjectId(self.sessionId)
        }
    )
    Log.i('session_details', signedSession)
    if signedSession is None:
        self.set_status(401)
        code = 4002
        message = 'Invalid - [ Authorization ]'
        response = {
            'code': code,
            'status': status,
            'result': [],
            'message': message
        }
        self.write(response)
        await self.finish()
    else:
        self.sessionId = ObjectId(self.sessionId)
        self.profileId = signedSession['profileId']
        self.entityId = signedSession['entityId']
        self.accountId = signedSession['accountId']
