#!/usr/bin/env python3
"""
Main entry point for the audio analysis pipeline.
This script provides a command-line interface to the orchestrator.
"""

import os
import sys
import argparse
import logging
from orchestrator.orchestrator import AudioOrchestrator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('audio_analysis.log', mode='a')
    ]
)
logger = logging.getLogger(__name__)

def parse_arguments():
    """Parse command line arguments for the main script."""
    parser = argparse.ArgumentParser(description="Audio Analysis Pipeline")
    
    # Input and output directories
    parser.add_argument("--input-dir", type=str, default="input_files",
                        help="Directory containing input audio files")
    parser.add_argument("--hume-output-dir", type=str, default="outputs/hume",
                        help="Directory to save Hume AI output files")
    parser.add_argument("--elevenlabs-output-dir", type=str, default="outputs/elevenlabs",
                        help="Directory to save ElevenLabs output files")
    parser.add_argument("--processed-output-dir", type=str, default="outputs/processed",
                        help="Directory to save processed output files")
    parser.add_argument("--claude-output-dir", type=str, default="outputs/claude",
                        help="Directory to save Claude AI output files")
    
    # Processing options
    parser.add_argument("--force", action="store_true",
                        help="Force reprocessing even if results exist")
    parser.add_argument("--skip-visualization", action="store_true",
                        help="Skip visualization generation")
    parser.add_argument("--job-id", type=str, default=None,
                        help="Process a specific job ID")
    parser.add_argument("--file", type=str, default=None,
                        help="Process a specific file")
    parser.add_argument("--transcript", type=str, default=None,
                        help="Process a specific transcript file with Claude (bypasses audio processing)")
    parser.add_argument("--file-pattern", type=str, default="*.*",
                        help="Pattern to match files to process")
    
    # Service selection
    parser.add_argument("--skip-hume", action="store_true",
                        help="Skip Hume AI processing")
    parser.add_argument("--skip-elevenlabs", action="store_true",
                        help="Skip ElevenLabs processing")
    parser.add_argument("--skip-claude", action="store_true",
                        help="Skip Claude AI analysis")
    parser.add_argument("--elevenlabs-only", action="store_true",
                        help="Only run ElevenLabs processing (shortcut for --skip-hume)")
    parser.add_argument("--hume-only", action="store_true",
                        help="Only run Hume AI processing (shortcut for --skip-elevenlabs)")
    parser.add_argument("--claude-only", action="store_true",
                        help="Only run Claude AI analysis (requires a transcript file)")
    
    # Debug options
    parser.add_argument("--debug", action="store_true",
                        help="Enable debug logging")
    
    return parser.parse_args()

