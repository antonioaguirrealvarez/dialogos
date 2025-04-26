#!/usr/bin/env python3
import os
import json
import argparse
import glob
import time
import logging
import sys
import traceback
from datetime import datetime

# Import our modules with updated paths using traditional import paths
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from processors.sentiment_processor import SentimentProcessor
from processors.claude.processor import ClaudeProcessor
from clients.hume.client import HumeClient
from clients.elevenlabs.client import ElevenLabsClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('orchestrator/orchestrator.log', mode='a')
    ]
)
logger = logging.getLogger(__name__)

class AudioOrchestrator:
    def __init__(self, input_dir="input_files", hume_output_dir="outputs/hume", elevenlabs_output_dir="outputs/elevenlabs", processed_output_dir="outputs/processed", claude_output_dir="outputs/claude", job_id_file="job_id.txt"):
        """
        Initialize the Audio Orchestrator.
        
        Args:
            input_dir: Directory containing input audio files
            hume_output_dir: Directory to save Hume results
            elevenlabs_output_dir: Directory to save ElevenLabs results
            processed_output_dir: Directory to save processed results
            claude_output_dir: Directory to save Claude AI results
            job_id_file: File to store job IDs
        """
        self.input_dir = input_dir
        self.hume_output_dir = hume_output_dir
        self.elevenlabs_output_dir = elevenlabs_output_dir
        self.processed_output_dir = processed_output_dir
        self.claude_output_dir = claude_output_dir
        self.job_id_file = job_id_file
        self.job_mappings_file = os.path.join(hume_output_dir, "job_mappings.json")
        
        # Initialize job mappings
        self.job_mappings = self._load_job_mappings()
        
        # Create output directories if they don't exist
        try:
            os.makedirs(hume_output_dir, exist_ok=True)
            os.makedirs(elevenlabs_output_dir, exist_ok=True)
            os.makedirs(processed_output_dir, exist_ok=True)
            os.makedirs(claude_output_dir, exist_ok=True)
            logger.info(f"Output directories initialized")
        except Exception as e:
            logger.error(f"Failed to create output directories: {str(e)}")
            raise
    
    def _load_job_mappings(self):
        """
        Load job mappings from file.
        
        Returns:
            dict: Dictionary mapping audio file names to job IDs
        """
        if os.path.exists(self.job_mappings_file):
            try:
                with open(self.job_mappings_file, 'r') as f:
                    mappings = json.load(f)
                logger.info(f"Loaded {len(mappings)} job mappings from {self.job_mappings_file}")
                return mappings
            except json.JSONDecodeError:
                logger.error(f"Error loading job mappings from {self.job_mappings_file}: Invalid JSON format")
                return {}
            except Exception as e:
                logger.error(f"Error loading job mappings: {str(e)}")
                return {}
        logger.info(f"No existing job mappings file found at {self.job_mappings_file}")
        return {}
    
    def _save_job_mappings(self):
        """
        Save job mappings to file.
        """
        try:
            with open(self.job_mappings_file, 'w') as f:
                json.dump(self.job_mappings, f, indent=2)
            logger.info(f"Job mappings saved to {self.job_mappings_file}")
        except Exception as e:
            logger.error(f"Error saving job mappings: {str(e)}")
    
    def process_transcript_with_claude(self, transcript_file, force_reprocess=False):
        """
        Process a transcript file directly with Claude, bypassing the audio processing steps.
        
        Args:
            transcript_file: Path to the transcript file
            force_reprocess: Force reprocessing even if results exist
            
        Returns:
            dict: Results of Claude processing
        """
        try:
            if not os.path.exists(transcript_file):
                logger.error(f"Transcript file not found: {transcript_file}")
                return None
                
            logger.info(f"Processing transcript with Claude: {transcript_file}")
            
            # Get file basename without extension
            file_basename = os.path.splitext(os.path.basename(transcript_file))[0]
            # Remove _transcript_cleaned suffix if present
            if file_basename.endswith("_transcript_cleaned"):
                file_basename = file_basename.replace("_transcript_cleaned", "")
            
            result = {}
            
            # Check if we have Hume predictions for this file
            # This would allow us to perform quintile analysis before Claude processing
            predictions_pattern = os.path.join(self.hume_output_dir, f"*{file_basename}*.json")
            predictions_files = glob.glob(predictions_pattern)
            
            # Also check for job ID pattern
            job_id_pattern = os.path.join(self.hume_output_dir, "job_*_predictions.json")
            job_files = glob.glob(job_id_pattern)
            
            # Look for matching predictions files
            matching_prediction_file = None
            
            # First check direct filename matches
            for pred_file in predictions_files:
                logger.info(f"Found potential matching predictions file: {pred_file}")
                matching_prediction_file = pred_file
                break
                
            # If no direct match found, look through job files to see if any contain this audio
            if not matching_prediction_file:
                logger.info(f"No direct match found, checking job files")
                
                for job_file in job_files:
                    logger.info(f"Checking job file: {job_file}")
                    
                    try:
                        # Read the job file
                        with open(job_file, 'r') as f:
                            job_data = json.load(f)
                            
                        # Check if this job file mentions our file
                        if 'media' in job_data and 'source' in job_data['media']:
                            source_file = os.path.basename(job_data['media']['source'])
                            
                            if file_basename in source_file:
                                matching_prediction_file = job_file
                                logger.info(f"Found potential matching job file: {matching_prediction_file}")
                                break
                    except Exception:
                        # Skip files we can't read
                        continue
            
            # Perform quintile analysis if we have a predictions file
            if matching_prediction_file and os.path.exists(matching_prediction_file):
                logger.info(f"Performing quintile analysis before Claude processing")
                
                # Define quintile analysis file path
                quintile_analysis_file = os.path.join(self.processed_output_dir, f"{file_basename}_quintile_analysis.json")
                processed_data_file = os.path.join(self.processed_output_dir, f"{file_basename}_processed_data.csv")
                sentiment_evolution_plot_file = os.path.join(self.processed_output_dir, f"{file_basename}_sentiment_evolution.png")
                
                # Process the sentiment data
                try:
                    processor = SentimentProcessor(matching_prediction_file)
                    processed_data = processor.process_sentiment_data()
                    
                    if processed_data is not None:
                        # Save processed data
                        processor.save_processed_data(processed_data_file)
                        
                        # Save quintile analysis
                        logger.info(f"Creating quintile analysis for {file_basename}")
                        processor.save_quintile_analysis(quintile_analysis_file)
                        
                        # Create visualization if it doesn't exist
                        if not os.path.exists(sentiment_evolution_plot_file):
                            logger.info(f"Creating sentiment evolution visualization for {file_basename}")
                            processor.plot_sentiment_evolution(sentiment_evolution_plot_file)
                        
                        # Add to results
                        result.update({
                            "hume_predictions": matching_prediction_file,
                            "processed_data": processed_data_file,
                            "quintile_analysis": quintile_analysis_file,
                            "sentiment_evolution_plot": sentiment_evolution_plot_file
                        })
                        
                        logger.info(f"Quintile analysis completed before Claude processing")
                        
                        # Now process the quintile analysis to extract emotions using Claude and prompt_3.txt
                        logger.info(f"Processing quintile analysis for emotions with Claude")
                        claude_processor = ClaudeProcessor()
                        emotions_result = claude_processor.process_quintile_emotions(
                            quintile_analysis_file=quintile_analysis_file,
                            output_dir=self.claude_output_dir
                        )
                        
                        if emotions_result:
                            logger.info(f"Emotions analysis completed successfully")
                            logger.info(f"Emotions analysis file: {emotions_result.get('emotions_analysis_file')}")
                            result.update({
                                "emotions_analysis_file": emotions_result.get('emotions_analysis_file'),
                                "emotions_data": emotions_result.get('emotions_data')
                            })
                        else:
                            logger.warning(f"Failed to process quintile analysis for emotions")
                    else:
                        logger.warning(f"Could not process sentiment data from matching predictions file")
                except Exception as e:
                    logger.error(f"Error in quintile analysis: {str(e)}")
                    logger.debug(traceback.format_exc())
            
            # Process with Claude (now as the final step)
            claude_processor = ClaudeProcessor()
            claude_result = claude_processor.process_transcript(
                transcript_file=transcript_file,
                output_dir=self.claude_output_dir,
                force_reprocess=force_reprocess
            )
            
            if claude_result:
                # Log all the output files that were created
                logger.info(f"Claude processing completed for {file_basename}")
                logger.info(f"Claude response file: {claude_result.get('claude_response_file')}")
                logger.info(f"Claude structured JSON file: {claude_result.get('claude_structured_json_file')}")
                logger.info(f"Summary file: {claude_result.get('summary_file')}")
                logger.info(f"Sentiment file: {claude_result.get('sentiment_file')}")
                
                # Add Claude results to the overall results
                result.update({
                    "claude_response_file": claude_result.get('claude_response_file'),
                    "claude_structured_json_file": claude_result.get('claude_structured_json_file'),
                    "claude_summary_file": claude_result.get('summary_file'),
                    "claude_sentiment_file": claude_result.get('sentiment_file'),
                    "claude_data": claude_result.get('claude_data'),
                    "structured_data": claude_result.get('structured_data')
                })
            
            return result
            
        except Exception as e:
            logger.error(f"Error in process_transcript_with_claude: {str(e)}")
            logger.debug(traceback.format_exc())
            return None
    
    def process_file(self, audio_file, force_reprocess=False, skip_visualization=False, skip_claude=False, job_id=None, max_wait_time=600, skip_hume=False, skip_elevenlabs=False):
        """
        Process a single audio file.
        
        Args:
            audio_file: Path to the audio file
            force_reprocess: Force reprocessing even if results exist
            skip_visualization: Skip visualization step
            skip_claude: Skip Claude AI analysis
            job_id: Use a specific job ID (overrides looking up from mappings)
            max_wait_time: Maximum time to wait for job completion in seconds
            skip_hume: Skip Hume AI processing
            skip_elevenlabs: Skip ElevenLabs processing
            
        Returns:
            success: True if successful, False otherwise
        """
        try:
            # Get file basename without extension
            base_filename = os.path.basename(audio_file)
            file_basename = os.path.splitext(base_filename)[0]
            
            logger.info(f"Processing file: {base_filename}")
            
            result = {}
            cleaned_transcript_path = None
            
            # Process with ElevenLabs if not skipped
            if not skip_elevenlabs:
                try:
                    elevenlabs_client = ElevenLabsClient()
                    elevenlabs_result = elevenlabs_client.transcribe_audio(
                        audio_file_path=audio_file,
                        force_reprocess=force_reprocess,
                        output_dir=self.elevenlabs_output_dir
                    )
                    
                    if elevenlabs_result and len(elevenlabs_result) >= 3:
                        transcript_data, cleaned_transcript, json_path = elevenlabs_result[:3]
                        result["elevenlabs_transcript"] = cleaned_transcript
                        result["elevenlabs_transcript_path"] = json_path
                        cleaned_transcript_path = os.path.join(self.elevenlabs_output_dir, f"{file_basename}_transcript_cleaned.txt")
                        logger.info(f"ElevenLabs transcription completed for {file_basename}")
                    else:
                        logger.warning(f"ElevenLabs transcription failed or returned incomplete data for {file_basename}")
                except Exception as e:
                    logger.error(f"Error during ElevenLabs processing: {str(e)}")
                    logger.debug(traceback.format_exc())
            
            # Skip Hume processing if requested
            if skip_hume:
                logger.info("Skipping Hume AI processing as requested")
                
                # If we have a transcript, we can still do Claude processing at the end
                if cleaned_transcript_path and os.path.exists(cleaned_transcript_path) and not skip_claude:
                    # Claude processing will be done at the end of the function
                    pass
                else:
                    return result
            
            # Initialize the Hume client
            hume_client = HumeClient()
            
            # Check if we have a job ID for this file
            if job_id:
                logger.info(f"Using provided job ID: {job_id}")
            elif file_basename in self.job_mappings:
                job_id = self.job_mappings[file_basename]
                logger.info(f"Found existing job ID for {file_basename}: {job_id}")
            
            # Check if predictions file exists
            predictions_file = os.path.join(self.hume_output_dir, f"job_{job_id}_predictions.json" if job_id else f"{file_basename}_predictions.json")
            processed_data_file = os.path.join(self.processed_output_dir, f"{file_basename}_processed_data.csv")
            sentiment_evolution_plot_file = os.path.join(self.processed_output_dir, f"{file_basename}_sentiment_evolution.png")
            
            # Define quintile analysis file path
            quintile_analysis_file = os.path.join(self.processed_output_dir, f"{file_basename}_quintile_analysis.json")
            
            # Check if we need to process the file
            if not force_reprocess and os.path.exists(predictions_file) and os.path.exists(processed_data_file):
                logger.info(f"Results for {file_basename} already exist. Use --force to reprocess.")
                
                # Create a new processor with the existing data for visualization or quintile analysis
                processor = SentimentProcessor(predictions_file)
                processor.process_sentiment_data()
                
                # If visualization file doesn't exist, we can still do that part
                if not os.path.exists(sentiment_evolution_plot_file) and not skip_visualization:
                    logger.info(f"Creating visualizations for {file_basename}")
                    try:
                        # Create visualization
                        processor.plot_sentiment_evolution(sentiment_evolution_plot_file)
                    except Exception as e:
                        logger.error(f"Error creating visualizations: {str(e)}")
                        logger.debug(traceback.format_exc())
                
                # Save quintile analysis (ensure this happens regardless of visualization)
                if not os.path.exists(quintile_analysis_file) or force_reprocess:
                    processor.save_quintile_analysis(quintile_analysis_file)
                
                result["hume_job_id"] = job_id
                result["hume_predictions_file"] = predictions_file
                result["processed_data_file"] = processed_data_file
                
                # Update result with the file paths
                result.update({
                    "hume_predictions": predictions_file,
                    "processed_data": processed_data_file,
                    "quintile_analysis": quintile_analysis_file
                })
                if not skip_visualization:
                    result["sentiment_evolution_plot"] = sentiment_evolution_plot_file
                
                # Process with Claude as the final step
                if not skip_claude and cleaned_transcript_path and os.path.exists(cleaned_transcript_path):
                    claude_result = self._process_with_claude(cleaned_transcript_path, file_basename, force_reprocess)
                    if claude_result:
                        result.update(claude_result)
                
                return result
            
            # If we don't have a job ID, submit a new job
            if not job_id:
                logger.info(f"Submitting new job for {file_basename}")
                job_id = hume_client.submit_job(audio_file)
                
                if not job_id:
                    logger.error(f"Error submitting job for {file_basename}")
                    return result
                
                # Save the job ID
                self.job_mappings[file_basename] = job_id
                self._save_job_mappings()
                
                # Also save to job_id.txt for backwards compatibility
                try:
                    with open(self.job_id_file, 'w') as f:
                        f.write(job_id)
                    logger.info(f"Job ID saved to {self.job_id_file}")
                except Exception as e:
                    logger.error(f"Error saving job ID to file: {str(e)}")
            
            # Wait for job completion with timeout
            max_attempts = max_wait_time // 5  # Check every 5 seconds
            logger.info(f"Waiting for job completion (max {max_wait_time} seconds)")
            if not hume_client.wait_for_job_completion(job_id, max_attempts=max_attempts, check_interval=5):
                logger.error(f"Job for {file_basename} did not complete successfully within timeout")
                logger.info(f"Job ID: {job_id} - You can check the status later using: python orchestrator/orchestrator.py --job-id {job_id}")
                result["hume_job_id"] = job_id
                return result
            
            # Get predictions - this is the only file we need now
            logger.info(f"Retrieving predictions for job ID: {job_id}")
            predictions = hume_client.get_job_predictions(job_id)
            if not predictions:
                logger.error(f"Error getting predictions for {file_basename}")
                result["hume_job_id"] = job_id
                return result
            
            # Update predictions file to include job_id in the filename
            predictions_file = os.path.join(self.hume_output_dir, f"job_{job_id}_predictions.json")
            
            # Save predictions to file
            if not hume_client.save_predictions_to_file(predictions, predictions_file):
                logger.error(f"Error saving predictions for {file_basename}")
                result["hume_job_id"] = job_id
                return result
            
            # Process the data using our new processor
            logger.info(f"Processing predictions data for {file_basename}")
            processor = SentimentProcessor(predictions_file)
            processed_data = processor.process_sentiment_data()
            
            if processed_data is None:
                logger.error(f"Error processing data for {file_basename}")
                result["hume_job_id"] = job_id
                result["hume_predictions_file"] = predictions_file
                return result
            
            # Save processed data
            if not processor.save_processed_data(processed_data_file):
                logger.error(f"Error saving processed data for {file_basename}")
                result["hume_job_id"] = job_id
                result["hume_predictions_file"] = predictions_file
                return result
            
            # Save quintile analysis - MOVED EARLIER IN THE PIPELINE
            logger.info(f"Creating quintile analysis for {file_basename}")
            processor.save_quintile_analysis(quintile_analysis_file)
            
            # Create visualization
            if not skip_visualization:
                logger.info(f"Creating sentiment evolution visualization for {file_basename}")
                try:
                    processor.plot_sentiment_evolution(sentiment_evolution_plot_file)
                except Exception as e:
                    logger.error(f"Error creating visualization: {str(e)}")
                    logger.debug(traceback.format_exc())
            
            # Update result with the file paths
            result.update({
                "hume_job_id": job_id,
                "hume_predictions_file": predictions_file,
                "hume_predictions": predictions_file,
                "processed_data_file": processed_data_file,
                "processed_data": processed_data_file,
                "quintile_analysis": quintile_analysis_file
            })
            if not skip_visualization:
                result["sentiment_evolution_plot"] = sentiment_evolution_plot_file
                result["visualization_file"] = sentiment_evolution_plot_file
            
            # Process with Claude as the final step (after quintile analysis and visualization)
            if not skip_claude and cleaned_transcript_path and os.path.exists(cleaned_transcript_path):
                claude_result = self._process_with_claude(cleaned_transcript_path, file_basename, force_reprocess)
                if claude_result:
                    result.update(claude_result)
            
            return result
        except Exception as e:
            logger.error(f"Error processing file {audio_file}: {str(e)}")
            logger.debug(traceback.format_exc())
            return {}
    
    def _process_with_claude(self, transcript_file, file_basename, force_reprocess=False):
        """
        Process a transcript with Claude AI.
        
        Args:
            transcript_file: Path to the transcript file
            file_basename: The base filename (without extension)
            force_reprocess: Force reprocessing even if results exist
            
        Returns:
            dict: Claude processing results, or None if processing fails
        """
        try:
            logger.info(f"Processing transcript with Claude AI for {file_basename}")
            claude_processor = ClaudeProcessor()
            claude_result = claude_processor.process_transcript(
                transcript_file=transcript_file,
                output_dir=self.claude_output_dir,
                force_reprocess=force_reprocess
            )
            
            if claude_result:
                # Create a dict with Claude results
                claude_results = {
                    "claude_response_file": claude_result.get("claude_response_file"),
                    "claude_structured_json_file": claude_result.get("claude_structured_json_file"),
                    "claude_summary_file": claude_result.get("summary_file"),
                    "claude_sentiment_file": claude_result.get("sentiment_file"),
                    "claude_share_of_voice_chart": claude_result.get("share_of_voice_chart"),
                    "claude_sentiment_chart": claude_result.get("sentiment_chart")
                }
                logger.info(f"Claude AI processing completed for {file_basename}")
                logger.info(f"Claude response file: {claude_result.get('claude_response_file')}")
                logger.info(f"Claude structured JSON file: {claude_result.get('claude_structured_json_file')}")
                return claude_results
            else:
                logger.warning(f"Claude AI processing failed for {file_basename}")
                return None
        except Exception as e:
            logger.error(f"Error during Claude AI processing: {str(e)}")
            logger.debug(traceback.format_exc())
            return None
    
    def process_all_files(self, file_pattern="*.*", force_reprocess=False, skip_visualization=False, skip_claude=False, skip_hume=False, skip_elevenlabs=False):
        """
        Process all files in the input directory.
        
        Args:
            file_pattern: Pattern to match files to process
            force_reprocess: Force reprocessing even if results exist
            skip_visualization: Skip visualization step
            skip_claude: Skip Claude AI analysis
            skip_hume: Skip Hume AI processing
            skip_elevenlabs: Skip ElevenLabs processing
            
        Returns:
            dict: Dictionary mapping filenames to processing results
        """
        # Get all files matching the pattern
        files = glob.glob(os.path.join(self.input_dir, file_pattern))
        
        # Filter for audio files
        audio_extensions = ['.mp3', '.wav', '.mp4', '.m4a', '.aac', '.ogg', '.flac']
        audio_files = [f for f in files if os.path.splitext(f)[1].lower() in audio_extensions]
        
        if not audio_files:
            logger.warning(f"No audio files found in {self.input_dir} matching pattern {file_pattern}")
            return {}
        
        logger.info(f"Found {len(audio_files)} audio files to process")
        
        # Process each file
        results = {}
        for audio_file in audio_files:
            file_basename = os.path.basename(audio_file)
            logger.info(f"Processing {file_basename}...")
            
            result = self.process_file(
                audio_file=audio_file,
                force_reprocess=force_reprocess,
                skip_visualization=skip_visualization,
                skip_claude=skip_claude,
                skip_hume=skip_hume,
                skip_elevenlabs=skip_elevenlabs
            )
            
            results[file_basename] = result
        
        return results

