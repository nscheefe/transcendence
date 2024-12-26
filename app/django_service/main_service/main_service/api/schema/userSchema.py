from datetime import datetime

import graphene
import grpc

# Import the protobuf service stubs and request classes for each model
from main_service.protos.user_pb2_grpc import UserServiceStub
from  main_service.protos.user_pb2 import GetUserRequest, CreateUserRequest
from main_service.protos.friendship_pb2_grpc import FriendshipServiceStub
from main_service.protos.friendship_pb2 import GetFriendshipByIdRequest, GetFriendshipsByUserIdRequest
from main_service.protos.notification_pb2_grpc import NotificationServiceStub
from main_service.protos.notification_pb2 import GetNotificationByIdRequest, GetNotificationsByUserIdRequest
from main_service.protos.permission_pb2_grpc import PermissionServiceStub
from main_service.protos.permission_pb2 import GetPermissionByIdRequest
from main_service.protos.profile_pb2_grpc import ProfileServiceStub
from main_service.protos.profile_pb2 import GetProfileByIdRequest, GetProfileByUserIdRequest
from main_service.protos.role_pb2_grpc import RoleServiceStub
from main_service.protos.role_pb2 import GetRoleByIdRequest
from main_service.protos.rolePermission_pb2_grpc import RolePermissionServiceStub
from main_service.protos.rolePermission_pb2 import GetRolePermissionsByRoleIdRequest
from main_service.protos.settings_pb2_grpc import SettingServiceStub
from main_service.protos.settings_pb2 import GetSettingsByUserIdRequest
from main_service.protos.userAchievement_pb2_grpc import UserAchievementServiceStub
from main_service.protos.userAchievement_pb2 import GetUserAchievementsByUserIdRequest

# Define the GraphQL types for each model
class UserType(graphene.ObjectType):
    id = graphene.Int()
    name = graphene.String()
    mail = graphene.String()
    isAuth = graphene.Boolean()
    blocked = graphene.Boolean()
    created_at = graphene.DateTime()
    updated_at = graphene.DateTime()
    role_id = graphene.Int()
    last_login = graphene.DateTime()
    last_login_ip = graphene.String()

class FriendshipType(graphene.ObjectType):
    user_id = graphene.Int()
    friend_id = graphene.Int()
    established_at = graphene.DateTime()
    accepted = graphene.Boolean()

class NotificationType(graphene.ObjectType):
    user_id = graphene.Int()
    message = graphene.String()
    read = graphene.Boolean()
    sent_at = graphene.DateTime()

class PermissionType(graphene.ObjectType):
    name = graphene.String()
    description = graphene.String()

class ProfileType(graphene.ObjectType):
    user_id = graphene.Int()
    avatar_url = graphene.String()
    nickname = graphene.String()
    bio = graphene.String()
    additional_info = graphene.String()

class RoleType(graphene.ObjectType):
    name = graphene.String()
    role_permissions = graphene.List(lambda: RolePermissionType)  # Nested Role Permissions
    def resolve_role_permissions(self, info):
        """Resolver fetching RolePermission details for the Role"""
        channel = grpc.insecure_channel('user_service:50051')
        client = RolePermissionServiceStub(channel)
        request = GetRolePermissionsByRoleIdRequest(role_id=self.id)
        response = client.GetRolePermissionsByRoleId(request)

        return [
            RolePermissionType(
                role_id=record.role_id,
                permission_id=record.permission_id
            )
            for record in response.role_permissions
        ]


class RolePermissionType(graphene.ObjectType):
    role_id = graphene.Int()
    permission_id = graphene.Int()
    permission = graphene.Field(lambda: PermissionType)  # Nested PermissionType
    def resolve_permission(self, info):
        """Resolver for nested Permission inside RolePermissionType"""
        channel = grpc.insecure_channel("user_service:50051")
        client = PermissionServiceStub(channel)
        request = GetPermissionByIdRequest(id=self.permission_id)
        response = client.GetPermissionById(request)

        return PermissionType(
            name=response.name,
            description=response.description
        )


