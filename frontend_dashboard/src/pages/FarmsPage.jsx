// frontend_dashboard/src/pages/FarmsPage.jsx
import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom'; // Assuming you'll add React Router
import { getFarms } from '../services/api'; // Updated path
import './FarmsPage.css'; // Create this file for styling

function FarmsPage() {
  const [farms, setFarms] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchFarms = async () => {
      try {
        setLoading(true);
        const response = await getFarms();
        setFarms(response.data);
        setError(null);
      } catch (err) {
        console.error("Error fetching farms:", err);
        setError(err.message || 'Failed to fetch farms. Is the backend running?');
        if (err.response) {
          console.error("Error details:", err.response.data);
          setError(`Failed to fetch farms: ${err.response.status} ${err.response.statusText}. ${err.response.data.detail || ''}`);
        }
      } finally {
        setLoading(false);
      }
    };

    fetchFarms();
  }, []);

  if (loading) return <p>Loading farms...</p>;
  if (error) return <p style={{ color: 'red' }}>Error: {error}</p>;

  return (
    <div className="farms-page">
      <h1>Available Farms</h1>
      {farms.length === 0 ? (
        <p>No farms found. You can add farms via the API or a future admin interface.</p>
      ) : (
        <ul className="farms-list">
          {farms.map((farm) => (
            <li key={farm.id} className="farm-item">
              {/* Link to a farm detail page - to be created */}
              <Link to={`/farms/${farm.id}`}> 
                <h2>{farm.name}</h2>
              </Link>
              <p><strong>Location:</strong> {farm.location_text || 'N/A'}</p>
              <p><strong>Total Area:</strong> {farm.total_area_hectares ? `${farm.total_area_hectares} ha` : 'N/A'}</p>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

export default FarmsPage;
