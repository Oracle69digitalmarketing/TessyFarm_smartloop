// frontend_dashboard/src/services/api.js
// ... (apiClient and other existing functions) ...

// --- Farm Endpoints ---
// ... (getFarms, getFarmById, createFarm, updateFarm) ...

// --- Field Endpoints ---
export const getFields = (farmId) => {
  let url = '/fields/';
  if (farmId) {
    url += `?farm_id=${farmId}`;
  }
  return apiClient.get(url);
};
export const getFieldById = (fieldId) => apiClient.get(`/fields/${fieldId}`);
export const createField = (fieldData) => apiClient.post('/fields/', fieldData); // <--- NEW
export const updateField = (fieldId, fieldData) => apiClient.put(`/fields/${fieldId}`, fieldData); // <--- NEW
// export const deleteField = (fieldId) => apiClient.delete(`/fields/${fieldId}`); // <--- For future implementation

// --- Crop Cycle Endpoints ---
// ... (getCropCycles, getCropCycleById) ...

// --- Prediction Endpoints ---
// ... (getCurrentYieldPredictionForField, getYieldPredictionForCycle) ...

// --- Sensor Data Endpoints ---
// ... (placeholder for getSensorDataForField) ...

export default apiClient;
