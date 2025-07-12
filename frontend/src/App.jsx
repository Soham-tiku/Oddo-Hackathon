import React from 'react';
import { Routes, Route } from 'react-router-dom';
import HomePage from './pages/HomePage';
import AskQuestion from './pages/AskQuestion';
import QuestionDetails from './pages/QuestionDetails';
import Navbar from './components/Navbar';
import Login from './pages/Login';
import Register from './pages/Register';

function App() {
  return (
    <>
      <Navbar />
      <div className="text-white p-4">
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/ask" element={<AskQuestion />} />
          <Route path="/question/:id" element={<QuestionDetails />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
        </Routes>
      </div>
    </>
  );
}

export default App;
