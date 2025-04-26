#!/usr/bin/env python3
"""
Test script for Claude client connectivity.
This script tests the basic functionality of the Claude client by sending a simple prompt.
"""

import os
import sys
import json
import logging
import argparse

# Add parent directory to path for importing modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the Claude client
from clients.claude.client import ClaudeClient

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('claude_client_test.log', mode='a')
    ]
)
logger = logging.getLogger(__name__)

def load_prompt_from_file(prompt_file):
    """
    Load a prompt from a file in the prompts directory.
    
    Args:
        prompt_file: Name of the prompt file in the prompts/claude directory
        
    Returns:
        str: The prompt text
    """
    # Ensure the path is correct
    prompt_path = os.path.join('prompts', 'claude', prompt_file)
    
    try:
        with open(prompt_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        logger.error(f"Prompt file not found: {prompt_path}")
        return None
    except Exception as e:
        logger.error(f"Error reading prompt file: {str(e)}")
        return None

def main():
    """
    Main function to test the Claude client connectivity.
    """
    parser = argparse.ArgumentParser(description="Test Claude API connectivity")
    parser.add_argument("--prompt", "-p", default="default_prompt.txt", 
                        help="Prompt file to use from prompts/claude directory")
    parser.add_argument("--text", "-t", help="Optional text to analyze (overrides prompt file)")
    parser.add_argument("--output", "-o", default="claude_response.json",
                        help="Output file to save the response")
    parser.add_argument("--debug", "-d", action="store_true", help="Enable debug logging")
    args = parser.parse_args()
    
    # Enable debug logging if requested
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.setLevel(logging.DEBUG)
        logger.debug("Debug logging enabled")
    
    logger.info("===== Claude Client Connectivity Test =====")
    
    # Ensure the prompts directory exists
    os.makedirs(os.path.join('prompts', 'claude'), exist_ok=True)
    
    # Create default prompt file if it doesn't exist
    default_prompt_path = os.path.join('prompts', 'claude', 'default_prompt.txt')
    if args.prompt == "default_prompt.txt" and not os.path.exists(default_prompt_path):
        logger.info(f"Creating default prompt file at {default_prompt_path}")
        with open(default_prompt_path, 'w', encoding='utf-8') as f:
            f.write("Hello Claude! Please analyze this text: {text}\n\n"
                    "Provide a brief summary and key insights.")
    
    try:
        # Initialize the Claude client
        logger.info("Initializing Claude client...")
        client = ClaudeClient()
        
        # Get the content to analyze
        if args.text:
            # Use provided text
            text_to_analyze = args.text
            logger.info(f"Using provided text ({len(text_to_analyze)} characters)")
        else:
            # Load prompt from file
            prompt_template = load_prompt_from_file(args.prompt)
            if not prompt_template:
                logger.error("No prompt available. Please provide a valid prompt file or text.")
                return 1
            
            # For this test, we'll use a sample text if none is provided in the arguments
            sample_text = "This is a sample conversation for testing Claude API connectivity."
            text_to_analyze = prompt_template.format(text=sample_text)
            logger.info(f"Using prompt template from {args.prompt} with sample text")
        
        # Send the request to Claude
        logger.info("Sending request to Claude API...")
        response = client.analyze_text(text_to_analyze)
        
        if response:
            logger.info("Successfully received response from Claude!")
            
            # Extract the text from the response
            content_text = response.get("content", [{}])[0].get("text", "")
            preview = content_text[:200] + "..." if len(content_text) > 200 else content_text
            
            logger.info("\nResponse preview:")
            logger.info("-------------------")
            logger.info(preview)
            logger.info("-------------------")
            
            # Save the response to a file
            try:
                with open(args.output, 'w', encoding='utf-8') as f:
                    json.dump(response, f, indent=2)
                logger.info(f"Full response saved to {args.output}")
            except Exception as e:
                logger.error(f"Error saving response to file: {str(e)}")
            
            return 0
        else:
            logger.error("Failed to get a response from Claude API.")
            return 1
            
    except Exception as e:
        logger.error(f"Error during Claude client test: {str(e)}")
        if args.debug:
            import traceback
            logger.debug(traceback.format_exc())
        return 1

if __name__ == "__main__":
    sys.exit(main()) 