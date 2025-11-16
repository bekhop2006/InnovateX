/**
 * Auth Page - Login/Register
 */
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import LoginForm from '../components/LoginForm';
import RegisterForm from '../components/RegisterForm';
import './AuthPage.scss';

const AuthPage = () => {
  const [mode, setMode] = useState('login'); // 'login' or 'register'
  const { login, register, error } = useAuth();
  const navigate = useNavigate();

  const handleLogin = async (email, password) => {
    await login(email, password);
    navigate('/dashboard');
  };

  const handleRegister = async (userData) => {
    await register(userData);
    navigate('/dashboard');
  };

  return (
    <div className="auth-page">
      <div className="auth-container">
        <div className="auth-header">
          <h1>InnovateX Document Scanner</h1>
          <p>Sign in to access your scan history and manage documents</p>
        </div>

        {mode === 'login' ? (
          <LoginForm
            onLogin={handleLogin}
            onSwitchToRegister={() => setMode('register')}
            error={error}
          />
        ) : (
          <RegisterForm
            onRegister={handleRegister}
            onSwitchToLogin={() => setMode('login')}
            error={error}
          />
        )}
      </div>
    </div>
  );
};

export default AuthPage;

