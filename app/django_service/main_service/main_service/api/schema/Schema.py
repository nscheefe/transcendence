# app/django_service/main_service/main_service/api/schema/combinedSchema.py
import graphene
from .userSchema import Query as UserQuery, Mutation as UserMutation
from .statSchema import Query as StatQuery, Mutation as StatMutation
from .gameSchema import Query as gameQuery, Mutation as gameMutation
from .chatSchema import Query as chatQuery, Mutation as chatMutation

class Query(UserQuery, StatQuery, gameQuery,chatQuery, graphene.ObjectType):
    pass

class Mutation(UserMutation, StatMutation, gameMutation, chatMutation, graphene.ObjectType):
    pass

schema = graphene.Schema(query=Query, mutation=Mutation)