import grpc
from google.protobuf.timestamp_pb2 import Timestamp
from django.db import IntegrityError
from user_service.protos import userAchievement_pb2_grpc, userAchievement_pb2
from user.models import UserAchievement


class UserAchievementServiceHandler(userAchievement_pb2_grpc.UserAchievementServiceServicer):
    def __init__(self):
        pass

    def GetUserAchievementById(self, request, context):
        """
        Retrieve a UserAchievement by its ID.
        """
        try:
            # Retrieve the UserAchievement by ID
            user_achievement = UserAchievement.objects.get(id=request.id)

            # Convert the unlocked_at field to a protobuf Timestamp
            unlocked_at_proto = Timestamp()
            unlocked_at_proto.FromDatetime(user_achievement.unlocked_at)

            # Return the achievement as a protobuf message
            return userAchievement_pb2.UserAchievement(
                id=user_achievement.id,
                user_id=user_achievement.user.id,
                achievement_id=user_achievement.achievement.id,
                unlocked_at=unlocked_at_proto
            )
        except UserAchievement.DoesNotExist:
            # UserAchievement not found
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details('UserAchievement not found')
            return userAchievement_pb2.UserAchievement()
        except Exception as e:
            # Handle unexpected errors
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f'Failed to retrieve UserAchievement: {str(e)}')
            return userAchievement_pb2.UserAchievement()

    def GetUserAchievementsByUserId(self, request, context):
        """
        Retrieve all UserAchievements for a specific user (by user_id).
        """
        try:
            # Query the database for user achievements
            user_achievements = UserAchievement.objects.filter(user_id=request.user_id).order_by('-unlocked_at')

            # Initialize a list to store the response objects
            user_achievements_proto = []

            # Process each user achievement object
            for user_achievement in user_achievements:
                try:
                    # Skip records with missing data
                    if not user_achievement.user or not user_achievement.achievement or not user_achievement.unlocked_at:
                        continue

                    # Convert the unlocked_at field to a protobuf Timestamp
                    unlocked_at_proto = Timestamp()
                    unlocked_at_proto.FromDatetime(user_achievement.unlocked_at)

                    # Append the serialized user achievement to the list
                    user_achievements_proto.append(
                        userAchievement_pb2.UserAchievement(
                            id=user_achievement.id,
                            user_id=user_achievement.user.id,
                            achievement_id=user_achievement.achievement.id,
                            unlocked_at=unlocked_at_proto
                        )
                    )

                except Exception as e:
                    # Log serialization issues and skip problematic records
                    print(f"Serialization error for achievement ID {getattr(user_achievement, 'id', None)}: {e}")
                    continue

            # Ensure the response is always an empty list if there are no achievements
            if not user_achievements_proto:
                user_achievements_proto = []

            # Return the list of user achievements
            return userAchievement_pb2.UserAchievementsResponse(
                userAchievements=user_achievements_proto
            )

        except Exception as e:
            # Handle unexpected errors gracefully
            print(f"Unexpected error in GetUserAchievementsByUserId: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Failed to retrieve UserAchievements: {str(e)}")

            # Return an empty response in case of failure
            return userAchievement_pb2.UserAchievementsResponse(userAchievements=[])

    def UpdateUserAchievement(self, request, context):
        """
        Update an existing UserAchievement by its ID.
        """
        try:
            # Fetch the UserAchievement by its ID
            user_achievement = UserAchievement.objects.get(id=request.id)

            # Update the fields if they are provided in the request
            if request.HasField("achievement_id"):
                user_achievement.achievement_id = request.achievement_id
            if request.HasField("unlocked_at"):
                user_achievement.unlocked_at = request.unlocked_at.ToDatetime()  # Convert protobuf Timestamp to Python datetime

            # Save the changes
            user_achievement.save()

            # Convert the updated unlocked_at to a protobuf Timestamp
            unlocked_at_proto = Timestamp()
            unlocked_at_proto.FromDatetime(user_achievement.unlocked_at)

            # Return the updated UserAchievement as a protobuf message
            return userAchievement_pb2.UserAchievement(
                id=user_achievement.id,
                user_id=user_achievement.user.id,
                achievement_id=user_achievement.achievement.id,
                unlocked_at=unlocked_at_proto
            )
        except UserAchievement.DoesNotExist:
            # Handle the case where the UserAchievement does not exist
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("UserAchievement with the given ID does not exist")
            return userAchievement_pb2.UserAchievement()
        except IntegrityError as e:
            # Handle data integrity issues (e.g., conflicting fields)
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details(f"Data integrity error: {str(e)}")
            return userAchievement_pb2.UserAchievement()
        except Exception as e:
            # Handle unexpected errors
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Failed to update UserAchievement: {str(e)}")
            return userAchievement_pb2.UserAchievement()

    def CreateUserAchievement(self, request, context):
        """
        Create a new UserAchievement.
        """
        try:
            # Create a new UserAchievement instance
            user_achievement = UserAchievement(
                user_id=request.user_id,
                achievement_id=request.achievement_id,
                unlocked_at=request.unlocked_at.ToDatetime()  # Convert protobuf Timestamp to Python datetime
            )
            user_achievement.save()

            # Convert the unlocked_at field to a protobuf Timestamp
            unlocked_at_proto = Timestamp()
            unlocked_at_proto.FromDatetime(user_achievement.unlocked_at)

            # Return the newly created achievement as a protobuf message
            return userAchievement_pb2.UserAchievement(
                id=user_achievement.id,
                user_id=user_achievement.user.id,
                achievement_id=user_achievement.achievement.id,
                unlocked_at=unlocked_at_proto
            )
        except IntegrityError as e:
            # Handle data integrity issues (e.g., duplicate entries)
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details(f'Data integrity error: {str(e)}')
            return userAchievement_pb2.UserAchievement()
        except Exception as e:
            # Handle unexpected errors
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f'Failed to create UserAchievement: {str(e)}')
            return userAchievement_pb2.UserAchievement()

    @classmethod
    def as_servicer(cls):
        """
        Helper function for registering the servicer with the gRPC server.
        """
        return cls()
