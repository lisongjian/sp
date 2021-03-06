#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
加解密模块
@author zhenyong
"""
import random
import base64

from hashlib import sha1
from Crypto import Random
from Crypto.Cipher import AES


class AESCipher:
    """ AES 加密解密 """

    def __init__(self, key):
        self.bs = 16
        if len(key) >= 16:
            self.key = key[:16]
        else:
            self.key = self._pad(key)

    def encrypt(self, raw):
        raw = self._pad(raw)
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return base64.b64encode(iv + cipher.encrypt(raw))

    def decrypt(self, enc):
        enc = base64.b64decode(enc)
        iv = enc[:AES.block_size]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return self._unpad(cipher.decrypt(enc[AES.block_size:]))

    def _pad(self, s):
        return s + (self.bs - len(s) % self.bs) * chr(self.bs - len(s) % self.bs)

    def _unpad(self, s):
        return s[:-ord(s[len(s) - 1:])]


class RC4Cipher:
    """ RC4 加密解密 """

    def __init__(self, key):
        self.key = key

    def crypt(self, data, key):
        """RC4 algorithm"""
        x = 0
        box = range(256)
        for i in range(256):
            x = (x + box[i] + ord(key[i % len(key)])) % 256
            box[i], box[x] = box[x], box[i]
        x = y = 0
        out = []
        for char in data:
            x = (x + 1) % 256
            y = (y + box[x]) % 256
            box[x], box[y] = box[y], box[x]
            out.append(chr(ord(char) ^ box[(box[x] + box[y]) % 256]))

        return ''.join(out)

    def encrypt(self, data, encode=base64.b64encode, salt_length=16):
        """RC4 encryption with random salt and final encoding"""
        salt = ''
        for n in range(salt_length):
            salt += chr(random.randrange(256))
        data = salt + self.crypt(data, sha1(self.key + salt).digest())
        if encode:
            data = encode(data)
        return data

    def decrypt(self, data, decode=base64.b64decode, salt_length=16):
        """RC4 decryption of encoded data"""
        if decode:
            data = decode(data)
        salt = data[:salt_length]
        return self.crypt(data[salt_length:], sha1(self.key + salt).digest())
