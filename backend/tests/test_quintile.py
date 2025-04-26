#!/usr/bin/env python
"""
Test script for the quintile analysis functionality in the sentiment processor.
"""

import os
import sys
import json
import logging
from processors.sentiment_processor import SentimentProcessor

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    try:
        # Define paths
        predictions_file = "outputs/hume/job_d13f8cb6-9f79-4bd2-9d14-a2780d83cdaa_predictions.json"
        output_dir = "outputs/processed"
        
        if not os.path.exists(predictions_file):
            logger.error(f"Predictions file not found: {predictions_file}")
            return False
            
        # Initialize the processor
        logger.info(f"Initializing sentiment processor with predictions file: {predictions_file}")
        processor = SentimentProcessor(predictions_file)
        
        # Process the sentiment data
        logger.info("Processing sentiment data...")
        df = processor.process_sentiment_data()
        if df is None:
            logger.error("Failed to process sentiment data")
            return False
            
        # Save the processed data
        processed_data_file = os.path.join(output_dir, "sample_audio_processed_data.csv")
        logger.info(f"Saving processed data to {processed_data_file}")
        processor.save_processed_data(processed_data_file)
        
        # Save the quintile analysis
        quintile_analysis_file = os.path.join(output_dir, "sample_audio_quintile_analysis.json")
        logger.info(f"Saving quintile analysis to {quintile_analysis_file}")
        if processor.save_quintile_analysis(quintile_analysis_file):
            logger.info("Quintile analysis saved successfully")
        else:
            logger.error("Failed to save quintile analysis")
            return False
            
        # Generate visualization
        visualization_file = os.path.join(output_dir, "sample_audio_sentiment_evolution.png")
        logger.info(f"Generating sentiment evolution visualization to {visualization_file}")
        if processor.plot_sentiment_evolution(visualization_file):
            logger.info("Visualization created successfully")
        else:
            logger.error("Failed to create visualization")
            
        # Print the quintile analysis
        quintile_analysis = processor.get_quintile_analysis()
        logger.info("Quintile analysis results:")
        logger.info(f"Conversation length: {quintile_analysis.get('conversation_length_seconds', 0):.2f} seconds")
        
        # Print the top sentiment for each speaker and quintile
        for speaker, quintiles in quintile_analysis.get("speakers", {}).items():
            logger.info(f"\nSpeaker: {speaker}")
            for quintile, data in quintiles.items():
                logger.info(f"  {quintile}: {data.get('time_range')} - Dominant emotion: {data.get('dominant_emotion')} ({data.get('emotion_score', 0):.3f})")
        
        logger.info("\nQuintile analysis completed successfully!")
        return True
    
    except Exception as e:
        logger.error(f"Error in test script: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return False

if __name__ == "__main__":
    main() 