from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, File, HTTPException, Response, UploadFile, status

from app.agents.graph import invoke_agent
from app.api.schemas import ChatRequest, ChatResponse, HealthResponse, IndexResponse, SourceResponse
from app.core.config import get_settings
from app.core.security import ALLOWED_DOCUMENT_SUFFIXES, safe_filename
from app.database.connection import check_database_connection
from app.rag.loader import load_documents
from app.rag.retriever import index_documents

router = APIRouter()
CONVERSATIONS: dict[str, list[dict]] = {}


@router.get("/health", response_model=HealthResponse, responses={503: {"model": HealthResponse}})
def health_check(response: Response) -> HealthResponse:
    settings = get_settings()
    connected = check_database_connection()
    if not connected:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    return HealthResponse(status="ok" if connected else "degraded", service=settings.app_name, version=settings.app_version, environment=settings.environment, database="connected" if connected else "unavailable")


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    conversation_id = request.conversation_id or str(uuid4())
    result = invoke_agent(request.message, conversation_id)
    record = {"message": request.message, "answer": result.get("final_answer", ""), "route": result.get("route")}
    CONVERSATIONS.setdefault(conversation_id, []).append(record)
    return ChatResponse(
        conversation_id=conversation_id,
        route=result.get("route", "unknown"),
        answer=result.get("final_answer", ""),
        tools_used=result.get("tools_used", []),
        sources=result.get("sources", []),
        sql_query=result.get("sql_query"),
        sql_result=result.get("sql_result"),
        business_result=result.get("business_result"),
        errors=result.get("errors", []),
    )


@router.post("/documents/upload")
async def upload_document(file: UploadFile = File(...)) -> dict:
    settings = get_settings()
    filename = safe_filename(file.filename or "upload.txt")
    suffix = Path(filename).suffix.lower()
    if suffix not in ALLOWED_DOCUMENT_SUFFIXES:
        raise HTTPException(400, "Only .md and .txt documents are accepted")
    content = await file.read(settings.upload_max_mb * 1024 * 1024 + 1)
    if len(content) > settings.upload_max_mb * 1024 * 1024:
        raise HTTPException(413, "Document is too large")
    upload_dir = settings.documents_path / "uploads"
    upload_dir.mkdir(parents=True, exist_ok=True)
    (upload_dir / filename).write_bytes(content)
    return {"filename": filename, "status": "uploaded", "index_required": True}


@router.post("/documents/index", response_model=IndexResponse)
def index() -> IndexResponse:
    try:
        count = index_documents(reset=True)
        return IndexResponse(chunks_indexed=count)
    except Exception as exc:
        raise HTTPException(500, f"Document indexing failed: {type(exc).__name__}") from exc


@router.get("/sources", response_model=SourceResponse)
def sources() -> SourceResponse:
    return SourceResponse(sources=[doc.metadata for doc in load_documents()])


@router.get("/conversations/{conversation_id}")
def conversation(conversation_id: str) -> dict:
    if conversation_id not in CONVERSATIONS:
        raise HTTPException(404, "Conversation not found")
    return {"conversation_id": conversation_id, "messages": CONVERSATIONS[conversation_id]}
