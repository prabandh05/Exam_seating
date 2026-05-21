import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from './context/AuthContext';
import LoginPage from './pages/auth/LoginPage';
import AdminLayout from './pages/admin/AdminLayout';
import InvigilatorLayout from './pages/invigilator/InvigilatorLayout';
import StudentLayout from './pages/student/StudentLayout';

const ProtectedRoute: React.FC<{ children: React.ReactNode; role: string }> = ({ children, role }) => {
  const { user, isAuthenticated } = useAuth();
  if (!isAuthenticated) return <Navigate to="/login" />;
  if (user?.role !== role) return <Navigate to="/login" />;
  return <>{children}</>;
};

const App: React.FC = () => {
  const { user, isAuthenticated } = useAuth();

  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/admin/*" element={
        <ProtectedRoute role="admin"><AdminLayout /></ProtectedRoute>
      } />
      <Route path="/invigilator/*" element={
        <ProtectedRoute role="invigilator"><InvigilatorLayout /></ProtectedRoute>
      } />
      <Route path="/student/*" element={
        <ProtectedRoute role="student"><StudentLayout /></ProtectedRoute>
      } />
      <Route path="/" element={
        isAuthenticated ? (
          <Navigate to={`/${user?.role}`} />
        ) : (
          <Navigate to="/login" />
        )
      } />
      <Route path="*" element={<Navigate to="/" />} />
    </Routes>
  );
};

export default App;
