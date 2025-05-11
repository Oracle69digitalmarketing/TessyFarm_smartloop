# tessyfarm_smartloop/ml_models/scripts/batch_yield_predictor.py
import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime
import joblib
import json

# --- Path Setup for Module Imports ---
CONTAINER_BACKEND_API_ROOT = "/app"
if CONTAINER_BACKEND_API_ROOT not in sys.path:
    sys.path.insert(0, CONTAINER_BACKEND_API_ROOT)

# --- Database and Configuration Imports ---
try:
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker, Session
    from app.core.config import settings as app_settings
    from app.models.farm import CropCycle, SensorReading, Field, YieldPrediction # Import YieldPrediction
except ImportError as e:
    print(f"Error importing backend modules: {e}")
    print(f"Ensure backend_api is mounted at /app in Docker and PYTHONPATH is effectively /app.")
    print(f"Current sys.path: {sys.path}")
    sys.exit(1)

# --- Constants for Model Artifact Paths ---
BASE_ML_MODELS_PATH_IN_CONTAINER = "/app/ml_models"
MODEL_DIR = os.path.join(BASE_ML_MODELS_PATH_IN_CONTAINER, "saved_models")
MODEL_FILENAME = "yield_prediction_model_v1.joblib"
SCALER_FILENAME = "yield_feature_scaler_v1.joblib"
FEATURE_NAMES_FILENAME = "yield_model_feature_names_v1.json"
MODEL_VERSION = "v1" # Version of your model logic/features

MODEL_PATH = os.path.join(MODEL_DIR, MODEL_FILENAME)
SCALER_PATH = os.path.join(MODEL_DIR, SCALER_FILENAME)
FEATURE_NAMES_PATH = os.path.join(MODEL_DIR, FEATURE_NAMES_FILENAME)

