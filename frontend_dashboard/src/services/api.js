// frontend_dashboard/src/services/api.js
import axios from 'axios';

// Determine the API base URL. For development, this typically points to your local backend.
// In a production build, this might be a different URL.
// Vite exposes environment variables prefixed with VITE_ to the client-side code.
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// You can add interceptors for handling global errors or adding auth tokens later
// apiClient.interceptors.request.use(config => {
//   const token = localStorage.getItem('authToken');
//   if (token) {
//     config.headers.Authorization = `Bearer ${token}`;
//   }
//   return config;
// });

// apiClient.interceptors.response.use(
//   response => response,
//   error => {
//     // Handle global errors, e.g., redirect to login on 401
//     if (error.response && error.response.status === 401) {
//       // window.location = '/login'; // Or use React Router's navigate
//     }
//     return Promise.reject(error);
//   }
// );


// --- Farm Endpoints ---
export const getFarms = () => apiClient.get('/farms/');
export const getFarmById = (farmId) => apiClient.get(`/farms/${farmId}`); // Returns FarmResponseWithFields
export const createFarm = (farmData) => apiClient.post('/farms/', farmData);
export const updateFarm = (farmId, farmData) => apiClient.put(`/farms/${farmId}`, farmData);
// export const deleteFarm = (farmId) => apiClient.delete(`/farms/${farmId}`); // For future implementation


// --- Field Endpoints ---
export const getFields = (farmId) => { // Can filter by farm_id
  let url = '/fields/';
  if (farmId) {
    url += `?farm_id=${farmId}`;
  }
  return apiClient.get(url);
};
export const getFieldById = (fieldId) => apiClient.get(`/fields/${fieldId}`); // Returns FieldResponseWithCropCycles
// --- Functions to be added when implementing Field forms ---
// export const createField = (fieldData) => apiClient.post('/fields/', fieldData);
// export const updateField = (fieldId, fieldData) => apiClient.put(`/fields/${fieldId}`, fieldData);
// export const deleteField = (fieldId) => apiClient.delete(`/fields/${fieldId}`);


// --- Crop Cycle Endpoints ---
export const getCropCycles = (fieldId) => { // Can filter by field_id
  let url = '/crop-cycles/';
  if (fieldId) {
    url += `?field_id=${fieldId}`;
  }
  return apiClient.get(url);
};
export const getCropCycleById = (cycleId) => apiClient.get(`/crop-cycles/${cycleId}`);
// --- Functions to be added when implementing Crop Cycle forms ---
// export const createCropCycle = (cycleData) => apiClient.post('/crop-cycles/', cycleData);
// export const updateCropCycle = (cycleId, cycleData) => apiClient.put(`/crop-cycles/${cycleId}`, cycleData);
// export const deleteCropCycle = (cycleId) => apiClient.delete(`/crop-cycles/${cycleId}`);


// --- Prediction Endpoints ---
export const getCurrentYieldPredictionForField = (fieldId) =>
  apiClient.get(`/predictions/fields/${fieldId}/current-yield-prediction`);

export const getYieldPredictionForCycle = (cropCycleId) =>
  apiClient.get(`/predictions/yield-predictions/${cropCycleId}`);


// --- Sensor Data Endpoints ---
// Placeholder for when you implement the specific backend endpoint
// export const getSensorDataForField = (fieldId, queryParams) => 
//   apiClient.get(`/fields/${fieldId}/sensor-data`, { params: queryParams }); 
// Example queryParams: { type: 'temperature', start_date: 'YYYY-MM-DD', end_date: 'YYYY-MM-DD' }

export default apiClient;
