// frontend_dashboard/src/pages/AddFarmPage.jsx
import React from 'react';
import { useNavigate } from 'react-router-dom';
import FarmForm from '../components/FarmForm';
import { createFarm } from '../services/api';

function AddFarmPage() {
  const navigate = useNavigate();

  const handleSubmit = async (farmData) => {
    try {
      const response = await createFarm(farmData);
      alert('Farm created successfully!');
      navigate(`/farms/${response.data.id}`); // Navigate to the new farm's detail page
    } catch (error) {
      console.error('Failed to create farm:', error);
      // The FarmForm component will display specific API errors if passed up
      throw error; // Re-throw to let FarmForm handle displaying the error
    }
  };

  return (
    <div className="page-container">
      <h2>Create New Farm</h2>
      <FarmForm 
        onSubmit={handleSubmit} 
        submitButtonText="Create Farm" 
      />
    </div>
  );
}

export default AddFarmPage;
