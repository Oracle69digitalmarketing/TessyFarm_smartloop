// frontend_dashboard/src/App.jsx
import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import FarmsPage from './pages/FarmsPage';
import FarmDetailPage from './pages/FarmDetailPage'; // <--- IMPORT NEW PAGE
// Import other pages here later
// import FieldDetailPage from './pages/FieldDetailPage'; 
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
            <Route path="/" element={<FarmsPage />} /> {/* Default to FarmsPage */}
            <Route path="/farms" element={<FarmsPage />} /> 
            <Route path="/farms/:farmId" element={<FarmDetailPage />} /> {/* <--- ADDED ROUTE */}
            {/* Example for a future field detail page */}
            {/* <Route path="/fields/:fieldId" element={<FieldDetailPage />} /> */}
            {/* Add more routes here */}
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
