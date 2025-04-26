# Touchy Feely AI

A toolkit for processing audio conversations using ElevenLabs transcription, Hume AI sentiment analysis, and Claude AI conversation analysis. This toolkit applies principles from the Stanford course "Touchy Feely" to evaluate conversations via audio.

## Overview

This project contains tools for:
1. Transcribing audio files using ElevenLabs Speech-to-Text API
2. Analyzing sentiment and emotional content using Hume AI
3. Analyzing conversation dynamics and communication patterns using Claude AI
4. Processing and visualizing sentiment and conversation data

## Project Structure

```
.
├── orchestrator/          # Contains the main orchestration logic
│   └── orchestrator.py    # Main orchestrator handling the pipeline
│
├── clients/               # API client implementations
│   ├── claude/            # Claude AI API client
│   │   └── client.py
│   ├── elevenlabs/        # ElevenLabs API client
│   │   └── client.py
│   └── hume/              # Hume AI API client
│       └── client.py
│
├── processors/            # Data processing logic
│   ├── claude/            # Claude data processor
│   │   └── processor.py
│   └── sentiment_processor.py # Hume sentiment processor
│
├── prompts/               # Prompt templates for Claude AI
│   └── claude/
│       ├── prompt_1.txt
│       ├── prompt_2.txt
│       ├── sentiment_prompt.txt
│       └── summary_prompt.txt
│
├── outputs/               # All output files
│   ├── claude/            # Claude AI output results
│   ├── elevenlabs/        # ElevenLabs output results
│   ├── hume/              # Hume AI output results
│   └── processed/         # Processed/combined outputs
│
├── tests/                 # Test scripts
│   ├── test_elevenlabs.py
│   ├── test_claude.py
│   └── test_sentiment_processor.py
│
├── input_files/           # Input audio files
├── main.py                # Main entry point script
├── .env                   # Environment variables
├── requirements.txt       # Dependencies
└── README.md              # This file
```

## Setup

1. Clone the repository
2. Install the dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Create a `.env` file with your API keys:
   ```
   ELEVENLABS_API_KEY=your_elevenlabs_api_key
   HUME_API_KEY=your_hume_api_key
   ANTHROPIC_API_KEY=your_anthropic_api_key
   ```

## Usage

### Running the Full Pipeline

To process an audio file with ElevenLabs, Hume AI, and Claude AI:

```
python main.py --file your_audio_file.mp4
```

### Using Specific Services

```
# Transcription Only (ElevenLabs)
python main.py --file your_audio_file.mp4 --elevenlabs-only

# Sentiment Analysis Only (Hume AI)
python main.py --file your_audio_file.mp4 --hume-only

# Claude AI Analysis Only (requires a transcript file)
python main.py --file your_audio_file.mp4 --claude-only

# Skip specific services
python main.py --file your_audio_file.mp4 --skip-hume
python main.py --file your_audio_file.mp4 --skip-elevenlabs
python main.py --file your_audio_file.mp4 --skip-claude
```

### Processing Existing Transcript

To process an existing transcript directly with Claude:

```
python main.py --transcript path/to/transcript.txt
```

### Processing All Files in Input Directory

```
python main.py
```

### Additional Options

- `--force`: Force reprocessing even if results exist
- `--skip-visualization`: Skip visualization generation
- `--job-id JOB_ID`: Process a specific Hume AI job ID
- `--debug`: Enable debug logging
- `--file-pattern PATTERN`: Pattern to match files to process (default: "*.*")

## API Keys

### ElevenLabs

1. Create an account on [ElevenLabs](https://elevenlabs.io/)
2. Get your API key from the profile settings
3. Add it to your `.env` file as `ELEVENLABS_API_KEY`

### Hume AI

1. Create an account on [Hume AI](https://hume.ai/)
2. Get your API key from the dashboard
3. Add it to your `.env` file as `HUME_API_KEY`

### Claude AI (Anthropic)

1. Create an account on [Anthropic](https://www.anthropic.com/)
2. Get your API key from the developer dashboard
3. Add it to your `.env` file as `ANTHROPIC_API_KEY`

## Output Files

The pipeline generates several types of output files:

- **ElevenLabs outputs** (in `outputs/elevenlabs/`):
  - `*_transcript.json`: Raw transcript data
  - `*_transcript_cleaned.txt`: Cleaned transcript with speaker information

- **Hume AI outputs** (in `outputs/hume/`):
  - `job_*_predictions.json`: Raw sentiment prediction data

- **Claude AI outputs** (in `outputs/claude/`):
  - `claude_response.json`: Raw Claude AI response
  - `claude_structured_analysis.json`: Structured analysis data
  - Visualization charts for share of voice and sentiment

- **Processed outputs** (in `outputs/processed/`):
  - `*_processed_data.csv`: Processed sentiment data
  - `*_sentiment_evolution.png`: Visualization of sentiment over time

## Claude AI Analysis Features

Claude AI provides deep analysis of conversation transcripts with the following capabilities:

### 1. Communication Depth Analysis

Analyzes conversations based on the principles from Stanford's "Touchy Feely" course, categorizing communication into depth levels:

- **Level 1**: Surface-level communication (facts, general topics)
- **Level 2**: Personal opinions and judgments
- **Level 3**: Emotional context and feelings
- **Level 4**: Vulnerability and deep personal insights

### 2. Conversation Insights

- **Share of Voice Analysis**: Distribution of speaking time among participants
- **Key Points Summary**: Main topics and important points raised
- **Communication Pattern Recognition**: Identifies patterns in how participants communicate

### 3. Detailed Recommendations

- Specific suggestions for improving communication effectiveness
- Alternative phrasings and approaches to deepen conversation
- Practice suggestions based on identified patterns

### 4. Visualizations

- Share of voice pie charts
- Speaker sentiment score comparisons
- Communication depth distribution charts

## Running Individual Components

### Test ElevenLabs Transcription

```
python tests/test_elevenlabs.py --file your_audio_file.mp4
```

### Test Hume AI Processing

```
python tests/test_sentiment_processor.py --file path/to/predictions.json
```

### Test Claude AI Analysis

```
python tests/test_claude.py --file path/to/transcript.txt
```

## License

This project is licensed under the MIT License - see the LICENSE file for details. 