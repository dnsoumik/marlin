#!/usr/bin/VtsAdminSignInHandler
# -*- coding: utf-8 -*-

"""
"""
import json
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
class SignInHandler(tornado.web.RequestHandler, MongoMixin, metaclass=ABCMeta):

    SUPPORTED_METHODS = ('POST', 'PUT', 'OPTIONS')

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
                Log.i(e)
                code = 4100
                message = 'Expected Request Type JSON.'
                raise Exception

            entityQ = self.entity.find(
                {
                    '_id': self.entityId
                },
                limit=1
            )
            entity = []
            async for r in entityQ:
                entity.append(r)

            if not len(entity):
                code = 4003
                message = 'You are not Authorized.'
                self.set_status(401)
                raise Exception

            applicationId = self.request.arguments.get('applicationId')
            app = []
            if applicationId is not None:
                try:
                    applicationId = ObjectId(applicationId)
                    appQ = self.applications.find_one(
                        {
                            '_id': applicationId
                        },
                        limit=1
                    )
                    app.append(appQ)
                except:
                    code = 4006
                    message = 'Invalid application Id.'
                    self.set_status(401)
                    raise Exception

            if applicationId is None or len(app):
                method = self.request.arguments.get('method')
                if method == None:
                    code = 4130
                    message = 'Missing Argument - [ method ].'
                    raise Exception
                # if method == 0:
                #     try:
                #         # TODO: need to give validation
                #         username = str(self.request.arguments['username'])
                #         password = str(self.request.arguments['password'])
                #     except Exception as e:
                #         code = 4110
                #         template = "Exception: {0}. Argument: {1!r}"
                #         message = template.format(type(e).__name__, e.args)
                #         raise Exception
                #     try:
                #         accountQ = self.account.find(
                #             {
                #                 'contact.0.value': int(username),
                #                 'privacy.0.value': password
                #             },
                #             {
                #                 '_id': 1
                #             },
                #             limit=1
                #         )
                #
                #         account = []
                #         async for r in accountQ:
                #             account.append(r)
                #         if len(account):
                #             '''
                #                 Searching for profile
                #                 Blocked for 20 sec ( in microseconds )
                #             '''
                #             profileQ = self.profile.find(
                #                 {
                #                     'accountId': account[0]['_id'],
                #                     'applicationId': app[0]['_id'],
                #                     # '$or': [
                #                     #    {
                #                     #        'lastSignInRequest': None
                #                     #    },
                #                     #    {
                #                     #        'lastSignInRequest':
                #                     #            {
                #                     #                '$lt': self.time - 20000000
                #                     #            }
                #                     #    }
                #                     # ]
                #                 },
                #                 {
                #                     '_id': 1,
                #                     'entityId': 1,
                #                     'role': 1
                #                 },
                #                 limit=1
                #             )
                #             profile = []
                #             async for r in profileQ:
                #                 profile.append(r)
                #             if not len(profile):
                #                 subAdminAppQ = self.applications.find(
                #                     {
                #                         'apiId': 402023
                #                     }
                #                 )
                #                 subAdminApp = []
                #                 async for i in subAdminAppQ:
                #                     subAdminApp.append(i)
                #                 profileQ = self.profile.find(
                #                     {
                #                         'accountId': account[0]['_id'],
                #                         'applicationId': subAdminApp[0]['_id']
                #                     },
                #                     {
                #                         '_id': 1,
                #                         'entityId': 1,
                #                         'role': 1
                #                     },
                #                     limit=1
                #                 )
                #                 profile = []
                #                 async for i in profileQ:
                #                     profile.append(i)
                #             if len(profile):
                #                 role = profile[0]['role']
                #                 '''
                #                 # Sign in blocked for 20min based on phone number
                #                 Log.i('last_sign_in_time', profile[0].get('lastSignInRequest'))
                #                 if profile[0].get('lastSignInRequest') != None and profile[0].get('lastSignInRequest') > self.time - 20000000:
                #
                #                     # TODO: for counter logic
                #                     self.write(
                #                                 {
                #                                     'status': False,
                #                                     'message': 'Please try again after later.',
                #                                     'code': 4040,
                #                                     'result': []
                #                                 }
                #                             )
                #                     self.finish()
                #                     return
                #                 '''
                #
                #                 entities = []
                #                 for p in profile:
                #                     entQ = self.entity.find(
                #                         {
                #                             '_id': p['entityId']
                #                         },
                #                         {
                #                             '_id': 1,
                #                             'name': 1
                #                         },
                #                         limit=1
                #                     )
                #                     ent = []
                #                     async for r in entQ:
                #                         ent.append(r)
                #
                #                     if len(ent):
                #                         k = FN_ENCRYPT(str(ent[0]['_id']), True)
                #                         v = {
                #                             'key': k.decode(),
                #                             'name': ent[0]['name']
                #                         }
                #                         entities.append(v)
                #                 if not len(entities):
                #                     Log.d('ENT', 'No Entity Found.')
                #                     message = 'No Entity Found.'
                #                     raise Exception
                #                 else:
                #                     '''
                #                         Saving the Last Sign In Reqested Time
                #                     '''
                #                     updateResult = await self.profile.update_one(
                #                         {
                #                             '_id': profile[0]['_id']
                #                         },
                #                         {
                #                             '$set':
                #                                 {
                #                                     'lastSignInRequest': self.time
                #                                 }
                #                         }
                #                     )
                #                     if updateResult.modified_count:
                #                         bToken = JWT_ENCODE(str(account[0]['_id']))
                #                         xApiKey = FN_ENCRYPT(str(app[0]['_id']), True)
                #                         if role == 1 or role == 2:
                #                             xApiKey = FN_ENCRYPT(str(subAdminApp[0]['_id']), True)
                #                         secureCache = {
                #                             'bearerToken': bToken.decode(),
                #                             'apiKey': xApiKey.decode()
                #                         }
                #                         secureCache['accessOrigin'] = entities
                #                         result.append(secureCache)
                #                         status = True
                #                         code = 2000
                #                         message = 'Sign In Successful, Welcome Back.'
                #                     else:
                #                         code = 5310
                #                         message = 'Internal Error, Please Contact the Support Team.'
                #             else:
                #                 code = 4310
                #                 message = 'Wrong Username or Password.'
                #         else:
                #             code = 4311
                #             message = 'Wrong Username or Password.'
                #     except Exception as e:
                #         exc_type, exc_obj, exc_tb = sys.exc_info()
                #         fname = exc_tb.tb_frame.f_code.co_filename
                #         Log.d('EX2',
                #               'FILE: ' + str(fname) + ' LINE: ' + str(exc_tb.tb_lineno) + ' TYPE: ' + str(exc_type))
                #         code = 5210
                #         message = 'Internal Error, Please Contact the Support Team.'
                #         # TODO: for sign in with email
                #         raise Exception
                #         account = self.account.find(
                #             {
                #                 'contact.1.value': userName,
                #                 'privacy.0.value': password
                #             },
                #             limit=1
                #         )
                #         if len(account):
                #             profile = self.profile.find(
                #                 {
                #                     'accountId': account[0]['_id'],
                #                     'applicationId': app[0]['_id']
                #                 }
                #             )
                #             if len(profile):
                #                 entities = []
                #                 for p in profile:
                #                     ent = self.entity.find(
                #                         {
                #                             '_id': p['entityId']
                #                         },
                #                         limit=1
                #                     )
                #                     if len(ent):
                #                         v = {
                #                             'id': str(ent[0]['id']),
                #                             'name': ent[0]['name']
                #                         }
                #                         entities.append(v)
                #                 if not len(entities):
                #                     Log.d('ENT', 'No Entity Found.')
                #                     message = 'No Entity Found.'
                #                     raise Exception
                #                 else:
                #                     result.append(
                #                         str(JWT_ENCODE(
                #                             str(account[0]['_id'])
                #                         )
                #                         )
                #                     )
                #                     result.append(entities)
                #                     status = True
                #                     code = 2000
                #                     message = 'Sign In Successful, Welcome Back.'
                #             else:
                #                 code = 4320
                #                 message = 'Wrong Username or Password.'
                #         else:
                #             code = 4321
                #             message = 'Wrong Username or Password.'
                # elif method == 1:
                #     try:
                #         phoneNumber = self.request.arguments.get('phoneNumber')
                #         if phoneNumber == None:
                #             code = 4241
                #             message = 'Missing Argument - [ phoneNumber ].'
                #             raise Exception
                #         else:
                #             phoneNumber = int(phoneNumber)
                #         countryCode = self.request.arguments.get('countryCode')
                #         if countryCode == None:
                #             code = 4251
                #             message = 'Missing Argument - [ countryCode ].'
                #             raise Exception
                #         else:
                #             countryCode = int(countryCode)
                #         countryQ = self.phoneCountry.find(
                #             {
                #                 'code': countryCode
                #             },
                #             limit=1
                #         )
                #         country = []
                #         async for r in countryQ:
                #             country.append(r)
                #
                #         if not len(country):
                #             code = 4242
                #             message = 'Invalid Country Code.'
                #             raise Exception
                #         if len(str(phoneNumber)) != country[0]['telMaxLength']:
                #             code = 4252
                #             message = 'Invalid Phone Number.'
                #             raise Exception('phoneNumber')
                #         else:
                #             phoneNumber = int(str(countryCode) + str(phoneNumber))
                #     except Exception as e:
                #         if not len(message):
                #             code = 4210
                #             template = "Exception: {0}. Argument: {1!r}"
                #             message = template.format(type(e).__name__, e.args)
                #         raise Exception
                #     accountQ = self.account.find(
                #         {
                #             'contact.0.value': phoneNumber
                #         },
                #         {
                #             '_id': 1
                #         },
                #         limit=1
                #     )
                #     account = []
                #     async for r in accountQ:
                #         account.append(r)
                #
                #     if len(account):
                #         '''
                #             Searching for profile
                #             Blocked for 20 sec ( in microseconds )
                #         '''
                #         profileQ = self.profile.find(
                #             {
                #                 'accountId': account[0]['_id'],
                #                 'applicationId': app[0]['_id'],
                #                 # '$or': [
                #                 #    {
                #                 #        'lastSignInRequest': None
                #                 #    },
                #                 #    {
                #                 #        'lastSignInRequest':
                #                 #            {
                #                 #                '$lt': self.time - 20000000
                #                 #            }
                #                 #    }
                #                 # ]
                #             },
                #             {
                #                 '_id': 1,
                #                 'lastSignInRequest': 1,
                #                 'retrySignInRequest': 1,
                #             },
                #             limit=1
                #         )
                #         profile = []
                #         async for r in profileQ:
                #             profile.append(r)
                #
                #         if not len(profile):
                #             if not app[0]['selfRegister']:
                #                 code = 4210
                #                 message = 'Phone Number is not registered.'
                #                 raise Exception
                #             try:
                #                 profileId = await self.profile.insert_one(
                #                     {
                #                         'active': False,
                #                         'locked': False,
                #                         'closed': False,
                #                         'time': timeNow(),
                #                         'accountId': account[0]['_id'],
                #                         'applicationId': app[0]['_id'],
                #                         'entityId': entity[0]['_id'],
                #                         'retrySignInRequest': 0,
                #                         'data': []
                #                     }
                #                 )
                #             except:
                #                 code = 5810
                #                 message = 'Internal Error, Please Contact the Support Team.'
                #                 raise Exception
                #         else:
                #             profileId = profile[0]['_id']
                #
                #         # Sign in blocked for 20min based on phone number
                #
                #         Log.i('last_sign_in_time', profile[0].get('lastSignInRequest'))
                #         Log.i('retry_sign_in_request', profile[0].get('retrySignInRequest'))
                #         # remote_ip = self.request.client_ip
                #         # Log.i('ip', self.request.client_ip)
                #         # Log.i('headers', self.request.headers)
                #         # return
                #
                #         if profile[0].get('retrySignInRequest') != None:
                #             retrySignInRequest = profile[0].get('retrySignInRequest')
                #         else:
                #             retrySignInRequest = 1
                #
                #         if profile[0].get('lastSignInRequest') != None and profile[0].get(
                #                 'lastSignInRequest') > self.time - 1200000000:
                #
                #             try:
                #                 checkrequest = profile[0].get('retrySignInRequest')
                #                 if checkrequest == None:
                #                     checkrequest = 0
                #             except:
                #                 checkrequest = 0
                #
                #             if checkrequest > 2:
                #
                #                 self.write(
                #                     {
                #                         'status': False,
                #                         'message': 'Too many attemps, please try again later.',
                #                         'code': 4040,
                #                         'result': []
                #                     }
                #                 )
                #                 self.finish()
                #                 return
                #             else:
                #                 retrySignInRequest = retrySignInRequest + 1
                #         else:
                #             retrySignInRequest = 1
                #
                #         oOtpQ = self.oneTimePassword.find(
                #             {
                #                 'profileId': profileId,
                #             },
                #             {
                #                 '_id': 1
                #             },
                #             limit=1
                #         )
                #         oOtp = []
                #         async for r in oOtpQ:
                #             oOtp.append(r)
                #
                #         nOtp = random.randint(100000, 999999)
                #         if phoneNumber in [911234567890, 917005612276, 919738378908, 919612342112, 917005464481,
                #                            917005612277, 917005612278]:
                #             nOtp = 123456
                #
                #         rOtpQ = await self.oneTimePassword.delete_one({'profileId': profileId})
                #         if (rOtpQ.deleted_count >= 0):
                #             a = await self.oneTimePassword.insert_one(
                #                 {
                #                     'createdAt': dtime.now(),
                #                     'profileId': profileId,
                #                     'value': nOtp,
                #                     'phoneNumber': phoneNumber,
                #                 }
                #             )
                #
                #             '''
                #                 Saving the Last Sign In Reqested Time
                #             '''
                #
                #             updateResult = await self.profile.update_one(
                #                 {
                #                     '_id': profileId
                #                 },
                #                 {
                #                     '$set':
                #                         {
                #                             'lastSignInRequest': self.time,
                #                             'retrySignInRequest': retrySignInRequest
                #                         }
                #                 }
                #             )
                #             if updateResult.modified_count:
                #                 Log.i('Phone Number: ', str(phoneNumber) + ' OTP: ' + str(nOtp))
                #                 # TODO: this need to be chaged to http client
                #                 gwResp = MSG91_GW.send(str(phoneNumber), str(entity[0]['smsGwId']), nOtp)
                #                 if gwResp:
                #                     # if True:
                #                     #     Log.i('MSG91 Gateway Response', gwResp)
                #                     status = True
                #                     code = 2000
                #                     message = 'A 6-digit One Time Password has been sent to your Phone Number.'
                #                 else:
                #                     code = 5030
                #                     message = 'Internal Error, Please Contact the Support Team.'
                #                     raise Exception
                #             else:
                #                 code = 5020
                #                 message = 'Internal Error, Please Contact the Support Team.'
                #                 raise Exception
                #         else:
                #             code = 50101
                #             message = 'Internal Error, Please Contact the Support Team.'
                #     else:
                #         code = 4210
                #         message = 'Phone Number is not registered.'
                # el
                if method == 2:

                    username = self.request.arguments.get('username')
                    if type(username) == str:
                        Log.i(type(username))
                    code, message = Validate.i(
                        username,
                        'Username',
                        dataType=str,
                        maxLength=15,
                        minLength=6
                    )
                    if code != 4100:
                        raise Exception
                    else:
                        username = str(username).replace(' ', '')

                    password = self.request.arguments.get('password')
                    code, message = Validate.i(
                        password,
                        'Password',
                        dataType=str,
                        maxLength=40
                    )
                    if code != 4100:
                        raise Exception

                    try:
                        usernamePhone = int(username)
                    except:
                        usernamePhone = None

                    try:
                        account = await self.account.find_one(
                            {
                                '$or': [
                                    {
                                        'contact.0.value': username,
                                        'privacy.0.value': password,
                                    },
                                    # {
                                    #     'contact.1.value': usernamePhone,
                                    #     'privacy.0.value': password,
                                    # },
                                    {
                                        'contact.2.value': username,
                                        'privacy.0.value': password,
                                    }
                                ]
                            },
                            {
                                '_id': 1
                            }
                        )
                        if account is not None:
                            '''
                                Saving the Last Sign In Requested Time
                            '''
                            profile = []
                            if applicationId is None:
                                profileQ = self.profile.find(
                                    {
                                        'accountId': account['_id'],
                                        'entityId': self.entityId
                                    },
                                    {
                                        '_id': 1,
                                        'entityId': 1,
                                        'lastSignInRequest': 1
                                    }
                                )
                            else:
                                profileQ = self.profile.find(
                                    {
                                        'accountId': account['_id'],
                                        'entityId': self.entityId,
                                        'applicationId': applicationId
                                    },
                                    {
                                        '_id': 1,
                                        'entityId': 1,
                                        'lastSignInRequest': 1
                                    }
                                )
                            async for p in profileQ:
                                profile.append(p)

                            Log.i("profiles", len(profile))
                            if not len(profile):
                                message = 'No profiles found.'
                            else:
                                self.profileId = profile[0]['_id']
                                profileU = await self.profile.update_one(
                                    {
                                        '_id': self.profileId
                                    },
                                    {
                                        '$set':
                                            {
                                                'lastSignInRequest': self.time
                                            }
                                    }
                                )
                                # if (usernamePhone) == 911123123123:
                                #     nOtp = 111111
                                # else:
                                #     nOtp = random.randint(100000, 999999)

                                createSession = await self.signedSession.insert_one(
                                    {
                                        'createdOn': datetime.now(),
                                        'accountId': account['_id'],
                                        'profileId': profile[0]['_id'],
                                        'entityId': entity[0]['_id'],
                                        'createdAt': timeNow(),
                                        'createdBy': profile[0]['_id']
                                    },
                                )
                                if createSession.inserted_id is not None:
                                    xToken = JWT_ENCODE(str(createSession.inserted_id))
                                    result.append(xToken)
                                    status = True
                                    code = 2000
                                    message = 'Sign In Successful, Welcome Back.'
                                else:
                                    code = 5020
                                    message = 'Internal Error, Please Contact the Support Team.'
                                    raise Exception
                        else:
                            code = 4311
                            message = 'Wrong Username or Password.'
                    except Exception as e:
                        exc_type, exc_obj, exc_tb = sys.exc_info()
                        fname = exc_tb.tb_frame.f_code.co_filename
                        Log.d('EX2',
                              'FILE: ' + str(fname) + ' LINE: ' + str(exc_tb.tb_lineno) + ' TYPE: ' + str(exc_type))
                        code = 5210
                        message = 'Internal Error, Please Contact the Support Team.'
                        # TODO: for sign in with email
                        raise Exception
                else:
                    code = 4110
                    message = 'Sign In method not supported.'
            else:
                message = 'Application ID not found.'
                code = 4200
        except Exception as e:
            status = False
            # self.set_status(400)
            if not len(message):
                template = 'Exception: {0}. Argument: {1!r}'
                code = 5010
                iMessage = template.format(type(e).__name__, e.args)
                message = 'Internal Error, Please Contact the Support Team.'
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = exc_tb.tb_frame.f_code.co_filename
                Log.w('EXC', iMessage)
                Log.d('EX2', 'FILE: ' + str(fname) + ' LINE: ' + str(exc_tb.tb_lineno) + ' TYPE: ' + str(exc_type))
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
            message = 'Internal Error, Please Contact the Support Team.'
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
