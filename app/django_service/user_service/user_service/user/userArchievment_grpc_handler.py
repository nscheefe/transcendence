import grpc
from django.utils import timezone
from user_service.protos import userAchievement_pb2_grpc, userAchievement_pb2
from user.models import UserAchievement

class UserAchievementServiceHandler(userAchievement_pb2_grpc.UserAchievementServiceServicer):
    def __init__(self):
        pass

    def GetUserAchievement(self, request, context):
        try:
            user_achievement = UserAchievement.objects.get(user_id=request.user_id, achievement_id=request.achievement_id)
            return userAchievement_pb2_grpc.UserAchievement(
                user_id=user_achievement.user.id,
                achievement_id=user_achievement.achievement_id,
                unlocked_at=google.protobuf.timestamp_pb2.Timestamp(seconds=int(user_achievement.unlocked_at.timestamp()))
            )
        except UserAchievement.DoesNotExist:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details('UserAchievement not found')
            return userAchievement_pb2_grpc.UserAchievement()

    def CreateUserAchievement(self, request, context):
        user_achievement = UserAchievement(
            user_id=request.user_id,
            achievement_id=request.achievement_id,
            # unlocked_at is set to default=timezone.now
        )
        user_achievement.save()
        return userAchievement_pb2_grpc.UserAchievement(
            user_id=user_achievement.user.id,
            achievement_id=user_achievement.achievement_id,
            unlocked_at=google.protobuf.timestamp_pb2.Timestamp(seconds=int(user_achievement.unlocked_at.timestamp()))
        )

    @classmethod
    def as_servicer(cls):
        return cls()


