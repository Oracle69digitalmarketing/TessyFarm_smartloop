// frontend_dashboard/src/pages/EditFieldPage.jsx
import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import FieldForm from '../components/FieldForm';
import { getFieldById, updateField } from '../services/api';

function EditFieldPage() {
  const { fieldId } = useParams();
  const navigate = useNavigate();
  const [initialData, setInitialData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchField = async () => {
      if (!fieldId) {
        setError("Field ID is missing.");
        setLoading(false);
        return;
      }
      try {
        setLoading(true);
        const response = await getFieldById(fieldId);
        setInitialData(response.data);
        setError(null);
      } catch (err) {
        console.error("Failed to fetch field for editing:", err);
        setError(err.response?.data?.detail || err.message || "Failed to load field data.");
      } finally {
        setLoading(false);
      }
    };
    fetchField();
  }, [fieldId]);

  const handleSubmit = async (fieldData) => {
    try {
      await updateField(fieldId, fieldData);
      alert('Field updated successfully!');
      navigate(`/fields/${fieldId}`); // Navigate back to the field's detail page
    } catch (error) {
      console.error('Failed to update field:', error);
      throw error; // Re-throw for FieldForm
    }
  };

  if (loading) return <p>Loading field data for editing...</p>;
  if (error) return <p style={{color: 'red'}}>Error: {error}</p>;
  if (!initialData && !loading) return <p>Field data not found.</p>;

  return (
    <div className="page-container">
      <h2>Edit Field: {initialData?.name || 'Field'}</h2>
      {initialData && (
        <FieldForm 
          onSubmit={handleSubmit} 
          initialData={initialData}
          submitButtonText="Update Field"
          isEditMode={true}
        />
      )}
    </div>
  );
}

export default EditFieldPage;
