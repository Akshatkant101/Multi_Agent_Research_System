from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pipeline import run_research_pipeline # Importing your existing logic
import uvicorn

app = FastAPI(
    title="Multi-Agent Research API",
    description="API for automated web research using Gemini & Tavily",
    version="1.0.0"
)

# Define the request shape
class ResearchRequest(BaseModel):
    topic: str

# Define the response shape (helps with documentation)
class ResearchResponse(BaseModel):
    report: str
    feedback: str
    scraped_content: str

@app.post("/research", response_model=ResearchResponse)
async def conduct_research(request: ResearchRequest):
    try:
        # Call your orchestrator
        # Note: In production, you'd use BackgroundTasks or WebSockets 
        # because research takes 15-30 seconds.
        state = run_research_pipeline(request.topic)
        
        return {
            "report": state["report"],
            "feedback": state["feedback"],
            "scraped_content": state["scraped_content"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)