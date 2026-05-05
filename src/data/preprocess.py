"""
Data preprocessing utilities for trust scoring system.
"""

import pandas as pd
import numpy as np
import re


def clean_review_text(text):
    """
    Clean review text for processing.
    
    Args:
        text (str): Raw review text
        
    Returns:
        str: Cleaned text
    """
    if pd.isna(text) or text == 'nan':
        return ''
    
    text = str(text)
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove special characters but keep punctuation
    text = re.sub(r'[^\w\s\.\!\?\,\;\:]', '', text)
    
    # Strip whitespace
    text = text.strip()
    
    return text


def preprocess_reviews(df):
    """
    Preprocess review DataFrame.
    
    Args:
        df (pd.DataFrame): Raw review data
        
    Returns:
        pd.DataFrame: Preprocessed data
    """
    df = df.copy()
    
    # Clean text
    if 'text' in df.columns:
        df['text'] = df['text'].apply(clean_review_text)
    
    # Handle missing values
    df['rating'] = df['rating'].fillna(3)
    df['verified'] = df['verified'].fillna(False)
    df['helpful_votes'] = df['helpful_votes'].fillna(0)
    df['total_votes'] = df['total_votes'].fillna(0)
    
    return df