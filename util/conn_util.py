#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Mongo Database Connection Class
import motor.motor_asyncio

from build_config import CONFIG
from util.log_util import Log


class MongoMixin(object):
    # serviceDb = None

    '''
    try:
        #USER_DBPOOL = txmongo.MongoConnection(
        #        CONFIG['database'][0]['host'],
        #        CONFIG['database'][0]['port'],
        #    )
        #USER_DATABASE = getattr(USER_DBPOOL, CONFIG['database'][0]['key'])
        Log.i('MONGO', 'User Database Service has been Initialized!')
    except:
        Log.i('MONGO', 'User Database Service has been Initialization Failed!')

    '''

    # def initUserDb():
    try:
        client = motor.motor_asyncio.AsyncIOMotorClient(
            CONFIG['database'][0]['host'],
            CONFIG['database'][0]['port'],
        )

        # options = {'async': True}
        # await client.fsync(**options)
        # MongoMixin.userDb = client[CONFIG['database'][0]['key']]

        userDb = client[CONFIG['database'][0]['key']]
        client = None
        # Log.i(userDb)

        Log.i('MONGO', '{} has been Initialized!'.format(CONFIG['database'][0]['key']))
    except:
        userDb = None
        Log.i('MONGO', 'Ether Database has been Initialization Failed!')

# # Firebase Connection Class
# class FirebaseMixin(object):
# #     # serviceDb = None
# #
#     fb = None
#     try:
#         TAG = 'Firebase'
#         import firebase_admin
#         from firebase_admin import credentials
#         credPath = CONFIG['database'][4]['cred']
#
#         cred = credentials.Certificate(credPath)
#         fb = firebase_admin.initialize_app(cred)
#
#         Log.i('Firebase', 'has been Initialized! {}'.format(fb.name))
#
#         #client = motor.motor_asyncio.AsyncIOMotorClient(
#         #    CONFIG['database'][1]['host'],
#         #    CONFIG['database'][1]['port'],
#         #)
#
#     except Exception as e:
#         fb = None
#         Log.i('Firebase', 'has been Initialization Failed! {}'.format(e))
#
