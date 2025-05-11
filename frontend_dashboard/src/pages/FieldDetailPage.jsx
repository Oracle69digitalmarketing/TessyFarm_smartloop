// frontend_dashboard/src/pages/FieldDetailPage.jsx
import React, { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom'; // useNavigate for back navigation
import { getFieldById, getCurrentYieldPredictionForField } from '../services/api';
import './FieldDetailPage.css'; // Create this for styling

function FieldDetailPage() {
  const { fieldId } = useParams();
  const navigate = useNavigate(); // For the back button

  const [field, setField] = useState(null);
  const [yieldPrediction, setYieldPrediction] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchFieldData = async () => {
      if (!fieldId) return;
      try {
        setLoading(true);
        setError(null);

        // Fetch field details (which includes crop cycles)
        const fieldResponse = await getFieldById(fieldId);
        setField(fieldResponse.data);

        // Fetch current yield prediction for this field
        try {
            const predictionResponse = await getCurrentYieldPredictionForField(fieldId);
            if (predictionResponse.data) { // Prediction might be null if none exists
                setYieldPrediction(predictionResponse.data);
            } else {
                setYieldPrediction(null); // Explicitly set to null if no prediction
            }
        } catch (predictionError) {
            if (predictionError.response && predictionError.response.status === 404) {
                console.info(`No yield prediction found for field ID ${fieldId}.`);
                setYieldPrediction(null); // No prediction available is not necessarily a page error
            } else {
                console.error(`Error fetching yield prediction for field ID ${fieldId}:`, predictionError);
                // Optionally set a non-critical error for prediction part
                // setError(prevError => prevError ? `${prevError}\nFailed to fetch yield prediction.` : 'Failed to fetch yield prediction.');
            }
        }

      } catch (err) {
        console.error(`Error fetching data for field ID ${fieldId}:`, err);
        setError(err.message || `Failed to fetch field data.`);
        if (err.response) {
            console.error("Error details:", err.response.data);
            setError(`Failed to fetch field: ${err.response.status} ${err.response.statusText}. ${err.response.data.detail || ''}`);
        }
      } finally {
        setLoading(false);
      }
    };

    fetchFieldData();
  }, [fieldId]);

  if (loading) return <p>Loading field details...</p>;
  if (error && !field) return <p style={{ color: 'red' }}>Error: {error}</p>; // Show main error only if field data failed
  if (!field) return <p>Field not found.</p>;

  return (
    <div className="field-detail-page">
      {/* Better back navigation that takes user to the farm they came from, if possible.
          For now, a generic back or link to all farms.
          If farmId was passed via state or query param, we could use it.
          Or, simply navigate(-1) for browser back.
      */}
      <button onClick={() => navigate(-1)} className="back-button">&larr; Back</button>
      
      <header className="field-header">
        <h1>Field: {field.name}</h1>
        <p><strong>Farm ID:</strong> <Link to={`/farms/${field.farm_id}`}>{field.farm_id}</Link></p>
        <p><strong>Area:</strong> {field.area_hectares ? `${field.area_hectares} ha` : 'N/A'}</p>
        <p><strong>Soil Type:</strong> {field.soil_type || 'N/A'}</p>
        <p><strong>Field ID:</strong> {field.id}</p>
        <p><strong>Created:</strong> {new Date(field.created_at).toLocaleDateString()}</p>
      </header>

      {error && <p style={{ color: 'orange' }}>Note: {error}</p>} {/* Display non-critical errors here, e.g. prediction fetch failure */}

      <section className="yield-prediction-section">
        <h2>Current Yield Prediction</h2>
        {yieldPrediction ? (
          <div className="prediction-details">
            <p><strong>Predicted Yield:</strong> {yieldPrediction.predicted_yield_tonnes.toFixed(2)} tonnes/ha</p>
            <p><strong>Model Version:</strong> {yieldPrediction.model_version}</p>
            <p><strong>Prediction Date:</strong> {new Date(yieldPrediction.prediction_date).toLocaleString()}</p>
            {yieldPrediction.input_features_summary && (
              <details>
                <summary>View Input Features Summary</summary>
                <pre>{JSON.stringify(yieldPrediction.input_features_summary, null, 2)}</pre>
              </details>
            )}
          </div>
        ) : (
          <p>No current yield prediction available for this field.</p>
        )}
      </section>

      <section className="crop-cycles-section">
        <h2>Crop Cycles in this Field</h2>
        {field.crop_cycles && field.crop_cycles.length > 0 ? (
          <ul className="crop-cycles-list">
            {field.crop_cycles.map((cycle) => (
              <li key={cycle.id} className={`crop-cycle-item ${cycle.actual_harvest_date ? 'historical' : 'active'}`}>
                {/* Link to a future CropCycleDetailPage or expand inline */}
                <Link to={`/crop-cycles/${cycle.id}`}>
                  <h3>{cycle.crop_type}</h3>
                </Link>
                <p><strong>Status:</strong> {cycle.actual_harvest_date ? `Completed` : `Active`}</p>
                <p><strong>Planting Date:</strong> {new Date(cycle.planting_date).toLocaleDateString()}</p>
                {cycle.actual_harvest_date ? (
                  <p><strong>Harvest Date:</strong> {new Date(cycle.actual_harvest_date).toLocaleDateString()}</p>
                ) : (
                  <p><strong>Expected Harvest:</strong> {cycle.expected_harvest_date ? new Date(cycle.expected_harvest_date).toLocaleDateString() : 'N/A'}</p>
                )}
                {cycle.actual_yield_tonnes !== null && cycle.actual_yield_tonnes !== undefined && ( // Check for null or undefined
                  <p><strong>Actual Yield:</strong> {cycle.actual_yield_tonnes.toFixed(2)} tonnes</p>
                )}
                <p><i>{cycle.notes || 'No notes.'}</i></p>
              </li>
            ))}
          </ul>
        ) : (
          <p>No crop cycles found for this field.</p>
        )}
      </section>
    </div>
  );
}

export default FieldDetailPage;
