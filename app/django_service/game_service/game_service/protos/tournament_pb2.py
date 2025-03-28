# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# NO CHECKED-IN PROTOBUF GENCODE
# source: tournament.proto
# Protobuf Python Version: 5.29.0
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(
    _runtime_version.Domain.PUBLIC,
    5,
    29,
    0,
    '',
    'tournament.proto'
)
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from google.protobuf import timestamp_pb2 as google_dot_protobuf_dot_timestamp__pb2
from google.protobuf import empty_pb2 as google_dot_protobuf_dot_empty__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x10tournament.proto\x12\rtranscendence\x1a\x1fgoogle/protobuf/timestamp.proto\x1a\x1bgoogle/protobuf/empty.proto\"\x8d\x02\n\x0eTournamentRoom\x12\n\n\x02id\x18\x01 \x01(\x05\x12\x0c\n\x04name\x18\x02 \x01(\t\x12\x11\n\tis_active\x18\x03 \x01(\x08\x12\x0f\n\x07started\x18\x04 \x01(\x08\x12\x17\n\x0ftournament_size\x18\x05 \x01(\x05\x12\x14\n\x0c\x63hat_room_id\x18\x06 \x01(\x05\x12.\n\nstart_time\x18\x07 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\x12.\n\ncreated_at\x18\x08 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\x12.\n\nupdated_at\x18\t \x01(\x0b\x32\x1a.google.protobuf.Timestamp\"\xe2\x01\n\x0eTournamentUser\x12\n\n\x02id\x18\x01 \x01(\x05\x12\x1a\n\x12tournament_room_id\x18\x02 \x01(\x05\x12\r\n\x05State\x18\x03 \x01(\t\x12\x0f\n\x07user_id\x18\x04 \x01(\x05\x12\x12\n\nplay_order\x18\x05 \x01(\x05\x12\x14\n\x0cgames_played\x18\x06 \x01(\x05\x12.\n\ncreated_at\x18\x07 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\x12.\n\nupdated_at\x18\x08 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\"\x91\x01\n\x15TournamentGameMapping\x12\n\n\x02id\x18\x01 \x01(\x05\x12\x1a\n\x12tournament_room_id\x18\x02 \x01(\x05\x12\x0f\n\x07game_id\x18\x03 \x01(\x05\x12\x0f\n\x07user_id\x18\x04 \x01(\x05\x12.\n\ncreated_at\x18\x05 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\"6\n\x18GetTournamentRoomRequest\x12\x1a\n\x12tournament_room_id\x18\x01 \x01(\x05\"\x1c\n\x1aListTournamentRoomsRequest\"V\n\x1bListTournamentRoomsResponse\x12\x37\n\x10tournament_rooms\x18\x01 \x03(\x0b\x32\x1d.transcendence.TournamentRoom\"\x8a\x01\n\x1b\x43reateTournamentRoomRequest\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x17\n\x0ftournament_size\x18\x02 \x01(\x05\x12\x14\n\x0c\x63hat_room_id\x18\x03 \x01(\x05\x12.\n\nstart_time\x18\x04 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\"Z\n\x1bUpdateTournamentRoomRequest\x12\x1a\n\x12tournament_room_id\x18\x01 \x01(\x05\x12\x0c\n\x04name\x18\x02 \x01(\t\x12\x11\n\tis_active\x18\x03 \x01(\x08\"9\n\x1b\x44\x65leteTournamentRoomRequest\x12\x1a\n\x12tournament_room_id\x18\x01 \x01(\x05\"6\n\x18GetTournamentUserRequest\x12\x1a\n\x12tournament_user_id\x18\x01 \x01(\x05\"8\n\x1aListTournamentUsersRequest\x12\x1a\n\x12tournament_room_id\x18\x01 \x01(\x05\"V\n\x1bListTournamentUsersResponse\x12\x37\n\x10tournament_users\x18\x01 \x03(\x0b\x32\x1d.transcendence.TournamentUser\"^\n\x1b\x43reateTournamentUserRequest\x12\x1a\n\x12tournament_room_id\x18\x01 \x01(\x05\x12\x0f\n\x07user_id\x18\x02 \x01(\x05\x12\x12\n\nplay_order\x18\x03 \x01(\x05\"r\n\x1bUpdateTournamentUserRequest\x12\x1a\n\x12tournament_user_id\x18\x01 \x01(\x05\x12\x12\n\nplay_order\x18\x02 \x01(\x05\x12\x14\n\x0cgames_played\x18\x03 \x01(\x05\x12\r\n\x05state\x18\x04 \x01(\t\"9\n\x1b\x44\x65leteTournamentUserRequest\x12\x1a\n\x12tournament_user_id\x18\x01 \x01(\x05\"E\n\x1fGetTournamentGameMappingRequest\x12\"\n\x1atournament_game_mapping_id\x18\x01 \x01(\x05\"?\n!ListTournamentGameMappingsRequest\x12\x1a\n\x12tournament_room_id\x18\x01 \x01(\x05\"l\n\"ListTournamentGameMappingsResponse\x12\x46\n\x18tournament_game_mappings\x18\x01 \x03(\x0b\x32$.transcendence.TournamentGameMapping\"b\n\"CreateTournamentGameMappingRequest\x12\x1a\n\x12tournament_room_id\x18\x01 \x01(\x05\x12\x0f\n\x07game_id\x18\x02 \x01(\x05\x12\x0f\n\x07user_id\x18\x03 \x01(\x05\"H\n\"DeleteTournamentGameMappingRequest\x12\"\n\x1atournament_game_mapping_id\x18\x01 \x01(\x05\x32\xc5\x0b\n\x11TournamentService\x12[\n\x11GetTournamentRoom\x12\'.transcendence.GetTournamentRoomRequest\x1a\x1d.transcendence.TournamentRoom\x12l\n\x13ListTournamentRooms\x12).transcendence.ListTournamentRoomsRequest\x1a*.transcendence.ListTournamentRoomsResponse\x12\x61\n\x14\x43reateTournamentRoom\x12*.transcendence.CreateTournamentRoomRequest\x1a\x1d.transcendence.TournamentRoom\x12\x61\n\x14UpdateTournamentRoom\x12*.transcendence.UpdateTournamentRoomRequest\x1a\x1d.transcendence.TournamentRoom\x12Z\n\x14\x44\x65leteTournamentRoom\x12*.transcendence.DeleteTournamentRoomRequest\x1a\x16.google.protobuf.Empty\x12[\n\x11GetTournamentUser\x12\'.transcendence.GetTournamentUserRequest\x1a\x1d.transcendence.TournamentUser\x12l\n\x13ListTournamentUsers\x12).transcendence.ListTournamentUsersRequest\x1a*.transcendence.ListTournamentUsersResponse\x12\x61\n\x14\x43reateTournamentUser\x12*.transcendence.CreateTournamentUserRequest\x1a\x1d.transcendence.TournamentUser\x12\x61\n\x14UpdateTournamentUser\x12*.transcendence.UpdateTournamentUserRequest\x1a\x1d.transcendence.TournamentUser\x12Z\n\x14\x44\x65leteTournamentUser\x12*.transcendence.DeleteTournamentUserRequest\x1a\x16.google.protobuf.Empty\x12p\n\x18GetTournamentGameMapping\x12..transcendence.GetTournamentGameMappingRequest\x1a$.transcendence.TournamentGameMapping\x12\x81\x01\n\x1aListTournamentGameMappings\x12\x30.transcendence.ListTournamentGameMappingsRequest\x1a\x31.transcendence.ListTournamentGameMappingsResponse\x12v\n\x1b\x43reateTournamentGameMapping\x12\x31.transcendence.CreateTournamentGameMappingRequest\x1a$.transcendence.TournamentGameMapping\x12h\n\x1b\x44\x65leteTournamentGameMapping\x12\x31.transcendence.DeleteTournamentGameMappingRequest\x1a\x16.google.protobuf.Emptyb\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'tournament_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  DESCRIPTOR._loaded_options = None
  _globals['_TOURNAMENTROOM']._serialized_start=98
  _globals['_TOURNAMENTROOM']._serialized_end=367
  _globals['_TOURNAMENTUSER']._serialized_start=370
  _globals['_TOURNAMENTUSER']._serialized_end=596
  _globals['_TOURNAMENTGAMEMAPPING']._serialized_start=599
  _globals['_TOURNAMENTGAMEMAPPING']._serialized_end=744
  _globals['_GETTOURNAMENTROOMREQUEST']._serialized_start=746
  _globals['_GETTOURNAMENTROOMREQUEST']._serialized_end=800
  _globals['_LISTTOURNAMENTROOMSREQUEST']._serialized_start=802
  _globals['_LISTTOURNAMENTROOMSREQUEST']._serialized_end=830
  _globals['_LISTTOURNAMENTROOMSRESPONSE']._serialized_start=832
  _globals['_LISTTOURNAMENTROOMSRESPONSE']._serialized_end=918
  _globals['_CREATETOURNAMENTROOMREQUEST']._serialized_start=921
  _globals['_CREATETOURNAMENTROOMREQUEST']._serialized_end=1059
  _globals['_UPDATETOURNAMENTROOMREQUEST']._serialized_start=1061
  _globals['_UPDATETOURNAMENTROOMREQUEST']._serialized_end=1151
  _globals['_DELETETOURNAMENTROOMREQUEST']._serialized_start=1153
  _globals['_DELETETOURNAMENTROOMREQUEST']._serialized_end=1210
  _globals['_GETTOURNAMENTUSERREQUEST']._serialized_start=1212
  _globals['_GETTOURNAMENTUSERREQUEST']._serialized_end=1266
  _globals['_LISTTOURNAMENTUSERSREQUEST']._serialized_start=1268
  _globals['_LISTTOURNAMENTUSERSREQUEST']._serialized_end=1324
  _globals['_LISTTOURNAMENTUSERSRESPONSE']._serialized_start=1326
  _globals['_LISTTOURNAMENTUSERSRESPONSE']._serialized_end=1412
  _globals['_CREATETOURNAMENTUSERREQUEST']._serialized_start=1414
  _globals['_CREATETOURNAMENTUSERREQUEST']._serialized_end=1508
  _globals['_UPDATETOURNAMENTUSERREQUEST']._serialized_start=1510
  _globals['_UPDATETOURNAMENTUSERREQUEST']._serialized_end=1624
  _globals['_DELETETOURNAMENTUSERREQUEST']._serialized_start=1626
  _globals['_DELETETOURNAMENTUSERREQUEST']._serialized_end=1683
  _globals['_GETTOURNAMENTGAMEMAPPINGREQUEST']._serialized_start=1685
  _globals['_GETTOURNAMENTGAMEMAPPINGREQUEST']._serialized_end=1754
  _globals['_LISTTOURNAMENTGAMEMAPPINGSREQUEST']._serialized_start=1756
  _globals['_LISTTOURNAMENTGAMEMAPPINGSREQUEST']._serialized_end=1819
  _globals['_LISTTOURNAMENTGAMEMAPPINGSRESPONSE']._serialized_start=1821
  _globals['_LISTTOURNAMENTGAMEMAPPINGSRESPONSE']._serialized_end=1929
  _globals['_CREATETOURNAMENTGAMEMAPPINGREQUEST']._serialized_start=1931
  _globals['_CREATETOURNAMENTGAMEMAPPINGREQUEST']._serialized_end=2029
  _globals['_DELETETOURNAMENTGAMEMAPPINGREQUEST']._serialized_start=2031
  _globals['_DELETETOURNAMENTGAMEMAPPINGREQUEST']._serialized_end=2103
  _globals['_TOURNAMENTSERVICE']._serialized_start=2106
  _globals['_TOURNAMENTSERVICE']._serialized_end=3583
# @@protoc_insertion_point(module_scope)
