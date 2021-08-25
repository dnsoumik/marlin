#!/usr/bin/env python
# -*- coding: utf-8 -*-
import tornado

from build_config import CONFIG
from lib.xen_protocol import xenSecureV1
from util.conn_util import MongoMixin
from util.log_util import Log


@xenSecureV1
class CountryHandler(tornado.web.RequestHandler, MongoMixin):
    SUPPORTED_METHODS = ('GET', 'OPTIONS')

    account = MongoMixin.userDb[
        CONFIG['database'][0]['table'][0]['name']
    ]

    applications = MongoMixin.userDb[
        CONFIG['database'][0]['table'][1]['name']
    ]

    profile = MongoMixin.userDb[
        CONFIG['database'][0]['table'][2]['name']
    ]

    entity = MongoMixin.userDb[
        CONFIG['database'][0]['table'][5]['name']
    ]

    phoneCountry = MongoMixin.userDb[
        CONFIG['database'][0]['table'][6]['name']
    ]

    country = MongoMixin.userDb[
        CONFIG['database'][0]['table'][9]['name']
    ]

    def options(self):
        self.set_status(200)
        self.write({})
        self.finish()
        return

    async def get(self):

        status = False
        code = 4000
        result = []
        message = ''

        try:
            # TODO: this need to be moved in a global class
            profileQ = self.profile.find(
                {
                    'accountId': self.accountId,
                    'applicationId': self.applicationId,
                    'entityId': self.entityId
                },
                limit=1
            )
            profile = []
            async for i in profileQ:
                profile.append(i)
            if len(profile):
                appQ = self.applications.find(
                    {
                        '_id': self.applicationId
                    },
                    limit=1
                )
                app = []
                async for i in appQ:
                    app.append(i)
                if len(app):
                    if True:  # TODO: till here
                        self.apiId = app[0]['apiId']
                        Log.i(self.apiId)

                        try:
                            withExtra = bool(self.get_arguments('withExtra')[0])
                        except:
                            withExtra = False

                        try:
                            limit = int(self.get_arguments('limit')[0])
                        except:
                            limit = 0

                        try:
                            skip = int(self.get_arguments('skip')[0])
                        except:
                            skip = 0

                        countryQ = self.country.find(
                            {
                                'disabled': False,
                            },
                            limit=limit,
                            skip=skip
                        )

                        async for i in countryQ:

                            i['_id'] = str(i['_id'])

                            if not withExtra:
                                x = {}
                                x['code'] = i['code']
                                x['name'] = i['name']
                                x['flag'] = i['flag']
                                x['flagSymbol'] = i['flagSymbol']
                                x['dialCode'] = i['dialCode']
                                x['sDialCode'] = i['sDialCode']
                                result.append(
                                    x
                                )
                            else:
                                result.append(
                                    i
                                )

                        if len(result):
                            message = ''
                            code = 2000
                            status = True
                        else:
                            code = 3030
                            message = 'No data Found.'
                    else:
                        code = 4003
                        self.set_status(401)
                        message = 'You are not authorized.'
                else:
                    code = 4003
                    self.set_status(401)
                    message = 'You are not authorized.'
            else:
                code = 4003
                self.set_status(401)
                message = 'You are not authorized.'
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
            self.finish()
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
            self.finish()
            return
