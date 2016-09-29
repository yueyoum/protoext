#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       gen
Date Created:   2016-09-27 16:38
Description:

"""

import sys
from google.protobuf.compiler.plugin_pb2 import CodeGeneratorRequest, CodeGeneratorResponse

from protoext.lang_python import make_response_file as python_make_response_file
from protoext.lang_erlang import make_response_file as erlang_make_response_file

LANGUAGE_BACKEND = {
    'python': python_make_response_file,
    'erlang': erlang_make_response_file,
}


def protoext(lang=None):
    if not lang:
        lang = LANGUAGE_BACKEND.keys()
    else:
        lang = [lang]

    data = sys.stdin.read()

    req = CodeGeneratorRequest()
    req.ParseFromString(data)

    response = CodeGeneratorResponse()

    for l in lang:
        response_file = response.file.add()
        LANGUAGE_BACKEND[l](req.proto_file, response_file)

    result = response.SerializeToString()
    sys.stdout.write(result)


def protoext_python():
    protoext(lang='python')

def protoext_erlang():
    protoext(lang='erlang')

if __name__ == '__main__':
    protoext()
