from contextlib import asynccontextmanager

from fastapi import FastAPI, UploadFile, File, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import shutil
from pathlib import Path

from src.application import create_application, index_documents_with_components
from src.config.settings import settings

# Enable CORS for Vite frontend
rag_app = None

@asynccontextmanager
async def lifespan(_: FastAPI):
    global rag_app
    print("Starting API and loading RAG Application...")
    rag_app = create_application()
    print("RAG Application loaded successfully.")
    yield


app = FastAPI(title="Agentic Hybrid RAG API", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from typing import Optional, Dict, Any

class ChatRequest(BaseModel):
    query: str

class ChatResponse(BaseModel):
    answer: str
    cache_hit: bool
    route: Optional[str] = None
    processed_query: Optional[Dict[str, Any]] = None

@app.post("/api/chat", response_model=ChatResponse)
def chat_endpoint(request: ChatRequest):
    if not rag_app:
        raise HTTPException(status_code=503, detail="RAG Application not initialized")
    
    try:
        result = rag_app.ask(request.query)
        
        route = None
        if "route" in result and result["route"]:
            route = result["route"].value if hasattr(result["route"], "value") else str(result["route"])
            
        processed_query = None
        if "processed_query" in result and result["processed_query"]:
            pq = result["processed_query"]
            processed_query = {
                "normalized": pq.normalized if hasattr(pq, "normalized") else "",
                "keywords": pq.keywords if hasattr(pq, "keywords") else [],
                "entities": pq.entities if hasattr(pq, "entities") else [],
                "temporal": pq.temporal if hasattr(pq, "temporal") else False
            }
            
        return ChatResponse(
            answer=result.get("answer", "No answer generated."),
            cache_hit=result.get("cache_hit", False),
            route=route,
            processed_query=processed_query
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/upload")
def upload_document(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
        
    doc_path = Path(settings.documents_dir) / file.filename
    doc_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(doc_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    # Trigger background indexing
    if rag_app:
        background_tasks.add_task(index_documents_with_components, rag_app.components)
    
    return {"message": f"Successfully uploaded {file.filename}. Indexing started in background."}

@app.get("/api/documents")
def list_documents():
    if not rag_app:
        raise HTTPException(status_code=503, detail="RAG Application not initialized")
    docs = rag_app.components.registry.get_all()
    return [{"filename": Path(doc.source).name, "id": doc.document_id, "hash": doc.content_hash, "type": doc.source_type} for doc in docs]

@app.delete("/api/documents/{filename}")
def delete_document(filename: str):
    if not rag_app:
        raise HTTPException(status_code=503, detail="RAG Application not initialized")
    
    doc_path = Path(settings.documents_dir) / filename
    if doc_path.exists():
        doc_path.unlink()
    
    rag_app.components.registry.delete(doc_path.as_posix())
    return {"message": f"Successfully deleted {filename}"}
