# -*- coding: utf-8 -*-

"""
Author:        Wang Chao <yueyoum@gmail.com>
Filename:      lang_python.py
Date created:  2016-09-24 22:01:45
Description:

"""

import datetime
from protoext.base import Template, PackageTree


def make_response_file(proto_files, response_file):
    root = PackageTree()
    root.name = None

    response_file.name = 'out.py'

    for proto in proto_files:
        tmp = PythonTemplate()
        tmp.format(proto)

        tree = tmp.get_tree()
        root.merge_tree(tree)

    response_file.content = '{0}{1}{2}'.format(
        HEADER % datetime.datetime.now().isoformat(),
        root.get_content(),
        FOOTER
    )


class PythonTemplate(Template):
    def __init__(self):
        super(PythonTemplate, self).__init__()
        self.tree = PackageTree()

    def get_tree(self, index=0):
        """

        :rtype: PackageTree
        """
        t = self.tree
        for i in range(index):
            if not t.children:
                t.children.append(PackageTree())

            t = t.children[0]

        return t

    def finish(self):
        t = self.tree
        while True:
            if not t.children:
                t.content = "{0}\n{1}".format(t.content, self.get_content())
                break

            t = t.children[0]

    def set_package(self):
        pkg_list = self.package.split('.')
        for index, p in enumerate(pkg_list):
            t = self.get_tree(index)
            t.name = p
            t.content = "{0}class {1}(_Package):".format(' ' * self.indent * 4, p)

            self.indent += 1

    def visit_enum(self, enum_type):
        self.add_line("class {0}(object):".format(enum_type.name))
        self.indent += 1

        for value in enum_type.value:
            self.add_line("{0} = {1}".format(value.name, value.number))

        self.indent -= 1

    def visit_message(self, proto_message):
        self.add_line("class {0}(_Message):".format(proto_message.name))
        self.indent += 1

        if proto_message.enum_type:
            for enum_type in proto_message.enum_type:
                self.add_enum_type(enum_type)

        if proto_message.nested_type:
            for nested_type in proto_message.nested_type:
                self.add_message_type(nested_type)

        slots = "__slots__ = ["
        for field in proto_message.field:
            slots += '"{0}", '.format(field.name)

        slots += "]"
        self.add_line(slots)

        self.add_line('FULL_NAME = "{0}"'.format(self.get_full_name()))
        self.add_line()

        self.add_line("def __init__(self):")
        self.indent += 1
        for field in proto_message.field:
            self.add_line("self.{0} = None".format(field.name))

        self.add_line()
        self.indent -= 1
        self.add_line("def __str__(self):")
        self.indent += 1
        self.add_line("f = _Formatter()")
        self.add_line("f.format_message(self)")
        self.add_line("return f.get_content()")

        self.indent -= 2


##################


HEADER = """# Auto generate at %s.
# By proto-ext
# DO NOT EDIT

import math
import struct

int_1_byte = struct.Struct('>B')
int_2_byte = struct.Struct('>H')
int_4_byte = struct.Struct('>I')

INTEGER_32_MAX = 2 ** 31 - 1
INTEGER_32_MIN = - 2 ** 31


class _Package(object):
    pass


class _Message(object):
    __slots__ = []
    FULL_NAME = ''

## PROTOCOL START ##
"""

