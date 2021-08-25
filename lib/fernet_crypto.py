#!/usr/bin/env python
# -*- coding: utf-8 -*-

import base64
import calendar
import datetime as dtime
import os
import sys
import random
from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from util.log_util import Log

CODES = [
    b'ISO-KJHGIa*&^%KIYUGIU&^%&(%^*&^%*&^%*&^%T&YUKUTY&&)*T&T',
    b'ISO-@%$#4ert(&^(&*^(&*^&*^59856798679867987697^%$#$*T&T',
    b'ISO-**I&(^(&^(&*Y^(78yt98679867y98769867987669897$#*T&T',
]

# Monday, July 15, 2019 15:34:17
SALT = b'1563204857'
FERNETS = []

for c in CODES:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=SALT,
        iterations=100000,
        backend=default_backend()
    )
    key = base64.urlsafe_b64encode(kdf.derive(c))
    f = Fernet(key)
    FERNETS.append(f)


def FN_ENCRYPT(payload=str, encode=False):
    try:
        if len(FERNETS):
            index = random.randint(0, len(FERNETS) - 1)
            f = FERNETS[index]
            if type(encode) != bytes:
                return f.encrypt(payload.encode())
            else:
                return f.encrypt(payload)
    except Exception as e:
        Log.i(e)
        return False
    return False


def FN_DECRYPT(token=str):
    try:
        if len(FERNETS):
            for f in FERNETS:
                try:
                    if type(token) != bytes:
                        d_token = f.decrypt(token.encode())
                    else:
                        d_token = f.decrypt(token)
                    return d_token
                except Exception as e:
                    # Log.i(e)
                    continue
    except Exception as e:
        Log.i(e)
        return False
    return False
