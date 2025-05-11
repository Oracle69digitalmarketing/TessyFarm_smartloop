// frontend_dashboard/src/components/FieldForm.jsx
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { getFarms } from '../services/api'; // To fetch farms for the dropdown
import './FieldForm.css'; // Create this for styling

function FieldForm({ onSubmit, initialData = null, submitButtonText = "Submit", isEditMode = false, preselectedFarmId = null }) {
  const [formData, setFormData] = useState({
    name: '',
    farm_id: preselectedFarmId || '', // Initialize with preselectedFarmId if provided
    area_hectares: '',
    soil_type: ''
  });
  const [farms, setFarms] = useState([]);
  const [loadingFarms, setLoadingFarms] = useState(true);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    // Fetch all farms for the dropdown
    const fetchFarmsList = async () => {
      try {
        setLoadingFarms(true);
        const response = await getFarms();
        setFarms(response.data);
        // If creating a new field and preselectedFarmId is provided, ensure it's set.
        // If editing, farm_id will be set by initialData effect.
        if (!isEditMode && preselectedFarmId) {
            setFormData(prevData => ({ ...prevData, farm_id: preselectedFarmId }));
        }
      } catch (err) {
        console.error("Failed to fetch farms:", err);
        setError("Could not load farms for selection.");
      } finally {
        setLoadingFarms(false);
      }
    };
    fetchFarmsList();
  }, [isEditMode, preselectedFarmId]); // Rerun if preselectedFarmId changes (though unlikely for this form)

  useEffect(() => {
    if (isEditMode && initialData) {
      setFormData({
        name: initialData.name || '',
        farm_id: initialData.farm_id || '',
        area_hectares: initialData.area_hectares || '',
        soil_type: initialData.soil_type || ''
      });
    }
  }, [initialData, isEditMode]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prevData => ({
      ...prevData,
      [name]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!formData.farm_id) {
        setError("Please select a farm.");
        return;
    }
    setLoading(true);
    setError(null);
    try {
      const dataToSubmit = {
        ...formData,
        farm_id: parseInt(formData.farm_id, 10), // Ensure farm_id is an integer
        area_hectares: formData.area_hectares ? parseFloat(formData.area_hectares) : null
      };
      await onSubmit(dataToSubmit);
    } catch (err) {
      console.error("Field form submission error:", err);
      setError(err.response?.data?.detail || err.message || "An error occurred submitting the field data.");
    } finally {
      setLoading(false);
    }
  };

  if (loadingFarms) {
    return <p>Loading farm data...</p>;
  }

  return (
    <form onSubmit={handleSubmit} className="field-form">
      {error && <p className="form-error">Error: {error}</p>}
      
      <div className="form-group">
        <label htmlFor="farm_id">Belongs to Farm:</label>
        <select
          id="farm_id"
          name="farm_id"
          value={formData.farm_id}
          onChange={handleChange}
          required
          disabled={isEditMode} // Typically farm association doesn't change on edit, or handle carefully
        >
          <option value="">-- Select a Farm --</option>
          {farms.map(farm => (
            <option key={farm.id} value={farm.id}>
              {farm.name} (ID: {farm.id})
            </option>
          ))}
        </select>
      </div>

      <div className="form-group">
        <label htmlFor="name">Field Name:</label>
        <input
          type="text"
          id="name"
          name="name"
          value={formData.name}
          onChange={handleChange}
          required
          maxLength="100"
        />
      </div>

      <div className="form-group">
        <label htmlFor="area_hectares">Area (hectares):</label>
        <input
          type="number"
          id="area_hectares"
          name="area_hectares"
          value={formData.area_hectares}
          onChange={handleChange}
          step="0.01"
          min="0"
        />
      </div>

      <div className="form-group">
        <label htmlFor="soil_type">Soil Type:</label>
        <input
          type="text"
          id="soil_type"
          name="soil_type"
          value={formData.soil_type}
          onChange={handleChange}
          maxLength="50"
        />
      </div>

      <div className="form-actions">
        <button type="submit" disabled={loading || loadingFarms} className="button-primary">
          {loading ? (isEditMode ? 'Updating...' : 'Creating...') : submitButtonText}
        </button>
        <button type="button" onClick={() => navigate(-1)} className="button-secondary" disabled={loading || loadingFarms}>
          Cancel
        </button>
      </div>
    </form>
  );
}

export default FieldForm;
