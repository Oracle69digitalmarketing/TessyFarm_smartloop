// frontend_dashboard/src/App.jsx
import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
// ... (other page imports)
import AddFarmPage from './pages/AddFarmPage';
import EditFarmPage from './pages/EditFarmPage';
import AddFieldPage from './pages/AddFieldPage'; // <--- IMPORT
import EditFieldPage from './pages/EditFieldPage'; // <--- IMPORT
import './App.css';

function App() {
  return (
    <Router>
      <div>
        <nav className="app-nav">
          <ul>
            <li><Link to="/">Home</Link></li>
            <li><Link to="/farms">Farms</Link></li>
            <li><Link to="/farms/new">Add Farm</Link></li>
            {/* General "Add Field" link, farm selected in form */}
            <li><Link to="/fields/new">Add Field</Link></li> 
          </ul>
        </nav>
        <main className="app-content">
          <Routes>
            {/* ... (Farm routes) ... */}
            <Route path="/farms/new" element={<AddFarmPage />} />
            <Route path="/farms/:farmId/edit" element={<EditFarmPage />} />
            
            {/* Field Routes */}
            <Route path="/fields/new" element={<AddFieldPage />} /> {/* General add field */}
            <Route path="/farms/:farmId/fields/new" element={<AddFieldPage />} /> {/* Add field under specific farm */}
            <Route path="/fields/:fieldId" element={<FieldDetailPage />} />
            <Route path="/fields/:fieldId/edit" element={<EditFieldPage />} />
            
            {/* ... (Crop Cycle routes) ... */}
            <Route path="/crop-cycles/:cycleId" element={<CropCycleDetailPage />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
