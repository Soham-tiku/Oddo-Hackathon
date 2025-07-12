import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';

const Login = () => {
  const navigate = useNavigate();
  const [identifier, setIdentifier] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  const handleLogin = async (e) => {
    e.preventDefault();
    setError('');

    try {
      const res = await fetch('http://localhost:5000/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ identifier, password }),
      });

      const data = await res.json();

      if (!res.ok) {
        setError(data.error || 'Login failed');
        return;
      }

      localStorage.setItem('token', data.access_token);
      navigate('/');
    } catch (err) {
      setError('Server error. Try again later.');
    }
  };

  return (
    <div className="max-w-md mx-auto mt-16 text-white p-4">
      <h2 className="text-2xl font-semibold mb-4">Login</h2>
      <form onSubmit={handleLogin} className="space-y-4">
        <input
          type="text"
          placeholder="Email or Username"
          value={identifier}
          onChange={(e) => setIdentifier(e.target.value)}
          className="w-full p-3 rounded bg-gray-800 text-white border border-gray-600"
        />
        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          className="w-full p-3 rounded bg-gray-800 text-white border border-gray-600"
        />
        {error && <p className="text-red-400">{error}</p>}
        <button
          type="submit"
          className="w-full bg-blue-600 hover:bg-blue-700 py-2 rounded text-white"
        >
          Log In
        </button>
      </form>

      <p className="text-center mt-4 text-sm">
        Don’t have an account?{' '}
        <Link to="/register" className="text-blue-400 hover:underline">
          Sign up
        </Link>
      </p>
    </div>
  );
};

export default Login;
