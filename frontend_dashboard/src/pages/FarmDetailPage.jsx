// frontend_dashboard/src/pages/FarmDetailPage.jsx
import React, { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom'; // <--- Ensure Link is imported
import { getFarmById } from '../services/api';
import './FarmDetailPage.css';

function FarmDetailPage() {
  const { farmId } = useParams();
  const navigate = useNavigate(); // For the back button
  const [farm, setFarm] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchFarmDetails = async () => {
      try {
        setLoading(true);
        const response = await getFarmById(farmId);
        setFarm(response.data);
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
  }, [farmId]);

  if (loading) return <p>Loading farm details...</p>;
  if (error) return <p style={{ color: 'red' }}>Error: {error}</p>;
  if (!farm) return <p>Farm not found.</p>;

  return (
    <div className="farm-detail-page">
      <button onClick={() => navigate(-1)} className="back-button">&larr; Back</button> {/* Using button for navigate(-1) */}
      
      <header className="farm-header">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
          <div>
            <h1>{farm.name}</h1>
            <p><strong>Location:</strong> {farm.location_text || 'N/A'}</p>
            <p><strong>Total Area:</strong> {farm.total_area_hectares ? `${farm.total_area_hectares} ha` : 'N/A'}</p>
            <p><strong>Farm ID:</strong> {farm.id}</p>
            <p><strong>Created:</strong> {new Date(farm.created_at).toLocaleDateString()}</p>
          </div>
          {/* --- ADDED EDIT LINK/BUTTON --- */}
          <Link to={`/farms/${farm.id}/edit`} className="button-edit"> 
            Edit Farm
          </Link>
        </div>
        // In frontend_dashboard/src/pages/FieldDetailPage.jsx
// ... (inside the return, likely in the header)
// <header className="field-header">
//   <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
//     <div>
//       <h1>Field: {field.name}</h1>
//       {/* ... other field details ... */}
//     </div>
//     <Link to={`/fields/${field.id}/edit`} className="button-edit">Edit Field</Link>
//   </div>
// </header>
// ...
      </header>

      <section className="fields-section">
        <h2>Fields in this Farm</h2>
        {farm.fields && farm.fields.length > 0 ? (
          <ul className="fields-list">
            {farm.fields.map((field) => (
              <li key={field.id} className="field-item">
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
        // In frontend_dashboard/src/pages/FarmDetailPage.jsx
// ... (inside the return, in the fields-section)
// <section className="fields-section">
//   <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
//      <h2>Fields in this Farm</h2>
//      <Link to={`/farms/${farm.id}/fields/new`} state={{ farmId: farm.id }} className="button-add-new"> 
//         Add New Field
//      </Link>
//      {/* Or just <Link to={`/fields/new`} state={{ farmId: farm.id }} ... if using the general add field page and passing state */}
//   </div>
// ...
  
      </section>
    </div>
  );
}

export default FarmDetailPage;
