import grpc
from datetime import datetime
from google.protobuf.timestamp_pb2 import Timestamp
from django.db import IntegrityError
from user_service.protos import notification_pb2_grpc, notification_pb2
from user.models import Notification, User


class NotificationServiceHandler(notification_pb2_grpc.NotificationServiceServicer):
    def __init__(self):
        pass

    def CreateNotification(self, request, context):
        """
        Create a new Notification for a given user.
        """
        try:
            # Retrieve the user from the database
            user = User.objects.get(id=request.user_id)

            # Create the notification object
            notification = Notification(
                user=user,
                message=request.message,
                read=request.read,
                sent_at=datetime.utcnow()  # Set the current timestamp
            )
            notification.save()

            # Convert Python datetime to protobuf Timestamp
            sent_at_proto = Timestamp()
            sent_at_proto.FromDatetime(notification.sent_at)

            # Return the created notification as a protobuf message
            return notification_pb2.Notification(
                id=notification.id,
                user_id=notification.user.id,
                message=notification.message,
                read=notification.read,
                sent_at=sent_at_proto
            )
        except User.DoesNotExist:
            # User not found error
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details('User not found')
            return notification_pb2.Notification()
        except IntegrityError as e:
            # Handle data integrity issues
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details(f'Data integrity error: {str(e)}')
            return notification_pb2.Notification()
        except Exception as e:
            # Handle unexpected errors
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f'Failed to create notification: {str(e)}')
            return notification_pb2.Notification()

    def GetNotificationById(self, request, context):
        """
        Retrieve a Notification by its ID.
        """
        try:
            # Retrieve the notification from the database
            notification = Notification.objects.get(id=request.id)

            # Convert Python datetime to protobuf Timestamp
            sent_at_proto = Timestamp()
            sent_at_proto.FromDatetime(notification.sent_at)

            # Return the notification as a protobuf message
            return notification_pb2.Notification(
                id=notification.id,
                user_id=notification.user.id,
                message=notification.message,
                read=notification.read,
                sent_at=sent_at_proto
            )
        except Notification.DoesNotExist:
            # Notification not found error
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details('Notification not found')
            return notification_pb2.Notification()
        except Exception as e:
            # Handle unexpected errors
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f'Failed to retrieve notification: {str(e)}')
            return notification_pb2.Notification()

    def GetNotificationsByUserId(self, request, context):
        """
        Retrieve all Notifications for a specific user, ordered by sent_at timestamp.
        """
        try:
            # Retrieve notifications from the database for the given user_id
            notifications = Notification.objects.filter(user_id=request.user_id).order_by('-sent_at')

            # Prepare a list of protobuf Notification messages
            notifications_proto = []
            for notification in notifications:
                sent_at_proto = Timestamp()
                sent_at_proto.FromDatetime(notification.sent_at)

                notifications_proto.append(
                    notification_pb2.Notification(
                        id=notification.id,
                        user_id=notification.user.id,
                        message=notification.message,
                        read=notification.read,
                        sent_at=sent_at_proto
                    )
                )

            # Return the list of notifications in a NotificationsResponse
            return notification_pb2.NotificationsResponse(
                notifications=notifications_proto
            )
        except Exception as e:
            # Handle unexpected errors
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f'Failed to retrieve notifications: {str(e)}')
            return notification_pb2.NotificationsResponse()

    @classmethod
    def as_servicer(cls):
        """
        Helper function for registering the servicer with the gRPC server.
        """
        return cls()
