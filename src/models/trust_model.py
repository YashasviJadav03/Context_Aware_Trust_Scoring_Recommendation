"""
Trust model utilities and wrapper classes.
"""

import joblib
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from xgboost import XGBRegressor


class TrustModel:
    """
    Wrapper class for trust scoring model.
    """
    
    def __init__(self, model_path=None, scaler_path=None):
        """
        Initialize trust model.
        
        Args:
            model_path (str): Path to trained model
            scaler_path (str): Path to feature scaler
        """
        self.model = None
        self.scaler = None
        
        if model_path:
            self.load_model(model_path)
        if scaler_path:
            self.load_scaler(scaler_path)
    
    def load_model(self, model_path):
        """Load trained model."""
        self.model = joblib.load(model_path)
    
    def load_scaler(self, scaler_path):
        """Load feature scaler."""
        self.scaler = joblib.load(scaler_path)
    
    def predict(self, X):
        """
        Predict trust scores.
        
        Args:
            X (array-like): Feature matrix
            
        Returns:
            array: Trust scores
        """
        if self.model is None:
            raise ValueError("Model not loaded")
        
        # Scale features if scaler available
        if self.scaler is not None:
            X = self.scaler.transform(X)
        
        # Predict
        predictions = self.model.predict(X)
        
        # Clip to valid range
        return np.clip(predictions, 0, 1)
    
    def predict_single(self, features):
        """
        Predict trust score for single review.
        
        Args:
            features (dict): Feature dictionary
            
        Returns:
            float: Trust score
        """
        # Convert to DataFrame
        X = pd.DataFrame([features])
        
        # Predict
        score = self.predict(X)[0]
        
        return float(score)