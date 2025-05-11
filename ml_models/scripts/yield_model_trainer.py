# tessyfarm_smartloop/ml_models/scripts/yield_model_trainer.py
import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import joblib # For saving the model

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler # For scaling features

# --- Add project root to sys.path for imports if running script directly ---
# This allows importing modules from backend_api (like models, config, db session)
# Adjust the number of '..' based on where this script is located relative to the project root
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# --- Database and Configuration Imports ---
# We need to set up DB access similar to how other services do.
# This assumes the script can access the .env file from the project root.
try:
    from sqlalchemy import create_engine, text
    from sqlalchemy.orm import sessionmaker
    from backend_api.app.core.config import settings as app_settings # Reusing backend settings
    from backend_api.app.models.farm import CropCycle, SensorReading, Field # Import necessary models
except ImportError as e:
    print(f"Error importing backend modules: {e}")
    print("Ensure this script is run with PYTHONPATH configured or from an environment where backend_api is accessible.")
    print(f"Current sys.path: {sys.path}")
    sys.exit(1)


MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "saved_models")
MODEL_FILENAME = "yield_prediction_model_v1.joblib" # Standardized model name
SCALER_FILENAME = "yield_feature_scaler_v1.joblib" # For saving the feature scaler
MODEL_PATH = os.path.join(MODEL_DIR, MODEL_FILENAME)
SCALER_PATH = os.path.join(MODEL_DIR, SCALER_FILENAME)


