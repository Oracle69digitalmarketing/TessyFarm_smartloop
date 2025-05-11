// frontend_dashboard/src/components/CropCycleForm.jsx
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { getFields } from '../services/api'; // To fetch fields for the dropdown
import './CropCycleForm.css'; // Create this for styling

// Helper to format date for datetime-local input
const formatDateForInput = (dateString) => {
  if (!dateString) return '';
  const date = new Date(dateString);
  // Adjust for timezone offset to display local time correctly in input
  const timezoneOffset = date.getTimezoneOffset() * 60000; // offset in milliseconds
  const localDate = new Date(date.getTime() - timezoneOffset);
  return localDate.toISOString().slice(0, 16); // YYYY-MM-DDTHH:MM
};


function CropCycleForm({ onSubmit, initialData = null, submitButtonText = "Submit", isEditMode = false, preselectedFieldId = null }) {
  const [formData, setFormData] = useState({
    field_id: preselectedFieldId || '',
    crop_type: '',
    planting_date: '',
    expected_harvest_date: '',
    actual_harvest_date: '',
    actual_yield_tonnes: '',
    notes: ''
  });
  const [fields, setFields] = useState([]);
  const [loadingFields, setLoadingFields] = useState(true);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchFieldsList = async () => {
      try {
        setLoadingFields(true);
        const response = await getFields(); // Fetch all fields
        setFields(response.data);
        if (!isEditMode && preselectedFieldId) {
          setFormData(prevData => ({ ...prevData, field_id: preselectedFieldId }));
        }
      } catch (err) {
        console.error("Failed to fetch fields:", err);
        setError("Could not load fields for selection.");
      } finally {
        setLoadingFields(false);
      }
    };
    fetchFieldsList();
  }, [isEditMode, preselectedFieldId]);

  useEffect(() => {
    if (isEditMode && initialData) {
      setFormData({
        field_id: initialData.field_id || '',
        crop_type: initialData.crop_type || '',
        planting_date: formatDateForInput(initialData.planting_date),
        expected_harvest_date: formatDateForInput(initialData.expected_harvest_date),
        actual_harvest_date: formatDateForInput(initialData.actual_harvest_date),
        actual_yield_tonnes: initialData.actual_yield_tonnes !== null && initialData.actual_yield_tonnes !== undefined ? initialData.actual_yield_tonnes : '',
        notes: initialData.notes || ''
      });
    } else if (!isEditMode) { // For add mode, ensure dates are empty strings initially
        setFormData(prev => ({
            ...prev,
            planting_date: '',
            expected_harvest_date: '',
            actual_harvest_date: '',
        }));
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
    if (!formData.field_id) {
      setError("Please select a field.");
      return;
    }
    if (!formData.planting_date) {
        setError("Planting date is required.");
        return;
    }

    setLoading(true);
    setError(null);
    try {
      const dataToSubmit = {
        ...formData,
        field_id: parseInt(formData.field_id, 10),
        // Ensure dates are sent in ISO format (datetime-local input provides this, but ensure it's not empty string if optional)
        planting_date: formData.planting_date ? new Date(formData.planting_date).toISOString() : null,
        expected_harvest_date: formData.expected_harvest_date ? new Date(formData.expected_harvest_date).toISOString() : null,
        actual_harvest_date: formData.actual_harvest_date ? new Date(formData.actual_harvest_date).toISOString() : null,
        actual_yield_tonnes: formData.actual_yield_tonnes !== '' ? parseFloat(formData.actual_yield_tonnes) : null,
      };
      // Remove null dates if backend expects them to be absent rather than null, depends on Pydantic model
      if (!dataToSubmit.expected_harvest_date) delete dataToSubmit.expected_harvest_date;
      if (!dataToSubmit.actual_harvest_date) delete dataToSubmit.actual_harvest_date;
      if (dataToSubmit.actual_yield_tonnes === null) delete dataToSubmit.actual_yield_tonnes;


      await onSubmit(dataToSubmit);
    } catch (err) {
      console.error("Crop cycle form submission error:", err);
      setError(err.response?.data?.detail || err.message || "An error occurred submitting the crop cycle data.");
       if (typeof err.response?.data?.detail === 'string') {
        setError(err.response.data.detail);
      } else if (Array.isArray(err.response?.data?.detail)) {
        // Handle FastAPI validation errors (list of dicts)
        const messages = err.response.data.detail.map(d => `${d.loc.join('->')}: ${d.msg}`).join('; ');
        setError(messages);
      } else {
        setError(err.message || "An unknown error occurred.");
      }
    } finally {
      setLoading(false);
    }
  };

  if (loadingFields) {
    return <p>Loading field data...</p>;
  }

  return (
    <form onSubmit={handleSubmit} className="crop-cycle-form">
      {error && <p className="form-error">Error: {error}</p>}
      
      <div className="form-group">
        <label htmlFor="field_id">Belongs to Field:</label>
        <select
          id="field_id"
          name="field_id"
          value={formData.field_id}
          onChange={handleChange}
          required
          disabled={isEditMode} // Usually field doesn't change on edit
        >
          <option value="">-- Select a Field --</option>
          {fields.map(field => (
            <option key={field.id} value={field.id}>
              {field.name} (Farm ID: {field.farm_id}, Field ID: {field.id})
            </option>
          ))}
        </select>
      </div>

      <div className="form-group">
        <label htmlFor="crop_type">Crop Type:</label>
        <input
          type="text"
          id="crop_type"
          name="crop_type"
          value={formData.crop_type}
          onChange={handleChange}
          required
          maxLength="100"
        />
      </div>

      <div className="form-group">
        <label htmlFor="planting_date">Planting Date:</label>
        <input
          type="datetime-local"
          id="planting_date"
          name="planting_date"
          value={formData.planting_date}
          onChange={handleChange}
          required
        />
      </div>

      <div className="form-group">
        <label htmlFor="expected_harvest_date">Expected Harvest Date (Optional):</label>
        <input
          type="datetime-local"
          id="expected_harvest_date"
          name="expected_harvest_date"
          value={formData.expected_harvest_date}
          onChange={handleChange}
        />
      </div>
      
      <div className="form-group">
        <label htmlFor="actual_harvest_date">Actual Harvest Date (Optional - for completed cycles):</label>
        <input
          type="datetime-local"
          id="actual_harvest_date"
          name="actual_harvest_date"
          value={formData.actual_harvest_date}
          onChange={handleChange}
        />
      </div>

      <div className="form-group">
        <label htmlFor="actual_yield_tonnes">Actual Yield (Tonnes - for completed cycles):</label>
        <input
          type="number"
          id="actual_yield_tonnes"
          name="actual_yield_tonnes"
          value={formData.actual_yield_tonnes}
          onChange={handleChange}
          step="0.01"
          min="0"
        />
      </div>

      <div className="form-group">
        <label htmlFor="notes">Notes (Optional):</label>
        <textarea
          id="notes"
          name="notes"
          value={formData.notes}
          onChange={handleChange}
          rows="3"
        ></textarea>
      </div>

      <div className="form-actions">
        <button type="submit" disabled={loading || loadingFields} className="button-primary">
          {loading ? (isEditMode ? 'Updating...' : 'Creating...') : submitButtonText}
        </button>
        <button type="button" onClick={() => navigate(-1)} className="button-secondary" disabled={loading || loadingFields}>
          Cancel
        </button>
      </div>
    </form>
  );
}

export default CropCycleForm;