FOOTER = """
## PROTOCOL END ##

# TODO using c extension
def encode(obj):
    encoder = _Encoder()
    encoder.encode_message(obj)
    return ''.join(encoder.byte_chunks)

def decode(message):
    decoder = _Decoder(message)
    decoder.decode()
    return decoder.obj

class _Formatter(object):
    def __init__(self):
        self.indent = -1
        self.lines = []

    def get_content(self):
        return '\\n'.join(self.lines)

    def make_blank(self):
        return ' ' * 2 * self.indent

    def add_line(self, content=''):
        line = '{0}{1}'.format(self.make_blank(), content)
        self.lines.append(line)

    def format_message(self, obj):
        self.indent += 1
        line = '< {0} >'.format(obj.FULL_NAME)
        self.add_line(line)

        self.indent += 1

        for field in obj.__slots__:
            line = '{0}: '.format(field)
            self.add_line(line)

            value = getattr(obj, field)
            self.format_value(value)

        self.add_line()
        self.indent -= 2

    def format_value(self, value):
        if isinstance(value, _Message):
            self.format_message(value)
        elif isinstance(value, (list, tuple)):
            self.add_line('[')
            self.indent += 1
            self.add_line()

            for v in value:
                self.format_value(v)

            self.indent -= 1
            self.add_line(']')
        else:
            self.lines[-1] = self.lines[-1] + ' {0} '.format(value)


class _Decoder(object):
    def __init__(self, message):
        self.obj = None
        self.message = message
        self.index = 0

    def decode(self):
        if int_1_byte.unpack(self.message[self.index])[0] != 131:
            raise ValueError("Invalid version header")

        self.index += 1
        self.obj = self.decode_value()

    def decode_message(self, arity):
        if int_1_byte.unpack(self.message[self.index])[0] != 100:
            raise ValueError("Invalid Atom header")

        name = self.decode_value()
        name_list = name.split('.')

        obj = globals()[name_list[0]]
        for n in name_list[1:]:
            obj = getattr(obj, n)

        obj = obj()
        for i in range(arity-1):
            key = obj.__slots__[i]
            value = self.decode_value()
            setattr(obj, key, value)

        return obj

    def decode_value(self):
        tag = int_1_byte.unpack(self.message[self.index])[0]
        self.index += 1

        if tag == 97:
            value = int_1_byte.unpack(self.message[self.index])[0]
            self.index += 1
            return value

        if tag == 98:
            value = int_4_byte.unpack(self.message[self.index: self.index + 4])[0]
            self.index += 4
            return value

        if tag == 70:
            value = struct.unpack('>d', self.message[self.index: self.index + 8])[0]
            self.index += 8
            return value

        if tag == 100:
            length = int_2_byte.unpack(self.message[self.index: self.index + 2])[0]
            self.index += 2
            value = struct.unpack('{0}s'.format(length), self.message[self.index: self.index + length])[0]
            self.index += length

            if value == "undefined":
                return None
            if value == "true":
                return True
            if value == "false":
                return False

            return value

        if tag == 104:
            arity = int_1_byte.unpack(self.message[self.index])[0]
            self.index += 1
            return self.decode_message(arity)

        if tag == 105:
            arity = int_4_byte.unpack(self.message[self.index: self.index + 4])[0]
            self.index += 4
            return self.decode_message(arity)

        if tag == 107:
            length = int_2_byte.unpack(self.message[self.index: self.index + 2])[0]
            self.index += 2
            value = []
            for i in range(length):
                value.append(struct.unpack('>c', self.message[self.index])[0])
                self.index += 1

            return ''.join(value)

        if tag == 109:
            length = int_4_byte.unpack(self.message[self.index: self.index + 4])[0]
            self.index += 4
            value = struct.unpack('{0}s'.format(length), self.message[self.index: self.index + length])[0]
            self.index += length
            return value

        if tag == 110:
            n = int_1_byte.unpack(self.message[self.index])[0]
            self.index += 1
            sign = int_1_byte.unpack(self.message[self.index])[0]
            self.index += 1

            value = 0
            for i in range(n):
                d = int_1_byte.unpack(self.message[self.index])[0]
                self.index += 1

                value += d * 256 ** i

            if sign == 0:
                return value
            return -value

        if tag == 111:
            n = int_4_byte.unpack(self.message[self.index: self.index + 4])[0]
            self.index += 4
            sign = int_1_byte.unpack(self.message[self.index])[0]
            self.index += 1

            value = 0
            for i in range(n):
                d = int_1_byte.unpack(self.message[self.index])[0]
                self.index += 1

                value += d * 256 ** i

            if sign == 0:
                return value
            return -value

        if tag == 108:
            length = int_4_byte.unpack(self.message[self.index: self.index + 4])[0]
            self.index += 4

            value = []
            for i in range(length):
                value.append(self.decode_value())

            tail = int_1_byte.unpack(self.message[self.index])[0]
            if tail == 106:
                self.index += 1

            return value

        raise ValueError("UnSupported tag: {0}".format(tag))


class _Encoder(object):
    def __init__(self):
        self.byte_chunks = _encode_version()

    def encode_message(self, obj):
        self.byte_chunks.extend(
            _encode_tuple_header(len(obj.__slots__) + 1, obj.FULL_NAME)
        )

        for field in obj.__slots__:
            value = getattr(obj, field)
            self.encode_value(value)

    def encode_value(self, value):
        if value is None:
            self.byte_chunks.extend(_encode_atom("undefined"))
        elif value is True:
            self.byte_chunks.extend(_encode_atom("true"))
        elif value is False:
            self.byte_chunks.extend(_encode_atom("false"))

        elif isinstance(value, (int, long)):
            self.byte_chunks.extend(_encode_integer(value))
        elif isinstance(value, float):
            self.byte_chunks.extend(_encode_float(value))
        elif isinstance(value, (basestring, bytearray)):
            self.byte_chunks.extend(_encode_binary(value))
        elif isinstance(value, (list, tuple)):
            self.byte_chunks.extend(_encode_list_header(len(value)))

            for v in value:
                self.encode_value(v)

            self.byte_chunks.extend(_encode_list_tail())
        elif isinstance(value, _Message):
            self.encode_message(value)


def _encode_integer(value):
    if 0 <= value <= 255:
        return [int_1_byte.pack(97), int_1_byte.pack(value)]

    if INTEGER_32_MIN <= value <= INTEGER_32_MAX:
        return [int_1_byte.pack(98), int_4_byte.pack(value)]

    if value < 0:
        sign = 1
        value = -value
    else:
        sign = 0

    n = int(math.ceil(math.log(value, 256)))
    seq = []
    for i in range(n - 1, -1, -1):
        d, value = divmod(value, 256 ** i)
        seq.insert(0, d)

    chunks = []
    if n > 255:
        chunks.append(int_1_byte.pack(111))
        chunks.append(int_4_byte.pack(n))
    else:
        chunks.append(int_1_byte.pack(110))
        chunks.append(int_1_byte.pack(n))

    chunks.append(int_1_byte.pack(sign))
    for d in seq:
        chunks.append(int_1_byte.pack(d))

    return chunks


def _encode_float(value):
    return [
        int_1_byte.pack(70),
        struct.pack('>d', value)
    ]


def _encode_binary(value):
    length = len(value)
    return [
        int_1_byte.pack(109),
        int_4_byte.pack(length),
        struct.pack('{0}s'.format(length), value)
    ]


def _encode_atom(value):
    length = len(value)
    return [
        int_1_byte.pack(100),
        int_2_byte.pack(length),
        struct.pack('{0}s'.format(length), value)
    ]


def _encode_version():
    return [
        int_1_byte.pack(131)
    ]


def _encode_tuple_header(arity, name):
    if arity < 255:
        chunks = [
            int_1_byte.pack(104),
            int_1_byte.pack(arity),
        ]
    else:
        chunks = [
            int_1_byte.pack(105),
            int_4_byte.pack(arity),
        ]

    chunks.extend(_encode_atom(name))
    return chunks


def _encode_list_header(length):
    return [
        int_1_byte.pack(108),
        int_4_byte.pack(length)
    ]


def _encode_list_tail():
    return [
        int_1_byte.pack(106)
    ]


"""
