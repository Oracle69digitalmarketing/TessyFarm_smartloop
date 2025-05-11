// frontend_dashboard/src/App.jsx
import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import FarmsPage from './pages/FarmsPage';
import FarmDetailPage from './pages/FarmDetailPage';
import FieldDetailPage from './pages/FieldDetailPage'; // <--- IMPORT NEW PAGE
// Import other pages here later
// import CropCycleDetailPage from './pages/CropCycleDetailPage';
import './App.css';

function App() {
  return (
    <Router>
      <div>
        <nav className="app-nav">
          <ul>
            <li><Link to="/">Home</Link></li>
            <li><Link to="/farms">Farms</Link></li>
            {/* Add other global links here */}
          </ul>
        </nav>
        <main className="app-content">
          <Routes>
            <Route path="/" element={<FarmsPage />} />
            <Route path="/farms" element={<FarmsPage />} /> 
            <Route path="/farms/:farmId" element={<FarmDetailPage />} />
            <Route path="/fields/:fieldId" element={<FieldDetailPage />} /> {/* <--- ADDED ROUTE */}
            {/* Example for a future crop cycle detail page */}
            {/* <Route path="/crop-cycles/:cycleId" element={<CropCycleDetailPage />} /> */}
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
