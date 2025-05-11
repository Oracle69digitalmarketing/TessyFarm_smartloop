// frontend_dashboard/src/pages/EditCropCyclePage.jsx
import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import CropCycleForm from '../components/CropCycleForm';
import { getCropCycleById, updateCropCycle } from '../services/api';

function EditCropCyclePage() {
  const { cycleId } = useParams();
  const navigate = useNavigate();
  const [initialData, setInitialData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchCycle = async () => {
      if (!cycleId) {
        setError("Crop Cycle ID is missing.");
        setLoading(false);
        return;
      }
      try {
        setLoading(true);
        const response = await getCropCycleById(cycleId);
        setInitialData(response.data);
        setError(null);
      } catch (err) {
        console.error("Failed to fetch crop cycle for editing:", err);
        setError(err.response?.data?.detail || err.message || "Failed to load crop cycle data.");
      } finally {
        setLoading(false);
      }
    };
    fetchCycle();
  }, [cycleId]);

  const handleSubmit = async (cycleData) => {
    try {
      await updateCropCycle(cycleId, cycleData);
      alert('Crop Cycle updated successfully!');
      navigate(`/crop-cycles/${cycleId}`); // Navigate back to the cycle's detail page
    } catch (error) {
      console.error('Failed to update crop cycle:', error);
      throw error; // Re-throw for CropCycleForm
    }
  };

  if (loading) return <p>Loading crop cycle data for editing...</p>;
  if (error) return <p style={{color: 'red'}}>Error: {error}</p>;
  if (!initialData && !loading) return <p>Crop cycle data not found.</p>;

  return (
    <div className="page-container">
      <h2>Edit Crop Cycle: {initialData?.crop_type || 'Crop Cycle'} (ID: {cycleId})</h2>
      {initialData && (
        <CropCycleForm 
          onSubmit={handleSubmit} 
          initialData={initialData}
          submitButtonText="Update Crop Cycle"
          isEditMode={true}
        />
      )}
    </div>
  );
}

export default EditCropCyclePage;
