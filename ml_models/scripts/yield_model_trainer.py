# tessyfarm_smartloop/ml_models/scripts/yield_model_trainer.py
import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime # timedelta was imported but not used, can be removed if not needed
import joblib # For saving the model
import json # <--- ADDED: For saving feature names

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler

# --- Path Setup for Module Imports ---
# The backend_api code is mounted at /app in the container.
# We need to ensure /app is in sys.path to allow imports like 'from app.core...'.
CONTAINER_BACKEND_API_ROOT = "/app"
if CONTAINER_BACKEND_API_ROOT not in sys.path:
    sys.path.insert(0, CONTAINER_BACKEND_API_ROOT)

# --- Database and Configuration Imports ---
try:
    from sqlalchemy import create_engine # text was imported but not used
    from sqlalchemy.orm import sessionmaker, Session # <--- UPDATED: Import Session for type hinting
    from app.core.config import settings as app_settings # <--- UPDATED: Assuming backend_api/app/ is at /app/app/
    from app.models.farm import CropCycle, SensorReading, Field # <--- UPDATED: Models are under app.models
except ImportError as e:
    print(f"Error importing backend modules: {e}")
    print(f"Ensure backend_api is mounted at /app in Docker and PYTHONPATH is effectively /app.")
    print(f"Current sys.path: {sys.path}")
    sys.exit(1)

# --- Constants for Model Artifact Paths ---
# These paths are relative to the container's filesystem, assuming ml_models is mounted at /app/ml_models
BASE_ML_MODELS_PATH_IN_CONTAINER = "/app/ml_models"
MODEL_DIR = os.path.join(BASE_ML_MODELS_PATH_IN_CONTAINER, "saved_models")
MODEL_FILENAME = "yield_prediction_model_v1.joblib"
SCALER_FILENAME = "yield_feature_scaler_v1.joblib"
FEATURE_NAMES_FILENAME = "yield_model_feature_names_v1.json"

MODEL_PATH = os.path.join(MODEL_DIR, MODEL_FILENAME)
SCALER_PATH = os.path.join(MODEL_DIR, SCALER_FILENAME)
FEATURE_NAMES_PATH = os.path.join(MODEL_DIR, FEATURE_NAMES_FILENAME)


