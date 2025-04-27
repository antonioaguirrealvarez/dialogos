#!/usr/bin/env python3
"""
FastAPI application for the audio analysis pipeline.
This provides a REST API to the orchestrator.
"""

import os
import uuid
import json
import logging
import shutil
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel
import uvicorn

from orchestrator.orchestrator import AudioOrchestrator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('api.log', mode='a')
    ]
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Audio Analysis API",
    description="API for processing audio conversations and transcripts",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins in development
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

# Initialize orchestrator
orchestrator = AudioOrchestrator(
    input_dir="input_files",
    hume_output_dir="outputs/hume",
    elevenlabs_output_dir="outputs/elevenlabs",
    processed_output_dir="outputs/processed",
    claude_output_dir="outputs/claude"
)

# Create input directory if it doesn't exist
os.makedirs("input_files", exist_ok=True)

# Response models
class ProcessingResponse(BaseModel):
    job_id: str
    status: str
    message: str

class ProcessingStatus(BaseModel):
    job_id: str
    status: str
    results: Optional[Dict[str, Any]] = None

# Dictionary to track processing status
processing_jobs = {}

@app.get("/")
async def root():
    """Root endpoint to check if the API is running."""
    return {"message": "Audio Analysis API is running"}

@app.post("/process", response_model=ProcessingResponse)
async def process_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...)
):
    """
    Process an audio file or transcript.
    This endpoint accepts an audio file or a transcript file and returns a job ID.
    The processing is done asynchronously in the background.
    """
    # Generate a unique job ID
    job_id = str(uuid.uuid4())
    
    # Get file extension
    file_extension = os.path.splitext(file.filename)[1].lower()
    
    # Save the uploaded file to the input directory
    file_path = os.path.join("input_files", f"{job_id}{file_extension}")
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Update job status
    processing_jobs[job_id] = {"status": "processing", "file_path": file_path}
    
    # Determine if it's an audio file or a transcript
    is_audio = file_extension in ['.wav', '.mp3', '.m4a', '.aac', '.ogg', '.flac']
    is_transcript = file_extension in ['.txt', '.md', '.json']
    
    # Process the file in the background
    background_tasks.add_task(
        process_file_background,
        job_id,
        file_path,
        is_audio,
        is_transcript
    )
    
    return ProcessingResponse(
        job_id=job_id,
        status="processing",
        message=f"File {file.filename} uploaded and processing started. Check status with /status/{job_id}"
    )

@app.post("/process-text", response_model=ProcessingResponse)
async def process_text(
    background_tasks: BackgroundTasks,
    text: str = Form(...)
):
    """
    Process a text transcript.
    This endpoint accepts a text transcript and returns a job ID.
    The processing is done asynchronously in the background.
    """
    # Generate a unique job ID
    job_id = str(uuid.uuid4())
    
    # Save the text to a file
    file_path = os.path.join("input_files", f"{job_id}.txt")
    
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(text)
    
    # Update job status
    processing_jobs[job_id] = {"status": "processing", "file_path": file_path}
    
    # Process the file in the background
    background_tasks.add_task(
        process_file_background,
        job_id,
        file_path,
        False,  # Not an audio file
        True    # Is a transcript
    )
    
    return ProcessingResponse(
        job_id=job_id,
        status="processing",
        message=f"Text transcript received and processing started. Check status with /status/{job_id}"
    )

@app.get("/status/{job_id}", response_model=ProcessingStatus)
async def get_status(job_id: str):
    """
    Get the status of a processing job.
    This endpoint returns the status of a processing job and the results if available.
    """
    if job_id not in processing_jobs:
        raise HTTPException(status_code=404, detail=f"Job ID {job_id} not found")
    
    return ProcessingStatus(
        job_id=job_id,
        status=processing_jobs[job_id]["status"],
        results=processing_jobs[job_id].get("results")
    )

@app.get("/results/{job_id}")
async def get_results(job_id: str):
    """
    Get the results of a processing job.
    This endpoint returns the results of a processing job as a JSON file.
    """
    if job_id not in processing_jobs:
        raise HTTPException(status_code=404, detail=f"Job ID {job_id} not found")
    
    if processing_jobs[job_id]["status"] != "completed":
        raise HTTPException(status_code=400, detail=f"Job {job_id} is still processing or failed")
    
    # Get the results
    structured_analysis_path = processing_jobs[job_id]["results"].get("claude_structured_json_file")
    emotions_analysis_path = processing_jobs[job_id]["results"].get("quintile_analysis")
    
    if not structured_analysis_path or not emotions_analysis_path:
        raise HTTPException(status_code=404, detail=f"Results not found for job {job_id}")
    
    # Return the results as a dictionary
    results = {
        "structured_analysis": load_json_file(structured_analysis_path),
        "emotions_analysis": load_json_file(emotions_analysis_path)
    }
    
    return results

def load_json_file(file_path):
    """Load a JSON file and return its contents as a dictionary."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading JSON file {file_path}: {str(e)}")
        return {"error": f"Could not load file: {str(e)}"}

async def process_file_background(job_id: str, file_path: str, is_audio: bool, is_transcript: bool):
    """
    Process a file in the background.
    This function is called by the background task to process a file.
    """
    try:
        logger.info(f"Starting background processing for job {job_id}")
        
        if is_audio:
            # Process audio file
            logger.info(f"Processing audio file: {file_path}")
            results = orchestrator.process_file(
                audio_file=file_path,
                force_reprocess=True
            )
        elif is_transcript:
            # Process transcript file
            logger.info(f"Processing transcript file: {file_path}")
            results = orchestrator.process_transcript_with_claude(
                transcript_file=file_path,
                force_reprocess=True
            )
        else:
            # Unsupported file type
            logger.error(f"Unsupported file type for {file_path}")
            processing_jobs[job_id] = {
                "status": "failed",
                "error": "Unsupported file type"
            }
            return
        
        # Check if processing was successful
        if results:
            logger.info(f"Processing completed for job {job_id}")
            processing_jobs[job_id] = {
                "status": "completed",
                "results": results
            }
        else:
            logger.error(f"Processing failed for job {job_id}")
            processing_jobs[job_id] = {
                "status": "failed",
                "error": "Processing failed"
            }
    except Exception as e:
        logger.error(f"Error processing job {job_id}: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        processing_jobs[job_id] = {
            "status": "failed",
            "error": str(e)
        }

if __name__ == "__main__":
    # Run the FastAPI app with uvicorn
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True) 