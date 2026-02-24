from fastapi import FastAPI, File, UploadFile, Form, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
import os
import uuid

from crewai import Crew, Process
from agents import financial_analyst, verifier, investment_advisor, risk_assessor
from task import analyze_financial_document, verification, investment_analysis, risk_assessment
from database import SessionLocal, AnalysisResult
from celery_worker import process_financial_document_task


app = FastAPI(title="Financial Document Analyzer")

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "Financial Document Analyzer API is running"}

@app.post("/analyze")
async def analyze_financial_document_route(
    file: UploadFile = File(...),
    query: str = Form(default="Analyze this financial document for investment insights")
):
    """Analyze financial document and provide comprehensive investment recommendations asynchronously"""
    
    file_id = str(uuid.uuid4())
    file_path = f"data/financial_document_{file_id}.pdf"
    
    try:
        # Ensure data directory exists
        os.makedirs("data", exist_ok=True)
        
        # Save uploaded file
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # Validate query
        if not query:
            query = "Analyze this financial document for investment insights"
            
        # Create DB record
        db = SessionLocal()
        analysis_record = AnalysisResult(
            id=file_id,
            filename=file.filename,
            query=query.strip(),
            status="pending"
        )
        db.add(analysis_record)
        db.commit()
        db.close()
        
        # Trigger Celery task asynchronously
        process_financial_document_task.delay(file_id, file_path, query.strip())
        
        return JSONResponse(
            status_code=202,
            content={
                "message": "Analysis started successfully. Check status endpoint.",
                "analysis_id": file_id,
                "status_endpoint": f"/status/{file_id}",
                "file_processed": file.filename
            }
        )
        
    except Exception as e:
        # Clean up physical file on immediate error
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except:
                pass
        raise HTTPException(status_code=500, detail=f"Error initiating analysis: {str(e)}")

@app.get("/status/{analysis_id}")
async def get_analysis_status(analysis_id: str):
    """Check the status of an ongoing or completed analysis"""
    db = SessionLocal()
    try:
        analysis = db.query(AnalysisResult).filter(AnalysisResult.id == analysis_id).first()
        if not analysis:
            raise HTTPException(status_code=404, detail="Analysis ID not found")
            
        response = {
            "analysis_id": analysis.id,
            "filename": analysis.filename,
            "query": analysis.query,
            "status": analysis.status,
            "created_at": str(analysis.created_at)
        }
        
        if analysis.status == "completed":
            response["result"] = analysis.result
            response["completed_at"] = str(analysis.completed_at)
        elif analysis.status == "failed":
            response["error_message"] = analysis.error_message
            response["completed_at"] = str(analysis.completed_at)
            
        return response
    finally:
        db.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)