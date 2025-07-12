import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';

const Register = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({ username: '', email: '', password: '' });
  const [error, setError] = useState('');

  const handleRegister = async (e) => {
    e.preventDefault();
    setError('');

    try {
      const res = await fetch('http://localhost:5000/api/auth/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData),
      });

      const data = await res.json();

      if (!res.ok) {
        setError(data.error || 'Registration failed');
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
      <h2 className="text-2xl font-semibold mb-4">Sign Up</h2>
      <form onSubmit={handleRegister} className="space-y-4">
        <input
          type="text"
          placeholder="Username"
          value={formData.username}
          onChange={(e) => setFormData({ ...formData, username: e.target.value })}
          className="w-full p-3 rounded bg-gray-800 text-white border border-gray-600"
        />
        <input
          type="email"
          placeholder="Email"
          value={formData.email}
          onChange={(e) => setFormData({ ...formData, email: e.target.value })}
          className="w-full p-3 rounded bg-gray-800 text-white border border-gray-600"
        />
        <input
          type="password"
          placeholder="Password"
          value={formData.password}
          onChange={(e) => setFormData({ ...formData, password: e.target.value })}
          className="w-full p-3 rounded bg-gray-800 text-white border border-gray-600"
        />
        {error && <p className="text-red-400">{error}</p>}
        <button
          type="submit"
          className="w-full bg-green-600 hover:bg-green-700 py-2 rounded text-white"
        >
          Sign Up
        </button>
      </form>

      <p className="text-center mt-4 text-sm">
        Already have an account?{' '}
        <Link to="/login" className="text-blue-400 hover:underline">
          Log in
        </Link>
      </p>
    </div>
  );
};

export default Register;