# --- Database Setup ---
# Using settings from backend_api.app.core.config
db_url = app_settings.ASSEMBLED_DATABASE_URL
engine = create_engine(db_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def fetch_historical_data(db: SessionLocal) -> pd.DataFrame:
    """
    Fetches historical crop cycle data and associated aggregated sensor readings.
    """
    print("Fetching historical data from database...")
    
    # Query completed crop cycles (ones with actual yield and harvest date)
    # Ensure relationships are loaded if needed (e.g. field for area)
    # For simplicity, directly querying fields needed.
    # Using SQLAlchemy text for a more complex query or joining, or use ORM capabilities.
    
    # This query assumes direct fetching. A more robust way would be to iterate crop cycles
    # and then fetch sensor data for each, then aggregate.
    # For simplicity here, we'll just query crop cycles. Feature engineering will be key.
    
    query = db.query(
        CropCycle.id.label("crop_cycle_id"),
        CropCycle.crop_type,
        CropCycle.planting_date,
        CropCycle.actual_harvest_date,
        CropCycle.actual_yield_tonnes,
        Field.area_hectares.label("field_area_hectares"), # Assuming CropCycle has a 'field' relationship
        Field.soil_type # Assuming CropCycle has a 'field' relationship
    ).join(Field, CropCycle.field_id == Field.id)\
     .filter(CropCycle.actual_yield_tonnes.isnot(None))\
     .filter(CropCycle.actual_harvest_date.isnot(None))
    
    crop_cycles_df = pd.read_sql(query.statement, db.bind)
    print(f"Found {len(crop_cycles_df)} completed crop cycles with yield data.")
    if crop_cycles_df.empty:
        return pd.DataFrame()

    all_features = []
    for index, cycle in crop_cycles_df.iterrows():
        print(f"Processing crop cycle ID: {cycle['crop_cycle_id']}")
        # Fetch sensor data for this cycle
        sensor_query = db.query(SensorReading)\
            .filter(SensorReading.timestamp >= cycle['planting_date'])\
            .filter(SensorReading.timestamp <= cycle['actual_harvest_date'])\
            .filter(SensorReading.device_id.contains(f"field_{cycle['field_id']}")) # Example: filter by field-related devices
            # More specific device filtering based on field_id would be needed.
            # This requires a convention for device_ids or a mapping table.
            # For now, let's assume we can get *some* relevant sensor data.
            # A simpler approach if device_id mapping is complex:
            # sensor_query = db.query(SensorReading)\
            #     .filter(SensorReading.timestamp >= cycle['planting_date'])\
            #     .filter(SensorReading.timestamp <= cycle['actual_harvest_date'])
            # This would fetch ALL sensor data in that period, then you'd need to associate to field.

        sensor_df = pd.read_sql(sensor_query.statement, db.bind)
        
        if sensor_df.empty:
            print(f"  No sensor data found for crop cycle {cycle['crop_cycle_id']}. Skipping.")
            continue

        # --- Feature Engineering ---
        features = {"crop_cycle_id": cycle['crop_cycle_id'], "actual_yield_tonnes_per_hectare": 0}

        # Calculate duration of cycle
        cycle_duration_days = (cycle['actual_harvest_date'] - cycle['planting_date']).days
        if cycle_duration_days <= 0:
            print(f"  Invalid cycle duration ({cycle_duration_days} days) for cycle {cycle['crop_cycle_id']}. Skipping.")
            continue
        features['cycle_duration_days'] = cycle_duration_days
        
        # Sensor features (examples)
        features['avg_temp'] = sensor_df['temperature'].mean()
        features['min_temp'] = sensor_df['temperature'].min()
        features['max_temp'] = sensor_df['temperature'].max()
        features['avg_humidity'] = sensor_df['humidity'].mean()
        features['avg_soil_moisture'] = sensor_df['soil_moisture'].mean()
        
        # Growing Degree Days (GDD) - simplified example
        # GDD = ((Tmax + Tmin) / 2) - Tbase. Assume Tbase = 10°C
        # This requires daily Tmax/Tmin. Our sensor_df might be more granular.
        # For simplicity, let's use overall avg temp as a proxy.
        # A proper GDD would require daily aggregation first.
        t_base = 10
        avg_daily_temp_proxy = (features['max_temp'] + features['min_temp']) / 2 # Very rough
        gdd_proxy = max(0, avg_daily_temp_proxy - t_base) * cycle_duration_days
        features['gdd_approx'] = gdd_proxy

        # Static features from crop_cycle and field
        features['field_area_hectares'] = cycle['field_area_hectares']
        # features['crop_type_encoded'] = 1 if 'Maize' in cycle['crop_type'] else 0 # Simple encoding
        # features['soil_type_encoded'] = 1 if 'Loam' in cycle['soil_type'] else 0 # Simple encoding

        # Target variable (yield per hectare)
        if cycle['field_area_hectares'] and cycle['field_area_hectares'] > 0:
            features['actual_yield_tonnes_per_hectare'] = cycle['actual_yield_tonnes'] / cycle['field_area_hectares']
        else:
            print(f"  Field area is 0 or None for cycle {cycle['crop_cycle_id']}. Skipping yield per hectare calculation.")
            continue # Skip if we can't calculate the target properly

        all_features.append(features)
        print(f"  Engineered features for crop cycle {cycle['crop_cycle_id']}.")

    if not all_features:
        print("No data available after feature engineering.")
        return pd.DataFrame()
        
    return pd.DataFrame(all_features)


def train_yield_model():
    print("Starting yield model training process...")
    db = SessionLocal()
    try:
        data_df = fetch_historical_data(db)
    finally:
        db.close()

    if data_df.empty or 'actual_yield_tonnes_per_hectare' not in data_df.columns:
        print("No training data fetched or target variable missing. Exiting training.")
        return

    # Drop rows with NaN in critical feature columns or target before splitting
    # Define critical features needed for training
    # For this example, let's assume all features derived are critical.
    # More sophisticated imputation could be used.
    required_cols_for_model = [
        'avg_temp', 'min_temp', 'max_temp', 'avg_humidity', 'avg_soil_moisture',
        'gdd_approx', 'cycle_duration_days', 'field_area_hectares', # Add encoded categoricals if used
        'actual_yield_tonnes_per_hectare' # Target
    ]
    data_df = data_df.dropna(subset=[col for col in required_cols_for_model if col != 'actual_yield_tonnes_per_hectare'])
    
    if data_df.empty:
        print("No valid training data after NaN drop. Exiting.")
        return

    # Define features (X) and target (y)
    # Exclude non-feature columns like 'crop_cycle_id' and the target itself
    feature_columns = [col for col in data_df.columns if col not in ['crop_cycle_id', 'actual_yield_tonnes_per_hectare']]
    X = data_df[feature_columns]
    y = data_df['actual_yield_tonnes_per_hectare']

    if X.empty:
        print("Feature set X is empty. Cannot train model.")
        return

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Feature Scaling
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Store the feature names after fitting the scaler, in the correct order
    # This ensures consistency during prediction.
    trained_feature_names = list(X_train.columns)


    model = RandomForestRegressor(n_estimators=100, random_state=42, oob_score=True, max_depth=10, min_samples_split=5)
    model.fit(X_train_scaled, y_train)

    # Evaluation
    y_pred_train = model.predict(X_train_scaled)
    y_pred_test = model.predict(X_test_scaled)

    train_rmse = np.sqrt(mean_squared_error(y_train, y_pred_train))
    test_rmse = np.sqrt(mean_squared_error(y_test, y_pred_test))
    train_r2 = r2_score(y_train, y_pred_train)
    test_r2 = r2_score(y_test, y_pred_test)
    oob = model.oob_score_ if hasattr(model, 'oob_score_') else "N/A"

    print("\n--- Model Training Complete ---")
    print(f"Training RMSE: {train_rmse:.3f}")
    print(f"Test RMSE: {test_rmse:.3f}")
    print(f"Training R2: {train_r2:.3f}")
    print(f"Test R2: {test_r2:.3f}")
    print(f"OOB Score: {oob if isinstance(oob, str) else f'{oob:.3f}'}")


    # Save the model and scaler
    if not os.path.exists(MODEL_DIR):
        os.makedirs(MODEL_DIR)
    
    joblib.dump(model, MODEL_PATH)
    print(f"Model saved to {MODEL_PATH}")
    joblib.dump(scaler, SCALER_PATH) # Save the scaler
    print(f"Scaler saved to {SCALER_PATH}")
    
    # Save feature names with the model (or as separate file)
    # This is crucial for ensuring prediction script uses features in the same order/way
    feature_names_path = os.path.join(MODEL_DIR, "yield_model_feature_names_v1.json")
    with open(feature_names_path, 'w') as f:
        json.dump(trained_feature_names, f)
    print(f"Feature names saved to {feature_names_path}")


if __name__ == "__main__":
    # Ensure you have some data in your farms, fields, crop_cycles (with actual yields),
    # and sensor_readings tables before running this.
    # You might need to manually insert some sample historical data using the API endpoints
    # we created earlier or directly into the DB for the first run.
    
    # Example: Create a farm, a field, a crop cycle with actual yield, and some sensor data.
    # Then run this script.
    train_yield_model()

