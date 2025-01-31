# app/django_service/main_service/main_service/api/schema/combinedSchema.py
from ariadne import make_executable_schema, ScalarType
from datetime import datetime

from main_service.api.schema.objectTypes import query, mutation, subscription

#resolver
from main_service.api.schema.userSchema import resolver as user_resolver
from main_service.api.schema.chatSchema import resolver as chat_resolver
from main_service.api.schema.statSchema import resolvers as stat_resolver
from main_service.api.schema.gameSchema import resolver as game_resolver
from main_service.api.schema.notificationSchema import resolver as notification_resolver

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
        id: Int!
        userId: Int!
        friendId: Int!
        establishedAt: DateTime
        accepted: Boolean!
        blocked: Boolean!
    }

    type Notification {
        id: Int!
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
        stat(id: Int!): Stat
        statsByUser(userId: Int!): [UserStat!]!
        calculateUserStats(userId: Int!): CalculateStatsResponse!
           game(game_id: Int!): Game
        ongoing_games: [Game]
        game_event(game_event_id: Int!): GameEvent
        hello: String
        tournament(tournament_id: Int!): Tournament
        tournaments: [Tournament]
                tournament_users(tournament_id: Int!): [TournamentUser]
        tournament_games(tournament_id: Int!): [TournamentGame]
        friendships: [Friendship!]
            StatList: [StatsWithProfile!]!

    }
    type onlineStatus {
        userId: Int!
        status: Boolean!
    }

    type Subscription {
        ping_test: Ping!
        chatRoomsForUser: ChatRoom!
        chat_room_message(chat_room_id: Int!): ChatRoomMessage!
        notificationsForUser: Notification!
        onlineStatus(user_id: Int!): onlineStatus
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

   input FriendshipCreateInput {
       friendId: Int!
   }

    input FriendshipBlockInput {
        id: Int
        friendId: Int!
        blocked: Boolean!
    }

   input FriendshipUpdateInput {
       id: Int!
       accepted: Boolean!
       blocked: Boolean
   }

   input FriendshipDeleteInput {
       id: Int!
   }

   input FriendshipInput {
       create: FriendshipCreateInput
       block: FriendshipBlockInput
       update: FriendshipUpdateInput
       delete: FriendshipDeleteInput
   }

    input NotificationCreateInput {
        message: String!
        read: Boolean!
        sentAt: DateTime
    }

    input NotificationUpdateInput {
        id: Int!
        message: String!
        read: Boolean!
    }

    input NotificationDeleteInput {
        id: Int!
    }

    input NotificationInput {
        create: NotificationCreateInput
        update: NotificationUpdateInput
        delete: NotificationDeleteInput
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
        avatarUrl: String
        nickname: String
        bio: String
        additionalInfo: String
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
    type StatsWithProfile {
        profile: Profile!
        stats: ProfileStats!
    }

    type ProfileStats {
        totalGames: Int!
        totalWins: Int!
        totalLosses: Int!
        winRatio: Float!
    }
    type Mutation {
        createUser(input: UserInput!): User
        manageProfile(avatarUrl: String, nickname: String, bio: String, additionalInfo: String): ProfileMutationResponse
        manageFriendship(friendshipData: FriendshipInput!): FriendshipMutationResponse
        manageNotification(notificationData: NotificationInput!): NotificationMutationResponse
        manageSetting(settingData: SettingInput!): SettingMutationResponse
        manageUserAchievement(achievementData: UserAchievementInput!): UserAchievementMutationResponse
        createStat(input: CreateStatInput!): CreateStatPayload!
        create_game: Game
        create_game_event(game_id: Int!, event_type: String!, event_data: String!): GameEvent
        start_game(game_id: Int!): StartGameResponse
        create_tournament(name: String!, tournament_size: Int!): Tournament
        create_tournament_user(tournament_id: Int!, user_id: Int!): TournamentUserResponse
        update_tournament_user(
           tournament_user_id: Int!,
           state: String,
           play_order: Int,
           games_played: Int
       ): TournamentUserResponse
        create_tournament_game(tournament_id: Int!, user_id: Int!, opponent_id: Int!): TournamentGame
        create_friend_game(player_a: Int!, player_b: Int!): Game!
        update_game_state(game_id: Int!, state: String!): Game!
        create_chat_room(name: String!, game_id: Int): ChatRoom
        add_user_to_chat_room(chat_room_id: Int!, user_id: Int!): ChatRoomUser
        startChatWithUser(user_id: Int!, game_id: Int): ChatRoom
        create_chat_room_message(chat_room_id: Int!, content: String!): ChatRoomMessage
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
    type Stat {
        id: Int!
        gameId: Int!
        winnerId: Int!
        loserId: Int!
        createdAt: String!
    }

    type UserStat {
        id: Int!
        userId: Int!
        stat: Stat!
        didWin: Boolean!
    }

    type CalculateStatsResponse {
        totalGames: Int!
        totalWins: Int!
        totalLosses: Int!
    }

    input CreateStatInput {
        gameId: Int!
        winnerId: Int!
        loserId: Int!
    }

    type CreateStatPayload {
        success: Boolean!
        stat: Stat
        message: String
    }

    type Tournament {
        id: Int
        name: String
        users: [TournamentUser] # Extend tournament type
        is_active: Boolean
        started: Boolean
        chat_room_id: Int
        tournament_size: Int
        start_time: String
        created_at: String
        updated_at: String
    }

type TournamentUser {
    id: Int
    name: String
    user_id: Int
    tournament_id: Int
    play_order: Int  
    games_played: Int 
    state: String
    created_at: String
    updated_at: String
}
    type TournamentGame {
        id: Int
        game_id: Int
        user_id: Int
        tournament_id: Int
        created_at: String
        updated_at: String
    }

    type Game {
        id: Int
        state: String
        points_player_a: Int
        points_player_b: Int
        player_a_id: Int
        player_b_id: Int
        finished: Boolean
        created_at: String
        updated_at: String
    }

    type GameEvent {
        id: Int
        game_id: Int
        event_type: String
        event_data: String
        timestamp: String
    }

    type TournamentUserResponse {
        success: Boolean
        user: TournamentUser
    }


    type StartGameResponse {
        success: Boolean
        websocket_url: String
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
schema = make_executable_schema(type_defs, user_resolver, chat_resolver, stat_resolver, game_resolver, notification_resolver)
