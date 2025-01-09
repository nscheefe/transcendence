# app/django_service/main_service/main_service/api/schema/combinedSchema.py
import graphene
from .userSchema import Query as UserQuery, Mutation as UserMutation
from .statSchema import Query as StatQuery, Mutation as StatMutation
from .gameSchema import Query as gameQuery, Mutation as gameMutation, Subscription as gameSubscription, PingSubscription
from .chatSchema import Query as chatQuery, Mutation as chatMutation, Subscription as chatSubscription

from .authSchema import Mutation as authMutation
from .adminSchema import Query as adminQuery, Mutation as adminMutation
from .chatSchema import Mutation

class Query(UserQuery, StatQuery, gameQuery, chatQuery, adminQuery, graphene.ObjectType):
    pass

class Mutation(UserMutation, StatMutation, gameMutation, chatMutation, adminMutation, graphene.ObjectType):
    pass

class Subscription(gameSubscription, chatSubscription, graphene.ObjectType):
    pass

schema = graphene.Schema(query=Query, mutation=Mutation, subscription=Subscription)
schemaAuth = graphene.Schema(mutation=authMutation)

