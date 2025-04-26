#!/usr/bin/env python3
import os
import requests
import json
import time
import logging
import sys
import traceback
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)

class HumeClient:
    def __init__(self, artifacts_output_dir="outputs/hume/artifacts"):
        """
        Initialize the Hume AI client.
        
        Args:
            artifacts_output_dir: Directory to save artifact files
        """
        # Get API key from environment variables
        self.api_key = os.getenv("HUME_API_KEY")
        if not self.api_key:
            logger.error("Hume AI key not found. Please set the HUME_API_KEY environment variable.")
            raise ValueError("Error: Hume AI key not found. Please set the HUME_API_KEY environment variable.")
        
        self.batch_jobs_endpoint = "https://api.hume.ai/v0/batch/jobs"
        self.headers = {
            "X-Hume-Api-Key": self.api_key
        }
        
        # Artifacts output directory
        self.artifacts_output_dir = artifacts_output_dir
        
        # Supported audio formats
        self.supported_extensions = ['.mp3', '.wav', '.m4a', '.aac', '.flac', '.ogg', '.mp4']
        
        logger.info("Hume AI client initialized")
        logger.debug(f"API key found (ends with: {self.api_key[-4:]})")
    
    def submit_job(self, audio_file_path, timeout=60):
        """
        Submit a job to analyze an audio file using Hume AI's Expression Measurement API.
        
        Args:
            audio_file_path: Path to the audio file to analyze
            timeout: Request timeout in seconds
            
        Returns:
            job_id: The job ID if successful, None otherwise
        """
        # Check supported file extensions
        file_ext = os.path.splitext(audio_file_path)[1].lower()
        
        if file_ext not in self.supported_extensions:
            logger.warning(f"File extension {file_ext} might not be supported. Supported formats include: {', '.join(self.supported_extensions)}")
            logger.info("Attempting to process anyway as Hume AI may be able to extract the audio.")
        
        # Enhanced configuration with more features enabled
        config = {
            "models": {
                # Enable prosody analysis with speaker identification
                "prosody": {
                    "identify_speakers": True,
                    # Use window approach for more granular analysis
                    "window": {
                        "length": 4,
                        "step": 1
                    }
                },
                # Enable language analysis with sentiment and speaker identification
                "language": {
                    "identify_speakers": True,
                    "sentiment": {},
                    "granularity": "sentence"
                }
                # Removed transcription model as it was causing errors
            }
        }
        
        # Convert the config to a JSON string
        json_config = json.dumps(config)
        
        logger.info(f"Opening file: {audio_file_path}")
        logger.debug(f"Using config: {json_config}")
        
        try:
            # Verify file can be opened
            file_size = os.path.getsize(audio_file_path) / (1024 * 1024)  # Size in MB
            logger.info(f"File size: {file_size:.2f} MB")
            
            if file_size > 100:
                logger.warning(f"File size {file_size:.2f} MB exceeds the 100 MB limit for direct uploads. API may reject this file.")
            
            with open(audio_file_path, "rb") as test_file:
                # Just test if file can be opened
                pass
            
            # Prepare the multipart form data
            files = {
                'file': open(audio_file_path, 'rb')
            }
            
            data = {
                'json': json_config
            }
            
            logger.info(f"Submitting job for audio file: {audio_file_path}")
            logger.info("This may take a while depending on the file size and length...")
            
            try:
                # Use a timeout to prevent indefinite hangs
                response = requests.post(
                    self.batch_jobs_endpoint,
                    headers=self.headers,
                    data=data,
                    files=files,
                    timeout=timeout
                )
                
                # Check if the response is successful (200 OK or 202 Accepted)
                if response.status_code not in [200, 202]:
                    logger.error(f"Error submitting job: {response.status_code}")
                    logger.error(f"Error details: {response.text}")
                    return None
                
                try:
                    response_data = response.json()
                    logger.debug(f"API Response: {response_data}")
                    if "job_id" in response_data:
                        job_id = response_data["job_id"]
                        logger.info(f"Job submitted successfully! Job ID: {job_id}")
                        return job_id
                    else:
                        logger.error(f"Error: Response does not contain job_id: {response_data}")
                        return None
                except json.JSONDecodeError:
                    logger.error(f"Error: Could not parse response as JSON: {response.text}")
                    return None
            except requests.exceptions.Timeout:
                logger.error(f"Request timed out after {timeout} seconds when submitting job")
                return None
            except requests.exceptions.RequestException as e:
                logger.error(f"Request error when submitting job: {str(e)}")
                return None
        except FileNotFoundError:
            logger.error(f"Error: Could not find or open the file {audio_file_path}")
            return None
        except Exception as e:
            logger.error(f"Error submitting job: {str(e)}")
            logger.debug(traceback.format_exc())
            return None
        finally:
            # Ensure file is closed if it was opened
            if 'files' in locals() and 'file' in files:
                files["file"].close()
    
    def check_job_status(self, job_id, timeout=30):
        """
        Check the status of a job.
        
        Args:
            job_id: The job ID to check
            timeout: Request timeout in seconds
            
        Returns:
            status: The job status if successful, None otherwise
        """
        status_endpoint = f"{self.batch_jobs_endpoint}/{job_id}"
        try:
            logger.debug(f"Checking job status for job ID: {job_id}")
            
            try:
                # Add timeout to prevent indefinite hangs
                response = requests.get(status_endpoint, headers=self.headers, timeout=timeout)
                
                if response.status_code != 200:
                    logger.error(f"Error checking job status: {response.status_code}")
                    logger.error(f"Error details: {response.text}")
                    return None
                
                try:
                    job_info = response.json()
                    
                    # Based on documentation, the status field is in the state object
                    if "state" in job_info and "status" in job_info["state"]:
                        status = job_info["state"]["status"]
                        logger.debug(f"Job status: {status}")
                        
                        # Get progress information if available
                        if "progress" in job_info["state"]:
                            logger.debug(f"Progress: {job_info['state']['progress']}%")
                        
                        return status
                    else:
                        logger.error(f"Error: Status field not found in job info response")
                        logger.debug(f"Available fields: {', '.join(job_info.keys())}")
                        return None
                except KeyError as e:
                    logger.error(f"Error accessing field in job status response: {e}")
                    return None
                except Exception as e:
                    logger.error(f"Error parsing job status response: {e}")
                    return None
            except requests.exceptions.Timeout:
                logger.error(f"Request timed out after {timeout} seconds when checking job status")
                return None
            except requests.exceptions.RequestException as e:
                logger.error(f"Request error when checking job status: {str(e)}")
                return None
        except Exception as e:
            logger.error(f"Error checking job status: {str(e)}")
            logger.debug(traceback.format_exc())
            return None
    
    def get_job_predictions(self, job_id, timeout=60):
        """
        Get the predictions for a completed job.
        
        Args:
            job_id: The job ID to get predictions for
            timeout: Request timeout in seconds
            
        Returns:
            predictions: The predictions if successful, None otherwise
        """
        predictions_endpoint = f"{self.batch_jobs_endpoint}/{job_id}/predictions"
        try:
            logger.info(f"Getting predictions for job ID: {job_id}")
            
            headers = self.headers.copy()
            headers['Accept'] = 'application/json; charset=utf-8'
            
            try:
                # Add timeout to prevent indefinite hangs
                response = requests.get(
                    predictions_endpoint, 
                    headers=headers,
                    timeout=timeout
                )
                
                if response.status_code != 200:
                    logger.error(f"Error getting predictions: {response.status_code}")
                    logger.error(f"Error details: {response.text}")
                    return None
                
                try:
                    predictions = response.json()
                    # Print a preview of the predictions structure
                    if predictions:
                        if isinstance(predictions, dict):
                            keys = list(predictions.keys())
                            logger.info(f"Prediction data contains keys: {keys}")
                        else:
                            logger.info(f"Prediction data is a list with {len(predictions)} items")
                    return predictions
                except json.JSONDecodeError:
                    logger.error(f"Error: Could not parse predictions response as JSON")
                    return None
            except requests.exceptions.Timeout:
                logger.error(f"Request timed out after {timeout} seconds when getting predictions")
                return None
            except requests.exceptions.RequestException as e:
                logger.error(f"Request error when getting predictions: {str(e)}")
                return None
        except Exception as e:
            logger.error(f"Error getting predictions: {str(e)}")
            logger.debug(traceback.format_exc())
            return None
    
    def get_job_artifacts(self, job_id, output_dir, timeout=60):
        """
        Get the artifacts (CSV files) for a completed job.
        
        Args:
            job_id: The job ID to get artifacts for
            output_dir: The directory to save the artifacts to
            timeout: Request timeout in seconds
            
        Returns:
            success: True if successful, False otherwise
        """
        artifacts_endpoint = f"{self.batch_jobs_endpoint}/{job_id}/artifacts"
        try:
            logger.info(f"Getting artifacts for job ID: {job_id}")
            
            headers = self.headers.copy()
            headers['Accept'] = 'application/octet-stream'
            
            try:
                # Add timeout to prevent indefinite hangs
                response = requests.get(
                    artifacts_endpoint, 
                    headers=headers,
                    timeout=timeout
                )
                
                if response.status_code != 200:
                    logger.error(f"Error getting artifacts: {response.status_code}")
                    logger.error(f"Error details: {response.text}")
                    return False
                
                # Create artifacts directory
                artifacts_dir = os.path.join(output_dir, "artifacts")
                os.makedirs(artifacts_dir, exist_ok=True)
                
                # Save the artifacts zip file
                artifacts_zip_path = os.path.join(artifacts_dir, "artifacts.zip")
                with open(artifacts_zip_path, 'wb') as f:
                    f.write(response.content)
                
                logger.info(f"Artifacts saved to {artifacts_zip_path}")
                
                # Extract the zip file
                try:
                    import zipfile
                    with zipfile.ZipFile(artifacts_zip_path, 'r') as zip_ref:
                        zip_ref.extractall(artifacts_dir)
                    logger.info(f"Artifacts extracted to {artifacts_dir}")
                    return True
                except zipfile.BadZipFile:
                    logger.error(f"The downloaded artifacts file is not a valid zip file")
                    return False
            except requests.exceptions.Timeout:
                logger.error(f"Request timed out after {timeout} seconds when getting artifacts")
                return False
            except requests.exceptions.RequestException as e:
                logger.error(f"Request error when getting artifacts: {str(e)}")
                return False
        except Exception as e:
            logger.error(f"Error getting artifacts: {str(e)}")
            logger.debug(traceback.format_exc())
            return False
    
    def save_predictions_to_file(self, predictions, output_path):
        """
        Save predictions to a JSON file.
        
        Args:
            predictions: The predictions to save
            output_path: Path to save the predictions to
            
        Returns:
            success: True if successful, False otherwise
        """
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Save predictions to file
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(predictions, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Predictions saved to {output_path}")
            return True
        except Exception as e:
            logger.error(f"Error saving predictions to file: {str(e)}")
            logger.debug(traceback.format_exc())
            return False
    
    def wait_for_job_completion(self, job_id, max_attempts=60, check_interval=5):
        """
        Wait for a job to complete with graceful handling of interruptions and timeouts.
        
        Args:
            job_id: The job ID to wait for
            max_attempts: The maximum number of attempts to check the job status
            check_interval: The interval in seconds between status checks
            
        Returns:
            success: True if the job completed successfully, False otherwise
        """
        logger.info(f"Waiting for job {job_id} to complete (max {max_attempts*check_interval} seconds)...")
        
        # Progress animation
        progress_animation = ["-", "\\", "|", "/"]
        animation_idx = 0
        
        try:
            for attempt in range(max_attempts):
                # Display progress animation
                progress_text = f"Processing {progress_animation[animation_idx]} (Attempt {attempt+1}/{max_attempts})"
                sys.stdout.write(f"\r{progress_text}")
                sys.stdout.flush()
                animation_idx = (animation_idx + 1) % len(progress_animation)
                
                # Check job status
                status = self.check_job_status(job_id)
                
                if status == "COMPLETED":
                    sys.stdout.write("\n")  # Move to next line
                    logger.info("Job completed successfully!")
                    return True
                elif status == "FAILED":
                    sys.stdout.write("\n")  # Move to next line
                    logger.error("Job failed.")
                    return False
                elif not status:
                    sys.stdout.write("\n")  # Move to next line
                    logger.warning("Could not retrieve job status. Retrying...")
                
                # Wait before checking again
                try:
                    time.sleep(check_interval)
                except KeyboardInterrupt:
                    sys.stdout.write("\n")  # Move to next line
                    logger.warning("Job status check interrupted by user")
                    logger.info(f"You can check job status later with: python hume_orchestrator.py --job-id {job_id}")
                    return False
            
            sys.stdout.write("\n")  # Move to next line
            logger.warning(f"Maximum attempts ({max_attempts}) reached. Job did not complete in time.")
            logger.info(f"You can try again later with the same job ID: python hume_orchestrator.py --job-id {job_id}")
            return False
        
        except KeyboardInterrupt:
            sys.stdout.write("\n")  # Move to next line
            logger.warning("Job status check interrupted by user")
            logger.info(f"You can check job status later with: python hume_orchestrator.py --job-id {job_id}")
            return False
        except Exception as e:
            sys.stdout.write("\n")  # Move to next line
            logger.error(f"Error waiting for job completion: {str(e)}")
            logger.debug(traceback.format_exc())
            return False 