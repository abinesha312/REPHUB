// App.jsx
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { useState } from 'react';
import Navbar from './components/Navbar';
import HomePage from './pages/HomePage';
import ResumesPage from './pages/ResumePage';
import JobsPage from './pages/JobsPage';
import MatchPage from './pages/MatchPage';
import './App.css';

function App() {
  const [userId, setUserId] = useState(1); // Mock user ID for development

  return (
    <BrowserRouter>
      <Navbar />
      <div className="container">
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/resumes" element={<ResumesPage userId={userId} />} />
          <Route path="/jobs" element={<JobsPage userId={userId} />} />
          <Route path="/match" element={<MatchPage userId={userId} />} />
        </Routes>
      </div>
    </BrowserRouter>
  );
}

export default App;