# --- Database Setup ---
db_url = app_settings.ASSEMBLED_DATABASE_URL
engine = create_engine(db_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def fetch_historical_data(db: Session) -> pd.DataFrame: # <--- UPDATED: Type hint to Session
    """
    Fetches historical crop cycle data and associated aggregated sensor readings.
    """
    print("Fetching historical data from database...")
    
    query = db.query(
        CropCycle.id.label("crop_cycle_id"),
        CropCycle.field_id.label("field_id"), # <--- ADDED: To use in sensor data query filter
        CropCycle.crop_type,
        CropCycle.planting_date,
        CropCycle.actual_harvest_date,
        CropCycle.actual_yield_tonnes,
        Field.area_hectares.label("field_area_hectares"),
        Field.soil_type
    ).join(Field, CropCycle.field_id == Field.id)\
     .filter(CropCycle.actual_yield_tonnes.isnot(None))\
     .filter(CropCycle.actual_harvest_date.isnot(None))
    
    crop_cycles_df = pd.read_sql(query.statement, db.bind) # Use db.bind for SQLAlchemy < 2.0, or db for >= 2.0 with new API
    print(f"Found {len(crop_cycles_df)} completed crop cycles with yield data.")
    if crop_cycles_df.empty:
        return pd.DataFrame()

    all_features_list = [] # Renamed to avoid conflict with 'features' dict
    for index, cycle in crop_cycles_df.iterrows():
        print(f"Processing crop cycle ID: {cycle['crop_cycle_id']} (Field ID: {cycle['field_id']})")
        
        # Fetch sensor data for this cycle.
        # IMPORTANT: The device_id filtering logic here is a placeholder.
        # You need a robust way to link sensors to specific fields/crop_cycles.
        # This might involve a device_to_field mapping table or specific device naming conventions.
        sensor_query = db.query(SensorReading)\
            .filter(SensorReading.timestamp >= cycle['planting_date'])\
            .filter(SensorReading.timestamp <= cycle['actual_harvest_date'])\
            .filter(SensorReading.device_id.contains(f"field_{cycle['field_id']}")) # Example filter
            # If your device IDs don't follow this pattern, this query will not find data.
            # Consider broader query for debugging:
            # .filter(SensorReading.device_id.startswith("field_")) # or based on known device IDs for that field

        sensor_df = pd.read_sql(sensor_query.statement, db.bind)
        
        if sensor_df.empty:
            print(f"  No sensor data found for crop cycle {cycle['crop_cycle_id']} (Field ID: {cycle['field_id']}) with current filter. Skipping.")
            continue

        # --- Feature Engineering ---
        features = {"crop_cycle_id": cycle['crop_cycle_id']}

        cycle_duration_days = (cycle['actual_harvest_date'] - cycle['planting_date']).days
        if cycle_duration_days <= 0:
            print(f"  Invalid cycle duration ({cycle_duration_days} days) for cycle {cycle['crop_cycle_id']}. Skipping.")
            continue
        features['cycle_duration_days'] = cycle_duration_days
        
        # Sensor features (ensure columns exist and handle NaNs from .mean() if sensor_df is empty for a type)
        features['avg_temp'] = sensor_df['temperature'].mean() if 'temperature' in sensor_df else np.nan
        features['min_temp'] = sensor_df['temperature'].min() if 'temperature' in sensor_df else np.nan
        features['max_temp'] = sensor_df['temperature'].max() if 'temperature' in sensor_df else np.nan
        features['avg_humidity'] = sensor_df['humidity'].mean() if 'humidity' in sensor_df else np.nan
        features['avg_soil_moisture'] = sensor_df['soil_moisture'].mean() if 'soil_moisture' in sensor_df else np.nan
        
        t_base = 10
        # Ensure min_temp and max_temp are not NaN before GDD calculation
        if pd.notna(features['max_temp']) and pd.notna(features['min_temp']):
            avg_daily_temp_proxy = (features['max_temp'] + features['min_temp']) / 2
            features['gdd_approx'] = max(0, avg_daily_temp_proxy - t_base) * cycle_duration_days
        else:
            features['gdd_approx'] = np.nan # Or some other imputation

        features['field_area_hectares'] = cycle['field_area_hectares']
        # Placeholder for categorical encoding - to be implemented
        # features['crop_type_encoded'] = encode_crop_type(cycle['crop_type'])
        # features['soil_type_encoded'] = encode_soil_type(cycle['soil_type'])

        if cycle['field_area_hectares'] and cycle['field_area_hectares'] > 0 and pd.notna(cycle['actual_yield_tonnes']):
            features['actual_yield_tonnes_per_hectare'] = cycle['actual_yield_tonnes'] / cycle['field_area_hectares']
        else:
            print(f"  Field area is 0/None or actual_yield_tonnes is None for cycle {cycle['crop_cycle_id']}. Cannot calculate target. Skipping.")
            continue

        all_features_list.append(features)
        print(f"  Engineered features for crop cycle {cycle['crop_cycle_id']}.")

    if not all_features_list:
        print("No data available after feature engineering.")
        return pd.DataFrame()
        
    return pd.DataFrame(all_features_list)


def train_yield_model():
    print("Starting yield model training process...")
    print(f"Attempting to load backend modules. Current sys.path: {sys.path}") # For debugging imports
    db = SessionLocal()
    try:
        data_df = fetch_historical_data(db)
    finally:
        db.close()

    if data_df.empty or 'actual_yield_tonnes_per_hectare' not in data_df.columns:
        print("No training data fetched or target variable missing. Exiting training.")
        return

    # Define critical features needed for training (before NaN drop for these specifically)
    # These are the columns that will go into X after processing
    # Categorical encoded columns would be added here later.
    feature_columns_for_model = [
        'avg_temp', 'min_temp', 'max_temp', 'avg_humidity', 'avg_soil_moisture',
        'gdd_approx', 'cycle_duration_days', 'field_area_hectares'
    ]
    # Ensure all these feature columns exist in data_df, even if they are all NaN for some rows
    for col in feature_columns_for_model:
        if col not in data_df.columns:
            data_df[col] = np.nan # Add column with NaNs if completely missing

    # Drop rows where the target or essential input features are NaN
    # Essential features here are those that, if missing, make the row unusable.
    # For example, if cycle_duration_days is NaN, the row is likely problematic.
    essential_cols_for_dropna = feature_columns_for_model + ['actual_yield_tonnes_per_hectare']
    data_df = data_df.dropna(subset=essential_cols_for_dropna, how='any') # Drop if any essential is NaN
                                                                       # Consider 'all' if some NaNs in features are imputable
    
    if data_df.empty:
        print("No valid training data after NaN drop based on essential features and target. Exiting.")
        return

    X = data_df[feature_columns_for_model] # Use the defined list of feature columns
    y = data_df['actual_yield_tonnes_per_hectare']

    if X.empty:
        print("Feature set X is empty. Cannot train model.")
        return

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    trained_feature_names = list(X_train.columns) # Get feature names from DataFrame used for fitting scaler

    model = RandomForestRegressor(n_estimators=100, random_state=42, oob_score=True, max_depth=10, min_samples_split=5)
    model.fit(X_train_scaled, y_train)

    y_pred_train = model.predict(X_train_scaled)
    y_pred_test = model.predict(X_test_scaled)

    train_rmse = np.sqrt(mean_squared_error(y_train, y_pred_train))
    test_rmse = np.sqrt(mean_squared_error(y_test, y_pred_test))
    train_r2 = r2_score(y_train, y_pred_train)
    test_r2 = r2_score(y_test, y_pred_test)
    oob = model.oob_score_ if hasattr(model, 'oob_score_') and model.oob_score_ else "N/A" # Check if oob_score_ available

    print("\n--- Model Training Complete ---")
    print(f"Features used for training: {trained_feature_names}")
    print(f"Training RMSE: {train_rmse:.3f}")
    print(f"Test RMSE: {test_rmse:.3f}")
    print(f"Training R2: {train_r2:.3f}")
    print(f"Test R2: {test_r2:.3f}")
    print(f"OOB Score: {oob if isinstance(oob, str) else f'{oob:.3f}'}")

    if not os.path.exists(MODEL_DIR):
        os.makedirs(MODEL_DIR)
        print(f"Created directory: {MODEL_DIR}")
    
    joblib.dump(model, MODEL_PATH)
    print(f"Model saved to {MODEL_PATH}")
    joblib.dump(scaler, SCALER_PATH)
    print(f"Scaler saved to {SCALER_PATH}")
    
    with open(FEATURE_NAMES_PATH, 'w') as f: # Use FEATURE_NAMES_PATH constant
        json.dump(trained_feature_names, f)
    print(f"Feature names saved to {FEATURE_NAMES_PATH}")


if __name__ == "__main__":
    print(f"Running Yield Model Trainer from: {os.getcwd()}")
    print(f"MODEL_DIR will be: {MODEL_DIR}")
    train_yield_model()
    
