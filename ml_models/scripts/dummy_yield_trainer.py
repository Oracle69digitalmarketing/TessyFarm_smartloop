# tessyfarm_smartloop/ml_models/scripts/dummy_yield_trainer.py
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
import joblib
import numpy as np
import os

MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "saved_models")
MODEL_PATH = os.path.join(MODEL_DIR, "dummy_yield_model_v1.joblib")

def train_dummy_model():
    print("Starting dummy model training...")
    # Simulate historical data
    # In a real scenario, this data would come from your database by querying
    # crop_cycles and joining with aggregated sensor_readings.
    data = {
        'avg_temp_season': [25, 26, 24, 27, 25, 28, 26, 23, 25, 27],
        'total_rainfall_mm_season': [500, 550, 480, 600, 520, 620, 530, 470, 510, 580],
        'soil_avg_moisture_season': [0.5, 0.55, 0.48, 0.6, 0.52, 0.62, 0.53, 0.47, 0.51, 0.58],
        'planting_density_factor': [1.0, 1.1, 0.9, 1.2, 1.0, 1.1, 0.95, 1.05, 1.15, 0.9],
        'actual_yield_tonnes': [5.0, 5.3, 4.7, 5.8, 5.1, 6.0, 5.4, 4.5, 5.2, 5.7] # Target
    }
    df = pd.DataFrame(data)

    X = df[['avg_temp_season', 'total_rainfall_mm_season', 'soil_avg_moisture_season', 'planting_density_factor']]
    y = df['actual_yield_tonnes']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = RandomForestRegressor(n_estimators=100, random_state=42, oob_score=True) # Added oob_score
    model.fit(X_train, y_train)

    predictions = model.predict(X_test)
    mse = mean_squared_error(y_test, predictions)
    rmse = np.sqrt(mse)
    print(f"Model Training Complete.")
    print(f"Test RMSE: {rmse:.2f}")
    if hasattr(model, 'oob_score_') and model.oob_score_: # Check if oob_score is available
         print(f"Model OOB Score: {model.oob_score_:.4f}")


    # Save the model
    if not os.path.exists(MODEL_DIR):
        os.makedirs(MODEL_DIR)
    joblib.dump(model, MODEL_PATH)
    print(f"Model saved to {MODEL_PATH}")

if __name__ == "__main__":
    train_dummy_model()
