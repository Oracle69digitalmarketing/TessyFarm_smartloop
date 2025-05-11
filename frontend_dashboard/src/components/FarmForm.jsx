// frontend_dashboard/src/components/FarmForm.jsx
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import './FarmForm.css'; // Create this for styling

function FarmForm({ onSubmit, initialData = null, submitButtonText = "Submit", isEditMode = false }) {
  const [formData, setFormData] = useState({
    name: '',
    location_text: '',
    total_area_hectares: ''
  });
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    if (isEditMode && initialData) {
      setFormData({
        name: initialData.name || '',
        location_text: initialData.location_text || '',
        total_area_hectares: initialData.total_area_hectares || ''
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
    setLoading(true);
    setError(null);
    try {
      // Convert area to float, handle empty string
      const dataToSubmit = {
        ...formData,
        total_area_hectares: formData.total_area_hectares ? parseFloat(formData.total_area_hectares) : null
      };
      await onSubmit(dataToSubmit);
      // Navigation will be handled by the parent component (AddFarmPage or EditFarmPage)
    } catch (err) {
      console.error("Form submission error:", err);
      setError(err.response?.data?.detail || err.message || "An error occurred.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="farm-form">
      {error && <p className="form-error">Error: {error}</p>}
      
      <div className="form-group">
        <label htmlFor="name">Farm Name:</label>
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
        <label htmlFor="location_text">Location:</label>
        <input
          type="text"
          id="location_text"
          name="location_text"
          value={formData.location_text}
          onChange={handleChange}
          maxLength="255"
        />
      </div>

      <div className="form-group">
        <label htmlFor="total_area_hectares">Total Area (hectares):</label>
        <input
          type="number"
          id="total_area_hectares"
          name="total_area_hectares"
          value={formData.total_area_hectares}
          onChange={handleChange}
          step="0.01"
          min="0"
        />
      </div>

      <div className="form-actions">
        <button type="submit" disabled={loading} className="button-primary">
          {loading ? (isEditMode ? 'Updating...' : 'Creating...') : submitButtonText}
        </button>
        <button type="button" onClick={() => navigate(-1)} className="button-secondary" disabled={loading}>
          Cancel
        </button>
      </div>
    </form>
  );
}

export default FarmForm;
