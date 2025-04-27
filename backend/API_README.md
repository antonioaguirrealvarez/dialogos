# Audio Analysis API

This is the FastAPI backend for the audio transcript/insight application. It processes audio conversations or text transcripts to produce insights and analysis.

## Setup

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Set up your API keys in the `.env` file:
```
# Hume AI API Key
HUME_API_KEY=your_hume_key

# ElevenLabs API Key
ELEVENLABS_API_KEY=your_elevenlabs_key

# Claude API Key
ANTHROPIC_API_KEY=your_claude_key
```

## Running the API

Start the API server:
```bash
cd backend
python api.py
```

The API will be available at `http://localhost:8000`. You can access the Swagger documentation at `http://localhost:8000/docs`.

## API Endpoints

### `GET /`
Check if the API is running.

**Response:**
```json
{"message": "Audio Analysis API is running"}
```

### `POST /process`
Upload and process an audio file or transcript.

**Request:**
- Form data with a file upload

**Response:**
```json
{
  "job_id": "unique-job-id",
  "status": "processing",
  "message": "File filename.mp3 uploaded and processing started. Check status with /status/unique-job-id"
}
```

### `POST /process-text`
Process a text transcript.

**Request:**
- Form data with a "text" field containing the transcript

**Response:**
```json
{
  "job_id": "unique-job-id",
  "status": "processing",
  "message": "Text transcript received and processing started. Check status with /status/unique-job-id"
}
```

### `GET /status/{job_id}`
Get the status of a processing job.

**Response:**
```json
{
  "job_id": "unique-job-id",
  "status": "completed|processing|failed",
  "results": {} // Present if status is "completed"
}
```

### `GET /results/{job_id}`
Get the complete results of a processing job.

**Response:**
```json
{
  "structured_analysis": {
    // Contents of the Claude structured analysis JSON
  },
  "emotions_analysis": {
    // Contents of the emotions analysis JSON
  }
}
```

## Supported File Types

- **Audio files**: `.wav`, `.mp3`, `.m4a`, `.aac`, `.ogg`, `.flac`
- **Transcript files**: `.txt`, `.md`, `.json`

## Integration with Frontend

The frontend can communicate with this API to:
1. Upload audio files or text transcripts
2. Check the status of processing jobs
3. Retrieve and display the results when ready

The results include structured analysis of the conversation and emotions analysis, which can be visualized in the frontend dashboard. 