from strawberry.asgi import GraphQL
from .graphql_schema import schema

graphql_app = GraphQL(schema)