def main():
    """Main entry point for the audio analysis pipeline."""
    args = parse_arguments()
    
    # Set debug logging if requested
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        for handler in logging.getLogger().handlers:
            handler.setLevel(logging.DEBUG)
        logger.debug("Debug logging enabled")
    
    # Handle shortcut arguments
    if args.elevenlabs_only:
        args.skip_hume = True
        args.skip_claude = True
    if args.hume_only:
        args.skip_elevenlabs = True
        args.skip_claude = True
    if args.claude_only:
        args.skip_hume = True
        args.skip_elevenlabs = True
    
    try:
        # Create orchestrator
        orchestrator = AudioOrchestrator(
            input_dir=args.input_dir,
            hume_output_dir=args.hume_output_dir,
            elevenlabs_output_dir=args.elevenlabs_output_dir,
            processed_output_dir=args.processed_output_dir,
            claude_output_dir=args.claude_output_dir
        )
        
        # Process transcript directly with Claude if specified
        if args.transcript:
            if not os.path.exists(args.transcript):
                logger.error(f"Transcript file not found: {args.transcript}")
                return
                
            logger.info(f"Processing transcript with Claude: {args.transcript}")
            
            # Use the orchestrator to process the transcript 
            # This ensures that quintile analysis is done before Claude processing
            claude_result = orchestrator.process_transcript_with_claude(
                transcript_file=args.transcript,
                force_reprocess=args.force
            )
            
            if claude_result:
                logger.info("Processing completed successfully")
                
                # Log the Claude-specific results
                if "claude_response_file" in claude_result:
                    logger.info(f"Claude response file: {claude_result.get('claude_response_file')}")
                if "claude_structured_json_file" in claude_result:
                    logger.info(f"Claude structured JSON file: {claude_result.get('claude_structured_json_file')}")
                if "claude_summary_file" in claude_result:
                    logger.info(f"Summary file: {claude_result.get('claude_summary_file')}")
                if "claude_sentiment_file" in claude_result:
                    logger.info(f"Sentiment file: {claude_result.get('claude_sentiment_file')}")
                
                # Log quintile analysis results if available
                if "quintile_analysis" in claude_result:
                    logger.info(f"Quintile analysis file: {claude_result.get('quintile_analysis')}")
                if "sentiment_evolution_plot" in claude_result:
                    logger.info(f"Sentiment evolution plot: {claude_result.get('sentiment_evolution_plot')}")
                
                # Skip printing the full data structures when logging other results
                skip_keys = ["summary_data", "sentiment_data"]
                for key, value in claude_result.items():
                    if key in skip_keys:
                        continue
                    if key not in ["claude_response_file", "claude_structured_json_file", 
                                  "claude_summary_file", "claude_sentiment_file",
                                  "quintile_analysis", "sentiment_evolution_plot"]:
                        logger.info(f"  {key}: {value}")
            else:
                logger.error("Processing failed")
            
            return
        
        # Process based on provided arguments
        if args.job_id:
            logger.info(f"Processing existing job ID: {args.job_id}")
            # Find the file associated with this job ID
            found = False
            for filename, job_id in orchestrator.job_mappings.items():
                if job_id == args.job_id:
                    audio_file = os.path.join(args.input_dir, filename)
                    if os.path.exists(audio_file):
                        logger.info(f"Found file for job ID {args.job_id}: {filename}")
                        result = orchestrator.process_file(
                            audio_file=audio_file,
                            job_id=args.job_id,
                            force_reprocess=args.force,
                            skip_visualization=args.skip_visualization,
                            skip_claude=args.skip_claude,
                            skip_hume=args.skip_hume,
                            skip_elevenlabs=args.skip_elevenlabs
                        )
                        found = True
                        if result:
                            logger.info(f"Processing completed for job ID {args.job_id}")
                            for key, value in result.items():
                                logger.info(f"  {key}: {value}")
                        else:
                            logger.error(f"Processing failed for job ID {args.job_id}")
                        break
            
            if not found:
                logger.error(f"Could not find file for job ID {args.job_id} in job mappings.")
        
        elif args.file:
            logger.info(f"Processing specific file: {args.file}")
            audio_file = os.path.join(args.input_dir, args.file) if not os.path.isabs(args.file) else args.file
            if not os.path.exists(audio_file):
                logger.error(f"File not found: {audio_file}")
                return
            
            result = orchestrator.process_file(
                audio_file=audio_file, 
                force_reprocess=args.force,
                skip_visualization=args.skip_visualization,
                skip_claude=args.skip_claude,
                skip_hume=args.skip_hume,
                skip_elevenlabs=args.skip_elevenlabs
            )
            
            if result:
                logger.info(f"Processing completed for {args.file}")
                for key, value in result.items():
                    logger.info(f"  {key}: {value}")
            else:
                logger.error(f"Processing failed for {args.file}")
        
        else:
            logger.info("Processing all audio files")
            results = orchestrator.process_all_files(
                file_pattern=args.file_pattern,
                force_reprocess=args.force,
                skip_visualization=args.skip_visualization,
                skip_claude=args.skip_claude,
                skip_hume=args.skip_hume,
                skip_elevenlabs=args.skip_elevenlabs
            )
            
            logger.info(f"Processed {len(results)} files")
            for filename, result in results.items():
                if result:
                    logger.info(f"Processing successful for {filename}")
                else:
                    logger.error(f"Processing failed for {filename}")
    
    except Exception as e:
        logger.error(f"Unexpected error in main function: {str(e)}")
        if args.debug:
            import traceback
            logger.debug(traceback.format_exc())

if __name__ == "__main__":
    main() 