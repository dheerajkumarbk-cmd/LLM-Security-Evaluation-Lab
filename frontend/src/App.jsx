import React from 'react';
import { BrowserRouter, Routes, Route, NavLink } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import RunDetail from './pages/RunDetail';
import Compare from './pages/Compare';
import History from './pages/History';
import LiveTest from './pages/LiveTest';
import Methodology from './pages/Methodology';

function App() {
  return (
    <BrowserRouter>
      <div className="app-container">
        <aside className="sidebar">
          <h1>LLM Security Lab</h1>
          <nav className="nav-links">
            <NavLink to="/" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`} end>Dashboard</NavLink>
            <NavLink to="/compare" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>Compare</NavLink>
            <NavLink to="/history" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>History</NavLink>
            <NavLink to="/live" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>Live Test</NavLink>
            <NavLink to="/methodology" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>Methodology</NavLink>
          </nav>
        </aside>
        <main className="main-content">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/runs/:id" element={<RunDetail />} />
            <Route path="/compare" element={<Compare />} />
            <Route path="/history" element={<History />} />
            <Route path="/live" element={<LiveTest />} />
            <Route path="/methodology" element={<Methodology />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}

export default App;
