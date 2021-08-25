#!/usr/bin/env python
# -*- coding: utf-8 -*-
import random
import sys

import jwt
from datetime import datetime as dtime

from lib.fernet_crypto import FN_ENCRYPT, FN_DECRYPT

sys.path.append('./utils')

from bson.objectid import ObjectId

SECRETS = [
    'IS-*HGJHFKJL^%*&^(&%T&I^RU^%EI^%^*&(*^*%%*^(^&O^*(*P(UYUFHGJL^KKJGFHRTO&^*&YUTYII',
    'IS-%*^&*YUTIFUKGLH(&^%(&^GTLO*&^%$^%RI^%RO*^*O&YP&*^(^&*(&*^(&*JJKJuBKMLFGHJ**UJH',
]
OPTIONS = {
    'verify_signature': True,
    'verify_exp': True,
    'verify_nbf': False,
    'verify_iat': True,
    'verify_aud': False
}


def JWT_ENCODE(payload=str):
    try:
        kyE = FN_ENCRYPT(payload, True)
        if (kyE):
            index = random.randint(0, len(SECRETS) - 1)
            kyEn = jwt.encode(
                {
                    'key': kyE.decode(),
                    'exp': dtime.datetime.utcnow() + dtime.timedelta(seconds=31536000)
                },
                SECRETS[index],
                algorithm='HS256'
            )
            if type(kyEn) is bytes:
                return kyEn.decode()
            else:
                return kyEn
        else:
            return False
    except:
        return False


def JWT_DECODE(token=str):
    try:
        if len(SECRETS):
            for s in SECRETS:
                try:
                    tokenObj = jwt.decode(token, s, options=OPTIONS)
                    kyDe = FN_DECRYPT(tokenObj['key'])
                    if kyDe:
                        return kyDe
                except:
                    continue

    except:
        return False

    return False
