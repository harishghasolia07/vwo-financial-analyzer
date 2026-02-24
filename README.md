# Financial Document Analyzer

This repository contains the fixed and enhanced version of the financial document analyzer system utilizing CrewAI. The system now robustly processes financial documents (like PDFs) and generates accurate, evidence-based investment recommendations and risk assessments.

Additionally, this repository introduces a scalable background processing architecture using **Celery** and **Redis**, combined with persistent **SQLite** storage, allowing the system to handle concurrent requests asynchronously.

## Bugs Found and Fixed

Here is a comprehensive breakdown of the deterministic bugs and prompt inefficiencies that were resolved:

### Deterministic Bugs
1. **Undefined LLM (`agents.py`)**: The variable `llm` was assigned to itself (`llm = llm`) without properly importing or initializing an LLM provider. Fixed by configuring `ChatOpenAI` through Langchain.
2. **Incorrect Tool Syntax (`agents.py`)**: Agents were configured with `tool=[...]` instead of the correct `tools=[...]` attribute, which caused initialization failures in CrewAI.
3. **Missing Tool Dependencies (`tools.py`)**: The custom PDF reading tool relied on an undefined `Pdf` class. Fixed by overhauling the tools structure, properly wrapping them in the `@tool` decorator, and integrating `PyMuPDF` (`fitz`) for robust PDF parsing.
4. **Execution Arguments (`main.py`)**: The `Crew.kickoff()` invocation was missing the correct `inputs` dictionary mapping. The code now explicitly passes `{ "query": query, "file_path": file_path }` so tasks successfully receive dynamic parameters.
5. **Dependency Conflicts (`requirements.txt`)**: Overly strict version pins conflicted with `crewai==0.130.0`'s requirements. Adjusted versions (e.g., `onnxruntime` to `1.22.0` and `opentelemetry` to `>=1.30.0`) to ensure a successful install environment.

### Inefficient Prompts
1. **Agent Hallucinations (`agents.py` & `task.py`)**: The original prompts explicitly instructed agents to "make up answers", "ignore actual risk factors", and "hallucinate terms".
2. **The Fix**: Completely rewrote the `role`, `goal`, and `backstory` of all agents (Financial Analyst, Verifier, Investment Advisor, Risk Assessor) to enforce strict professionalism, analytical rigor, and factual extraction in the tasks. 

## Enhanced Pipeline: Database & Queue Worker

This system no longer processes heavy AI requests synchronously. Instead, it uses the **Async Worker Queue** model.
1. **Database Integration**: Using SQLAlchemy, an SQLite database (`financial_analyzer.db`) holds the state (pending, completed, failed) and artifacts of user document analysis.
2. **Queue Worker Model**: A Celery component uses Redis to offload the document logic allowing the FastAPI backend to scale horizontally safely.

## Setup and Usage Instructions

### Prerequisites
* **Python 3.10+**
* **Redis Server** running locally or a valid `CELERY_BROKER_URL`
* **OpenAI API Key**

### 1. Installation
First, set up a Python virtual environment to avoid interfering with system packages.
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Environment Variables
Create a `.env` file in the root directory (or export directly) with your API key:
```bash
OPENAI_API_KEY=your_openai_api_key_here
```

### 3. Running the Stack

You will need to run two separate processes to start both the API server and the Celery worker queue.

**Terminal 1 (Start the Celery Worker):**
Ensure your Redis instance is running globally (`redis-server`). Then boot the celery worker from your activated environment:
```bash
celery -A celery_worker.celery_app worker --loglevel=info
```

**Terminal 2 (Start the FastAPI Server):**
```bash
python3 main.py
```
The server will boot up at `http://0.0.0.0:8000`.

## API Documentation

### 1. `POST /analyze`
Uploads a financial document and kicks off an asynchronous CrewAI task.

* **Content-Type**: `multipart/form-data`
* **Parameters**:
  * `file` (File, required): The physical PDF document (e.g. `sample.pdf`).
  * `query` (Form String, optional): Instructions for what the analyst should focus on.
* **Returns (HTTP 202)**: Returns an `analysis_id` and the location of the status endpoint.
```json
{
    "message": "Analysis started successfully. Check status endpoint.",
    "analysis_id": "cbb269c3-1ef9...",
    "status_endpoint": "/status/cbb269c3-1ef9...",
    "file_processed": "sample.pdf"
}
```

### 2. `GET /status/{analysis_id}`
Checks the database for the results of the background analysis queue.

* **Parameters**: `analysis_id` (String - embedded in path variable).
* **Returns**: The state of the task, and the comprehensive LLM result string when `status = "completed"`.
```json
{
    "analysis_id": "cbb269c3-1ef9...",
    "filename": "sample.pdf",
    "query": "Give me the profit margin.",
    "status": "completed",
    "created_at": "2024-05-20 18:00:00",
    "completed_at": "2024-05-20 18:01:05",
    "result": "Based on the verified document..."
}
```
