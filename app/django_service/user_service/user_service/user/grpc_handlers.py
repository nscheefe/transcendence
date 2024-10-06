import grpc
from ..protos import (
    role_pb2_grpc,
    rolePermission_pb2_grpc,
    settings_pb2_grpc,
    user_pb2_grpc,
    userAchievement_pb2_grpc,
    profile_pb2_grpc,
    notification_pb2_grpc,
    friendship_pb2_grpc,
    permission_pb2_grpc,
)

class RoleServiceHandler(role_pb2_grpc.RoleServiceServicer):
    def CreateRole(self, request, context):
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetRoleById(self, request, context):
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

class RolePermissionServiceHandler(rolePermission_pb2_grpc.RolePermissionServiceServicer):
    def CreateRolePermission(self, request, context):
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetRolePermissionsByRoleId(self, request, context):
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

class SettingServiceHandler(settings_pb2_grpc.SettingServiceServicer):
    def CreateSetting(self, request, context):
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetSettingById(self, request, context):
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetSettingsByUserId(self, request, context):
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

class UserServiceHandler(user_pb2_grpc.UserServiceServicer):
    def CreateUser(self, request, context):
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetUser(self, request, context):
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetUsersByRoleId(self, request, context):
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

class UserAchievementServiceHandler(userAchievement_pb2_grpc.UserAchievementServiceServicer):
    def GetUserAchievementById(self, request, context):
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set.details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetUserAchievementsByUserId(self, request, context):
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set.details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def CreateUserAchievement(self, request, context):
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set.details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

class ProfileServiceHandler(profile_pb2_grpc.ProfileServiceServicer):
    def CreateProfile(self, request, context):
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set.details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetProfileById(self, request, context):
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set.details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

class NotificationServiceHandler(notification_pb2_grpc.NotificationServiceServicer):
    def CreateNotification(self, request, context):
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set.details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetNotificationsByUserId(self, request, context):
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set.details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

class FriendshipServiceHandler(friendship_pb2_grpc.FriendshipServiceServicer):
    def CreateFriendship(self, request, context):
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set.details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetFriendshipsByUserId(self, request, context):
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set.details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

class PermissionServiceHandler(permission_pb2_grpc.PermissionServiceServicer):
    def CreatePermission(self, request, context):
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set.details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetPermissionById(self, request, context):
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set.details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

def grpc_handlers(server):
    role_service_handler = RoleServiceHandler.as_servicer()
    role_pb2_grpc.add_RoleServiceServicer_to_server(role_service_handler, server)

    role_permission_service_handler = RolePermissionServiceHandler.as_servicer()
    rolePermission_pb2_grpc.add_RolePermissionServiceServicer_to_server(role_permission_service_handler, server)

    setting_service_handler = SettingServiceHandler.as_servicer()
    settings_pb2_grpc.add_SettingServiceServicer_to_server(setting_service_handler, server)

    user_service_handler = UserServiceHandler.as_servicer()
    user_pb2_grpc.add_UserServiceServicer_to_server(user_service_handler, server)

    user_achievement_service_handler = UserAchievementServiceHandler.as_servicer()
    userAchievement_pb2_grpc.add_UserAchievementServiceServicer_to_server(user_achievement_service_handler, server)

    profile_service_handler = ProfileServiceHandler.as_servicer()
    profile_pb2_grpc.add_ProfileServiceServicer_to_server(profile_service_handler, server)

    notification_service_handler = NotificationServiceHandler.as_servicer()
    notification_pb2_grpc.add_NotificationServiceServicer_to_server(notification_service_handler, server)

    friendship_service_handler = FriendshipServiceHandler.as_servicer()
    friendship_pb2_grpc.add_FriendshipServiceServicer_to_server(friendship_service_handler, server)

    permission_service_handler = PermissionServiceHandler.as_servicer()
    permission_pb2_grpc.add_PermissionServiceServicer_to_server(permission_service_handler, server)