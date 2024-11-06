import grpc
from django.db import IntegrityError
from user_service.protos import notification_pb2_grpc, notification_pb2
from user.models import Notification, User

class NotificationServiceHandler(notification_pb2_grpc.NotificationServiceServicer):
    def __init__(self):
        pass

    def GetNotification(self, request, context):
        try:
            notification = Notification.objects.get(id=request.id)
            return notification_pb2.Notification(
                id=notification.id,
                user_id=notification.user.id,
                message=notification.message,
                read=notification.read,
                sent_at=notification.sent_at.isoformat()
            )
        except Notification.DoesNotExist:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details('Notification not found')
            return notification_pb2.Notification()

    def CreateNotification(self, request, context):
        try:
            user = User.objects.get(id=request.user_id)
            notification = Notification(user=user, message=request.message, read=request.read)
            notification.save()
            return notification_pb2.Notification(
                id=notification.id,
                user_id=notification.user.id,
                message=notification.message,
                read=notification.read,
                sent_at=notification.sent_at.isoformat()
            )
        except User.DoesNotExist:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details('User not found')
            return notification_pb2.Notification()

    def UpdateNotificationReadStatus(self, request, context):
        try:
            notification = Notification.objects.get(id=request.id)
            notification.read = request.read
            notification.save()
            return notification_pb2.Notification(
                id=notification.id,
                user_id=notification.user.id,
                message=notification.message,
                read=notification.read,
                sent_at=notification.sent_at.isoformat()
            )
        except Notification.DoesNotExist:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details('Notification not found')
            return notification_pb2.Notification()

    def ListNotificationsForUser(self, request, context):
        notifications = Notification.objects.filter(user_id=request.user_id).order_by('-sent_at')
        for notification in notifications:
            yield notification_pb2.Notification(
                id=notification.id,
                user_id=notification.user.id,
                message=notification.message,
                read=notification.read,
                sent_at=notification.sent_at.isoformat()
            )

    @classmethod
    def as_servicer(cls):
        return cls()

