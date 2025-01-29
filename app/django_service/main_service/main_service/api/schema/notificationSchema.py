import asyncio
from asyncio.log import logger
from datetime import datetime, timedelta
import logging

import grpc
from google.protobuf.timestamp_pb2 import Timestamp

from ariadne import ObjectType, SubscriptionType
from channels.layers import get_channel_layer
from main_service.api.schema.objectTypes import query, mutation, subscription

from main_service.api.schema.userSchema import resolver as user_resolver
import main_service.protos.notification_pb2 as notification_pb2
import main_service.protos.notification_pb2_grpc as notification_pb2_grpc
import main_service.protos.user_pb2 as user_pb2
import main_service.protos.user_pb2_grpc as user_pb2_grpc

GRPC_HOST = "user_service"
GRPC_PORT = "50051"
GRPC_TARGET = f"{GRPC_HOST}:{GRPC_PORT}"

logger = logging.getLogger(__name__)

subscription = SubscriptionType()

@subscription.source("notificationsForUser")
async def notifications_for_user_source(_, info):
    user_id = info.context["request"].scope.get("user_id")

    async def fetch_notifications():
        last_sent_at = None
        async with grpc.aio.insecure_channel(GRPC_TARGET) as channel:
            notification_stub = notification_pb2_grpc.NotificationServiceStub(channel)
            user_stub = user_pb2_grpc.UserServiceStub(channel)
            grpc_request = notification_pb2.GetNotificationsByUserIdRequest(user_id=user_id)
            while True:
                # Fetch notifications
                response = await notification_stub.GetNotificationsByUserId(grpc_request)
                new_notifications = []
                for notification in response.notifications:
                    sent_at = notification.sent_at.ToDatetime()
                    if last_sent_at is None or sent_at > last_sent_at:
                        new_notifications.append({
                            "id": notification.id,
                            "userId": notification.user_id,
                            "message": notification.message,
                            "read": notification.read,
                            "sentAt": sent_at.isoformat(),
                        })
                if new_notifications:
                    last_sent_at = max(datetime.fromisoformat(notification["sentAt"]) for notification in new_notifications)
                    for notification in new_notifications:
                        yield notification

                # Update lastLogin
                last_login_timestamp = Timestamp()
                last_login_timestamp.FromDatetime(datetime.utcnow())
                update_request = user_pb2.UpdateUserLastLoginRequest(
                    id=user_id,
                    last_login=last_login_timestamp
                )
                await user_stub.UpdateUserLastLogin(update_request)

                await asyncio.sleep(10)  # Poll every 10 seconds

    return fetch_notifications()

@subscription.field("notificationsForUser")
async def resolve_notifications_for_user(notification, info):
    return notification


@subscription.source("onlineStatus")
async def online_status_source(_, info, user_id):
    async with grpc.aio.insecure_channel(GRPC_TARGET) as channel:
        user_stub = user_pb2_grpc.UserServiceStub(channel)
        grpc_request = user_pb2.GetUserRequest(id=user_id)
        while True:
            response = await user_stub.GetUser(grpc_request)
            last_login = response.last_login.ToDatetime() if response.HasField("last_login") else None
            is_online = last_login and (datetime.utcnow() - last_login) < timedelta(minutes=1)
            if is_online is None:
                is_online = False
            yield {"userId": user_id, "status": is_online}
            await asyncio.sleep(11)  # Check every 10 seconds

@subscription.field("onlineStatus")
async def resolve_online_status(status, info, user_id):
    return status

resolver = [query, mutation, subscription]
