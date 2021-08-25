#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

from bson import ObjectId

from lib.fernet_crypto import FN_DECRYPT
from lib.jwt_filter import JWT_DECODE
from util.log_util import Log
from util.time_util import timeNow

sys.path.append('./utils')


def xenSecureV1(handler_class):
    """ Handle Xen Protocol """

    def wrap_execute(handler_execute):

        def require_auth(handler, kwargs):

            code = 4000
            status = False
            message = ''
            result = []

            try:
                handler.sessionId = None
                try:
                    handler.request.client_ip = handler.request.headers.get("X-Real-IP") or \
                                                handler.request.headers.get("X-Forwarded-For") or \
                                                handler.request.remote_ip
                except:
                    handler.request.client_ip = handler.request.remote_ip
                Log.i('client_ip', handler.request.client_ip)

                handler.time = timeNow()
                handler.set_header('Xen-Protocol-Version', '1.2')
                requestCros = handler.request.headers.get('Origin')
                handler.set_header('Access-Control-Allow-Origin', '*')
                handler.set_header('Access-Control-Allow-Headers', '*')
                handler.set_header('Access-Control-Allow-Methods', 'DELETE,OPTIONS,GET,HEAD,PATCH,POST,PUT')

                Log.i('Method', handler.request.method)
                if requestCros is not None or handler.request.method == 'OPTIONS':
                    handler.set_header('Access-Control-Allow-Origin', '*')
                requestHeader = handler.request.headers.get('Access-Control-Request-Headers')
                # Log.i('Headers', requestHeader)
                if requestHeader is not None or handler.request.method == 'OPTIONS':
                    handler.set_header('Access-Control-Allow-Headers', requestHeader)
                    handler.set_header('Access-Control-Allow-Methods', 'DELETE,OPTIONS,GET,HEAD,PATCH,POST,PUT')
                    handler._transforms = []
                    handler.set_status(204)
                    handler.write('')
                    # handler.finish()
                    return True

                bearerToken = handler.request.headers.get('Authorization')
                if bearerToken:
                    bearerToken = str(bearerToken).split('Bearer ')
                    if len(bearerToken):
                        bearerToken = bearerToken[1]
                        sessionId = JWT_DECODE(bearerToken)
                        if sessionId is None:
                            handler.set_status(401)
                            code = 4001
                            message = 'Invalid - [ Authorization ]'
                            response = {
                                'code': code,
                                'status': status,
                                'result': [],
                                'message': message
                            }
                            Log.d('Xen', response)
                            handler.write(response)
                            handler.finish()
                            return False

                        if type(sessionId) is bytes:
                            sessionId = sessionId.decode()

                        handler.sessionId = sessionId
                        Log.i('Authorization', sessionId)
                    else:
                        raise Exception('Bearer Token')
                else:
                    handler._transforms = []
                    handler.set_status(501)
                    code = 4010
                    message = 'Missing - [ Authorization ]'
                    raise Exception

                try:
                    # Saving query params in get_arguments
                    handler.request.get_arguments = handler.request.arguments
                except:
                    handler.request.get_arguments = None

                return True
            except Exception as e:

                if code == 4000:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    fname = exc_tb.tb_frame.f_code.co_filename
                    Log.d('Xen', 'FILE: ' + str(fname) + ' LINE: ' + str(exc_tb.tb_lineno) + ' TYPE: ' + str(exc_type))
                    handler._transforms = []
                    handler.set_status(401)
                    code = 4001
                    message = 'Invalid headers.'

                response = {
                    'code': code,
                    'status': status,
                    'result': [],
                    'message': message
                }
                Log.d('Xen', response)
                handler.write(response)
                handler.finish()

            return False

        def _execute(self, transforms, *args, **kwargs):
            try:
                require_auth(self, kwargs)
            except Exception:
                return False

            return handler_execute(self, transforms, *args, **kwargs)

        return _execute

    handler_class._execute = wrap_execute(handler_class._execute)
    return handler_class


def noXenSecureV1(handler_class):
    """ Handle No-Xen Protocol """

    def wrap_execute(handler_execute):

        def require_auth(handler, kwargs):

            code = 4000
            status = False
            result = []
            message = ''

            try:

                try:
                    handler.request.client_ip = handler.request.headers.get("X-Real-IP") or \
                                                handler.request.headers.get("X-Forwarded-For") or \
                                                handler.request.remote_ip
                except:
                    handler.request.client_ip = handler.request.remote_ip
                Log.i('client_ip', handler.request.client_ip)

                handler.time = timeNow()
                handler.set_header('No-Xen-Protocol-Version', '1.0')
                requestCros = handler.request.headers.get('Origin')
                if requestCros != None:
                    handler.set_header('Access-Control-Allow-Origin', requestCros)
                requestHeader = handler.request.headers.get('Access-Control-Request-Headers')
                if requestHeader is not None:
                    handler.set_header('Access-Control-Allow-Headers', requestHeader)
                    handler.set_header('Access-Control-Allow-Methods', 'DELETE,GET,HEAD,PATCH,POST,PUT')
                    handler._transforms = []
                    handler.set_status(204)
                    handler.write({})
                    handler.finish()
                xOriginKey = handler.request.headers.get('x-Origin-Key')
                if xOriginKey:
                    entityId = FN_DECRYPT(xOriginKey)
                    if not entityId:
                        raise Exception('x-Origin-Key')
                    else:
                        handler.entityId = ObjectId(entityId.decode('utf-8'))
                        Log.i('x-Origin-Key', handler.entityId)
                else:
                    handler._transforms = []
                    handler.set_status(501)
                    code = 4020,
                    message = 'Missing - [ x-Origin-Key ].'
                    raise Exception

                return True
            except Exception as e:

                if code == 4000:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    fname = exc_tb.tb_frame.f_code.co_filename
                    Log.d('No-Xen',
                          'FILE: ' + str(fname) + ' LINE: ' + str(exc_tb.tb_lineno) + ' TYPE: ' + str(exc_type))
                    handler._transforms = []
                    handler.set_status(401)
                    code = 4001
                    message = 'Invalid headers.'

                response = {
                    'code': code,
                    'status': status,
                    'result': [],
                    'message': message
                }
                Log.d('No-Xen', response)
                handler.write(response)
                handler.finish()

            return False

        def _execute(self, transforms, *args, **kwargs):
            try:
                require_auth(self, kwargs)
            except Exception:
                return False

            return handler_execute(self, transforms, *args, **kwargs)

        return _execute

    handler_class._execute = wrap_execute(handler_class._execute)
    return handler_class
