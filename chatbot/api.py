from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from main import agent_with_memory


app = FastAPI()

# allow requests from the Vite dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    message: str
    session_id: str = "default"  # fallback if frontend doesn't send one


@app.post("/chat")
async def chat(request: ChatRequest):
    # thread_id keeps conversation memory separate per session
    config = {"configurable": {"thread_id": request.session_id}}
    response = agent_with_memory.invoke(  # type: ignore
        {"messages": [("user", request.message)]},
        config=config
    )
    return {"response": response["messages"][-1].content}


@app.get("/health")
async def health():
    return {"status": "ok"}