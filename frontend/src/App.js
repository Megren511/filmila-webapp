import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import Navbar from './components/Navbar';
import HomePage from './pages/HomePage';
import FilmUpload from './pages/FilmUpload';
import WatchFilm from './pages/WatchFilm';
import Login from './pages/Login';
import Register from './pages/Register';
import FilmmakerDashboard from './pages/FilmmakerDashboard';
import ProtectedRoute from './components/ProtectedRoute';
import { AuthProvider } from './context/AuthContext';

const theme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#e50914',
    },
    secondary: {
      main: '#ffffff',
    },
  },
});

function App() {
  return (
    <AuthProvider>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <Router>
          <Navbar />
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route 
              path="/dashboard" 
              element={
                <ProtectedRoute requiredRole="filmmaker">
                  <FilmmakerDashboard />
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/upload" 
              element={
                <ProtectedRoute requiredRole="filmmaker">
                  <FilmUpload />
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/watch/:filmId" 
              element={
                <ProtectedRoute>
                  <WatchFilm />
                </ProtectedRoute>
              } 
            />
          </Routes>
        </Router>
      </ThemeProvider>
    </AuthProvider>
  );
}

export default App;
