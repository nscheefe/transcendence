# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: permission.proto
"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x10permission.proto\x12\x06models\";\n\nPermission\x12\n\n\x02id\x18\x01 \x01(\x05\x12\x0c\n\x04name\x18\x02 \x01(\t\x12\x13\n\x0b\x64\x65scription\x18\x03 \x01(\t\"<\n\x17\x43reatePermissionRequest\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x13\n\x0b\x64\x65scription\x18\x02 \x01(\t\"&\n\x18GetPermissionByIdRequest\x12\n\n\x02id\x18\x01 \x01(\x05\x32\xa7\x01\n\x11PermissionService\x12G\n\x10\x43reatePermission\x12\x1f.models.CreatePermissionRequest\x1a\x12.models.Permission\x12I\n\x11GetPermissionById\x12 .models.GetPermissionByIdRequest\x1a\x12.models.Permissionb\x06proto3')

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'permission_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  _PERMISSION._serialized_start=28
  _PERMISSION._serialized_end=87
  _CREATEPERMISSIONREQUEST._serialized_start=89
  _CREATEPERMISSIONREQUEST._serialized_end=149
  _GETPERMISSIONBYIDREQUEST._serialized_start=151
  _GETPERMISSIONBYIDREQUEST._serialized_end=189
  _PERMISSIONSERVICE._serialized_start=192
  _PERMISSIONSERVICE._serialized_end=359
# @@protoc_insertion_point(module_scope)
