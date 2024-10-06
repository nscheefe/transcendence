import grpc
from django.db import IntegrityError
from user_service.protos import friendship_pb2_grpc, friendship_pb2
from user.models import Friendship, User

class FriendshipServiceHandler(friendship_pb2_grpc.FriendshipServiceServicer):
    def __init__(self):
        pass

    def CreateFriendship(self, request, context):
        try:
            user = User.objects.get(id=request.user_id)
            friend = User.objects.get(id=request.friend_id)
            friendship, created = Friendship.objects.get_or_create(
                user=user,
                friend=friend,
                defaults={'accepted': False}  # Default value for new friendships
            )
            if not created:
                context.set_code(grpc.StatusCode.ALREADY_EXISTS)
                context.set_details('Friendship already exists')
                return friendship_pb2.FriendshipResponse(success=False)
            return friendship_pb2.FriendshipResponse(
                id=friendship.id,
                user_id=friendship.user.id,
                friend_id=friendship.friend.id,
                established_at=friendship.established_at.isoformat(),
                accepted=friendship.accepted,
                success=True
            )
        except User.DoesNotExist:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details('User not found')
            return friendship_pb2.FriendshipResponse(success=False)

    def UpdateFriendshipStatus(self, request, context):
        try:
            friendship = Friendship.objects.get(id=request.id)
            friendship.accepted = request.accepted
            friendship.save()
            return friendship_pb2.FriendshipResponse(
                id=friendship.id,
                user_id=friendship.user.id,
                friend_id=friendship.friend.id,
                established_at=friendship.established_at.isoformat(),
                accepted=friendship.accepted,
                success=True
            )
        except Friendship.DoesNotExist:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details('Friendship not found')
            return friendship_pb2.FriendshipResponse(success=False)

    def ListFriendshipsForUser(self, request, context):
        friendships = Friendship.objects.filter(user_id=request.user_id).order_by('-established_at')
        for friendship in friendships:
            yield friendship_pb2.FriendshipResponse(
                id=friendship.id,
                user_id=friendship.user.id,
                friend_id=friendship.friend.id,
                established_at=friendship.established_at.isoformat(),
                accepted=friendship.accepted,
                success=True
            )

    @classmethod
    def as_servicer(cls):
        return cls()

