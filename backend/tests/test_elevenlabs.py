#!/usr/bin/env python3
"""
Test script for the ElevenLabs client.
This script can be used to test the ElevenLabs client in isolation.
"""

import os
import sys
import argparse
import logging
from datetime import datetime
import traceback
import json

# Add parent directory to path to allow importing modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import client
from clients.elevenlabs.client import ElevenLabsClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('elevenlabs_process.log', mode='a')
    ]
)
logger = logging.getLogger(__name__)

def main():
    """
    Main function to test the ElevenLabs client for audio transcription.
    """
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Test the ElevenLabs speech-to-text capabilities")
    parser.add_argument("--file", "-f", required=True, help="Path to the audio file to transcribe")
    parser.add_argument("--output-dir", "-o", default="elevenlabs_results", help="Directory to save output files")
    parser.add_argument("--model", "-m", default="scribe_v1", help="Model ID to use (scribe_v1 or scribe_v1_experimental)")
    parser.add_argument("--language", "-l", help="Language code (ISO-639-1 or ISO-639-3), auto-detected if not specified")
    parser.add_argument("--speakers", "-s", type=int, help="Number of speakers in the audio (if known)")
    parser.add_argument("--no-diarize", action="store_true", help="Disable speaker diarization")
    parser.add_argument("--no-events", action="store_true", help="Disable audio event tagging")
    parser.add_argument("--timestamps", "-t", choices=["none", "word", "character"], default="word",
                      help="Granularity of timestamps (none, word, character)")
    parser.add_argument("--debug", "-d", action="store_true", help="Enable debug logging")
    args = parser.parse_args()
    
    # Set debug logging if requested
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.setLevel(logging.DEBUG)
        # Also set debug level for ElevenLabs client logger
        logging.getLogger('elevenlabs_client').setLevel(logging.DEBUG)
        logger.debug("Debug logging enabled")
    
    # Print start message
    logger.info("===== ElevenLabs Speech-to-Text Test =====")
    logger.info(f"Input file: {args.file}")
    logger.info(f"Output directory: {args.output_dir}")
    logger.info(f"Model: {args.model}")
    
    # Check if file exists
    if not os.path.exists(args.file):
        logger.error(f"Error: File {args.file} does not exist")
        return 1
    
    # Create output directory if it doesn't exist
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Get file basename without extension
    file_basename = os.path.splitext(os.path.basename(args.file))[0]
    
    try:
        # Initialize the ElevenLabs client
        logger.info("Initializing ElevenLabs client")
        elevenlabs_client = ElevenLabsClient()
        
        # Transcribe the audio file
        logger.info(f"Transcribing audio file: {args.file}")
        transcript_data = elevenlabs_client.transcribe_audio(
            audio_file_path=args.file,
            model_id=args.model,
            diarize=not args.no_diarize,
            language_code=args.language,
            tag_audio_events=not args.no_events,
            num_speakers=args.speakers,
            timestamps_granularity=args.timestamps
        )
        
        if transcript_data is None:
            logger.error("Transcription failed")
            return 1
        
        # Save the raw transcript data to a JSON file
        json_output_path = os.path.join(args.output_dir, f"{file_basename}_transcript.json")
        if elevenlabs_client.save_transcript_to_file(transcript_data, json_output_path):
            logger.info(f"Raw transcript data saved to {json_output_path}")
        else:
            logger.warning("Failed to save raw transcript data")
        
        # Extract and save the cleaned transcript with speaker annotations
        logger.info("Extracting cleaned transcript with speaker annotations")
        cleaned_transcript = elevenlabs_client.extract_cleaned_transcript_with_speakers(transcript_data)
        
        if cleaned_transcript:
            # Clean up punctuation
            logger.info("Cleaning up punctuation")
            cleaned_transcript = elevenlabs_client.clean_punctuation(cleaned_transcript)
            
            # Save the cleaned transcript
            cleaned_output_path = os.path.join(args.output_dir, f"{file_basename}_transcript_cleaned.txt")
            if elevenlabs_client.save_cleaned_transcript(cleaned_transcript, cleaned_output_path):
                logger.info(f"Cleaned transcript saved to {cleaned_output_path}")
            else:
                logger.warning("Failed to save cleaned transcript")
                
            # Print a preview of the cleaned transcript
            logger.info("Transcript preview (first 500 characters):")
            logger.info("-------------------")
            logger.info(cleaned_transcript[:500] + ("..." if len(cleaned_transcript) > 500 else ""))
            logger.info("-------------------")
        else:
            logger.warning("Failed to extract cleaned transcript")
        
        # Print success message
        logger.info("\n===== Processing complete! =====")
        logger.info(f"Output files are available in {args.output_dir}")
        return 0
    
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        logger.debug(traceback.format_exc())
        return 1

if __name__ == "__main__":
    sys.exit(main()) 