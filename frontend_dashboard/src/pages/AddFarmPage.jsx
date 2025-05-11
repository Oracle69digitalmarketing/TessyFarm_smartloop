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
    // At the top of frontend_dashboard/src/pages/FarmsPage.jsx, inside the return:
// import { Link } from 'react-router-dom'; // Ensure Link is imported if not already
// ...
// return (
//   <div className="farms-page">
//     <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
//       <h1>Available Farms</h1>
//       <Link to="/farms/new" className="button-add-new">Add New Farm</Link>
//     </div>
// ...
// );

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
