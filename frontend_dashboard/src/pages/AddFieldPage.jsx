// frontend_dashboard/src/pages/AddFieldPage.jsx
import React from 'react';
import { useNavigate, useParams, useLocation } from 'react-router-dom';
import FieldForm from '../components/FieldForm';
import { createField } from '../services/api';

function AddFieldPage() {
  const navigate = useNavigate();
  const { farmId: farmIdFromParams } = useParams(); // To catch /farms/:farmId/fields/new
  const location = useLocation(); // To catch farmId from state if passed via Link

  // Determine preselectedFarmId:
  // 1. From route params (e.g. /farms/:farmId/fields/new)
  // 2. From location state (if navigated with state: <Link to="/fields/new" state={{ farmId: someId }} />)
  const preselectedFarmId = farmIdFromParams || location.state?.farmId || null;

  const handleSubmit = async (fieldData) => {
    try {
      const response = await createField(fieldData);
      alert('Field created successfully!');
      // Navigate to the field detail page, or back to the farm it was added to
      navigate(`/fields/${response.data.id}`); 
      // Or navigate(`/farms/${response.data.farm_id}`);
    } catch (error) {
      console.error('Failed to create field:', error);
      throw error; // Re-throw for FieldForm to display
    }
  };

  return (
    <div className="page-container">
      <h2>Create New Field</h2>
      <FieldForm 
        onSubmit={handleSubmit} 
        submitButtonText="Create Field"
        preselectedFarmId={preselectedFarmId ? parseInt(preselectedFarmId, 10) : null}
      />
    </div>
  );
}

export default AddFieldPage;
