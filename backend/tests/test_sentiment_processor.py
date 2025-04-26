#!/usr/bin/env python3
"""
Test script for the sentiment processor.
This script can be used to test the sentiment processor in isolation.
"""

import os
import sys
import argparse
import logging
import json
import matplotlib.pyplot as plt

# Add parent directory to path to allow importing modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import processor
from processors.sentiment_processor import SentimentProcessor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """
    Main function to test the sentiment processor.
    """
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Test the sentiment processor")
    parser.add_argument("--file", "-f", help="Path to the predictions JSON file")
    parser.add_argument("--output-dir", "-o", default="results", help="Directory to save output files")
    parser.add_argument("--top-n", "-n", type=int, default=15, help="Number of top sentiments to include in visualizations")
    parser.add_argument("--debug", "-d", action="store_true", help="Enable debug logging")
    args = parser.parse_args()
    
    # Set debug logging if requested
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.setLevel(logging.DEBUG)
        # Also set debug level for sentiment processor logger
        logging.getLogger('sentiment_processor').setLevel(logging.DEBUG)
        logger.debug("Debug logging enabled")
    
    # Print start message
    logger.info("===== Sentiment Processor Test =====")
    logger.info(f"Output directory: {args.output_dir}")
    
    # Check if file exists
    if not args.file:
        # If no file specified, try to find a predictions file in the results directory
        if os.path.exists(args.output_dir):
            logger.info(f"Searching for prediction files in {args.output_dir}")
            prediction_files = [f for f in os.listdir(args.output_dir) if f.endswith("_predictions.json")]
            
            if prediction_files:
                prediction_files.sort(key=lambda x: os.path.getmtime(os.path.join(args.output_dir, x)), reverse=True)
                args.file = os.path.join(args.output_dir, prediction_files[0])
                logger.info(f"Found {len(prediction_files)} prediction files. Using most recent: {args.file}")
            else:
                logger.error("No predictions files found in results directory")
                return 1
        else:
            logger.error("No file specified and results directory does not exist")
            return 1
    
    # Create output directory if it doesn't exist
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Get file basename
    file_basename = os.path.splitext(os.path.basename(args.file))[0]
    logger.info(f"Processing file with basename: {file_basename}")
    
    try:
        # Log file stats
        file_size_mb = os.path.getsize(args.file) / (1024 * 1024)
        logger.info(f"File size: {file_size_mb:.2f} MB")
        
        # Initialize the sentiment processor
        logger.info(f"Initializing sentiment processor with file: {args.file}")
        processor = SentimentProcessor(args.file)
        
        # Process the data
        logger.info("Processing sentiment data...")
        processed_data = processor.process_sentiment_data()
        
        if processed_data is None:
            logger.error("Error processing data - no data was returned")
            return 1
        
        # Log some information about the processed data
        logger.info(f"Processed {len(processed_data)} segments")
        speakers = processed_data['speaker_id'].unique()
        logger.info(f"Found {len(speakers)} speakers: {', '.join(str(s) for s in speakers)}")
        
        # Save the processed data
        output_csv = os.path.join(args.output_dir, f"{file_basename}_processed_data.csv")
        logger.info(f"Saving processed data to: {output_csv}")
        if processor.save_processed_data(output_csv):
            logger.info(f"Successfully saved processed data to {output_csv}")
        else:
            logger.error(f"Failed to save processed data to {output_csv}")
        
        # Log info about the top sentiments
        top_sentiments = processor.top_sentiments[:args.top_n]
        logger.info(f"Top {len(top_sentiments)} sentiments: {', '.join(top_sentiments)}")
        
        # Create the sentiment evolution plot
        output_plot = os.path.join(args.output_dir, f"{file_basename}_sentiment_evolution.png")
        logger.info(f"Creating sentiment evolution plot: {output_plot}")
        if processor.plot_sentiment_evolution(output_plot, top_n_sentiments=args.top_n):
            logger.info(f"Successfully created sentiment evolution plot: {output_plot}")
        else:
            logger.error(f"Failed to create sentiment evolution plot: {output_plot}")
        
        logger.info("===== Processing complete! =====")
        return 0
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        logger.debug(traceback.format_exc())
        return 1

if __name__ == "__main__":
    sys.exit(main()) 