// frontend_dashboard/src/pages/EditFarmPage.jsx
import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import FarmForm from '../components/FarmForm';
import { getFarmById, updateFarm } from '../services/api';

function EditFarmPage() {
  const { farmId } = useParams();
  const navigate = useNavigate();
  const [initialData, setInitialData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchFarm = async () => {
      try {
        setLoading(true);
        const response = await getFarmById(farmId);
        setInitialData(response.data);
        setError(null);
      } catch (err) {
        console.error("Failed to fetch farm for editing:", err);
        setError(err.response?.data?.detail || err.message || "Failed to load farm data.");
      } finally {
        setLoading(false);
      }
    };
    fetchFarm();
  }, [farmId]);

  const handleSubmit = async (farmData) => {
    try {
      await updateFarm(farmId, farmData);
      alert('Farm updated successfully!');
      navigate(`/farms/${farmId}`); // Navigate back to the farm's detail page
    } catch (error) {
      console.error('Failed to update farm:', error);
      throw error; // Re-throw to let FarmForm handle displaying the error
    }
  };

  if (loading) return <p>Loading farm data for editing...</p>;
  if (error) return <p style={{color: 'red'}}>Error: {error}</p>;
  if (!initialData) return <p>Farm data not found.</p>;

  return (
    <div className="page-container">
      <h2>Edit Farm: {initialData.name}</h2>
      <FarmForm 
        onSubmit={handleSubmit} 
        initialData={initialData}
        submitButtonText="Update Farm"
        isEditMode={true}
      />
    </div>
  );
}

export default EditFarmPage;
