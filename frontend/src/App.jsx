import React, { useState } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { ThemeProvider, createTheme, CssBaseline } from '@mui/material';
import Navbar from './components/Navbar';
import HomePage from './pages/HomePage';
import ResumePage from './pages/ResumePage';
import MatchPage from './pages/MatchPage';

const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
  },
});

function App() {
  const [userId] = useState(1); // Default user for demo

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <BrowserRouter>
        <Navbar />
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/resumes" element={<ResumePage userId={userId} />} />
          <Route path="/match" element={<MatchPage userId={userId} />} />
        </Routes>
      </BrowserRouter>
    </ThemeProvider>
  );
}

export default App;
