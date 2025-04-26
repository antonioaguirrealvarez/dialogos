#!/usr/bin/env python3
import os
import sys
import requests
import json
import logging
import time
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)

class ClaudeClient:
    def __init__(self):
        """
        Initialize the Claude API client
        """
        # Get API key from environment variables
        self.api_key = os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            logger.error("Claude API key not found. Please set the ANTHROPIC_API_KEY environment variable.")
            raise ValueError("Error: Claude API key not found. Please set the ANTHROPIC_API_KEY environment variable.")
        
        # API endpoints
        self.messages_endpoint = "https://api.anthropic.com/v1/messages"
        
        # Default headers
        self.headers = {
            "x-api-key": self.api_key,
            "content-type": "application/json",
            "anthropic-version": "2023-06-01"  # Using a stable API version
        }
        
        logger.info("Claude API client initialized")
        
    def analyze_text(self, text, system_prompt=None, max_tokens=1024, temperature=0.7):
        """
        Send text to Claude for analysis
        
        Args:
            text: The text content to analyze
            system_prompt: Optional system prompt to give context to Claude
            max_tokens: Maximum number of tokens in the response (default: 1024)
            temperature: Temperature parameter for response randomness (default: 0.7)
            
        Returns:
            dict: The parsed response from Claude
        """
        try:
            # Prepare request payload
            payload = {
                "model": "claude-3-7-sonnet-20250219",  # Using Claude 3.7 Sonnet
                "max_tokens": max_tokens,
                "temperature": temperature,
                "messages": [
                    {"role": "user", "content": text}
                ]
            }
            
            # Add system prompt if provided
            if system_prompt:
                payload["system"] = system_prompt
            
            logger.info(f"Sending request to Claude with {len(text)} characters of text")
            
            # Make the API request
            response = requests.post(
                self.messages_endpoint,
                headers=self.headers,
                json=payload
            )
            
            # Check if response was successful
            if response.status_code == 200:
                result = response.json()
                logger.info("Successfully received response from Claude")
                return result
            else:
                logger.error(f"Error from Claude API: {response.status_code}")
                logger.error(f"Response: {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error analyzing text with Claude: {str(e)}")
            return None
            
    def analyze_conversation_summary(self, transcript, system_prompt=None):
        """
        Analyze a conversation transcript and provide a summary
        
        Args:
            transcript: Text transcript of the conversation
            system_prompt: Optional system prompt to give context to Claude
            
        Returns:
            dict: The parsed response from Claude with summary information
        """
        if not system_prompt:
            system_prompt = """
            You are an expert conversation analyst. You will be provided with a transcript of a conversation.
            Analyze the transcript and provide a summary with the following elements:
            1. A brief overview of the conversation topic and context
            2. Share of voice (percentage of words/talking time) for each speaker
            3. Key points made by each speaker
            4. Overall tone and dynamics of the conversation
            
            Format your response in a clear, structured way that makes it easy to understand the conversation dynamics.
            """
        
        return self.analyze_text(transcript, system_prompt=system_prompt, max_tokens=2048)
        
    def analyze_conversation_sentiment(self, transcript, system_prompt=None):
        """
        Analyze the sentiment of a conversation transcript
        
        Args:
            transcript: Text transcript of the conversation
            system_prompt: Optional system prompt to give context to Claude
            
        Returns:
            dict: The parsed response from Claude with sentiment analysis
        """
        if not system_prompt:
            system_prompt = """
            You are an expert in sentiment analysis. You will be provided with a transcript of a conversation.
            Analyze the transcript and provide sentiment analysis with the following elements:
            1. Overall sentiment of the conversation (positive, negative, neutral, mixed)
            2. Sentiment breakdown for each speaker
            3. Emotional tone and key emotions detected (joy, frustration, excitement, etc.)
            4. Any significant sentiment shifts during the conversation
            
            Present your analysis in a structured JSON format that could be easily parsed,
            with separate sections for overall sentiment and per-speaker sentiment.
            Include numerical scores where possible (on a scale of -1 to 1 for sentiment).
            """
        
        return self.analyze_text(transcript, system_prompt=system_prompt, max_tokens=2048) 