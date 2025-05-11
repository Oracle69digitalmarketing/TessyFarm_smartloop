// frontend_dashboard/src/services/api.js
import axios from 'axios';

const apiClient = axios.create({
  baseURL: 'http://localhost:8000/api/v1', // Your backend API URL
  headers: {
    'Content-Type': 'application/json',
  },
});

// --- Farm Endpoints ---
export const getFarms = () => apiClient.get('/farms/');
export const getFarmById = (farmId) => apiClient.get(`/farms/${farmId}`);
// Add create, update, delete later:
// export const createFarm = (farmData) => apiClient.post('/farms/', farmData);

// --- Field Endpoints ---
export const getFields = (farmId) => {
  let url = '/fields/';
  if (farmId) {
    url += `?farm_id=${farmId}`;
  }
  return apiClient.get(url);
};
export const getFieldById = (fieldId) => apiClient.get(`/fields/${fieldId}`);

// --- Crop Cycle Endpoints ---
export const getCropCycles = (fieldId) => {
  let url = '/crop-cycles/';
  if (fieldId) {
    url += `?field_id=${fieldId}`;
  }
  return apiClient.get(url);
};
export const getCropCycleById = (cycleId) => apiClient.get(`/crop-cycles/${cycleId}`);

// --- Prediction Endpoints ---
export const getCurrentYieldPredictionForField = (fieldId) => 
  apiClient.get(`/predictions/fields/${fieldId}/current-yield-prediction`);

export const getYieldPredictionForCycle = (cropCycleId) =>
  apiClient.get(`/predictions/yield-predictions/${cropCycleId}`);

// Add more functions as you create more backend endpoints
// Example for sensor data (if you create the new backend endpoint)
// export const getSensorDataForField = (fieldId, params) => apiClient.get(`/fields/${fieldId}/sensor-data`, { params });

export default apiClient;
