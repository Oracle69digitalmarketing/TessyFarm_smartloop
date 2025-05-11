// frontend_dashboard/src/pages/CropCycleDetailPage.jsx
import React, { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { getCropCycleById, getYieldPredictionForCycle } from '../services/api'; // Assuming getYieldPredictionForCycle exists
import './CropCycleDetailPage.css'; // Create this for styling

function CropCycleDetailPage() {
  const { cycleId } = useParams();
  const navigate = useNavigate();

  const [cropCycle, setCropCycle] = useState(null);
  const [yieldPrediction, setYieldPrediction] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchCropCycleData = async () => {
      if (!cycleId) return;
      try {
        setLoading(true);
        setError(null);

        // Fetch crop cycle details
        const cycleResponse = await getCropCycleById(cycleId);
        setCropCycle(cycleResponse.data);

        // Fetch yield prediction for this specific crop cycle
        try {
          const predictionResponse = await getYieldPredictionForCycle(cycleId);
          if (predictionResponse.data) {
            setYieldPrediction(predictionResponse.data);
          } else {
            setYieldPrediction(null);
          }
        } catch (predictionError) {
          if (predictionError.response && predictionError.response.status === 404) {
            console.info(`No specific yield prediction found for crop cycle ID ${cycleId}.`);
            setYieldPrediction(null);
          } else {
            console.error(`Error fetching yield prediction for crop cycle ID ${cycleId}:`, predictionError);
            // Optionally set a non-critical error for prediction part
          }
        }

      } catch (err) {
        console.error(`Error fetching data for crop cycle ID ${cycleId}:`, err);
        setError(err.message || `Failed to fetch crop cycle data.`);
         if (err.response) {
            console.error("Error details:", err.response.data);
            setError(`Failed to fetch crop cycle: ${err.response.status} ${err.response.statusText}. ${err.response.data.detail || ''}`);
        }
      } finally {
        setLoading(false);
      }
    };

    fetchCropCycleData();
  }, [cycleId]);

  if (loading) return <p>Loading crop cycle details...</p>;
  if (error && !cropCycle) return <p style={{ color: 'red' }}>Error: {error}</p>;
  if (!cropCycle) return <p>Crop cycle not found.</p>;

  return (
    <div className="crop-cycle-detail-page">
      <button onClick={() => navigate(-1)} className="back-button">&larr; Back</button>
      
      <header className="crop-cycle-header">
        <h1>Crop Cycle: {cropCycle.crop_type}</h1>
        <p><strong>Field ID:</strong> <Link to={`/fields/${cropCycle.field_id}`}>{cropCycle.field_id}</Link></p>
        <p><strong>Status:</strong> {cropCycle.actual_harvest_date ? `Completed` : `Active`}</p>
        <p><strong>Planting Date:</strong> {new Date(cropCycle.planting_date).toLocaleDateString()}</p>
        {cropCycle.expected_harvest_date && (
          <p><strong>Expected Harvest:</strong> {new Date(cropCycle.expected_harvest_date).toLocaleDateString()}</p>
        )}
        {cropCycle.actual_harvest_date && (
          <p><strong>Actual Harvest Date:</strong> {new Date(cropCycle.actual_harvest_date).toLocaleDateString()}</p>
        )}
        {cropCycle.actual_yield_tonnes !== null && cropCycle.actual_yield_tonnes !== undefined && (
          <p><strong>Actual Yield:</strong> {cropCycle.actual_yield_tonnes.toFixed(2)} tonnes</p>
        )}
        <p><strong>Notes:</strong> {cropCycle.notes || 'N/A'}</p>
        <p><strong>Cycle ID:</strong> {cropCycle.id}</p>
        <p><strong>Created:</strong> {new Date(cropCycle.created_at).toLocaleDateString()}</p>
      </header>

      {error && !yieldPrediction && <p style={{ color: 'orange' }}>Note regarding prediction: {error}</p>}


      <section className="yield-prediction-section">
        <h2>Yield Prediction for this Cycle</h2>
        {yieldPrediction ? (
          <div className="prediction-details">
            <p><strong>Predicted Yield:</strong> {yieldPrediction.predicted_yield_tonnes.toFixed(2)} tonnes/ha (or total, adjust as per model output)</p>
            <p><strong>Model Version:</strong> {yieldPrediction.model_version}</p>
            <p><strong>Prediction Date:</strong> {new Date(yieldPrediction.prediction_date).toLocaleString()}</p>
            {yieldPrediction.input_features_summary && (
              <details>
                <summary>View Input Features Summary Used for this Prediction</summary>
                <pre>{JSON.stringify(yieldPrediction.input_features_summary, null, 2)}</pre>
              </details>
            )}
          </div>
        ) : (
          <p>No specific yield prediction available for this crop cycle.</p>
        )}
      </section>

      {/* Future sections: Sensor data specific to this cycle's timeframe, interventions log, etc. */}
    </div>
  );
}

export default CropCycleDetailPage;