def parse_arguments():
    """Parse command line arguments for the orchestrator script."""
    parser = argparse.ArgumentParser(description="Audio Analysis Orchestrator")
    
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
    parser.add_argument("--force", action="store_true",
                        help="Force reprocessing even if results exist")
    parser.add_argument("--skip-visualization", action="store_true",
                        help="Skip visualization generation")
    parser.add_argument("--skip-claude", action="store_true",
                        help="Skip Claude AI analysis")
    parser.add_argument("--job-id", type=str, default=None,
                        help="Process a specific job ID")
    parser.add_argument("--file", type=str, default=None,
                        help="Process a specific file")
    parser.add_argument("--transcript", type=str, default=None,
                        help="Process a specific transcript file with Claude (bypasses audio processing)")
    parser.add_argument("--file-pattern", type=str, default="*.*",
                        help="Pattern to match files to process")
    parser.add_argument("--skip-hume", action="store_true",
                        help="Skip Hume AI processing")
    parser.add_argument("--skip-elevenlabs", action="store_true",
                        help="Skip ElevenLabs processing")
    
    return parser.parse_args()

def main():
    """Main entry point for the orchestrator script."""
    args = parse_arguments()
    
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
            logger.info(f"Processing transcript with Claude: {args.transcript}")
            result = orchestrator.process_transcript_with_claude(
                transcript_file=args.transcript,
                force_reprocess=args.force
            )
            
            if result:
                logger.info("Claude processing completed successfully")
                for key, value in result.items():
                    if key not in ["summary_data", "sentiment_data"]:
                        logger.info(f"  {key}: {value}")
            else:
                logger.error("Claude processing failed")
            
            return
        
        # Process based on provided arguments
        if args.job_id:
            logger.info(f"Processing existing job ID: {args.job_id}")
            # Find the file associated with this job ID
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
                        if result:
                            logger.info(f"Processing completed for job ID {args.job_id}")
                        else:
                            logger.error(f"Processing failed for job ID {args.job_id}")
                        return
            
            logger.error(f"Could not find file for job ID {args.job_id} in job mappings.")
            return
        
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
        logger.debug(traceback.format_exc())

if __name__ == "__main__":
    main() 