# --- Database Setup ---
db_url = app_settings.ASSEMBLED_DATABASE_URL
engine = create_engine(db_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def load_model_artifacts():
    """Loads the model, scaler, and feature names."""
    print("Loading model artifacts...")
    if not all([os.path.exists(MODEL_PATH), os.path.exists(SCALER_PATH), os.path.exists(FEATURE_NAMES_PATH)]):
        print("Error: One or more model artifacts (model, scaler, feature_names) not found.")
        print(f"Checked paths: \n  Model: {MODEL_PATH}\n  Scaler: {SCALER_PATH}\n  Features: {FEATURE_NAMES_PATH}")
        return None, None, None
    
    model = joblib.load(MODEL_PATH)
    scaler = joblib.load(SCALER_PATH)
    with open(FEATURE_NAMES_PATH, 'r') as f:
        feature_names = json.load(f)
    
    print("Model, scaler, and feature names loaded successfully.")
    return model, scaler, feature_names

def fetch_and_engineer_prediction_features(db: Session, trained_feature_names: list) -> pd.DataFrame:
    """
    Fetches active crop cycles and engineers features for prediction.
    The feature engineering logic MUST MATCH the training script.
    """
    print("Fetching active crop cycles for prediction...")
    # Query active crop cycles (actual_harvest_date is NULL)
    query = db.query(
        CropCycle.id.label("crop_cycle_id"),
        CropCycle.field_id,
        CropCycle.crop_type,
        CropCycle.planting_date,
        Field.area_hectares.label("field_area_hectares"),
        Field.soil_type
    ).join(Field, CropCycle.field_id == Field.id)\
     .filter(CropCycle.actual_harvest_date.is_(None)) # Active cycles
    
    active_cycles_df = pd.read_sql(query.statement, db.bind)
    print(f"Found {len(active_cycles_df)} active crop cycles.")
    if active_cycles_df.empty:
        return pd.DataFrame()

    all_features_for_prediction_list = []
    for index, cycle in active_cycles_df.iterrows():
        print(f"Processing active crop cycle ID: {cycle['crop_cycle_id']} (Field ID: {cycle['field_id']})")
        
        # Fetch sensor data from planting_date to NOW
        sensor_query = db.query(SensorReading)\
            .filter(SensorReading.timestamp >= cycle['planting_date'])\
            .filter(SensorReading.timestamp <= datetime.utcnow()) \
            .filter(SensorReading.device_id.contains(f"field_{cycle['field_id']}"))

        sensor_df = pd.read_sql(sensor_query.statement, db.bind)
        
        if sensor_df.empty:
            print(f"  No sensor data found for active cycle {cycle['crop_cycle_id']}. Using NaNs for sensor features.")
            # Create a features dict with NaNs for sensor-derived features
            # This allows prediction even with missing sensor data if model handles NaNs (after scaling)
            # or if imputation is done. For now, NaNs will propagate.
            current_features = {"crop_cycle_id": cycle['crop_cycle_id']}
            sensor_feature_names = ['avg_temp', 'min_temp', 'max_temp', 'avg_humidity', 'avg_soil_moisture', 'gdd_approx']
            for feat_name in sensor_feature_names:
                current_features[feat_name] = np.nan
        else:
            current_features = {"crop_cycle_id": cycle['crop_cycle_id']}
            current_features['avg_temp'] = sensor_df['temperature'].mean() if 'temperature' in sensor_df else np.nan
            current_features['min_temp'] = sensor_df['temperature'].min() if 'temperature' in sensor_df else np.nan
            current_features['max_temp'] = sensor_df['temperature'].max() if 'temperature' in sensor_df else np.nan
            current_features['avg_humidity'] = sensor_df['humidity'].mean() if 'humidity' in sensor_df else np.nan
            current_features['avg_soil_moisture'] = sensor_df['soil_moisture'].mean() if 'soil_moisture' in sensor_df else np.nan
            
            t_base = 10
            # Cycle duration for prediction is from planting to now
            cycle_duration_days_so_far = (datetime.utcnow() - cycle['planting_date']).days
            current_features['cycle_duration_days'] = cycle_duration_days_so_far if cycle_duration_days_so_far > 0 else 0

            if pd.notna(current_features['max_temp']) and pd.notna(current_features['min_temp']) and cycle_duration_days_so_far > 0:
                avg_daily_temp_proxy = (current_features['max_temp'] + current_features['min_temp']) / 2
                current_features['gdd_approx'] = max(0, avg_daily_temp_proxy - t_base) * cycle_duration_days_so_far
            else:
                current_features['gdd_approx'] = np.nan
        
        # Static features
        current_features['field_area_hectares'] = cycle['field_area_hectares']
        # Add encoded categorical features here if they were used in training
        # current_features['crop_type_encoded'] = encode_crop_type(cycle['crop_type'])
        # current_features['soil_type_encoded'] = encode_soil_type(cycle['soil_type'])
        
        all_features_for_prediction_list.append(current_features)
        print(f"  Engineered features for prediction for crop cycle {cycle['crop_cycle_id']}.")

    if not all_features_for_prediction_list:
        return pd.DataFrame()
        
    features_df = pd.DataFrame(all_features_for_prediction_list)
    
    # Ensure all columns expected by the model are present, even if all NaN, and in correct order
    # This is crucial if some active cycles had no sensor data, leading to missing columns.
    # Or if some categorical features are not present in the current batch.
    final_features_df = pd.DataFrame(columns=trained_feature_names)
    for crop_cycle_id, group in features_df.groupby('crop_cycle_id'):
        row_dict = {'crop_cycle_id': crop_cycle_id}
        for col in trained_feature_names: # Iterate through the order of features model was trained on
            if col in group.columns:
                row_dict[col] = group[col].iloc[0] # Assumes one row per crop_cycle_id after this stage
            else:
                row_dict[col] = np.nan # Add NaN if feature couldn't be engineered (e.g. no sensor data)
        final_features_df = pd.concat([final_features_df, pd.DataFrame([row_dict])], ignore_index=True)

    return final_features_df


def store_predictions(db: Session, predictions_data: list):
    """Stores or updates yield predictions in the database."""
    if not predictions_data:
        return

    for pred_data in predictions_data:
        crop_cycle_id = pred_data['crop_cycle_id']
        predicted_yield = pred_data['predicted_yield_tonnes']
        input_features = pred_data['input_features_summary']

        # Check if a prediction for this cycle and model version already exists
        existing_prediction = db.query(YieldPrediction)\
            .filter(YieldPrediction.crop_cycle_id == crop_cycle_id)\
            .filter(YieldPrediction.model_version == MODEL_VERSION)\
            .first()

        if existing_prediction:
            print(f"Updating existing prediction for crop_cycle_id {crop_cycle_id} with model {MODEL_VERSION}.")
            existing_prediction.predicted_yield_tonnes = predicted_yield
            existing_prediction.prediction_date = datetime.utcnow()
            existing_prediction.input_features_summary = input_features
        else:
            print(f"Creating new prediction for crop_cycle_id {crop_cycle_id} with model {MODEL_VERSION}.")
            db_prediction = YieldPrediction(
                crop_cycle_id=crop_cycle_id,
                model_version=MODEL_VERSION,
                prediction_date=datetime.utcnow(),
                predicted_yield_tonnes=predicted_yield,
                input_features_summary=input_features
                # confidence_score can be added if model provides it
            )
            db.add(db_prediction)
    
    try:
        db.commit()
        print(f"Successfully stored/updated {len(predictions_data)} predictions.")
    except Exception as e:
        db.rollback()
        print(f"Error storing predictions: {e}")


def run_batch_predictions():
    print("Starting batch yield prediction process...")
    model, scaler, trained_feature_names = load_model_artifacts()

    if not model or not scaler or not trained_feature_names:
        print("Could not load all necessary model artifacts. Exiting.")
        return

    db = SessionLocal()
    try:
        # Fetch and engineer features for active crop cycles
        # The returned DataFrame should only contain the feature columns expected by the model,
        # plus 'crop_cycle_id'.
        features_for_prediction_df = fetch_and_engineer_prediction_features(db, trained_feature_names)

        if features_for_prediction_df.empty:
            print("No active crop cycles or features to make predictions on. Exiting.")
            return

        # Separate crop_cycle_ids before scaling and ensure correct feature order
        crop_cycle_ids = features_for_prediction_df['crop_cycle_id']
        
        # Select only the trained feature columns in the correct order and handle potential NaNs
        # This reordering/selection MUST happen BEFORE scaling
        X_predict = features_for_prediction_df[trained_feature_names].copy()
        
        # Handle NaNs before scaling: Impute if necessary, or ensure model can handle them.
        # For now, StandardScaler will error on NaNs. Let's try simple mean imputation.
        # This imputation should ideally mirror what was done (or would be done) in training for missing values.
        for col in X_predict.columns:
            if X_predict[col].isnull().any():
                mean_val = X_predict[col].mean() # Calculate mean from current batch, could use training set mean
                X_predict[col].fillna(mean_val, inplace=True)
                print(f"Imputed NaNs in column '{col}' with mean {mean_val:.2f}")

        # If after imputation, there are still NaNs (e.g., a column was all NaN),
        # then prediction for those rows might be problematic.
        if X_predict.isnull().any().any():
            print("Warning: Features for prediction still contain NaNs after imputation. Predictions may be unreliable or fail.")
            # Optionally, drop rows that still have NaNs or handle them based on model capabilities
            # X_predict.dropna(inplace=True) # This would remove rows and misalign with crop_cycle_ids if not careful


        # Scale the features using the loaded scaler
        X_predict_scaled = scaler.transform(X_predict)

        # Make predictions
        raw_predictions = model.predict(X_predict_scaled) # Yield per hectare

        predictions_to_store = []
        for i, crop_cycle_id in enumerate(crop_cycle_ids):
            # Get the original (unscaled) features used for this prediction for storage
            input_features_summary = features_for_prediction_df.loc[
                features_for_prediction_df['crop_cycle_id'] == crop_cycle_id, trained_feature_names
            ].iloc[0].to_dict()

            # Convert predicted yield per hectare back to total yield if needed, or store as per_hectare
            # Assuming model predicts yield_tonnes_per_hectare
            predicted_yield_per_hectare = raw_predictions[i]
            
            # Find field_area_hectares for this crop_cycle_id to calculate total yield (optional)
            # cycle_info = features_for_prediction_df.loc[features_for_prediction_df['crop_cycle_id'] == crop_cycle_id].iloc[0]
            # total_predicted_yield = predicted_yield_per_hectare * cycle_info['field_area_hectares']

            print(f"Predicted yield per hectare for crop_cycle_id {crop_cycle_id}: {predicted_yield_per_hectare:.2f} tonnes/ha")
            
            predictions_to_store.append({
                'crop_cycle_id': crop_cycle_id,
                'predicted_yield_tonnes': predicted_yield_per_hectare, # Storing per hectare prediction
                'input_features_summary': input_features_summary
            })
        
        store_predictions(db, predictions_to_store)

    except Exception as e:
        print(f"An error occurred during the batch prediction process: {e}")
    finally:
        db.close()
    print("Batch yield prediction process finished.")

if __name__ == "__main__":
    # This script would be run on a schedule.
    # Ensure you have:
    # 1. A trained model, scaler, and feature_names list in ml_models/saved_models/.
    # 2. Active crop cycles in your database (actual_harvest_date is NULL).
    # 3. Sensor data for these active crop cycles.
    run_batch_predictions()

