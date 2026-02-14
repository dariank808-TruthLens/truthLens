import strawberry

from .graphql_resolvers import Query, Mutation, Subscription

schema = strawberry.Schema(query=Query, mutation=Mutation, subscription=Subscription)
