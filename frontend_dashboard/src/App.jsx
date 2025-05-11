// frontend_dashboard/src/App.jsx
import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import FarmsPage from './pages/FarmsPage';
import FarmDetailPage from './pages/FarmDetailPage';
import FieldDetailPage from './pages/FieldDetailPage';
import CropCycleDetailPage from './pages/CropCycleDetailPage';
import AddFarmPage from './pages/AddFarmPage'; // <--- IMPORT
import EditFarmPage from './pages/EditFarmPage'; // <--- IMPORT
import './App.css';

function App() {
  return (
    <Router>
      <div>
        <nav className="app-nav">
          <ul>
            <li><Link to="/">Home</Link></li>
            <li><Link to="/farms">Farms</Link></li>
            <li><Link to="/farms/new">Add Farm</Link></li> {/* <--- ADD LINK */}
          </ul>
        </nav>
        <main className="app-content">
          <Routes>
            <Route path="/" element={<FarmsPage />} />
            <Route path="/farms" element={<FarmsPage />} /> 
            <Route path="/farms/new" element={<AddFarmPage />} /> {/* <--- ADD ROUTE */}
            <Route path="/farms/:farmId" element={<FarmDetailPage />} />
            <Route path="/farms/:farmId/edit" element={<EditFarmPage />} /> {/* <--- ADD ROUTE */}
            <Route path="/fields/:fieldId" element={<FieldDetailPage />} />
            <Route path="/crop-cycles/:cycleId" element={<CropCycleDetailPage />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;

// In frontend_dashboard/src/services/api.js
export const getFarmById = (farmId) => apiClient.get(`/farms/${farmId}`);
export const updateFarm = (farmId, farmData) => apiClient.put(`/farms/${farmId}`, farmData);
