import React, { useEffect, useState } from "react";
import QuestionCard from "../components/QuestionCard";
import FilterDropdown from "../components/FilterDropdown";
import { useNavigate } from "react-router-dom";

const HomePage = () => {
  const [questions, setQuestions] = useState([]);
  const navigate = useNavigate();

  useEffect(() => {
    fetch("http://localhost:5000/api/questions")
      .then((res) => res.json())
      .then((data) => setQuestions(data.questions))
      .catch((err) => console.error("Failed to fetch questions:", err));
  }, []);

  return (
    <div className="p-4 text-white">
      <div className="flex justify-between items-center mb-4">
        <h1 className="text-3xl font-semibold">StackIt</h1>
        <button
          onClick={() => navigate("/ask")}
          className="bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded"
        >
          Ask Question
        </button>
      </div>

      <FilterDropdown />

      <div
        className="space-y-4 mt-4 overflow-y-auto"
        style={{ maxHeight: "70vh" }}
      >
        {questions.length === 0 ? (
          <p>No questions yet.</p>
        ) : (
          questions.map((question) => (
            <QuestionCard key={question.id} question={question} />
          ))
        )}
      </div>
    </div>
  );
};

export default HomePage;
