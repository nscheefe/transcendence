import graphene
import grpc

# Import the protobuf service stubs and request classes for each model
from main_service.protos.user_pb2_grpc import UserServiceStub
from  main_service.protos.user_pb2 import GetUserRequest
from main_service.protos.friendship_pb2_grpc import FriendshipServiceStub
from main_service.protos.friendship_pb2 import GetFriendshipByIdRequest
from main_service.protos.notification_pb2_grpc import NotificationServiceStub
from main_service.protos.notification_pb2 import GetNotificationByIdRequest
from main_service.protos.permission_pb2_grpc import PermissionServiceStub
from main_service.protos.permission_pb2 import GetPermissionByIdRequest
from main_service.protos.profile_pb2_grpc import ProfileServiceStub
from main_service.protos.profile_pb2 import GetProfileByIdRequest
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

class RolePermissionType(graphene.ObjectType):
    role_id = graphene.Int()
    permission_id = graphene.Int()

class SettingType(graphene.ObjectType):
    user_id = graphene.Int()
    name = graphene.String()
    data = graphene.String()

class UserAchievementType(graphene.ObjectType):
    user_id = graphene.Int()
    achievement_id = graphene.Int()
    unlocked_at = graphene.DateTime()

# Define the GraphQL query type
class Query(graphene.ObjectType):
    user = graphene.Field(UserType, id=graphene.Int(required=True))
    friendship = graphene.Field(FriendshipType, id=graphene.Int(required=True))
    notification = graphene.Field(NotificationType, id=graphene.Int(required=True))
    permission = graphene.Field(PermissionType, id=graphene.Int(required=True))
    profile = graphene.Field(ProfileType, id=graphene.Int(required=True))
    role = graphene.Field(RoleType, id=graphene.Int(required=True))
    role_permission = graphene.Field(RolePermissionType, id=graphene.Int(required=True))
    setting = graphene.Field(SettingType, id=graphene.Int(required=True))
    user_achievement = graphene.Field(UserAchievementType, id=graphene.Int(required=True))

    def resolve_user(self, info, id):
        channel = grpc.insecure_channel('user_service:50051')
        client = UserServiceStub(channel)
        request = GetUserRequest(id=id)
        response = client.GetUser(request)
        return UserType(
            id=response.id,
            name=response.name,
            mail=response.mail,
            isAuth=response.isAuth,
            blocked=response.blocked,
            created_at=response.created_at,
            updated_at=response.updated_at,
            role_id=response.role_id,
            last_login=response.last_login,
            last_login_ip=response.last_login_ip
        )

    def resolve_friendship(self, info, id):
        channel = grpc.insecure_channel('user_service:50051')
        client = FriendshipServiceStub(channel)
        request = GetFriendshipByIdRequest(id=id)
        response = client.GetFriendshipById(request)
        return FriendshipType(id=response.id, user_id=response.user_id, friend_id=response.friend_id, status=response.status)

    def resolve_notification(self, info, id):
        channel = grpc.insecure_channel('user_service:50051')
        client = NotificationServiceStub(channel)
        request = GetNotificationByIdRequest(id=id)
        response = client.GetNotificationById(request)
        return NotificationType(id=response.id, user_id=response.user_id, message=response.message, seen=response.seen)

    def resolve_permission(self, info, id):
        channel = grpc.insecure_channel('user_service:50051')
        client = PermissionServiceStub(channel)
        request = GetPermissionByIdRequest(id=id)
        response = client.GetPermissionById(request)
        return PermissionType(id=response.id, name=response.name, description=response.description)

    def resolve_profile(self, info, id):
        channel = grpc.insecure_channel('user_service:50051')
        client = ProfileServiceStub(channel)
        request = GetProfileByIdRequest(id=id)
        response = client.GetProfileById(request)
        return ProfileType(id=response.id, user_id=response.user_id, bio=response.bio, image=response.image)

    def resolve_role(self, info, id):
        channel = grpc.insecure_channel('user_service:50051')
        client = RoleServiceStub(channel)
        request = GetRoleByIdRequest(id=id)
        response = client.GetRoleById(request)
        return RoleType(id=response.id, name=response.name)

    def resolve_role_permission(self, info, id):
        channel = grpc.insecure_channel('user_service:50051')
        client = RolePermissionServiceStub(channel)
        request = GetRolePermissionsByRoleIdRequest(id=id)
        response = client.GetRolePermissionsByRoleId(request)
        return RolePermissionType(id=response.id, role_id=response.role_id, permission_id=response.permission_id)

    def resolve_setting(self, info, id):
        channel = grpc.insecure_channel('user_service:50051')
        client = SettingServiceStub(channel)
        request = GetSettingsByUserIdRequest(id=id)
        response = client.GetSettingsByUserId(request)
        return SettingType(id=response.id, user_id=response.user_id, key=response.key, value=response.value)

    def resolve_user_achievement(self, info, id):
        channel = grpc.insecure_channel('user_service:50051')
        client = UserAchievementServiceStub(channel)
        request = GetUserAchievementsByUserIdRequest(id=id)
        response = client.GetUserAchievementsByUserId(request)
        return UserAchievementType(id=response.id, user_id=response.user_id, achievement_id=response.achievement_id, date_achieved=response.date_achieved)

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
        # Here you would implement the logic to create a user in your database
        # For demonstration, returning a mock object
        return CreateUser(user=UserType(id=1, **input))

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
