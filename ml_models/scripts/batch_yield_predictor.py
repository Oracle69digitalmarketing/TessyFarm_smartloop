# tessyfarm_smartloop/ml_models/scripts/batch_yield_predictor.py
import pandas as pd
import joblib
import os
from datetime import datetime

# Database imports (assuming this script runs in an environment with access to DB models and session)
# This part needs careful setup for a standalone script/service to connect to the DB
# For now, we'll mock the DB interaction part.
# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker
# from your_project_root.backend_api.app.core.config import settings # Adjust path as needed
# from your_project_root.backend_api.app.models.farm import CropCycle, YieldPrediction # Adjust path

MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "saved_models")
MODEL_PATH = os.path.join(MODEL_DIR, "dummy_yield_model_v1.joblib")
MODEL_VERSION = "dummy_v1"

# Mock database connection and models for standalone run
class MockDBSession:
    def add(self, item): print(f"DB MOCK: Adding {item}")
    def commit(self): print("DB MOCK: Committing")
    def query(self, model): return self # Chain for filter
    def filter(self, *args): return self # Chain for first
    def first(self): return None # Simulate no existing prediction
    def close(self): print("DB MOCK: Closing session")

class MockCropCycle:
    def __init__(self, id, field_id, crop_type, planting_date):
        self.id = id
        self.field_id = field_id
        self.crop_type = crop_type
        self.planting_date = planting_date

class MockYieldPrediction:
    def __init__(self, **kwargs): self.__dict__.update(kwargs)
    def __repr__(self): return f"<MockYieldPrediction {self.predicted_yield_tonnes}>"


def get_active_crop_cycles_and_features(db_session):
    """
    In a real scenario:
    1. Query ongoing CropCycle records from the database.
    2. For each cycle, fetch and aggregate relevant sensor data from sensor_readings
       (e.g., avg_temp, total_soil_moisture between planting_date and now).
    3. Fetch other static features (planting_density_factor from field/crop_cycle config).
    Returns a list of dictionaries, each with features and crop_cycle_id.
    """
    print("MOCK: Fetching active crop cycles and their features...")
    # Simulate data for two active crop cycles
    return [
        {
            "crop_cycle_id": 101, # Assume this ID exists in your crop_cycles table
            "features": pd.DataFrame([{
                'avg_temp_season': 26.5, 'total_rainfall_mm_season': 300, # Up to now
                'soil_avg_moisture_season': 0.53, 'planting_density_factor': 1.05
            }])
        },
        {
            "crop_cycle_id": 102,
            "features": pd.DataFrame([{
                'avg_temp_season': 24.0, 'total_rainfall_mm_season': 250,
                'soil_avg_moisture_season': 0.49, 'planting_density_factor': 0.95
            }])
        }
    ]

def store_prediction(db_session, crop_cycle_id, predicted_yield, input_features_summary):
    """
    In a real scenario:
    1. Check if a prediction for this crop_cycle_id and model_version already exists.
    2. If yes, update it. If no, create a new YieldPrediction record.
    """
    print(f"MOCK: Storing prediction for crop_cycle_id {crop_cycle_id}: {predicted_yield:.2f} tonnes.")
    existing_prediction = db_session.query(MockYieldPrediction).filter(MockYieldPrediction.crop_cycle_id == crop_cycle_id).first()
    if existing_prediction:
        print(f"MOCK: Updating existing prediction for {crop_cycle_id}")
        existing_prediction.predicted_yield_tonnes = predicted_yield
        existing_prediction.prediction_date = datetime.utcnow()
        existing_prediction.input_features_summary = input_features_summary
    else:
        new_prediction = MockYieldPrediction(
            crop_cycle_id=crop_cycle_id,
            model_version=MODEL_VERSION,
            prediction_date=datetime.utcnow(),
            predicted_yield_tonnes=predicted_yield,
            input_features_summary=input_features_summary.to_dict('records')[0] # Store features as dict
        )
        db_session.add(new_prediction)
    db_session.commit()


def run_batch_predictions():
    print("Starting batch yield prediction process...")
    try:
        model = joblib.load(MODEL_PATH)
        print(f"Model {MODEL_PATH} loaded successfully.")
    except FileNotFoundError:
        print(f"ERROR: Model file not found at {MODEL_PATH}. Please train the model first.")
        return
    except Exception as e:
        print(f"Error loading model: {e}")
        return

    # db_session = SessionLocal() # In real app, get a SQLAlchemy session
    db_session = MockDBSession() # Using mock for now

    try:
        active_cycles_data = get_active_crop_cycles_and_features(db_session)
        if not active_cycles_data:
            print("No active crop cycles found or no features to process.")
            return

        for cycle_data in active_cycles_data:
            crop_cycle_id = cycle_data["crop_cycle_id"]
            features_df = cycle_data["features"]
            
            # Ensure feature names match what the model was trained on
            # In a real scenario, you'd have a robust feature engineering pipeline
            expected_features = ['avg_temp_season', 'total_rainfall_mm_season', 'soil_avg_moisture_season', 'planting_density_factor']
            if not all(col in features_df.columns for col in expected_features):
                print(f"ERROR: Missing expected features for crop_cycle_id {crop_cycle_id}. Skipping.")
                continue

            try:
                prediction = model.predict(features_df[expected_features]) # Ensure correct feature order/names
                predicted_yield = prediction[0] # Assuming single prediction
                print(f"Predicted yield for crop_cycle_id {crop_cycle_id}: {predicted_yield:.2f} tonnes")
                store_prediction(db_session, crop_cycle_id, predicted_yield, features_df)
            except Exception as e:
                print(f"Error during prediction or storing for crop_cycle_id {crop_cycle_id}: {e}")

    finally:
        db_session.close()
    print("Batch yield prediction process finished.")

if __name__ == "__main__":
    # This script would be run on a schedule (e.g., by a cron job or a Celery task)
    run_batch_predictions()
