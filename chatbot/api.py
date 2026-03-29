from dotenv import load_dotenv
load_dotenv()

import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, validator
from main import agent_with_memory

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


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
    
    @validator('message')
    def message_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Message cannot be empty')
        if len(v) > 5000:
            raise ValueError('Message too long (max 5000 characters)')
        return v.strip()
    
    @validator('session_id')
    def session_id_valid(cls, v):
        if len(v) > 100:
            raise ValueError('Session ID too long')
        return v


@app.post("/chat")
async def chat(request: ChatRequest):
    """Handle chat requests with comprehensive error handling."""
    try:
        logger.info(f"Chat request - session: {request.session_id}, message length: {len(request.message)}")
        
        # thread_id keeps conversation memory separate per session
        config = {"configurable": {"thread_id": request.session_id}}
        
        # Invoke agent with message
        response = agent_with_memory.invoke(  # type: ignore
            {"messages": [("user", request.message)]},
            config=config
        )
        
        # Validate response structure
        if not response or "messages" not in response:
            logger.error(f"Invalid response structure from agent: {response}")
            raise HTTPException(
                status_code=500,
                detail="Invalid response from AI agent. Please try again."
            )
        
        if not response["messages"]:
            logger.error("Agent returned empty messages list")
            raise HTTPException(
                status_code=500,
                detail="AI agent returned no response. Please try again."
            )
        
        # Extract response content
        response_content = response["messages"][-1].content
        
        if not response_content:
            logger.warning("Agent returned empty content")
            response_content = "I'm having trouble generating a response. Please try rephrasing your question."
        
        logger.info(f"Chat response successful - session: {request.session_id}")
        return {"response": response_content}
    
    except ValueError as e:
        logger.warning(f"Validation error: {str(e)}")
        raise HTTPException(status_code=422, detail=str(e))
    
    except HTTPException:
        raise
    
    except TimeoutError:
        logger.error(f"Timeout during agent invocation - session: {request.session_id}")
        raise HTTPException(
            status_code=504,
            detail="Request timed out. The AI is taking too long to respond. Please try again."
        )
    
    except Exception as e:
        logger.error(f"Unexpected error in chat endpoint - session: {request.session_id}, error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred: {str(e)}. Please try again later."
        )


@app.get("/health")
async def health():
    return {"status": "ok"}