class SettingType(graphene.ObjectType):
    user_id = graphene.Int()
    name = graphene.String()
    data = graphene.String()

class UserAchievementType(graphene.ObjectType):
    user_id = graphene.Int()
    achievement_id = graphene.Int()
    unlocked_at = graphene.DateTime()

class UserType(graphene.ObjectType):
        id = graphene.Int()
        name = graphene.String()
        mail = graphene.String()
        isAuth = graphene.Boolean()
        blocked = graphene.Boolean()
        created_at = graphene.DateTime()
        updated_at = graphene.DateTime()
        role_id = graphene.Int()
        last_login = graphene.DateTime()
        last_login_ip = graphene.String()

        # Nested types
        profile = graphene.Field(lambda: ProfileType)  # User's Profile
        friendships = graphene.List(lambda: FriendshipType)  # User's Friendships
        notifications = graphene.List(lambda: NotificationType)  # User's Notifications
        settings = graphene.List(lambda: SettingType)  # User's Settings
        achievements = graphene.List(lambda: UserAchievementType)  # User's Achievements
        role = graphene.Field(lambda: RoleType)  # User's Role (with permissions)

        ### Resolvers ###
        def resolve_profile(self, info):
            """Fetch the user's profile."""
            try:
                channel = grpc.insecure_channel("user_service:50051")
                client = ProfileServiceStub(channel)
                request = GetProfileByUserIdRequest(user_id=self.id)
                response = client.GetProfileByUserId(request)

                return ProfileType(
                    user_id=response.user_id,
                    avatar_url=response.avatar_url,
                    nickname=response.nickname,
                    bio=response.bio,
                    additional_info=response.additional_info,
                )

            except grpc.RpcError as e:
                if e.code() == grpc.StatusCode.NOT_FOUND:
                    # Return None or raise a custom GraphQL error
                    return None  # Or handle in a more user-specific way
                else:
                    # Raise other unexpected errors as-is
                    raise e

        def resolve_friendships(self, info):
            """Fetch friendships for the user."""
            channel = grpc.insecure_channel("user_service:50051")
            client = FriendshipServiceStub(channel)
            request = GetFriendshipsByUserIdRequest(user_id=self.id)
            response = client.GetFriendshipsByUserId(request)

            return [
                FriendshipType(
                    user_id=record.user_id,
                    friend_id=record.friend_id,
                    established_at=datetime.fromtimestamp(record.established_at.seconds),
                    accepted=record.accepted
                )
                for record in response.friendships
            ]

        def resolve_notifications(self, info):
            """Fetch notifications for the user."""
            channel = grpc.insecure_channel("user_service:50051")
            client = NotificationServiceStub(channel)
            request = GetNotificationsByUserIdRequest(user_id=self.id)
            response = client.GetNotificationsByUserId(request)

            return [
                NotificationType(
                    user_id=record.user_id,
                    message=record.message,
                    read=record.read,
                    sent_at=datetime.fromtimestamp(record.sent_at.seconds),
                )
                for record in response.notifications
            ]

        def resolve_settings(self, info):
            """Fetch settings for the user."""
            channel = grpc.insecure_channel("user_service:50051")
            client = SettingServiceStub(channel)
            request = GetSettingsByUserIdRequest(user_id=self.id)
            response = client.GetSettingsByUserId(request)

            return [
                SettingType(
                    user_id=record.user_id,
                    name=record.name,
                    data=record.data
                )
                for record in response.settings
            ]

        def resolve_achievements(self, info):
            """Fetch achievements for the user."""
            channel = grpc.insecure_channel("user_service:50051")
            client = UserAchievementServiceStub(channel)

            # gRPC request
            request = GetUserAchievementsByUserIdRequest(user_id=self.id)
            response = client.GetUserAchievementsByUserId(request)

            # Check if achievements exist, otherwise return an empty list
            if not response.userAchievements:
                return []  # Explicitly return an empty list if no achievements exist

            # Map achievements to the required type
            return [
                UserAchievementType(
                    user_id=record.user_id,
                    achievement_id=record.achievement_id,
                    unlocked_at=datetime.fromtimestamp(record.unlocked_at.seconds)
                )
                for record in response.userAchievements
            ]

        def resolve_role(self, info):
            """Fetch the user's role."""
            channel = grpc.insecure_channel("user_service:50051")
            client = RoleServiceStub(channel)
            request = GetRoleByIdRequest(id=self.role_id)
            response = client.GetRoleById(request)

            return RoleType(
                name=response.name,
            )


