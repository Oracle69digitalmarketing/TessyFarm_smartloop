# In yield_model_trainer.py
# ...
# PROJECT_ROOT = ... (this helps for backend_api module imports)

# Define model paths based on the assumption that ml_models is at /app/ml_models in container
BASE_ML_MODELS_PATH_IN_CONTAINER = "/app/ml_models" 
MODEL_DIR = os.path.join(BASE_ML_MODELS_PATH_IN_CONTAINER, "saved_models")
MODEL_FILENAME = "yield_prediction_model_v1.joblib"
SCALER_FILENAME = "yield_feature_scaler_v1.joblib"
MODEL_PATH = os.path.join(MODEL_DIR, MODEL_FILENAME)
SCALER_PATH = os.path.join(MODEL_DIR, SCALER_FILENAME)
FEATURE_NAMES_FILENAME = "yield_model_feature_names_v1.json" # Added for consistency
FEATURE_NAMES_PATH = os.path.join(MODEL_DIR, FEATURE_NAMES_FILENAME) # Use this path later

# In train_dummy_model() / train_yield_model() when saving feature names:
# ...
# feature_names_path = FEATURE_NAMES_PATH # Use the defined constant
# with open(feature_names_path, 'w') as f:
#     json.dump(trained_feature_names, f)
# print(f"Feature names saved to {feature_names_path}")
