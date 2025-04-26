#!/usr/bin/env python3
import os
import requests
import json
import time
import logging
import sys
import traceback
import hashlib
from dotenv import load_dotenv
import re

# Load environment variables from .env file
load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)

class ElevenLabsClient:
    def __init__(self, job_mappings_file="outputs/elevenlabs/elevenlabs_job_mappings.json"):
        """
        Initialize the ElevenLabs client.
        
        Args:
            job_mappings_file: Path to the file storing job mappings
        """
        # Get API key from environment variables
        self.api_key = os.getenv("ELEVENLABS_API_KEY")
        if not self.api_key:
            logger.error("ElevenLabs API key not found. Please set the ELEVENLABS_API_KEY environment variable.")
            raise ValueError("Error: ElevenLabs API key not found. Please set the ELEVENLABS_API_KEY environment variable.")
        
        self.speech_to_text_endpoint = "https://api.elevenlabs.io/v1/speech-to-text"
        self.headers = {
            "xi-api-key": self.api_key
        }
        
        # Path to store job mappings
        self.job_mappings_file = job_mappings_file
        # Make sure directory exists
        os.makedirs(os.path.dirname(job_mappings_file), exist_ok=True)
        self.job_mappings = self._load_job_mappings()
        
        # Supported audio formats
        self.supported_extensions = ['.mp3', '.wav', '.m4a', '.aac', '.flac', '.ogg', '.mp4']
        
        logger.info("ElevenLabs client initialized")
        logger.debug(f"API key found (ends with: {self.api_key[-4:]})")
    
    def _load_job_mappings(self):
        """
        Load job mappings from file.
        
        Returns:
            dict: Dictionary mapping audio file identifiers to job information
        """
        if os.path.exists(self.job_mappings_file):
            try:
                with open(self.job_mappings_file, 'r', encoding='utf-8') as f:
                    mappings = json.load(f)
                logger.info(f"Loaded {len(mappings)} ElevenLabs job mappings from {self.job_mappings_file}")
                return mappings
            except json.JSONDecodeError:
                logger.error(f"Error loading ElevenLabs job mappings from {self.job_mappings_file}: Invalid JSON format")
                return {}
            except Exception as e:
                logger.error(f"Error loading ElevenLabs job mappings: {str(e)}")
                logger.debug(traceback.format_exc())
                return {}
        logger.info(f"No existing ElevenLabs job mappings file found at {self.job_mappings_file}")
        return {}
    
    def _save_job_mappings(self):
        """
        Save job mappings to file.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with open(self.job_mappings_file, 'w', encoding='utf-8') as f:
                json.dump(self.job_mappings, f, indent=2, ensure_ascii=False)
            logger.info(f"ElevenLabs job mappings saved to {self.job_mappings_file}")
            return True
        except Exception as e:
            logger.error(f"Error saving ElevenLabs job mappings: {str(e)}")
            logger.debug(traceback.format_exc())
            return False
    
    def _generate_file_identifier(self, file_path):
        """
        Generate a unique identifier for a file based on its path and modification time.
        
        Args:
            file_path: Path to the file
            
        Returns:
            str: A unique identifier for the file
        """
        try:
            # Get file basename and modification time
            file_basename = os.path.basename(file_path)
            file_mtime = os.path.getmtime(file_path)
            file_size = os.path.getsize(file_path)
            
            # Create a hash from the file path, mod time, and size
            identifier = f"{file_basename}_{file_mtime}_{file_size}"
            hash_id = hashlib.md5(identifier.encode()).hexdigest()
            
            return hash_id
        except Exception as e:
            logger.error(f"Error generating file identifier: {str(e)}")
            logger.debug(traceback.format_exc())
            # Fallback to just the filename
            return os.path.basename(file_path)
    
    def check_if_processed(self, audio_file_path, output_dir):
        """
        Check if a file has already been processed.
        
        Args:
            audio_file_path: Path to the audio file
            output_dir: Directory where outputs are stored
            
        Returns:
            tuple: (is_processed, existing_transcript_path, existing_json_path)
        """
        try:
            # Check if the file exists
            if not os.path.exists(audio_file_path):
                logger.error(f"File not found: {audio_file_path}")
                return False, None, None
            
            # Get file identifier
            file_id = self._generate_file_identifier(audio_file_path)
            file_basename = os.path.splitext(os.path.basename(audio_file_path))[0]
            
            # Define expected output paths
            json_path = os.path.join(output_dir, f"{file_basename}_transcript.json")
            cleaned_path = os.path.join(output_dir, f"{file_basename}_transcript_cleaned.txt")
            
            # Check if the file is in job mappings
            if file_id in self.job_mappings:
                logger.info(f"File {audio_file_path} was previously processed (ID: {file_id})")
                
                # Check if output files exist
                if os.path.exists(json_path) and os.path.exists(cleaned_path):
                    logger.info(f"Output files found at {json_path} and {cleaned_path}")
                    return True, cleaned_path, json_path
                else:
                    logger.warning(f"File was processed but outputs are missing, will reprocess")
                    return False, None, None
            
            # If not in job mappings, check if output files exist anyway
            if os.path.exists(json_path) and os.path.exists(cleaned_path):
                logger.info(f"Output files found but not in job mappings, will consider as processed")
                
                # Add to job mappings for future reference
                self.job_mappings[file_id] = {
                    "file_path": audio_file_path,
                    "processed_time": os.path.getmtime(json_path),
                    "json_path": json_path,
                    "cleaned_path": cleaned_path
                }
                self._save_job_mappings()
                
                return True, cleaned_path, json_path
            
            return False, None, None
        except Exception as e:
            logger.error(f"Error checking if file was processed: {str(e)}")
            logger.debug(traceback.format_exc())
            return False, None, None
    
    def transcribe_audio(self, audio_file_path, model_id="scribe_v1", diarize=True, 
                         language_code=None, tag_audio_events=True, num_speakers=None, 
                         timestamps_granularity="word", timeout=600, force_reprocess=False,
                         output_dir="elevenlabs_results"):
        """
        Transcribe an audio file using ElevenLabs' Speech-to-Text API.
        
        Args:
            audio_file_path: Path to the audio file to transcribe
            model_id: The ID of the model to use for transcription (scribe_v1 or scribe_v1_experimental)
            diarize: Whether to annotate which speaker is currently talking
            language_code: ISO-639-1 or ISO-639-3 language code (auto-detected if None)
            tag_audio_events: Whether to tag audio events like (laughter), (footsteps), etc.
            num_speakers: The maximum number of speakers to identify (if known)
            timestamps_granularity: Granularity of timestamps ('word' or 'character')
            timeout: Request timeout in seconds
            force_reprocess: Whether to force reprocessing even if already processed
            output_dir: Directory to save the outputs
            
        Returns:
            tuple: (transcript_data, cleaned_transcript, json_path, cleaned_path, is_new)
        """
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Check if the file has already been processed
        if not force_reprocess:
            is_processed, existing_cleaned_path, existing_json_path = self.check_if_processed(audio_file_path, output_dir)
            if is_processed:
                logger.info(f"Using existing transcript for {audio_file_path}")
                
                # Load the existing transcript data
                try:
                    with open(existing_json_path, 'r', encoding='utf-8') as f:
                        transcript_data = json.load(f)
                    
                    with open(existing_cleaned_path, 'r', encoding='utf-8') as f:
                        cleaned_transcript = f.read()
                    
                    return transcript_data, cleaned_transcript, existing_json_path, existing_cleaned_path, False
                except Exception as e:
                    logger.error(f"Error loading existing transcript: {str(e)}")
                    logger.debug(traceback.format_exc())
                    # If there's an error, continue with reprocessing
        
        # File extension check
        file_ext = os.path.splitext(audio_file_path)[1].lower()
        if file_ext not in self.supported_extensions:
            logger.warning(f"File extension {file_ext} might not be supported. Supported formats include: {', '.join(self.supported_extensions)}")
            logger.info("Attempting to process anyway as ElevenLabs may support this format.")
        
        try:
            # Verify file can be opened
            file_size = os.path.getsize(audio_file_path) / (1024 * 1024)  # Size in MB
            logger.info(f"File size: {file_size:.2f} MB")
            
            if file_size > 1000:  # 1GB limit
                logger.error(f"File size {file_size:.2f} MB exceeds the 1GB limit for direct uploads.")
                return None, None, None, None, False
            
            with open(audio_file_path, "rb") as test_file:
                # Just test if file can be opened
                pass
            
            # Get file basename without extension
            file_basename = os.path.splitext(os.path.basename(audio_file_path))[0]
            json_path = os.path.join(output_dir, f"{file_basename}_transcript.json")
            cleaned_path = os.path.join(output_dir, f"{file_basename}_transcript_cleaned.txt")
            
            # Prepare the multipart form data
            files = {
                'file': open(audio_file_path, 'rb')
            }
            
            # Prepare form data
            data = {
                'model_id': model_id,
                'diarize': str(diarize).lower(),
                'tag_audio_events': str(tag_audio_events).lower(),
                'timestamps_granularity': timestamps_granularity
            }
            
            # Add optional parameters if provided
            if language_code:
                data['language_code'] = language_code
            if num_speakers:
                data['num_speakers'] = str(num_speakers)
            
            logger.info(f"Transcribing audio file: {audio_file_path}")
            logger.info("This may take a while depending on the file size and length...")
            
            # Progress animation
            progress_animation = ["-", "\\", "|", "/"]
            animation_idx = 0
            start_time = time.time()
            
            try:
                # Use a timeout to prevent indefinite hangs
                response = requests.post(
                    self.speech_to_text_endpoint,
                    headers=self.headers,
                    data=data,
                    files=files,
                    timeout=timeout,
                    stream=True  # Stream the response to show progress
                )
                
                # Initialize response content
                response_content = b""
                
                # Stream the response with progress display
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        response_content += chunk
                        
                        # Display progress animation
                        elapsed_time = time.time() - start_time
                        progress_text = f"Processing {progress_animation[animation_idx]} (Elapsed: {int(elapsed_time)}s)"
                        sys.stdout.write(f"\r{progress_text}")
                        sys.stdout.flush()
                        animation_idx = (animation_idx + 1) % len(progress_animation)
                
                sys.stdout.write("\n")  # Move to next line after progress animation
                
                # Check if the response is successful (200 OK)
                if response.status_code != 200:
                    logger.error(f"Error transcribing audio: {response.status_code}")
                    try:
                        error_text = response_content.decode('utf-8')
                        logger.error(f"Error details: {error_text}")
                    except:
                        logger.error(f"Error details: Could not decode response content")
                    return None, None, None, None, False
                
                try:
                    # Parse the response content
                    transcript_data = json.loads(response_content.decode('utf-8'))
                    logger.debug(f"API Response: {json.dumps(transcript_data, indent=2)[:500]}...")  # Show first 500 chars
                    
                    if "text" in transcript_data:
                        logger.info(f"Transcription successful! Text length: {len(transcript_data['text'])} characters")
                        logger.info(f"Detected language: {transcript_data.get('language_code', 'unknown')} "
                                   f"(confidence: {transcript_data.get('language_probability', 0):.2f})")
                        
                        # Log word count if words are available
                        if "words" in transcript_data:
                            word_count = sum(1 for w in transcript_data["words"] if w.get("type") == "word")
                            logger.info(f"Word count: {word_count} words")
                        
                        # Extract cleaned transcript
                        cleaned_transcript = self.extract_cleaned_transcript_with_speakers(transcript_data)
                        if cleaned_transcript:
                            cleaned_transcript = self.clean_punctuation(cleaned_transcript)
                            
                            # Save transcript data
                            self.save_transcript_to_file(transcript_data, json_path)
                            self.save_cleaned_transcript(cleaned_transcript, cleaned_path)
                            
                            # Add to job mappings
                            file_id = self._generate_file_identifier(audio_file_path)
                            self.job_mappings[file_id] = {
                                "file_path": audio_file_path,
                                "processed_time": time.time(),
                                "json_path": json_path,
                                "cleaned_path": cleaned_path
                            }
                            self._save_job_mappings()
                            
                            return transcript_data, cleaned_transcript, json_path, cleaned_path, True
                        else:
                            logger.error("Failed to extract cleaned transcript")
                            return transcript_data, None, json_path, None, True
                    else:
                        logger.error(f"Error: Response does not contain text field: {response_content.decode('utf-8')[:200]}...")
                        return None, None, None, None, False
                except json.JSONDecodeError:
                    logger.error(f"Error: Could not parse response as JSON: {response_content.decode('utf-8')[:200]}...")
                    return None, None, None, None, False
            except requests.exceptions.Timeout:
                logger.error(f"Request timed out after {timeout} seconds when transcribing audio")
                return None, None, None, None, False
            except requests.exceptions.RequestException as e:
                logger.error(f"Request error when transcribing audio: {str(e)}")
                logger.debug(traceback.format_exc())
                return None, None, None, None, False
        except FileNotFoundError:
            logger.error(f"Error: Could not find or open the file {audio_file_path}")
            return None, None, None, None, False
        except Exception as e:
            logger.error(f"Error transcribing audio: {str(e)}")
            logger.debug(traceback.format_exc())
            return None, None, None, None, False
        finally:
            # Ensure file is closed if it was opened
            if 'files' in locals() and 'file' in files:
                files["file"].close()
    
    def save_transcript_to_file(self, transcript_data, output_path):
        """
        Save the transcript data to a JSON file.
        
        Args:
            transcript_data: The transcript data to save
            output_path: Path to save the transcript to
            
        Returns:
            success: True if successful, False otherwise
        """
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Save transcript to file
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(transcript_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Transcript saved to {output_path}")
            return True
        except Exception as e:
            logger.error(f"Error saving transcript to file: {str(e)}")
            logger.debug(traceback.format_exc())
            return False
    
    def extract_cleaned_transcript_with_speakers(self, transcript_data):
        """
        Extract a cleaned transcript with speaker annotations from the transcript data.
        
        Args:
            transcript_data: The transcript data from the ElevenLabs API
            
        Returns:
            cleaned_transcript: A string containing the cleaned transcript with speaker annotations
        """
        if not transcript_data or "words" not in transcript_data:
            logger.error("No valid transcript data provided")
            return None
        
        try:
            # Extract words with speaker IDs
            words = transcript_data["words"]
            cleaned_lines = []
            current_speaker = None
            current_line = ""
            
            for word_obj in words:
                # Skip non-word elements like spacing
                if word_obj.get("type") != "word":
                    continue
                
                word = word_obj.get("text", "")
                speaker = word_obj.get("speaker_id", "unknown")
                
                # If speaker changes, start a new line
                if speaker != current_speaker:
                    if current_line:  # Save the previous line if it's not empty
                        cleaned_lines.append(current_line)
                    current_speaker = speaker
                    current_line = f"[{speaker}]: {word}"
                else:
                    current_line += f" {word}"
            
            # Add the last line if not empty
            if current_line:
                cleaned_lines.append(current_line)
            
            # Join lines with newlines
            cleaned_transcript = "\n".join(cleaned_lines)
            
            return cleaned_transcript
        except Exception as e:
            logger.error(f"Error extracting cleaned transcript: {str(e)}")
            logger.debug(traceback.format_exc())
            return None
    
    def save_cleaned_transcript(self, cleaned_transcript, output_path):
        """
        Save the cleaned transcript to a text file.
        
        Args:
            cleaned_transcript: The cleaned transcript to save
            output_path: Path to save the transcript to
            
        Returns:
            success: True if successful, False otherwise
        """
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Save transcript to file
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(cleaned_transcript)
            
            logger.info(f"Cleaned transcript saved to {output_path}")
            return True
        except Exception as e:
            logger.error(f"Error saving cleaned transcript to file: {str(e)}")
            logger.debug(traceback.format_exc())
            return False
    
    def clean_punctuation(self, transcript):
        """
        Clean up punctuation in the transcript.
        
        Args:
            transcript: The transcript text to clean
            
        Returns:
            cleaned_text: The cleaned transcript text
        """
        if not transcript:
            return transcript
        
        # Fix common punctuation issues
        cleaned = transcript
        
        # Ensure proper spacing around punctuation
        cleaned = re.sub(r'\s+([.,;:!?])', r'\1', cleaned)  # Remove spaces before punctuation
        cleaned = re.sub(r'([.,;:!?])([^\s\d])', r'\1 \2', cleaned)  # Add space after punctuation if not followed by space/digit
        
        # Fix quotes
        cleaned = re.sub(r'"([^"]*)"', r'"\1"', cleaned)  # Normalize quotes
        
        # Fix multiple spaces
        cleaned = re.sub(r'\s+', ' ', cleaned)
        
        # Capitalize first letter of sentences
        cleaned = re.sub(r'([.!?]\s+)([a-z])', lambda m: m.group(1) + m.group(2).upper(), cleaned)
        
        return cleaned 