# Define the GraphQL query type
class Query(graphene.ObjectType):
    user = graphene.Field(UserType)


    def resolve_user(self, info):
        user_id = info.context.user_id
        if not user_id:
            raise Exception("Authentication required: user_id is missing")

        channel = grpc.insecure_channel('user_service:50051')
        client = UserServiceStub(channel)
        request = GetUserRequest(id=user_id)
        response = client.GetUser(request)
        return UserType(
            id=response.id,
            name=response.name,
            mail=response.mail,
            isAuth=response.isAuth,
            blocked=response.blocked,
            created_at=datetime.fromtimestamp(response.created_at.seconds),
            updated_at=datetime.fromtimestamp(response.updated_at.seconds),
            role_id=response.role_id,
            last_login=datetime.fromtimestamp(response.last_login.seconds),
            last_login_ip=response.last_login_ip
        )

    # Similar resolver functions need to be defined for other types like FriendshipType, NotificationType, etc.
# Define input classes for each type
class UserInput(graphene.InputObjectType):
    name = graphene.String()
    mail = graphene.String()
    isAuth = graphene.Boolean()
    blocked = graphene.Boolean()
    created_at = graphene.DateTime()
    updated_at = graphene.DateTime()
    role_id = graphene.Int()
    last_login = graphene.DateTime()
    last_login_ip = graphene.String()

class FriendshipInput(graphene.InputObjectType):
    user_id = graphene.Int()
    friend_id = graphene.Int()
    established_at = graphene.DateTime()
    accepted = graphene.Boolean()

class NotificationInput(graphene.InputObjectType):
    user_id = graphene.Int()
    message = graphene.String()
    read = graphene.Boolean()
    sent_at = graphene.DateTime()

class PermissionInput(graphene.InputObjectType):
    name = graphene.String()
    description = graphene.String()

class ProfileInput(graphene.InputObjectType):
    user_id = graphene.Int()
    avatar_url = graphene.String()
    nickname = graphene.String()
    bio = graphene.String()
    additional_info = graphene.String()

class RoleInput(graphene.InputObjectType):
    name = graphene.String()

class RolePermissionInput(graphene.InputObjectType):
    role_id = graphene.Int()
    permission_id = graphene.Int()

class SettingInput(graphene.InputObjectType):
    user_id = graphene.Int()
    name = graphene.String()
    data = graphene.String()

class UserAchievementInput(graphene.InputObjectType):
    user_id = graphene.Int()
    achievement_id = graphene.Int()
    unlocked_at = graphene.DateTime()



# Add create functions and mutations for each input class

# Mutation for creating a user
class CreateUser(graphene.Mutation):
    class Arguments:
        input = UserInput(required=True)

    user = graphene.Field(UserType)

    @staticmethod
    def mutate(root, info, input=None):

        grpc_host = "user_service"
        grpc_port = 50051
        service_endpoint = f"{grpc_host}:{grpc_port}"

        try:
            with grpc.insecure_channel(service_endpoint) as channel:
                stub = UserServiceStub(channel)
                grpc_request = CreateUserRequest(
                    name=input.name,
                    mail=input.mail,
                    isAuth=input.isAuth,
                    blocked=input.blocked,
                    role_id=input.role_id,
                    last_login_ip=input.last_login_ip or ""
                )
                grpc_response = stub.CreateUser(grpc_request)
                user_data = UserType(
                    id=grpc_response.id,
                    name=grpc_response.name,
                    mail=grpc_response.mail,
                    isAuth=grpc_response.isAuth,
                    blocked=grpc_response.blocked,
                    role_id=grpc_response.role_id,
                    last_login_ip=grpc_response.last_login_ip,
                    created_at=datetime.fromtimestamp(grpc_response.created_at.seconds)
                    if grpc_response.HasField("created_at") else None,
                    updated_at=datetime.fromtimestamp(grpc_response.updated_at.seconds)
                    if grpc_response.HasField("updated_at") else None,
                )
                return CreateUser(user=user_data)
        except grpc.RpcError as e:
            raise Exception(f"gRPC error: {e.details()} (Code: {e.code()})")
        except Exception as ex:
            raise Exception(f"Error occurred while creating user: {str(ex)}")

