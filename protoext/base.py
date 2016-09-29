# -*- coding: utf-8 -*-

"""
Author:        Wang Chao <yueyoum@gmail.com>
Filename:      base.py
Date created:  2016-09-24 22:01:45
Description:

"""

import sys
# from google.protobuf.descriptor_pb2 import FieldDescriptorProto


class Template(object):
    def __init__(self):
        self.lines = []
        self.indent = 0
        self.proto_file_name = ""
        self.package = ""
        self.name_stack = []

    def format(self, proto_file):
        """

        :type proto_file: google.protobuf.descriptor_pb2.FileDescriptorProto
        """

        self.package = proto_file.package
        self.proto_file_name = proto_file.name

        if proto_file.package:
            self.name_stack.append(proto_file.package)
            self.set_package()

        for enum_type in proto_file.enum_type:
            self.add_enum_type(enum_type)

        for message_type in proto_file.message_type:
            self.add_message_type(message_type)

        self.finish()

    def get_full_name(self):
        return '.'.join(self.name_stack)

    def get_content(self):
        return "\n".join(self.lines)

    def add_line(self, content=""):
        self.lines.append(' ' * self.indent * 4 + content)

    def finish(self):
        pass

    def set_package(self):
        pass

    def add_enum_type(self, enum_type):

        """

        :type enum_type: google.protobuf.descriptor_pb2.EnumDescriptorProto
        """
        self.name_stack.append(enum_type.name)
        self.visit_enum(enum_type)

        self.name_stack.pop(-1)
        self.add_line()

    def add_message_type(self, proto_message):
        """

        :type proto_message: google.protobuf.descriptor_pb2.DescriptorProto
        """
        self.name_stack.append(proto_message.name)
        self.visit_message(proto_message)

        self.name_stack.pop(-1)
        self.add_line()

    def visit_enum(self, enum_type):
        raise NotImplementedError()

    def visit_message(self, proto_message):
        raise NotImplementedError()


class PackageTree(object):
    def __init__(self):
        self.name = None
        self.content = ''
        self.children = []
        """:type: list[PackageTree]"""

        self.chunks = []

    def merge_tree(self, t):
        """

        :type t: PackageTree
        """

        for ch in self.children:
            if ch.name == t.name:
                if t.children:
                    for ch1 in t.children:
                        ch.merge_tree(ch1)
                else:
                    _, b = t.content.split('\n', 1)
                    ch.content = '{0}\n{1}'.format(ch.content, b)

                break
        else:
            self.children.append(t)

    def get_content(self):
        self.chunks = []

        def get_child_content(t):
            self.chunks.append(t.content)

            for _ch in t.children:
                get_child_content(_ch)

        get_child_content(self)
        return '\n'.join(self.chunks)

    def output(self, indent=0, out=sys.stderr):
        out.write("{0}{1}\n".format(' ' * indent * 4, self.name))
        for ch in self.children:
            ch.output(indent=indent + 1, out=out)
