#!/usr/bin/env python3
import os
import sys
import json
import pandas as pd
import logging
import traceback
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime

# Add parent directory to path for importing modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from clients.claude.client import ClaudeClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('processors/claude/claude_processor.log', mode='a')
    ]
)

class ClaudeProcessor:
    def __init__(self):
        """
        Initialize the Claude Processor for conversation analysis.
        """
        self.client = ClaudeClient()
        self.logger = logging.getLogger(__name__)
        
        # Create output directory if it doesn't exist
        os.makedirs('outputs/claude', exist_ok=True)
        
        # Store path to prompt files
        self.communication_prompt_file = os.path.join('prompts', 'claude', 'prompt_1.txt')
        self.json_formatting_prompt_file = os.path.join('prompts', 'claude', 'prompt_2.txt')
        self.emotion_analysis_prompt_file = os.path.join('prompts', 'claude', 'prompt_3.txt')
    
    def _load_prompt(self, prompt_file):
        """
        Load a prompt from a file.
        
        Args:
            prompt_file: Path to the prompt file
            
        Returns:
            str: The prompt text, or None if file not found
        """
        try:
            with open(prompt_file, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            self.logger.error(f"Prompt file not found: {prompt_file}")
            return None
        except Exception as e:
            self.logger.error(f"Error reading prompt file: {str(e)}")
            return None
    
    def _process_analysis_to_json(self, analysis_text):
        """
        Process the raw Claude analysis and convert it to structured JSON using the second prompt.
        
        Args:
            analysis_text: The raw text analysis from the first Claude call
            
        Returns:
            dict: The structured JSON response, or None if processing fails
        """
        try:
            # Load the JSON formatting prompt template
            json_prompt = self._load_prompt(self.json_formatting_prompt_file)
            if not json_prompt:
                self.logger.error(f"JSON formatting prompt file not found: {self.json_formatting_prompt_file}")
                return None
                
            # Append the analysis text to the prompt
            full_prompt = f"{json_prompt}\n\n{analysis_text}"
            self.logger.debug(f"Full JSON formatting prompt length: {len(full_prompt)} characters")
            
            # Send to Claude
            self.logger.info("Converting analysis to structured JSON format...")
            claude_response = self.client.analyze_text(full_prompt)
            
            if not claude_response:
                self.logger.error("Failed to get JSON conversion from Claude")
                return None
            
            # Extract the text content from Claude's response
            response_text = claude_response.get("content", [{}])[0].get("text", "")
            self.logger.debug(f"JSON formatting response length: {len(response_text)} characters")
            
            # Save the raw JSON response for debugging
            debug_file = os.path.join('outputs/claude', "json_formatting_raw_response.txt")
            with open(debug_file, 'w', encoding='utf-8') as f:
                f.write(response_text)
            
            # Try to parse the JSON from the response text
            # First, look for JSON code blocks in markdown format
            import re
            json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', response_text)
            
            if json_match:
                json_str = json_match.group(1)
                self.logger.debug(f"Found JSON code block, length: {len(json_str)} characters")
                try:
                    structured_data = json.loads(json_str)
                    return structured_data
                except json.JSONDecodeError as e:
                    self.logger.error(f"Failed to parse JSON from code block in Claude response: {str(e)}")
            
            # If no valid JSON code block, try direct JSON construction from the content
            self.logger.info("No valid JSON code block found, creating structured JSON manually")
            
            # Create a structured JSON object manually from the analysis text
            structured_data = {
                "raw_text": analysis_text,
                "processed_at": datetime.now().isoformat()
            }
            
            # Extract conversation summary
            summary_match = re.search(r'## 1\. Conversation Summary\s*\n(.*?)(?=\n##)', analysis_text, re.DOTALL)
            if summary_match:
                structured_data["conversation_summary"] = summary_match.group(1).strip()
            
            # Extract communication depth distribution
            depth_dist = {}
            depth_match = re.search(r'## 2\. Communication Depth Distribution\s*\n(.*?)(?=\n##)', analysis_text, re.DOTALL)
            if depth_match:
                depth_text = depth_match.group(1).strip()
                level_matches = re.findall(r'\*\*Level (\d+).*?\*\*:?\s*(\d+)%', depth_text)
                for level, percentage in level_matches:
                    depth_dist[f"level_{level}"] = int(percentage)
                structured_data["communication_depth_distribution"] = depth_dist
            
            # Extract key recommendations
            recommendations = []
            rec_match = re.search(r'## 3\. Key Recommendations Overview\s*\n(.*?)(?=\n##)', analysis_text, re.DOTALL)
            if rec_match:
                rec_text = rec_match.group(1).strip()
                rec_items = re.findall(r'\d+\.\s*(.*?)(?=\n\d+\.|\Z)', rec_text + '\n', re.DOTALL)
                recommendations = [item.strip() for item in rec_items if item.strip()]
                structured_data["key_recommendations_overview"] = recommendations
            
            # Extract detailed recommendations
            detailed_recs = []
            detailed_match = re.search(r'## 4\. Detailed Recommendations\s*(.*)', analysis_text, re.DOTALL)
            if detailed_match:
                detailed_text = detailed_match.group(1).strip()
                rec_blocks = re.split(r'### Recommendation \d+:', detailed_text)[1:]  # Skip the first empty split
                
                for block in rec_blocks:
                    rec = {}
                    
                    # Extract title
                    title_match = re.search(r'^(.*?)(?=\n\*\*)', block, re.DOTALL)
                    if title_match:
                        rec["title"] = title_match.group(1).strip()
                    
                    # Extract current pattern
                    pattern_match = re.search(r'\*\*Current Pattern:?\*\*\s*(.*?)(?=\n\*\*)', block, re.DOTALL)
                    if pattern_match:
                        rec["current_pattern"] = pattern_match.group(1).strip()
                    
                    # Extract improvement opportunity
                    improve_match = re.search(r'\*\*Improvement Opportunity:?\*\*\s*(.*?)(?=\n\*\*)', block, re.DOTALL)
                    if improve_match:
                        rec["improvement_opportunity"] = improve_match.group(1).strip()
                    
                    # Extract example reframing
                    example_match = re.search(r'\*\*Example Reframing:?\*\*\s*(.*?)(?=\n\*\*)', block, re.DOTALL)
                    if example_match:
                        example_text = example_match.group(1).strip()
                        before_after = {}
                        before_match = re.search(r'- Before:\s*"(.*?)"', example_text)
                        after_match = re.search(r'- After:\s*"(.*?)"', example_text)
                        if before_match:
                            before_after["before"] = before_match.group(1)
                        if after_match:
                            before_after["after"] = after_match.group(1)
                        rec["example_reframing"] = before_after
                    
                    # Extract benefits
                    benefits_match = re.search(r'\*\*Benefits:?\*\*\s*(.*?)(?=\n\*\*|$)', block, re.DOTALL)
                    if benefits_match:
                        rec["benefits"] = benefits_match.group(1).strip()
                    
                    # Extract practice suggestion
                    practice_match = re.search(r'\*\*Practice Suggestion:?\*\*\s*(.*?)(?=\n\*\*|$)', block, re.DOTALL)
                    if practice_match:
                        rec["practice_suggestion"] = practice_match.group(1).strip()
                    
                    detailed_recs.append(rec)
                
                structured_data["detailed_recommendations"] = detailed_recs
            
            return structured_data
                
        except Exception as e:
            self.logger.error(f"Error processing analysis to JSON: {str(e)}")
            self.logger.debug(traceback.format_exc())
            return None

    def process_transcript(self, transcript_file, output_dir="outputs/claude", force_reprocess=False):
        """
        Process a transcript file using Claude for analysis.
        
        Args:
            transcript_file: Path to the transcript file (typically the cleaned ElevenLabs transcript)
            output_dir: Directory to save the processed output
            force_reprocess: Whether to force reprocessing even if results exist
            
        Returns:
            dict: Dictionary containing the results of processing
        """
        try:
            # Create output directory if it doesn't exist
            os.makedirs(output_dir, exist_ok=True)
            
            # Get file basename without extension
            file_basename = os.path.splitext(os.path.basename(transcript_file))[0]
            
            # Extract the audio file name from the transcript filename (removing _transcript_cleaned)
            audio_basename = file_basename.replace("_transcript_cleaned", "")
            
            # Define output files with unique names based on the audio file
            claude_response_file = os.path.join(output_dir, f"{audio_basename}_claude_response.json")
            claude_structured_json_file = os.path.join(output_dir, f"{audio_basename}_claude_structured_analysis.json")
            summary_file = os.path.join(output_dir, f"{audio_basename}_summary.json")
            sentiment_file = os.path.join(output_dir, f"{audio_basename}_sentiment.json")
            share_of_voice_chart = os.path.join(output_dir, f"{audio_basename}_share_of_voice.png")
            sentiment_chart = os.path.join(output_dir, f"{audio_basename}_sentiment_chart.png")
            
            # Log the file paths we're checking and creating
            self.logger.info(f"Audio basename: {audio_basename}")
            self.logger.info(f"Processing transcript: {file_basename}")
            self.logger.info(f"Claude response will be saved to: {claude_response_file}")
            self.logger.info(f"Claude structured analysis will be saved to: {claude_structured_json_file}")
            
            # Check if already processed
            if not force_reprocess and os.path.exists(claude_response_file) and os.path.exists(claude_structured_json_file):
                self.logger.info(f"Transcript {audio_basename} already processed. Use force_reprocess=True to reprocess.")
                
                # Load the existing results
                with open(claude_response_file, 'r', encoding='utf-8') as f:
                    claude_data = json.load(f)
                
                with open(claude_structured_json_file, 'r', encoding='utf-8') as f:
                    structured_data = json.load(f)
                
                return {
                    "claude_response_file": claude_response_file,
                    "claude_structured_json_file": claude_structured_json_file,
                    "summary_file": summary_file if os.path.exists(summary_file) else None,
                    "sentiment_file": sentiment_file if os.path.exists(sentiment_file) else None,
                    "share_of_voice_chart": share_of_voice_chart if os.path.exists(share_of_voice_chart) else None,
                    "sentiment_chart": sentiment_chart if os.path.exists(sentiment_chart) else None,
                    "claude_data": claude_data,
                    "structured_data": structured_data
                }
            
            # Read the transcript
            self.logger.info(f"Reading transcript file: {transcript_file}")
            try:
                with open(transcript_file, 'r', encoding='utf-8') as f:
                    transcript = f.read()
                self.logger.debug(f"Transcript length: {len(transcript)} characters")
            except Exception as e:
                self.logger.error(f"Error reading transcript file: {str(e)}")
                return None
            
            # Process with Claude - Using only the communication prompt
            self.logger.info("Analyzing conversation with Claude using communication prompt...")
            
            # Load the communication prompt template
            communication_prompt = self._load_prompt(self.communication_prompt_file)
            if not communication_prompt:
                self.logger.error(f"Communication prompt file not found: {self.communication_prompt_file}")
                return None
                
            # Append the transcript to the prompt (no need for formatting placeholders)
            full_prompt = f"{communication_prompt}\n\nTranscript:\n{transcript}"
            self.logger.debug(f"Full prompt length: {len(full_prompt)} characters")
            
            # Send to Claude
            claude_response = self.client.analyze_text(full_prompt)
            
            if not claude_response:
                self.logger.error("Failed to get analysis from Claude")
                return None
            
            # Extract the text content from Claude's response
            response_text = claude_response.get("content", [{}])[0].get("text", "")
            self.logger.debug(f"Response text length: {len(response_text)} characters")
            
            # Create response data structure
            claude_data = {
                "raw_response": claude_response,
                "response_text": response_text,
                "processed_at": datetime.now().isoformat()
            }
            
            # Save the results to a single JSON file
            with open(claude_response_file, 'w', encoding='utf-8') as f:
                json.dump(claude_data, f, indent=2, ensure_ascii=False)
            self.logger.info(f"Claude response saved to {claude_response_file}")
            
            # Process the analysis to structured JSON format using the second prompt
            structured_data = self._process_analysis_to_json(response_text)
            
            if structured_data:
                # Save the structured JSON data
                with open(claude_structured_json_file, 'w', encoding='utf-8') as f:
                    json.dump(structured_data, f, indent=2, ensure_ascii=False)
                self.logger.info(f"Structured JSON analysis saved to {claude_structured_json_file}")
                
                # TODO: Generate more specific outputs and visualizations
                # For now we just prepare the file names
            else:
                self.logger.warning("Failed to generate structured JSON analysis")
            
            # Return results
            return {
                "claude_response_file": claude_response_file,
                "claude_structured_json_file": claude_structured_json_file if structured_data else None,
                "summary_file": summary_file if os.path.exists(summary_file) else None,
                "sentiment_file": sentiment_file if os.path.exists(sentiment_file) else None,
                "share_of_voice_chart": share_of_voice_chart if os.path.exists(share_of_voice_chart) else None,
                "sentiment_chart": sentiment_chart if os.path.exists(sentiment_chart) else None,
                "claude_data": claude_data,
                "structured_data": structured_data
            }
            
        except Exception as e:
            self.logger.error(f"Error processing transcript with Claude: {str(e)}")
            self.logger.debug(traceback.format_exc())
            return None

    def process_quintile_emotions(self, quintile_analysis_file, output_dir="outputs/claude"):
        """
        Process a quintile analysis file using Claude to extract emotion data.
        
        Args:
            quintile_analysis_file: Path to the quintile analysis file
            output_dir: Directory to save the processed output
            
        Returns:
            dict: Dictionary containing the results of processing
        """
        try:
            # Create output directory if it doesn't exist
            os.makedirs(output_dir, exist_ok=True)
            
            # Get file basename without extension
            file_basename = os.path.splitext(os.path.basename(quintile_analysis_file))[0]
            
            # Extract the audio file name from the quintile analysis filename
            audio_basename = file_basename.replace("_quintile_analysis", "")
            
            # Define output file with unique name based on the audio file
            emotions_json_file = os.path.join(output_dir, f"{audio_basename}_emotions_analysis.json")
            
            # Log the file paths
            self.logger.info(f"Processing quintile analysis: {file_basename}")
            self.logger.info(f"Emotions analysis will be saved to: {emotions_json_file}")
            
            # Check if already processed - we won't reuse force_reprocess here as it should be handled by caller
            if os.path.exists(emotions_json_file):
                self.logger.info(f"Quintile analysis {audio_basename} already processed to emotions analysis.")
                
                # Load the existing results
                with open(emotions_json_file, 'r', encoding='utf-8') as f:
                    emotions_data = json.load(f)
                
                return {
                    "emotions_analysis_file": emotions_json_file,
                    "emotions_data": emotions_data
                }
            
            # Read the quintile analysis file
            self.logger.info(f"Reading quintile analysis file: {quintile_analysis_file}")
            try:
                with open(quintile_analysis_file, 'r', encoding='utf-8') as f:
                    quintile_analysis = f.read()
                self.logger.debug(f"Quintile analysis length: {len(quintile_analysis)} characters")
            except Exception as e:
                self.logger.error(f"Error reading quintile analysis file: {str(e)}")
                return None
            
            # Process with Claude using the emotion analysis prompt
            self.logger.info("Processing quintile analysis with Claude for emotion extraction...")
            
            # Load the emotion analysis prompt template
            emotion_prompt = self._load_prompt(self.emotion_analysis_prompt_file)
            if not emotion_prompt:
                self.logger.error(f"Emotion analysis prompt file not found: {self.emotion_analysis_prompt_file}")
                return None
                
            # Append the quintile analysis to the prompt
            full_prompt = f"{emotion_prompt}\n\n{quintile_analysis}"
            self.logger.debug(f"Full prompt length: {len(full_prompt)} characters")
            
            # Send to Claude
            claude_response = self.client.analyze_text(full_prompt)
            
            if not claude_response:
                self.logger.error("Failed to get emotion analysis from Claude")
                return None
            
            # Extract the text content from Claude's response
            response_text = claude_response.get("content", [{}])[0].get("text", "")
            self.logger.debug(f"Response text length: {len(response_text)} characters")
            
            # Try to parse the JSON from the response text
            import re
            json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', response_text)
            
            emotions_data = None
            if json_match:
                json_str = json_match.group(1)
                self.logger.debug(f"Found JSON code block, length: {len(json_str)} characters")
                try:
                    emotions_data = json.loads(json_str)
                except json.JSONDecodeError as e:
                    self.logger.error(f"Failed to parse JSON from code block in Claude response: {str(e)}")
            
            # If no valid JSON code block found, try to extract it from the text directly
            if not emotions_data:
                self.logger.info("No valid JSON code block found, trying to extract JSON directly")
                try:
                    # Look for JSON array in the text (should start with '[' and end with ']')
                    json_str = response_text
                    start_idx = json_str.find('[')
                    end_idx = json_str.rfind(']') + 1
                    
                    if start_idx >= 0 and end_idx > start_idx:
                        json_str = json_str[start_idx:end_idx]
                        emotions_data = json.loads(json_str)
                    else:
                        self.logger.error("Could not find JSON array markers in response")
                except json.JSONDecodeError as e:
                    self.logger.error(f"Failed to parse JSON directly from response: {str(e)}")
            
            if emotions_data:
                # Save the emotions data to a JSON file
                with open(emotions_json_file, 'w', encoding='utf-8') as f:
                    json.dump(emotions_data, f, indent=2, ensure_ascii=False)
                self.logger.info(f"Emotions analysis saved to {emotions_json_file}")
                
                return {
                    "emotions_analysis_file": emotions_json_file,
                    "emotions_data": emotions_data
                }
            else:
                self.logger.error("Failed to extract valid emotions data from Claude response")
                return None
                
        except Exception as e:
            self.logger.error(f"Error processing quintile emotions with Claude: {str(e)}")
            self.logger.debug(traceback.format_exc())
            return None 