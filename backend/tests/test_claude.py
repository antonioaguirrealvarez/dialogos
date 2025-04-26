#!/usr/bin/env python3
"""
Test script for Claude processing.
This script can be used to test the Claude processor in isolation.
"""

import os
import sys
import argparse
import logging
import json
import traceback

# Add parent directory to path to allow importing modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import processor
from processors.claude.processor import ClaudeProcessor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('claude_test.log', mode='a')
    ]
)
logger = logging.getLogger(__name__)

def main():
    """
    Main function to test the Claude processor for transcript analysis.
    """
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Test the Claude processor for transcript analysis")
    parser.add_argument("--file", "-f", required=True, help="Path to the transcript text file")
    parser.add_argument("--output-dir", "-o", default="outputs/claude", help="Directory to save output files")
    parser.add_argument("--force", action="store_true", help="Force reprocessing even if results exist")
    parser.add_argument("--debug", "-d", action="store_true", help="Enable debug logging")
    args = parser.parse_args()
    
    # Set debug logging if requested
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.setLevel(logging.DEBUG)
        logger.debug("Debug logging enabled")
    
    # Print start message
    logger.info("===== Claude Transcript Analysis Test =====")
    logger.info(f"Input file: {args.file}")
    logger.info(f"Output directory: {args.output_dir}")
    
    # Check if file exists
    if not os.path.exists(args.file):
        logger.error(f"Error: File {args.file} does not exist")
        return 1
    
    # Create output directory if it doesn't exist
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Get file basename without extension
    file_basename = os.path.splitext(os.path.basename(args.file))[0]
    logger.info(f"Processing file with basename: {file_basename}")
    
    try:
        # Initialize the Claude processor
        logger.info("Initializing Claude processor")
        processor = ClaudeProcessor()
        
        # Process the transcript
        logger.info(f"Processing transcript: {args.file}")
        result = processor.process_transcript(
            transcript_file=args.file,
            output_dir=args.output_dir,
            force_reprocess=args.force
        )
        
        if not result:
            logger.error("Processing failed")
            return 1
        
        # Log results
        logger.info("Processing successful!")
        logger.info(f"Summary file: {result.get('summary_file')}")
        logger.info(f"Sentiment file: {result.get('sentiment_file')}")
        logger.info(f"Share of voice chart: {result.get('share_of_voice_chart')}")
        logger.info(f"Sentiment chart: {result.get('sentiment_chart')}")
        
        # Print a preview of the summary
        if 'summary_data' in result and 'summary_text' in result['summary_data']:
            summary_preview = result['summary_data']['summary_text'][:500] + "..." if len(result['summary_data']['summary_text']) > 500 else result['summary_data']['summary_text']
            logger.info("\nSummary preview:")
            logger.info("-------------------")
            logger.info(summary_preview)
            logger.info("-------------------")
        
        logger.info("\n===== Processing complete! =====")
        logger.info(f"Output files are available in {args.output_dir}")
        return 0
    
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        logger.debug(traceback.format_exc())
        return 1

if __name__ == "__main__":
    sys.exit(main()) 