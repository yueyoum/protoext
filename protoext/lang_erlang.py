# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       lang_erlang
Date Created:   2016-09-27 17:12
Description:

"""
import datetime
from protoext.base import Template
from google.protobuf.descriptor_pb2 import FieldDescriptorProto


def make_response_file(proto_files, response_file):
    response_file.name = 'out.hrl'

    define_lines = []
    record_lines = []

    for proto in proto_files:
        t = ErlangTemplate()
        t.format(proto)
        define_lines.extend(t.define_lines)
        record_lines.extend(t.record_lines)

    response_file.content = '{0}{1}\n\n{2}'.format(
        HEADER % datetime.datetime.now().isoformat(),
        '\n'.join(define_lines),
        '\n'.join(record_lines)
    )


class ErlangTemplate(Template):
    def __init__(self):
        super(ErlangTemplate, self).__init__()
        self.define_lines = []
        self.record_lines = []

    def visit_enum(self, enum_type):
        for value in enum_type.value:
            macro = '{0}_{1}'.format(self.get_full_name(), value.name)
            macro = macro.replace('.', '_')
            macro = macro.upper()
            line = "-define(%s, %d)." % (macro, value.number)
            self.define_lines.append(line)

    def visit_message(self, proto_message):
        if proto_message.enum_type:
            for enum_type in proto_message.enum_type:
                self.add_enum_type(enum_type)

        if proto_message.nested_type:
            for nested_type in proto_message.nested_type:
                self.add_message_type(nested_type)

        self.record_lines.append("-record('%s', {" % self.get_full_name())

        for field in proto_message.field:
            line = "    %-30s:: %s," % (field.name, self.get_field_type(field))
            self.record_lines.append(line)

        self.record_lines[-1] = self.record_lines[-1][:-1]
        self.record_lines.append("}).\n")

    @staticmethod
    def get_field_type(field):
        if field.type in [
            FieldDescriptorProto.TYPE_DOUBLE,
            FieldDescriptorProto.TYPE_FLOAT,
        ]:
            tp = 'float()'
        elif field.type in [
            FieldDescriptorProto.TYPE_INT64,
            FieldDescriptorProto.TYPE_UINT64,
            FieldDescriptorProto.TYPE_INT32,
            FieldDescriptorProto.TYPE_FIXED64,
            FieldDescriptorProto.TYPE_FIXED32,
            FieldDescriptorProto.TYPE_UINT32,
            FieldDescriptorProto.TYPE_SFIXED32,
            FieldDescriptorProto.TYPE_SFIXED64,
            FieldDescriptorProto.TYPE_SINT32,
            FieldDescriptorProto.TYPE_SINT64,
            FieldDescriptorProto.TYPE_ENUM,
        ]:
            tp = 'integer()'
        elif field.type == FieldDescriptorProto.TYPE_BOOL:
            tp = 'boolean()'
        elif field.type in [
            FieldDescriptorProto.TYPE_STRING,
            FieldDescriptorProto.TYPE_BYTES,
        ]:
            tp = 'binary()'
        elif field.type == FieldDescriptorProto.TYPE_MESSAGE:
            type_name = field.type_name.lstrip('.')
            tp = "#'%s'{}" % type_name
        else:
            raise ValueError("Unsupported type: {0}".format(field.type))

        if field.label == FieldDescriptorProto.LABEL_REPEATED:
            tp = '[%s]' % tp

        return tp


#################

HEADER = """%% Auto generate at %s.
%% By proto-ext
%% DO NOT EDIT

"""
