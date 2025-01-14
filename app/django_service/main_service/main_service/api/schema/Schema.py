# app/django_service/main_service/main_service/api/schema/combinedSchema.py
from ariadne import QueryType, MutationType, make_executable_schema, ScalarType
from datetime import datetime
from .userSchema import type_defs as user_type_defs, query as user_query, mutation as user_mutation


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

# Create the executable schema
schema = make_executable_schema(user_type_defs, [user_query, user_mutation, datetime_scalar])
