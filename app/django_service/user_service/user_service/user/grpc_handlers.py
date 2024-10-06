# Import gRPC protobuf definitions
from user_service.protos import user_pb2_grpc, userAchievement_pb2_grpc, settings_pb2_grpc, rolePermission_pb2_grpc, role_pb2_grpc, profile_pb2_grpc, permission_pb2_grpc, notification_pb2_grpc, friendship_pb2_grpc

# Import handler classes
from user_service.user.user_grpc_handler import UserServiceHandler
from user_service.user.userArchievment_grpc_handler import UserAchievementServiceHandler
from user_service.user.setting_grpc_handler import SettingServiceHandler
from user_service.user.rolePermission_grpc_handler import RolePermissionServiceHandler
from user_service.user.role_grpc_handler import RoleServiceHandler
from user_service.user.profile_grpc_handler import ProfileServiceHandler
from user_service.user.permission_grpc_handler import PermissionServiceHandler
from user_service.user.notification_grpc_handler import NotificationServiceHandler
from user_service.user.friendship_grpc_handler import FriendshipServiceHandler

def grpc_handlers(server):
    # Register User Service
    user_service_handler = UserServiceHandler.as_servicer()
    user_pb2_grpc.add_UserServiceServicer_to_server(user_service_handler, server)

    # Register User Achievement Service
    user_achievement_service_handler = UserAchievementServiceHandler.as_servicer()
    userAchievement_pb2_grpc.add_UserAchievementServiceServicer_to_server(user_achievement_service_handler, server)

    # Register Setting Service
    setting_service_handler = SettingServiceHandler.as_servicer()
    settings_pb2_grpc.add_SettingServiceServicer_to_server(setting_service_handler, server)

    # Register Role Permission Service
    role_permission_service_handler = RolePermissionServiceHandler.as_servicer()
    rolePermission_pb2_grpc.add_RolePermissionServiceServicer_to_server(role_permission_service_handler, server)

    # Register Role Service
    role_service_handler = RoleServiceHandler.as_servicer()
    role_pb2_grpc.add_RoleServiceServicer_to_server(role_service_handler, server)

    # Register Profile Service
    profile_service_handler = ProfileServiceHandler.as_servicer()
    profile_pb2_grpc.add_ProfileServiceServicer_to_server(profile_service_handler, server)

    # Register Permission Service
    permission_service_handler = PermissionServiceHandler.as_servicer()
    permission_pb2_grpc.add_PermissionServiceServicer_to_server(permission_service_handler, server)

    # Register Notification Service
    notification_service_handler = NotificationServiceHandler.as_servicer()
    notification_pb2_grpc.add_NotificationServiceServicer_to_server(notification_service_handler, server)

    # Register Friendship Service
    friendship_service_handler = FriendshipServiceHandler.as_servicer()
    friendship_pb2_grpc.add_FriendshipServiceServicer_to_server(friendship_service_handler, server)
