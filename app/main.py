from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from strawberry.fastapi import GraphQLRouter

from app.agent.service import AgentService
from app.agent.types import AgentQueryRequest, AgentQueryResponse
from app.config import settings
from app.graphql.schema import schema


BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
INDEX_FILE = STATIC_DIR / "index.html"

app = FastAPI(title=settings.app_name)
graphql_app = GraphQLRouter(schema)
app.include_router(graphql_app, prefix="/graphql")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


def get_agent_service() -> AgentService:
    return AgentService(
        graphql_endpoint_url=settings.graphql_endpoint_url,
        default_limit=settings.agent_default_limit,
        llm_enabled=settings.agent_use_llm,
        llm_model=settings.openai_model,
    )


@app.get("/health", tags=["system"])
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/", include_in_schema=False)
def chat_ui() -> FileResponse:
    return FileResponse(INDEX_FILE)


@app.get("/chat", include_in_schema=False)
def chat_ui_alias() -> FileResponse:
    return FileResponse(INDEX_FILE)


@app.post(
    "/agent/query",
    tags=["agent"],
    response_model=AgentQueryResponse,
    response_model_exclude_none=True,
)
def agent_query(payload: AgentQueryRequest) -> AgentQueryResponse:
    agent_service = get_agent_service()
    return agent_service.run(
        message=payload.message,
        limit=payload.limit,
        chat_history=payload.chat_history,
        response_language=payload.response_language,
    )
