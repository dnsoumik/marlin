#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
from abc import ABCMeta

import tornado.web

from build_config import CONFIG
from lib.lib import initSession
from lib.xen_protocol import xenSecureV1
from util.conn_util import MongoMixin
from util.file_util import FileUtil
from util.log_util import Log


@xenSecureV1
class ProfileHandler(tornado.web.RequestHandler, MongoMixin, metaclass=ABCMeta):
    SUPPORTED_METHODS = ('GET', 'POST', 'DELETE', 'PUT', 'OPTIONS')

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

    serviceAccount = MongoMixin.userDb[
        CONFIG['database'][0]['table'][0]['name']
    ]

    fu = FileUtil()

    # def options(self):
    #     self.set_status(200)
    #     self.write({})
    #     self.finish()
    #     return

    async def prepare(self):
        await initSession(self)

    async def get(self):

        status = False
        code = 4000
        result = []
        message = ''

        try:
            profile = await self.profile.find_one(
                {
                    '_id': self.profileId
                }
            )
            if profile is None:
                message = 'Profile not found.'
                code = 4212
                raise Exception

            pAccountQ = self.account.find(
                {
                    '_id': self.accountId
                },
                limit=1
            )
            pAccount = []
            async for i in pAccountQ:
                pAccount.append(i)

            if len(pAccount):
                v = {}
                v['closed'] = profile['closed']
                v['locked'] = profile['locked']
                v['active'] = profile['active']
                v['id'] = str(profile.get('_id'))
                v['firstName'] = pAccount[0].get('firstName')
                v['lastName'] = pAccount[0].get('lastName')
                v['contact'] = pAccount[0].get('contact')

                result.append(v)
                status = True
                code = 2000
            else:
                code = 3002
                message = 'No Account Found.'
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
