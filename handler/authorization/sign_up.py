#!/usr/bin/VtsAdminSignInHandler
# -*- coding: utf-8 -*-

"""
"""
import json
import os
import re
import sys
from datetime import datetime

import tornado.web
from abc import ABCMeta

from bson import ObjectId

from build_config import CONFIG
from lib.jwt_filter import JWT_ENCODE
from lib.lib import Validate
from lib.xen_protocol import noXenSecureV1
from util.conn_util import MongoMixin
from util.log_util import Log
from util.time_util import timeNow


@noXenSecureV1
class SignUpHandler(tornado.web.RequestHandler, MongoMixin, metaclass=ABCMeta):
    SUPPORTED_METHODS = ('POST', 'OPTIONS')

    account = MongoMixin.userDb[
        CONFIG['database'][0]['table'][0]['name']
    ]

    applications = MongoMixin.userDb[
        CONFIG['database'][0]['table'][1]['name']
    ]

    profile = MongoMixin.userDb[
        CONFIG['database'][0]['table'][2]['name']
    ]

    oneTimePassword = MongoMixin.userDb[
        CONFIG['database'][0]['table'][3]['name']
    ]

    phoneCountry = MongoMixin.userDb[
        CONFIG['database'][0]['table'][6]['name']
    ]

    entity = MongoMixin.userDb[
        CONFIG['database'][0]['table'][5]['name']
    ]

    signedSession = MongoMixin.userDb[
        CONFIG['database'][0]['table'][10]['name']
    ]

    def options(self):
        self.set_status(200)
        self.write({})
        self.finish()
        return

    async def post(self):

        status = False
        code = 4000
        result = []
        message = ''

        try:
            try:
                # CONVERTS BODY INTO JSON
                self.request.arguments = json.loads(self.request.body.decode())
            except Exception as e:
                code = 4002
                message = 'Expected Request Type JSON.'
                raise Exception

            applicationId = self.request.arguments.get('applicationId')
            if applicationId is None:
                code = 4100
                message = 'Missing Argument - [ applicationId ].'
                raise Exception
            else:
                try:
                    applicationId = ObjectId(applicationId)
                except:
                    code = 4102
                    message = 'Invalid Argument - [ applicationId ].'
                    raise Exception

            appQ = self.applications.find(
                {
                    '_id': applicationId
                },
                limit=1
            )
            app = []
            async for i in appQ:
                app.append(i)
            if len(app) and app[0]['selfRegister']:
                entityQ = self.entity.find(
                    {
                        '_id': self.entityId
                    },
                    limit=1
                )
                entity = []
                async for i in entityQ:
                    entity.append(i)
                if not len(entity):
                    entityQ = self.entity.find(
                        {
                            'origin': []
                        },
                        limit=1
                    )
                    entity = []
                    async for i in entityQ:
                        entity.append(i)
                    if not len(entity):
                        code = 5050
                        message = 'Internal Error Please Contact the Support Team.'
                        raise Exception
                method = self.request.arguments.get('method')
                if method == None:
                    code = 4130
                    message = 'Missing Argument - [ method ].'
                    raise Exception
                elif type(method) != int:
                    code = 4131
                    message = 'Invalid Argument - [ method ].'
                    raise Exception
                if method == 0:
                    try:
                        userId = str(self.request.arguments['userId'])
                        password = str(self.request.arguments['password'])
                        status = True
                    except Exception as e:
                        status = False
                        code = 4110
                        template = "Exception: {0}. Argument: {1!r}"
                        message = template.format(type(e).__name__, e.args)
                elif method == 2:
                    try:
                        regexSp = re.compile('[@_`+!#$%^&*()<>?/\-|}{~:,.]')
                        regexEm = re.compile('[@`+!#$%^&*()<>?/\|}{~:],')
                        regexNp = re.compile('[1234567890]')

                        firstName = self.request.arguments.get('firstName')
                        if firstName is None:
                            code = 4510
                            message = 'Missing Argument - [ firstName ].'
                            raise Exception
                        elif type(firstName) != str:
                            code = 4511
                            message = 'Invalid Argument - [ firstName ].'
                            raise Exception
                        elif not len(str(firstName)):
                            code = 4512
                            message = 'Please enter the First Name.'
                            raise Exception
                        elif regexSp.search(firstName) is not None:
                            code = 4513
                            message = 'First name should not contain any special character.'
                            raise Exception
                        elif regexNp.search(firstName) is not None:
                            code = 4514
                            message = 'First name should not contain any number.'
                            raise Exception
                        elif len(firstName) > 50:
                            code = 4515
                            message = 'First name should be less than 50 characters.'
                            raise Exception

                        firstName = firstName.strip()
                        firstName = firstName.title()

                        lastName = self.request.arguments.get('lastName')
                        if lastName is None:
                            code = 4520
                            message = 'Missing Argument - [ lastName ].'
                            raise Exception
                        elif type(lastName) != str:
                            code = 4521
                            message = 'Invalid Argument - [ lastName ].'
                            raise Exception
                        elif not len(str(lastName)):
                            code = 4522
                            message = 'Please enter the Last Name.'
                            raise Exception
                        elif regexSp.search(lastName) is not None:
                            code = 4523
                            message = 'Last name should not contain any special character.'
                            raise Exception
                        elif regexNp.search(lastName) is not None:
                            code = 4524
                            message = 'Last name should not contain any number.'
                            raise Exception
                        elif len(lastName) > 50:
                            code = 4525
                            message = 'Last name should be less than 50 characters.'
                            raise Exception

                        lastName = lastName.strip()
                        lastName = lastName.title()

                        enUsername = self.request.arguments.get('username')
                        code, message = Validate.i(
                            enUsername,
                            'Username',
                            dataType=str,
                            notEmpty=True,
                            noSpecial=True,
                            minLength=6,
                            maxLength=15
                        )
                        if code != 4100:
                            raise Exception
                        else:
                            enUsername = enUsername.replace(" ", "")
                            enUsername = enUsername.lower()

                        phoneNumber = self.request.arguments.get('phoneNumber')
                        if phoneNumber is None:
                            code = 4241
                            message = 'Missing Argument - [ phoneNumber ].'
                            raise Exception

                        countryCode = self.request.arguments.get('dialCode')
                        if countryCode is None:
                            code = 4251
                            message = 'Missing Argument - [ dialCode ].'
                            raise Exception
                        elif type(countryCode) != int:
                            code = 4552
                            message = 'Invalid Argument - [ dialCode ].'
                            raise Exception
                        else:
                            countryCode = int(countryCode)
                        countryQ = self.phoneCountry.find(
                            {
                                'code': countryCode
                            },
                            limit=1
                        )
                        country = []
                        async for i in countryQ:
                            country.append(i)
                        if not len(country):
                            code = 4242
                            message = 'Dial code does not exist.'
                            raise Exception
                        if len(str(phoneNumber)) != country[0]['telMaxLength']:
                            code = 4252
                            message = 'Please enter a valid Phone Number.'
                            raise Exception('phoneNumber')
                        else:
                            orgPhoneNumber = int(phoneNumber)
                            phoneNumber = int(str(countryCode) + str(phoneNumber))

                        email = self.request.arguments.get('email')
                        Log.i(len(email))
                        if email is None or type(email) != str or not len(email):
                            code = 4510
                            message = 'Please enter your email.'
                            raise Exception
                        elif (len(email.split('@')) != 2 or '.' not in email or len(email) < 5):
                            code = 4532
                            message = 'Please enter a valid email.'
                            raise Exception
                        elif regexEm.search(lastName) is not None:
                            code = 4533
                            message = 'Email name should not contain any special characters.'
                            raise Exception
                        elif email is not None and len(email) > 60:
                            code = 4525
                            message = 'Email name should be less than 60 characters.'
                            raise Exception

                        email = email.replace(" ", "")
                        email = email.lower()

                        enPassword = self.request.arguments.get('password')
                        if enPassword is None:
                            code = 4610
                            message = 'Please enter your password.'
                            raise Exception

                        enPassword = enPassword.strip()

                    except Exception as e:
                        exc_type, exc_obj, exc_tb = sys.exc_info()
                        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                        Log.d('FILE: ' + str(fname), 'LINE: ' + str(exc_tb.tb_lineno) + ' TYPE: ' + str(exc_type))
                        if not len(message):
                            code = 4210
                            template = "Exception: {0}. Argument: {1!r}"
                            message = template.format(type(e).__name__, e.args)
                        raise Exception

                    accountData = {
                        'firstName': firstName,
                        'lastName': lastName,
                        'createdAt': timeNow(),
                        'createdBy': None,
                        'country': [
                            {
                                'code': country[0]['isoAlpha3Code'],
                                'name': country[0]['name'],
                                '_id': country[0]['cId'],
                            }
                        ],
                        'privacy': [
                            {
                                'value': enPassword
                            }
                        ],
                        'contact': [
                            {
                                'type': 0,
                                'value': enUsername,
                            },
                            {
                                'type': 1,
                                'verified': False,
                                'value': phoneNumber,
                                'dialCode': countryCode,
                                'sDialCode': country[0]['sCode'],
                                'phoneNumber': orgPhoneNumber,
                                'countryCode': country[0]['isoAlpha3Code']
                            },
                            {
                                'verified': False,
                                'value': email,
                                'type': 2
                            }
                        ]
                    }
                    try:
                        accountId = await self.account.insert_one(accountData)
                    except Exception as e:
                        exe = str(e).split(':')
                        if len(exe) < 2:
                            status = False
                            code = 4280
                            message = 'Internal Error Please Contact the Support Team.'
                        elif 'contact.0.value_1' in exe[2]:
                            status = False
                            code = 4281
                            message = 'This Username is already registered.'
                        elif 'contact.1.value_1' in exe[2]:
                            status = False
                            code = 4281
                            message = 'This Phone Number is already registered.'
                        elif 'contact.2.value_1' in exe[2]:
                            status = False
                            code = 4282
                            message = 'This email is already registered.'
                        else:
                            status = False
                            code = 4283
                            message = 'Internal Error Please Contact the Support Team.'
                        raise Exception
                    try:
                        accountId = accountId.inserted_id
                        profileId = await self.profile.insert_one(
                            {
                                'active': False,
                                'locked': False,
                                'closed': False,
                                'time': timeNow(),
                                'insertTime': self.time,
                                'accountId': accountId,
                                'applicationId': app[0]['_id'],
                                'entityId': entity[0]['_id'],
                                'data': [],
                            }
                        )
                        profileId = profileId.inserted_id
                    except:
                        code = 5830
                        message = 'Internal Error Please Contact the Support Team.'
                        raise Exception
                    createSession = await self.signedSession.insert_one(
                        {
                            'createdOn': datetime.now(),
                            'accountId': accountId,
                            'profileId': profileId,
                            'entityId': entity[0]['_id'],
                            'createdAt': timeNow(),
                            'createdBy': profileId
                        },
                    )
                    if createSession.inserted_id is not None:
                        xToken = JWT_ENCODE(str(createSession.inserted_id))
                        result.append(xToken)
                        status = True
                        code = 2000
                        message = 'Sign Up Successful, Welcome to Ether World.'
                else:
                    code = 4110
                    message = 'Sign In method not supported.'
                    raise Exception
            else:
                message = 'Application ID not found.'
                code = 4200
                raise Exception
        except Exception as e:
            status = False
            # self.set_status(400)
            if not len(message):
                template = 'Exception: {0}. Argument: {1!r}'
                code = 5010
                iMessage = template.format(type(e).__name__, e.args)
                message = 'Internal Error Please Contact the Support Team.'
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                Log.w('EXC', iMessage)
                Log.d('FILE: ' + str(fname), 'LINE: ' + str(exc_tb.tb_lineno) + ' TYPE: ' + str(exc_type))
        response = {
            'code': code,
            'status': status,
            'message': message
        }
        Log.d('RSP', response)
        try:
            response['result'] = result
            self.write(response)
            await self.finish()
            return
        except Exception as e:
            status = False
            template = 'Exception: {0}. Argument: {1!r}'
            code = 5011
            iMessage = template.format(type(e).__name__, e.args)
            message = 'Internal Error Please Contact the Support Team.'
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = exc_tb.tb_frame.f_code.co_filename
            Log.w('EXC', iMessage)
            Log.d('EX2', 'FILE: ' + str(fname) + ' LINE: ' + str(exc_tb.tb_lineno) + ' TYPE: ' + str(exc_type))
            response = {
                'code': code,
                'status': status,
                'message': message
            }
            self.write(response)
            await self.finish()
            return
