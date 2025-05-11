// frontend_dashboard/src/pages/AddCropCyclePage.jsx
import React from 'react';
import { useNavigate, useParams, useLocation } from 'react-router-dom';
import CropCycleForm from '../components/CropCycleForm';
import { createCropCycle } from '../services/api';

function AddCropCyclePage() {
  const navigate = useNavigate();
  const { fieldId: fieldIdFromParams } = useParams(); // To catch /fields/:fieldId/crop-cycles/new
  const location = useLocation();

  const preselectedFieldId = fieldIdFromParams || location.state?.fieldId || null;

  const handleSubmit = async (cycleData) => {
    try {
      const response = await createCropCycle(cycleData);
      alert('Crop Cycle created successfully!');
      navigate(`/crop-cycles/${response.data.id}`); // Navigate to the new cycle's detail page
      // Or navigate(`/fields/${response.data.field_id}`); // Or back to the field detail page
    } catch (error) {
      console.error('Failed to create crop cycle:', error);
      throw error; // Re-throw for CropCycleForm to display
    }
  };

  return (
    <div className="page-container">
      <h2>Create New Crop Cycle</h2>
      <CropCycleForm 
        onSubmit={handleSubmit} 
        submitButtonText="Create Crop Cycle"
        preselectedFieldId={preselectedFieldId ? parseInt(preselectedFieldId, 10) : null}
      />
    </div>
  );
}

export default AddCropCyclePage;
