import React, { useState } from "react";
import { useNavigate } from "react-router-dom";

const AskQuestion = () => {
  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");
  const [error, setError] = useState("");
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");

    const token = localStorage.getItem("token");
    if (!token) {
      setError("You must be logged in to post a question.");
      return;
    }

    try {
      const res = await fetch("http://localhost:5000/api/questions", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ title, content }),
      });

      const data = await res.json();

      if (!res.ok) {
        setError(data.error || "Failed to post question.");
        return;
      }

      navigate("/"); // redirect on success
    } catch (err) {
      console.error("❌ Error submitting question:", err);
      setError("Something went wrong. Please try again.");
    }
  };

  return (
    <div className="max-w-3xl mx-auto text-white mt-8 px-4">
      <h2 className="text-2xl font-semibold mb-4">Ask a New Question</h2>
      <form onSubmit={handleSubmit} className="space-y-4">
        <input
          type="text"
          placeholder="Enter question title"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          className="w-full p-3 bg-gray-800 border border-gray-600 rounded"
        />
        <textarea
          placeholder="Enter question content"
          value={content}
          onChange={(e) => setContent(e.target.value)}
          className="w-full p-3 h-40 bg-gray-800 border border-gray-600 rounded"
        />
        {error && <p className="text-red-400">{error}</p>}
        <button
          type="submit"
          className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded"
        >
          Submit
        </button>
      </form>
    </div>
  );
};

export default AskQuestion;
