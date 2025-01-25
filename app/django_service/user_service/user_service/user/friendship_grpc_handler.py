import grpc
from datetime import datetime
from google.protobuf.timestamp_pb2 import Timestamp
from django.db import IntegrityError
from user_service.protos import friendship_pb2_grpc, friendship_pb2
from user.models import Friendship, User


class FriendshipServiceHandler(friendship_pb2_grpc.FriendshipServiceServicer):
    def __init__(self):
        pass

    def CreateFriendship(self, request, context):
        """
        Create a new friendship between two users.
        """
        try:
            user = User.objects.get(id=request.user_id)
            friend = User.objects.get(id=request.friend_id)

            # Create a new friendship or return an existing one
            friendship, created = Friendship.objects.get_or_create(
                user=user,
                friend=friend,
                defaults={
                    'established_at': datetime.utcnow(),
                    'accepted': True
                }
            )

            # If the friendship already exists, return an error
            if not created:
                context.set_code(grpc.StatusCode.ALREADY_EXISTS)
                context.set_details('Friendship already exists')
                return friendship_pb2.Friendship()

            # Convert `established_at` to protobuf Timestamp
            established_at_proto = Timestamp()
            established_at_proto.FromDatetime(friendship.established_at)

            # Return the new friendship as a protobuf message
            return friendship_pb2.Friendship(
                id=friendship.id,
                user_id=friendship.user.id,
                friend_id=friendship.friend.id,
                established_at=established_at_proto,
                accepted=friendship.accepted
            )

        except User.DoesNotExist:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details('One or both users not found')
            return friendship_pb2.Friendship()
        except IntegrityError as e:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details(f'Data integrity error: {str(e)}')
            return friendship_pb2.Friendship()
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f'Failed to create friendship: {str(e)}')
            return friendship_pb2.Friendship()

    def UpdateFriendship(self, request, context):
        """
        Update an existing Friendship by its ID.
        """
        try:
            # Fetch the Friendship by ID
            friendship = Friendship.objects.get(id=request.id)

            # Update fields if they are provided in the request
            if request.HasField("accepted"):
                friendship.accepted = request.accepted
            if request.HasField("established_at"):
                friendship.established_at = request.established_at.ToDatetime()  # Convert protobuf Timestamp to datetime

            # Save the updated Friendship
            friendship.save()

            # Convert the updated `established_at` to protobuf Timestamp
            established_at_proto = Timestamp()
            established_at_proto.FromDatetime(friendship.established_at)

            # Return the updated Friendship
            return friendship_pb2.Friendship(
                id=friendship.id,
                user_id=friendship.user.id,
                friend_id=friendship.friend.id,
                established_at=established_at_proto,
                accepted=friendship.accepted
            )
        except Friendship.DoesNotExist:
            # Handle the case where the Friendship does not exist
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("Friendship with the provided ID does not exist")
            return friendship_pb2.Friendship()
        except Exception as e:
            # Handle unexpected errors
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Failed to update friendship: {str(e)}")
            return friendship_pb2.Friendship()

    def DeleteFriendship(self, request, context):
        """
        Delete a Friendship by its ID.
        """
        try:
            # Fetch the Friendship by ID
            friendship = Friendship.objects.get(id=request.id)

            # Delete the Friendship
            friendship.delete()

            # Return a success response
            return friendship_pb2.DeleteFriendshipResponse(success=True)
        except Friendship.DoesNotExist:
            # Handle the case where the Friendship does not exist
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("Friendship with the provided ID does not exist")
            return friendship_pb2.DeleteFriendshipResponse(success=False)
        except Exception as e:
            # Handle unexpected errors
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Failed to delete friendship: {str(e)}")
            return friendship_pb2.DeleteFriendshipResponse(success=False)

    def GetFriendshipById(self, request, context):
        """
        Retrieve a friendship by its ID.
        """
        try:
            # Fetch the friendship by ID
            friendship = Friendship.objects.get(id=request.id)

            # Convert `established_at` to protobuf Timestamp
            established_at_proto = Timestamp()
            established_at_proto.FromDatetime(friendship.established_at)

            # Return the friendship as a protobuf message
            return friendship_pb2.Friendship(
                id=friendship.id,
                user_id=friendship.user.id,
                friend_id=friendship.friend.id,
                established_at=established_at_proto,
                accepted=friendship.accepted
            )
        except Friendship.DoesNotExist:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details('Friendship not found')
            return friendship_pb2.Friendship()
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f'Failed to retrieve friendship: {str(e)}')
            return friendship_pb2.Friendship()

    def GetFriendshipsByUserId(self, request, context):
        """
        Retrieve all friendships for a given user ID.
        """
        try:
            # Fetch friendships where the user is `user_id`
            friendships = Friendship.objects.filter(user_id=request.user_id)

            friendships_proto = [
                friendship_pb2.Friendship(
                    id=friendship.id,
                    user_id=friendship.user.id,
                    friend_id=friendship.friend.id,
                    established_at=Timestamp(seconds=int(friendship.established_at.timestamp())),
                    accepted=friendship.accepted
                )
                for friendship in friendships
            ]

            # Return the friendships in a response
            return friendship_pb2.FriendshipsResponse(friendships=friendships_proto)

        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f'Failed to retrieve friendships: {str(e)}')
            return friendship_pb2.FriendshipsResponse()

    def GetFriendshipsByFriendId(self, request, context):
        """
        Retrieve all friendships for a given friend ID.
        """
        try:
            # Fetch friendships where the user is `friend_id`
            friendships = Friendship.objects.filter(friend_id=request.friend_id).order_by('-established_at')

            friendships_proto = []
            for friendship in friendships:
                # Convert `established_at` to protobuf Timestamp
                established_at_proto = Timestamp()
                established_at_proto.FromDatetime(friendship.established_at)

                friendships_proto.append(
                    friendship_pb2.Friendship(
                        id=friendship.id,
                        user_id=friendship.user.id,
                        friend_id=friendship.friend.id,
                        established_at=established_at_proto,
                        accepted=friendship.accepted
                    )
                )

            # Return the friendships in a response
            return friendship_pb2.FriendshipsResponse(friendships=friendships_proto)

        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f'Failed to retrieve friendships: {str(e)}')
            return friendship_pb2.FriendshipsResponse()

    @classmethod
    def as_servicer(cls):
        """
        Helper function for registering the servicer with the gRPC server.
        """
        return cls()
