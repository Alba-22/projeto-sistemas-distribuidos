# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: api.proto
"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\tapi.proto\"#\n\x06\x43lient\x12\x0b\n\x03\x43ID\x18\x01 \x01(\t\x12\x0c\n\x04\x64\x61ta\x18\x02 \x01(\t\"$\n\x07Product\x12\x0b\n\x03PID\x18\x01 \x01(\t\x12\x0c\n\x04\x64\x61ta\x18\x02 \x01(\t\"/\n\x05Order\x12\x0b\n\x03OID\x18\x01 \x01(\t\x12\x0b\n\x03\x43ID\x18\x02 \x01(\t\x12\x0c\n\x04\x64\x61ta\x18\x03 \x01(\t\"@\n\x05Reply\x12\r\n\x05\x65rror\x18\x01 \x01(\x05\x12\x18\n\x0b\x64\x65scription\x18\x02 \x01(\tH\x00\x88\x01\x01\x42\x0e\n\x0c_description\"\x10\n\x02ID\x12\n\n\x02ID\x18\x01 \x01(\t2\xa2\x02\n\x0b\x41\x64minPortal\x12!\n\x0c\x43reateClient\x12\x07.Client\x1a\x06.Reply\"\x00\x12 \n\x0eRetrieveClient\x12\x03.ID\x1a\x07.Client\"\x00\x12!\n\x0cUpdateClient\x12\x07.Client\x1a\x06.Reply\"\x00\x12\x1d\n\x0c\x44\x65leteClient\x12\x03.ID\x1a\x06.Reply\"\x00\x12#\n\rCreateProduct\x12\x08.Product\x1a\x06.Reply\"\x00\x12\"\n\x0fRetrieveProduct\x12\x03.ID\x1a\x08.Product\"\x00\x12#\n\rUpdateProduct\x12\x08.Product\x1a\x06.Reply\"\x00\x12\x1e\n\rDeleteProduct\x12\x03.ID\x1a\x06.Reply\"\x00\x32\xb6\x01\n\x0bOrderPortal\x12\x1f\n\x0b\x43reateOrder\x12\x06.Order\x1a\x06.Reply\"\x00\x12\x1e\n\rRetrieveOrder\x12\x03.ID\x1a\x06.Order\"\x00\x12\x1f\n\x0bUpdateOrder\x12\x06.Order\x1a\x06.Reply\"\x00\x12\x1c\n\x0b\x44\x65leteOrder\x12\x03.ID\x1a\x06.Reply\"\x00\x12\'\n\x14RetrieveClientOrders\x12\x03.ID\x1a\x06.Order\"\x00\x30\x01\x62\x06proto3')

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'api_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  _CLIENT._serialized_start=13
  _CLIENT._serialized_end=48
  _PRODUCT._serialized_start=50
  _PRODUCT._serialized_end=86
  _ORDER._serialized_start=88
  _ORDER._serialized_end=135
  _REPLY._serialized_start=137
  _REPLY._serialized_end=201
  _ID._serialized_start=203
  _ID._serialized_end=219
  _ADMINPORTAL._serialized_start=222
  _ADMINPORTAL._serialized_end=512
  _ORDERPORTAL._serialized_start=515
  _ORDERPORTAL._serialized_end=697
# @@protoc_insertion_point(module_scope)
