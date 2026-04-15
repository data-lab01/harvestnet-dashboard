import numpy as np
from typing import Dict, List, Tuple
from datetime import datetime, timedelta

class StorageLifePredictor:
    """Predicts safe storage days remaining based on sensor data"""
    
    def __init__(self):
        # Crop-specific coefficients (simplified - would be trained from real data)
        self.crop_params = {
            "maize": {"base_life": 180, "temp_coef": -8, "humid_coef": -3, "moisture_coef": -12},
            "rice": {"base_life": 200, "temp_coef": -6, "humid_coef": -2, "moisture_coef": -15},
            "wheat": {"base_life": 160, "temp_coef": -7, "humid_coef": -3, "moisture_coef": -10},
            "tomato": {"base_life": 14, "temp_coef": -1.5, "humid_coef": -0.8, "moisture_coef": 0},
            "onion": {"base_life": 90, "temp_coef": -4, "humid_coef": -5, "moisture_coef": -8},
            "potato": {"base_life": 120, "temp_coef": -5, "humid_coef": -2, "moisture_coef": -6},
        }
    
    def predict_safe_days(
        self, 
        crop_type: str, 
        current_temp: float, 
        current_humidity: float, 
        moisture_content: float,
        days_stored_so_far: int
    ) -> Tuple[int, float, str]:
        """
        Returns: (days_remaining, mold_risk_percent, recommendation)
        """
        params = self.crop_params.get(crop_type.lower(), self.crop_params["maize"])
        
        # Calculate deterioration rate
        temp_factor = max(0, (current_temp - 20) * params["temp_coef"])
        humid_factor = max(0, (current_humidity - 65) * params["humid_coef"])
        moisture_factor = max(0, (moisture_content - 13) * params["moisture_coef"]) if moisture_content else 0
        
        daily_loss_rate = (temp_factor + humid_factor + moisture_factor) / 100
        daily_loss_rate = max(0.002, min(0.1, daily_loss_rate))  # Clamp between 0.2% and 10%
        
        # Calculate remaining days (stop at 5% loss)
        remaining_days = int((0.05 - (daily_loss_rate * days_stored_so_far)) / daily_loss_rate)
        remaining_days = max(0, min(params["base_life"], remaining_days))
        
        # Calculate mold risk
        mold_risk = min(100, max(0, 
            (current_humidity - 70) * 3.33 +  # 0% at 70%, 100% at 100%
            (current_temp - 25) * 2 +          # 0% at 25°C, 50% at 50°C
            (moisture_content - 14) * 10 if moisture_content else 0
        ))
        
        # Generate recommendation
        if remaining_days <= 7:
            recommendation = "SELL IMMEDIATELY - Critical loss risk"
            status_color = "red"
        elif remaining_days <= 30:
            recommendation = "Plan to sell within 2 weeks"
            status_color = "yellow"
        else:
            recommendation = "Safe storage - monitor regularly"
            status_color = "green"
        
        return remaining_days, mold_risk, recommendation, status_color