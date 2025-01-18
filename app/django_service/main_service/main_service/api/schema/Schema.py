# app/django_service/main_service/main_service/api/schema/combinedSchema.py
from ariadne import make_executable_schema, ScalarType
from datetime import datetime

from main_service.api.schema.objectTypes import query, mutation, subscription

#resolver
from main_service.api.schema.userSchema import resolver as user_resolver
from main_service.api.schema.chatSchema import resolver as chat_resolver

# Define the DateTime scalar type
datetime_scalar = ScalarType("DateTime")

@datetime_scalar.serializer
def serialize_datetime(value):
    return value.isoformat()

@datetime_scalar.value_parser
def parse_datetime_value(value):
    return datetime.fromisoformat(value)

@datetime_scalar.literal_parser
def parse_datetime_literal(ast):
    return datetime.fromisoformat(ast.value)

type_defs = """
    scalar DateTime

    type User {
        id: Int!
        name: String!
        mail: String!
        blocked: Boolean!
        createdAt: DateTime
        updatedAt: DateTime
        roleId: Int!
        lastLogin: DateTime
        lastLoginIp: String
        profile: Profile
        friendships: [Friendship]
        notifications: [Notification]
        settings: [Setting]
        achievements: [UserAchievement]
        role: Role
    }

    type Friendship {
        userId: Int!
        friendId: Int!
        establishedAt: DateTime
        accepted: Boolean!
    }

    type Notification {
        userId: Int!
        message: String!
        read: Boolean!
        sentAt: DateTime
    }

    type Permission {
        name: String!
        description: String!
    }

    type Profile {
        id: Int!
        userId: Int!
        avatarUrl: String!
        nickname: String!
        bio: String!
        additionalInfo: String!
    }

    type GetAllProfilesResponse {
        profiles: [Profile]
        totalCount: Int!
    }

    type Query {
        user: User
        profile(userId: Int!): Profile
        getAllProfiles(limit: Int!, offset: Int!): GetAllProfilesResponse
        chat_rooms_for_user(user_id: Int!): [ChatRoom!]
    }

    type Subscription {
        ping_test: Ping!
        chat_room_message(chat_room_id: Int!): ChatRoomMessage!
    }

    type Role {
        name: String!
        rolePermissions: [RolePermission]
    }

    type RolePermission {
        roleId: Int!
        permissionId: Int!
        permission: Permission
    }

    type Setting {
        userId: Int!
        name: String!
        data: String!
    }

    type UserAchievement {
        userId: Int!
        achievementId: Int!
        unlockedAt: DateTime
    }

    type ChatRoomMessage {
        id: Int!
        content: String!
        sender_id: Int!
        chat_room_id: Int!
        timestamp: String!
    }

    type ChatRoomUser {
        id: Int!
        user_id: Int!
        chat_room_id: Int!
        joined_at: DateTime!
    }

    type ChatRoom {
        id: Int!
        game_id: Int!
        name: String!
        created_at: DateTime!
        users: [ChatRoomUser!]
        messages: [ChatRoomMessage!]
    }

    input FriendshipInput {
        friendId: Int!
        establishedAt: DateTime
        accepted: Boolean!
    }

    input NotificationInput {
        message: String!
        read: Boolean!
        sentAt: DateTime
    }

    input SettingInput {
        name: String!
        data: String!
    }

    input UserAchievementInput {
        achievementId: Int!
        unlockedAt: DateTime
    }

    input ProfileInput {
        avatarUrl: String!
        nickname: String!
        bio: String!
        additionalInfo: String!
    }

    input UserInput {
        id: Int
        name: String!
        mail: String!
        blocked: Boolean
        createdAt: DateTime
        updatedAt: DateTime
        roleId: Int
        lastLogin: DateTime
        lastLoginIp: String
    }

    type Mutation {
        createUser(input: UserInput!): User
        manageProfile(profileData: ProfileInput!): ProfileMutationResponse
        manageFriendship(friendshipData: FriendshipInput!): FriendshipMutationResponse
        manageNotification(notificationData: NotificationInput!): NotificationMutationResponse
        manageSetting(settingData: SettingInput!): SettingMutationResponse
        manageUserAchievement(achievementData: UserAchievementInput!): UserAchievementMutationResponse
    }

    type ProfileMutationResponse {
        success: Boolean!
        message: String!
    }

    type FriendshipMutationResponse {
        success: Boolean!
        message: String!
    }

    type NotificationMutationResponse {
        success: Boolean!
        message: String!
    }

    type SettingMutationResponse {
        success: Boolean!
        message: String!
    }

    type UserAchievementMutationResponse {
        success: Boolean!
        message: String!
    }

    type Ping {
        response: String!
    }
"""

@datetime_scalar.serializer
def serialize_datetime(value):
    return value.isoformat()

@datetime_scalar.value_parser
def parse_datetime_value(value):
    return datetime.fromisoformat(value)

@datetime_scalar.literal_parser
def parse_datetime_literal(ast):
    return datetime.fromisoformat(ast.value)

# Create the executable schema
schema = make_executable_schema(type_defs, user_resolver, chat_resolver)
