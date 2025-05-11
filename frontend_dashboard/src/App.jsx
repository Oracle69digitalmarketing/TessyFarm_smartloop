// frontend_dashboard/src/App.jsx
import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import FarmsPage from './pages/FarmsPage';
// Import other pages here later
// import FarmDetailPage from './pages/FarmDetailPage'; 
import './App.css'; // For global app styles

function App() {
  return (
    <Router>
      <div>
        <nav className="app-nav">
          <ul>
            <li><Link to="/">Home (Farms)</Link></li>
            {/* Add other global links here */}
          </ul>
        </nav>
        <main className="app-content">
          <Routes>
            <Route path="/" element={<FarmsPage />} />
            <Route path="/farms" element={<FarmsPage />} /> 
            {/* Example for a future farm detail page */}
            {/* <Route path="/farms/:farmId" element={<FarmDetailPage />} /> */}
            {/* Add more routes here */}
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
