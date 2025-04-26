#!/usr/bin/env python
"""
Test script for processing quintile emotions using Claude.
"""

import os
import sys
import json
import logging
from processors.claude.processor import ClaudeProcessor

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    try:
        # Define paths
        quintile_analysis_file = "outputs/processed/sample_audio_2_quintile_analysis.json"
        output_dir = "outputs/claude"
        
        if not os.path.exists(quintile_analysis_file):
            logger.error(f"Quintile analysis file not found: {quintile_analysis_file}")
            return False
            
        # Initialize the Claude processor
        logger.info(f"Initializing Claude processor")
        claude_processor = ClaudeProcessor()
        
        # Process the quintile emotions
        logger.info(f"Processing quintile emotions for: {quintile_analysis_file}")
        emotions_result = claude_processor.process_quintile_emotions(
            quintile_analysis_file=quintile_analysis_file,
            output_dir=output_dir
        )
        
        if emotions_result:
            logger.info("Emotions analysis completed successfully")
            logger.info(f"Emotions analysis file: {emotions_result.get('emotions_analysis_file')}")
            
            # Print some of the emotions data
            emotions_data = emotions_result.get('emotions_data')
            if emotions_data and isinstance(emotions_data, list):
                logger.info(f"Found {len(emotions_data)} emotion entries")
                
                # Print the first few entries
                for i, entry in enumerate(emotions_data[:5]):
                    logger.info(f"Entry {i+1}: Speaker: {entry.get('speaker')}, Quintile: {entry.get('quintile')}, Emotion: {entry.get('main_emotion')}")
            else:
                logger.error("No valid emotions data found in the result")
            
            return True
        else:
            logger.error("Failed to process quintile emotions")
            return False
    
    except Exception as e:
        logger.error(f"Error in test script: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return False

if __name__ == "__main__":
    main() 