from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter

from app.config import settings
from app.graphql.schema import schema


app = FastAPI(title=settings.app_name)
graphql_app = GraphQLRouter(schema)
app.include_router(graphql_app, prefix="/graphql")


@app.get("/health", tags=["system"])
def health() -> dict[str, str]:
    return {"status": "ok"}
