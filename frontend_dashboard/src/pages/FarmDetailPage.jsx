// frontend_dashboard/src/pages/FarmDetailPage.jsx
import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom'; // useParams to get farmId from URL
import { getFarmById } from '../services/api';
import './FarmDetailPage.css'; // Create this for styling

function FarmDetailPage() {
  const { farmId } = useParams(); // Get farmId from the URL parameter
  const [farm, setFarm] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchFarmDetails = async () => {
      try {
        setLoading(true);
        const response = await getFarmById(farmId);
        setFarm(response.data); // The backend returns FarmResponseWithFields
        setError(null);
      } catch (err) {
        console.error(`Error fetching farm details for ID ${farmId}:`, err);
        setError(err.message || `Failed to fetch farm details.`);
        if (err.response) {
            console.error("Error details:", err.response.data);
            setError(`Failed to fetch farm: ${err.response.status} ${err.response.statusText}. ${err.response.data.detail || ''}`);
        }
      } finally {
        setLoading(false);
      }
    };

    if (farmId) {
      fetchFarmDetails();
    }
  }, [farmId]); // Re-fetch if farmId changes

  if (loading) return <p>Loading farm details...</p>;
  if (error) return <p style={{ color: 'red' }}>Error: {error}</p>;
  if (!farm) return <p>Farm not found.</p>;

  return (
    <div className="farm-detail-page">
      <Link to="/farms" className="back-link">&larr; Back to Farms</Link>
      <header className="farm-header">
        <h1>{farm.name}</h1>
        <p><strong>Location:</strong> {farm.location_text || 'N/A'}</p>
        <p><strong>Total Area:</strong> {farm.total_area_hectares ? `${farm.total_area_hectares} ha` : 'N/A'}</p>
        <p><strong>Farm ID:</strong> {farm.id}</p>
        <p><strong>Created:</strong> {new Date(farm.created_at).toLocaleDateString()}</p>
      </header>

      <section className="fields-section">
        <h2>Fields in this Farm</h2>
        {farm.fields && farm.fields.length > 0 ? (
          <ul className="fields-list">
            {farm.fields.map((field) => (
              <li key={field.id} className="field-item">
                {/* Link to a future FieldDetailPage */}
                <Link to={`/fields/${field.id}`}> 
                  <h3>{field.name}</h3>
                </Link>
                <p><strong>Area:</strong> {field.area_hectares ? `${field.area_hectares} ha` : 'N/A'}</p>
                <p><strong>Soil Type:</strong> {field.soil_type || 'N/A'}</p>
              </li>
            ))}
          </ul>
        ) : (
          <p>No fields found for this farm.</p>
        )}
      </section>
    </div>
  );
}

export default FarmDetailPage;
