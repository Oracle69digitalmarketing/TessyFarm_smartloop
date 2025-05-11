// frontend_dashboard/src/App.jsx
import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import FarmsPage from './pages/FarmsPage';
import FarmDetailPage from './pages/FarmDetailPage';
import FieldDetailPage from './pages/FieldDetailPage';
import CropCycleDetailPage from './pages/CropCycleDetailPage'; // <--- IMPORT NEW PAGE
import './App.css';

function App() {
  return (
    <Router>
      <div>
        <nav className="app-nav">
          <ul>
            <li><Link to="/">Home</Link></li>
            <li><Link to="/farms">Farms</Link></li>
            {/* Fields link might not be top-level as it's usually context-dependent */}
          </ul>
        </nav>
        <main className="app-content">
          <Routes>
            <Route path="/" element={<FarmsPage />} />
            <Route path="/farms" element={<FarmsPage />} /> 
            <Route path="/farms/:farmId" element={<FarmDetailPage />} />
            <Route path="/fields/:fieldId" element={<FieldDetailPage />} />
            <Route path="/crop-cycles/:cycleId" element={<CropCycleDetailPage />} /> {/* <--- ADDED ROUTE */}
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
