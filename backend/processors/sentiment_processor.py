#!/usr/bin/env python3
import os
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import logging
import traceback
from matplotlib.ticker import FuncFormatter
from matplotlib.patches import Patch
from matplotlib.gridspec import GridSpec

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('processors/sentiment_processor.log', mode='a')
    ]
)

class SentimentProcessor:
    def __init__(self, predictions_file_path):
        """
        Initialize the Sentiment Processor.
        
        Args:
            predictions_file_path: Path to the predictions JSON file (job_job_id_predictions.json)
        """
        self.predictions_file_path = predictions_file_path
        self.predictions = None
        self.processed_data = None
        self.speakers_data = {}  # Data organized by speaker
        self.top_sentiments = []  # Store the top sentiments across the conversation
        self.quintile_analysis = {}  # Store the quintile analysis results
        self.conversation_length = 0  # Length of the entire conversation in seconds
        
        # Configure logging
        self.logger = logging.getLogger(__name__)
        
        # Set up a colorful palette for different sentiments
        self.colors = list(mcolors.TABLEAU_COLORS.values())
        # Extend with more colors if needed
        self.colors.extend(list(mcolors.CSS4_COLORS.values())[:20])
        
        # Load the predictions
        self._load_predictions()
    
    def _load_predictions(self):
        """
        Load the predictions from the JSON file.
        """
        try:
            self.logger.info(f"Loading predictions from {self.predictions_file_path}")
            with open(self.predictions_file_path, 'r', encoding='utf-8') as f:
                self.predictions = json.load(f)
            
            # Debug the structure of the predictions
            if isinstance(self.predictions, list):
                self.logger.info(f"Predictions format: list with {len(self.predictions)} items")
            elif isinstance(self.predictions, dict):
                keys = list(self.predictions.keys())
                self.logger.info(f"Predictions format: dict with keys {keys}")
                
                # Additional debug info about the structure
                if "models" in self.predictions:
                    model_keys = list(self.predictions["models"].keys())
                    self.logger.debug(f"Found models: {model_keys}")
                    
                    # Check for language model
                    if "language" in model_keys:
                        language_keys = list(self.predictions["models"]["language"].keys())
                        self.logger.debug(f"Language model keys: {language_keys}")
                        
                        # Check for speaker segments
                        if "speaker_segments" in language_keys:
                            num_segments = len(self.predictions["models"]["language"]["speaker_segments"])
                            self.logger.debug(f"Found {num_segments} speaker segments")
                
                # Check for source-style format
                if "source" in self.predictions and "results" in self.predictions:
                    self.logger.debug("Source-style prediction format detected")
                    if "predictions" in self.predictions["results"]:
                        pred_count = len(self.predictions["results"]["predictions"])
                        self.logger.debug(f"Found {pred_count} predictions in results")
            else:
                self.logger.warning(f"Unexpected predictions format: {type(self.predictions)}")
        except json.JSONDecodeError as e:
            self.logger.error(f"Error decoding JSON: {str(e)}")
            self.logger.debug(f"Error at position {e.pos}, line: {e.lineno}, column: {e.colno}")
            self.predictions = None
        except Exception as e:
            self.logger.error(f"Error loading predictions: {str(e)}")
            self.logger.debug(traceback.format_exc())
            self.predictions = None
    
    def process_sentiment_data(self):
        """
        Process the sentiment data from the predictions to extract the top sentiments 
        for each segment, organized by speaker and time.
        
        Returns:
            DataFrame: A DataFrame containing the speaker and sentiment data
        """
        if not self.predictions:
            self.logger.error("No predictions available, cannot process data")
            return None
        
        # List to store processed data
        data = []
        
        try:
            self.logger.info("Starting to extract speaker segments from predictions")
            
            # Handle different prediction formats - start with the source-results format
            if isinstance(self.predictions, list) and len(self.predictions) > 0:
                for pred_item in self.predictions:
                    if "source" in pred_item and "results" in pred_item and "predictions" in pred_item["results"]:
                        for result_item in pred_item["results"]["predictions"]:
                            # Check for models > prosody > grouped_predictions format
                            if "models" in result_item and "prosody" in result_item["models"]:
                                prosody_data = result_item["models"]["prosody"]
                                
                                if "grouped_predictions" in prosody_data:
                                    self.logger.info(f"Found grouped_predictions in prosody data")
                                    grouped_predictions = prosody_data["grouped_predictions"]
                                    
                                    for speaker_group in grouped_predictions:
                                        speaker_id = speaker_group.get("id", "unknown")
                                        self.logger.info(f"Processing data for speaker: {speaker_id}")
                                        
                                        if "predictions" in speaker_group:
                                            speaker_predictions = speaker_group["predictions"]
                                            
                                            for segment in speaker_predictions:
                                                segment_data = {
                                                    'speaker_id': speaker_id,
                                                    'start_time': segment.get("time", {}).get("begin", 0),
                                                    'end_time': segment.get("time", {}).get("end", 0),
                                                    'text': segment.get("text", "")
                                                }
                                                
                                                # Extract emotions data as sentiments
                                                if "emotions" in segment:
                                                    emotions = segment["emotions"]
                                                    # Sort by score to get top emotions
                                                    emotions = sorted(emotions, key=lambda x: x.get("score", 0), reverse=True)
                                                    
                                                    # Add top 15 emotions to the segment data as sentiments
                                                    for i, emotion in enumerate(emotions[:15], 1):
                                                        segment_data[f'sentiment_{i}'] = emotion.get("name", "Unknown")
                                                        segment_data[f'sentiment_score_{i}'] = emotion.get("score", 0)
                                                    
                                                    # Log top emotions for debugging
                                                    top_emotions = [(e.get("name"), e.get("score")) for e in emotions[:3]]
                                                    self.logger.debug(f"Top emotions for segment: {top_emotions}")
                                                    
                                                data.append(segment_data)
                            
                            # Also check for language model data if available
                            if "models" in result_item and "language" in result_item["models"]:
                                language_data = result_item["models"]["language"]
                                
                                if "grouped_predictions" in language_data:
                                    self.logger.info(f"Found grouped_predictions in language data")
                                    grouped_predictions = language_data["grouped_predictions"]
                                    
                                    for speaker_group in grouped_predictions:
                                        speaker_id = speaker_group.get("id", "unknown")
                                        self.logger.info(f"Processing language data for speaker: {speaker_id}")
                                        
                                        if "predictions" in speaker_group:
                                            speaker_predictions = speaker_group["predictions"]
                                            
                                            for segment in speaker_predictions:
                                                # Check if we already have this segment (based on time) from prosody
                                                start_time = segment.get("time", {}).get("begin", 0)
                                                end_time = segment.get("time", {}).get("end", 0)
                                                
                                                # Create or update segment data
                                                segment_data = {
                                                    'speaker_id': speaker_id,
                                                    'start_time': start_time,
                                                    'end_time': end_time,
                                                    'text': segment.get("text", "")
                                                }
                                                
                                                # Extract sentiment data if available
                                                if "sentiment" in segment:
                                                    sentiments = segment["sentiment"]
                                                    # Sort by score to get top sentiments
                                                    sentiments = sorted(sentiments, key=lambda x: x.get("score", 0), reverse=True)
                                                    
                                                    # Add top 15 sentiments to the segment data
                                                    for i, sentiment in enumerate(sentiments[:15], 1):
                                                        segment_data[f'sentiment_{i}'] = sentiment.get("name", "Unknown")
                                                        segment_data[f'sentiment_score_{i}'] = sentiment.get("score", 0)
                                                
                                                # Add to data list if not already present
                                                # This is a simplistic check - in production you might want a more
                                                # sophisticated way to merge segments with the same time range
                                                if not any(d['speaker_id'] == speaker_id and 
                                                          d['start_time'] == start_time and 
                                                          d['end_time'] == end_time for d in data):
                                                    data.append(segment_data)
            
            if not data:
                self.logger.warning("No speaker or sentiment data found in the predictions")
                # Try to log more details about the structure to help diagnose the issue
                self._log_prediction_structure(self.predictions)
                return None
            
            self.logger.info(f"Extracted {len(data)} segments with speaker and sentiment data")
            
            # Create DataFrame and sort by time
            df = pd.DataFrame(data)
            df = df.sort_values('start_time')
            df = df.reset_index(drop=True)
            
            # Calculate conversation length based on the last segment end time
            self.conversation_length = df['end_time'].max()
            self.logger.info(f"Total conversation length: {self.conversation_length:.2f} seconds")
            
            # Add quintile column to each segment
            df['quintile'] = df.apply(
                lambda row: self._determine_quintile(row['start_time'], row['end_time']), 
                axis=1
            )
            
            # Log some information about the data
            speaker_counts = df['speaker_id'].value_counts()
            self.logger.info(f"Speaker segments distribution: {dict(speaker_counts)}")
            
            # Collect all unique sentiments from the data
            all_sentiments = set()
            for i in range(1, 16):  # Check sentiment columns
                col = f'sentiment_{i}'
                if col in df.columns:
                    all_sentiments.update(df[col].dropna().unique())
            
            # Count sentiment frequencies
            sentiment_counts = {}
            for sentiment in all_sentiments:
                count = 0
                for i in range(1, 16):
                    col = f'sentiment_{i}'
                    if col in df.columns:
                        count += (df[col] == sentiment).sum()
                sentiment_counts[sentiment] = count
            
            # Sort by frequency and get top 15
            top_sentiments = sorted(sentiment_counts.items(), key=lambda x: x[1], reverse=True)
            self.top_sentiments = [s[0] for s in top_sentiments[:15]]
            
            self.logger.info(f"Top 15 sentiments across conversation: {', '.join(self.top_sentiments)}")
            
            # Create a streamlined DataFrame with just the top 15 sentiments
            self._create_streamlined_data(df)
            
            # Perform quintile analysis
            self._analyze_quintiles(df)
            
            # Store the processed data
            self.processed_data = df
            
            return df
        except Exception as e:
            self.logger.error(f"Error processing sentiment data: {str(e)}")
            self.logger.debug(traceback.format_exc())
            return None
    
    def _determine_quintile(self, start_time, end_time):
        """
        Determine which quintile a segment belongs to.
        For segments that span multiple quintiles, we use the midpoint.
        
        Args:
            start_time: Start time of the segment in seconds
            end_time: End time of the segment in seconds
            
        Returns:
            int: Quintile number (0-4) where 0 is the first quintile (0-20%)
        """
        if self.conversation_length == 0:
            return 0
            
        # Use the midpoint of the segment to determine quintile
        midpoint = (start_time + end_time) / 2
        quintile_size = self.conversation_length / 5
        
        # Calculate quintile (0-4)
        quintile = int(midpoint / quintile_size)
        
        # Handle edge case for exactly at the end
        if quintile == 5:
            quintile = 4
            
        return quintile
        
    def _analyze_quintiles(self, df):
        """
        Analyze sentiment by quintiles for each speaker.
        
        Args:
            df: DataFrame with the processed data including quintile information
        """
        try:
            self.logger.info("Starting quintile analysis")
            
            # Get unique speakers
            speakers = df['speaker_id'].unique()
            
            # Initialize the quintile analysis structure
            quintile_analysis = {
                "conversation_length_seconds": self.conversation_length,
                "speakers": {}
            }
            
            for speaker in speakers:
                # Filter data for this speaker
                speaker_data = df[df['speaker_id'] == speaker]
                
                # Initialize speaker's quintile data
                speaker_quintiles = {}
                
                # Process each quintile
                for quintile in range(5):  # 0-4 for the five quintiles
                    # Filter for the current quintile
                    quintile_data = speaker_data[speaker_data['quintile'] == quintile]
                    
                    # Skip if no data in this quintile
                    if quintile_data.empty:
                        continue
                        
                    # Calculate segment durations
                    quintile_data['duration'] = quintile_data['end_time'] - quintile_data['start_time']
                    total_duration = quintile_data['duration'].sum()
                    
                    # Create a dictionary to store weighted emotions
                    weighted_emotions = {}
                    
                    # Process each segment in the quintile
                    for _, segment in quintile_data.iterrows():
                        segment_duration = segment['duration']
                        weight = segment_duration / total_duration if total_duration > 0 else 0
                        
                        # Process each emotion in the segment
                        for i in range(1, 16):  # Check top 15 emotions
                            sentiment_col = f'sentiment_{i}'
                            score_col = f'sentiment_score_{i}'
                            
                            if sentiment_col in segment and score_col in segment:
                                sentiment_name = segment[sentiment_col]
                                sentiment_score = segment[score_col]
                                
                                # Add validation to ensure the sentiment name is a proper string, not a numeric value
                                if pd.notna(sentiment_name) and pd.notna(sentiment_score):
                                    # Skip numeric sentiment names or convert them to strings with prefix
                                    if isinstance(sentiment_name, (int, float)) or (isinstance(sentiment_name, str) and sentiment_name.isdigit()):
                                        sentiment_name = f"Emotion_{sentiment_name}"
                                    
                                    # Add to weighted emotions dict
                                    if sentiment_name not in weighted_emotions:
                                        weighted_emotions[sentiment_name] = 0
                                    
                                    # Add weighted score
                                    weighted_emotions[sentiment_name] += sentiment_score * weight
                    
                    # Find the dominant emotion for this quintile
                    if weighted_emotions:
                        dominant_emotion = max(weighted_emotions.items(), key=lambda x: x[1])
                        
                        # Calculate quintile time range
                        quintile_size = self.conversation_length / 5
                        start_time = quintile * quintile_size
                        end_time = (quintile + 1) * quintile_size
                        
                        # Store quintile analysis
                        quintile_label = f"quintile_{quintile+1}"  # 1-indexed for output
                        speaker_quintiles[quintile_label] = {
                            "time_range": f"{start_time:.2f}-{end_time:.2f}s",
                            "dominant_emotion": dominant_emotion[0],
                            "emotion_score": dominant_emotion[1],
                            "top_emotions": sorted(
                                weighted_emotions.items(), 
                                key=lambda x: x[1], 
                                reverse=True
                            )[:5]  # Get top 5 emotions
                        }
                
                # Add this speaker's data to the overall analysis
                quintile_analysis["speakers"][speaker] = speaker_quintiles
            
            self.quintile_analysis = quintile_analysis
            self.logger.info("Completed quintile analysis")
            
        except Exception as e:
            self.logger.error(f"Error in quintile analysis: {str(e)}")
            self.logger.debug(traceback.format_exc())
    
    def _create_streamlined_data(self, df):
        """
        Create a streamlined version of the data with just the top sentiments.
        
        Args:
            df: The full DataFrame with all sentiment data
        """
        try:
            # Create a copy with essential columns
            streamlined_df = df[['speaker_id', 'start_time', 'end_time', 'text', 'quintile']].copy()
            
            # Add columns for each top sentiment
            for sentiment in self.top_sentiments:
                streamlined_df[sentiment] = 0.0  # Initialize with zeros
                
                # Find the sentiment across all columns and get the max score
                for i in range(1, 16):
                    sentiment_col = f'sentiment_{i}'
                    score_col = f'sentiment_score_{i}'
                    
                    if sentiment_col in df.columns and score_col in df.columns:
                        # Where the sentiment matches, get the score
                        matches = df[sentiment_col] == sentiment
                        # Add the score where there are matches
                        streamlined_df.loc[matches, sentiment] = df.loc[matches, score_col].values
            
            self.processed_data = streamlined_df
            self.logger.info(f"Created streamlined data with {len(self.top_sentiments)} sentiment columns")
            
        except Exception as e:
            self.logger.error(f"Error creating streamlined data: {str(e)}")
            self.logger.debug(traceback.format_exc())
    
    def _log_prediction_structure(self, prediction_data, prefix="", depth=0):
        """
        Recursively log the structure of the prediction data for debugging.
        
        Args:
            prediction_data: The prediction data to log
            prefix: Prefix for the log line to show structure
            depth: Current depth in the structure
        """
        if depth > 5:
            self.logger.debug(f"{prefix}[Maximum depth reached]")
            return
            
        if isinstance(prediction_data, dict):
            self.logger.debug(f"{prefix}Dict with {len(prediction_data)} keys: {list(prediction_data.keys())}")
            for key, value in list(prediction_data.items())[:3]:  # Show first 3 items only
                self.logger.debug(f"{prefix} - {key}:")
                self._log_prediction_structure(value, prefix + "   ", depth + 1)
            if len(prediction_data) > 3:
                self.logger.debug(f"{prefix} ... [{len(prediction_data) - 3} more keys]")
        elif isinstance(prediction_data, list):
            self.logger.debug(f"{prefix}List with {len(prediction_data)} items")
            for i, item in enumerate(prediction_data[:3]):  # Show first 3 items only
                self.logger.debug(f"{prefix} - Item {i}:")
                self._log_prediction_structure(item, prefix + "   ", depth + 1)
            if len(prediction_data) > 3:
                self.logger.debug(f"{prefix} ... [{len(prediction_data) - 3} more items]")
        else:
            self.logger.debug(f"{prefix}Value: {type(prediction_data)} {str(prediction_data)[:100]}")
    
    def _organize_data_by_speaker(self):
        """
        Organize the processed data by speaker.
        """
        if self.processed_data is None:
            self.logger.warning("No processed data available. Run process_sentiment_data() first.")
            return
            
        # Group by speaker
        for speaker, data in self.processed_data.groupby('speaker_id'):
            self.speakers_data[speaker] = data
        
        self.logger.info(f"Organized data for {len(self.speakers_data)} speakers")
    
    def get_top_sentiments(self, n=15):
        """
        Get the top N sentiments across the conversation.
        
        Args:
            n: Number of top sentiments to return (default: 15)
            
        Returns:
            list: The top N sentiments
        """
        if not self.top_sentiments:
            self.logger.warning("No top sentiments computed yet. Run process_sentiment_data() first.")
            return []
            
        return self.top_sentiments[:n]
        
    def get_quintile_analysis(self):
        """
        Get the quintile analysis results.
        
        Returns:
            dict: The quintile analysis results
        """
        return self.quintile_analysis
    
    def save_quintile_analysis(self, output_path):
        """
        Save the quintile analysis to a JSON file.
        
        Args:
            output_path: Path to save the JSON file
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if not self.quintile_analysis:
                self.logger.warning("No quintile analysis available. Run process_sentiment_data() first.")
                return False
                
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(self.quintile_analysis, f, indent=2)
                
            self.logger.info(f"Saved quintile analysis to {output_path}")
            return True
        except Exception as e:
            self.logger.error(f"Error saving quintile analysis: {str(e)}")
            self.logger.debug(traceback.format_exc())
            return False
    
    def plot_sentiment_evolution(self, output_path, top_n_sentiments=15, figsize=(14, 10)):
        """
        Plot the evolution of sentiment over time.
        
        Args:
            output_path: Path to save the plot
            top_n_sentiments: Number of top sentiments to include in the plot
            figsize: Size of the figure (width, height) in inches
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if self.processed_data is None:
                self.logger.warning("No processed data available. Run process_sentiment_data() first.")
                return False
                
            # Get top sentiments to plot
            if not self.top_sentiments:
                self.logger.warning("No top sentiments computed yet.")
                return False
                
            top_sentiments = self.top_sentiments[:top_n_sentiments]
            
            # Organize data by speaker if not already done
            if not self.speakers_data:
                self._organize_data_by_speaker()
            
            # Create a figure with two subplots - one for each speaker
            plt.figure(figsize=figsize)
            gs = GridSpec(2, 1, height_ratios=[4, 1])
            
            ax_main = plt.subplot(gs[0])
            ax_legend = plt.subplot(gs[1])
            
            # Plot lines for each speaker-sentiment combination
            for i, (speaker, df) in enumerate(self.speakers_data.items()):
                # Sort by time
                df = df.sort_values('start_time')
                
                # For each top sentiment, plot a line
                for j, sentiment in enumerate(top_sentiments):
                    if sentiment in df.columns:
                        # Use rolling mean to smooth the values
                        window_size = min(5, len(df)) if len(df) > 1 else 1
                        smoothed = df[sentiment].rolling(window=window_size, center=True, min_periods=1).mean()
                        
                        # Plot with speaker-based color and sentiment-based line style
                        line_style = ['-', '--', '-.', ':'][j % 4]
                        color = self.colors[i % len(self.colors)]
                        
                        ax_main.plot(
                            df['start_time'], 
                            smoothed, 
                            label=f"{speaker} - {sentiment}",
                            linestyle=line_style,
                            color=color,
                            alpha=0.8,
                            linewidth=2
                        )
            
            # Set up the main plot
            ax_main.set_title("Evolution of Sentiment Over Time", fontsize=16)
            ax_main.set_xlabel("Time (seconds)", fontsize=12)
            ax_main.set_ylabel("Sentiment Score", fontsize=12)
            ax_main.grid(True, alpha=0.3)
            
            # Add vertical lines for quintiles
            if self.conversation_length > 0:
                quintile_size = self.conversation_length / 5
                for i in range(1, 5):  # 4 lines for 5 quintiles
                    quintile_time = i * quintile_size
                    ax_main.axvline(
                        x=quintile_time, 
                        color='gray', 
                        linestyle='--', 
                        alpha=0.5,
                        label=f"Quintile {i}" if i == 1 else ""
                    )
                    ax_main.text(
                        quintile_time, 
                        ax_main.get_ylim()[1] * 0.95,
                        f"Q{i+1}",
                        horizontalalignment='center',
                        verticalalignment='top',
                        fontsize=10,
                        alpha=0.7
                    )
            
            # Create custom time formatter for x-axis
            def format_time(x, pos):
                minutes = int(x // 60)
                seconds = int(x % 60)
                return f"{minutes}:{seconds:02d}"
            
            ax_main.xaxis.set_major_formatter(FuncFormatter(format_time))
            
            # Create custom legend in the second subplot
            ax_legend.axis('off')  # Turn off axis
            
            # Create legend items
            legend_items = []
            for i, (speaker, _) in enumerate(self.speakers_data.items()):
                color = self.colors[i % len(self.colors)]
                legend_items.append(Patch(color=color, label=f"Speaker: {speaker}"))
            
            # Add sentiment legend items
            for j, sentiment in enumerate(top_sentiments):
                line_style = ['-', '--', '-.', ':'][j % 4]
                legend_items.append(plt.Line2D([0], [0], color='black', linestyle=line_style, label=sentiment))
            
            # Add legend
            ax_legend.legend(
                handles=legend_items,
                loc='center',
                ncol=min(5, len(legend_items)),
                fontsize=10,
                frameon=True,
                fancybox=True,
                shadow=True
            )
            
            # Adjust layout
            plt.tight_layout()
            
            # Save figure
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            self.logger.info(f"Saved sentiment evolution plot to {output_path}")
            
            # Close the figure to free memory
            plt.close()
            
            return True
        
        except Exception as e:
            self.logger.error(f"Error creating sentiment evolution plot: {str(e)}")
            self.logger.debug(traceback.format_exc())
            return False
    
    def save_processed_data(self, output_path):
        """
        Save the processed data to a CSV file.
        
        Args:
            output_path: Path to save the CSV file
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if self.processed_data is None:
                self.logger.warning("No processed data available. Run process_sentiment_data() first.")
                return False
                
            self.processed_data.to_csv(output_path, index=False)
            self.logger.info(f"Saved processed data to {output_path}")
            return True
        except Exception as e:
            self.logger.error(f"Error saving processed data: {str(e)}")
            self.logger.debug(traceback.format_exc())
            return False 