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

class ChatRequest(BaseModel):
    query: str

class ChatResponse(BaseModel):
    answer: str
    cache_hit: bool

@app.post("/api/chat", response_model=ChatResponse)
def chat_endpoint(request: ChatRequest):
    if not rag_app:
        raise HTTPException(status_code=503, detail="RAG Application not initialized")
    
    try:
        result = rag_app.ask(request.query)
        return ChatResponse(
            answer=result.get("answer", "No answer generated."),
            cache_hit=result.get("cache_hit", False),
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