# Mutation for creating a friendship
class CreateFriendship(graphene.Mutation):
    class Arguments:
        input = FriendshipInput(required=True)

    friendship = graphene.Field(FriendshipType)

    @staticmethod
    def mutate(root, info, input=None):
        # Implement the logic to create a friendship
        return CreateFriendship(friendship=FriendshipType(user_id=1, friend_id=2, **input))

# Mutation for creating a notification
class CreateNotification(graphene.Mutation):
    class Arguments:
        input = NotificationInput(required=True)

    notification = graphene.Field(NotificationType)

    @staticmethod
    def mutate(root, info, input=None):
        # Implement the logic to create a notification
        return CreateNotification(notification=NotificationType(user_id=1, **input))

# Mutation for creating a permission
class CreatePermission(graphene.Mutation):
    class Arguments:
        input = PermissionInput(required=True)

    permission = graphene.Field(PermissionType)

    @staticmethod
    def mutate(root, info, input=None):
        # Implement the logic to create a permission
        return CreatePermission(permission=PermissionType(name=input.name, description=input.description))

# Mutation for creating a profile
class CreateProfile(graphene.Mutation):
    class Arguments:
        input = ProfileInput(required=True)

    profile = graphene.Field(ProfileType)

    @staticmethod
    def mutate(root, info, input=None):
        # Implement the logic to create a profile
        return CreateProfile(profile=ProfileType(user_id=1, **input))

# Mutation for creating a role
class CreateRole(graphene.Mutation):
    class Arguments:
        input = RoleInput(required=True)

    role = graphene.Field(RoleType)

    @staticmethod
    def mutate(root, info, input=None):
        # Implement the logic to create a role
        return CreateRole(role=RoleType(name=input.name))

# Mutation for creating a role permission
class CreateRolePermission(graphene.Mutation):
    class Arguments:
        input = RolePermissionInput(required=True)

    role_permission = graphene.Field(RolePermissionType)

    @staticmethod
    def mutate(root, info, input=None):
        # Implement the logic to create a role permission
        return CreateRolePermission(role_permission=RolePermissionType(role_id=input.role_id, permission_id=input.permission_id))

# Mutation for creating a setting
class CreateSetting(graphene.Mutation):
    class Arguments:
        input = SettingInput(required=True)

    setting = graphene.Field(SettingType)

    @staticmethod
    def mutate(root, info, input=None):
        # Implement the logic to create a setting
        # Assuming input already contains 'user_id', pass **input directly
        return CreateSetting(setting=SettingType(**input))

# Mutation for creating a user achievement
class CreateUserAchievement(graphene.Mutation):
    class Arguments:
        input = UserAchievementInput(required=True)

    user_achievement = graphene.Field(UserAchievementType)

    @staticmethod
    def mutate(root, info, input=None):
        # Implement the logic to create a user achievement
        return CreateUserAchievement(user_achievement=UserAchievementType(user_id=1, achievement_id=2, **input))

# Add all mutations to the Mutation class
class Mutation(graphene.ObjectType):
    create_user = CreateUser.Field()
    create_friendship = CreateFriendship.Field()
    create_notification = CreateNotification.Field()
    create_permission = CreatePermission.Field()
    create_profile = CreateProfile.Field()
    create_role = CreateRole.Field()
    create_role_permission = CreateRolePermission.Field()
    create_setting = CreateSetting.Field()
    create_user_achievement = CreateUserAchievement.Field()

# Update the schema to include mutations
schema = graphene.Schema(query=Query, mutation=Mutation)
