from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os
from datetime import datetime

from shared_memory import SharedStateMemory
from researcher_agent import ResearcherAgentWrapper, ResearcherAgent
from writer_agent import WriterModule, WriterAgentWrapper
from supervisor_agent import SupervisorAgent

app = FastAPI(title="Multi-Agent Automotive System")

# Initialize the multi-agent system
shared_memory = SharedStateMemory()
researcher = ResearcherAgentWrapper(shared_memory, ResearcherAgent())
writer = WriterAgentWrapper(shared_memory, WriterModule(output_dir="/app/reports"))
supervisor = SupervisorAgent(shared_memory, researcher, writer)

# Mount static files
os.environ["GOOGLE_API_KEY"] = "AIzaSyAXQD1xmjT3vy7Ek7e6BNqMWKxVwi4URts"
app.mount("/static", StaticFiles(directory="/app/static"), name="static")
app.mount("/reports", StaticFiles(directory="/app/reports"), name="reports")


class QueryRequest(BaseModel):
    query: str
    output_format: str = "both"


class QueryResponse(BaseModel):
    status: str
    type: Optional[str] = None
    message: str
    cars: Optional[List[str]] = None
    outputs: Optional[Dict[str, str]] = None
    data: Optional[Dict[str, Any]] = None
    workflow_id: Optional[str] = None


@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Serve the frontend HTML"""
    with open("/app/static/index.html", "r") as f:
        return f.read()


@app.post("/api/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    """Process a user query through the multi-agent system"""
    try:
        result = supervisor.process_user_query(request.query, request.output_format)
        return QueryResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/status")
async def get_status():
    """Get system status"""
    return supervisor.get_state_summary()


@app.get("/api/cars")
async def get_available_cars():
    """Get list of cars in shared memory"""
    return {"cars": list(shared_memory.research_data.keys())}


@app.get("/api/car/{car_name}")
async def get_car_data(car_name: str):
    """Get research data for a specific car"""
    data = shared_memory.get_latest_research(car_name)
    if data:
        return data
    raise HTTPException(status_code=404, detail="Car not found")


@app.get("/api/reports")
async def get_reports():
    """Get list of generated reports"""
    return {"reports": shared_memory.generated_reports}


@app.get("/api/report/{report_id}")
async def get_report(report_id: str):
    """Get report details by ID"""
    report = shared_memory.get_report(report_id)
    if report:
        return report
    raise HTTPException(status_code=404, detail="Report not found")


@app.get("/api/download/{filename}")
async def download_file(filename: str):
    """Download a generated file"""
    file_path = os.path.join("/app/reports", filename)
    if os.path.exists(file_path):
        return FileResponse(file_path, filename=filename)
    raise HTTPException(status_code=404, detail="File not found")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)