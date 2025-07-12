import React from "react";
import { useNavigate } from "react-router-dom";
import { FaArrowUp, FaArrowDown } from "react-icons/fa";

const QuestionCard = ({ question }) => {
  const navigate = useNavigate();

  return (
    <div className="bg-gray-800 p-4 rounded shadow hover:shadow-lg transition">
      <div className="flex justify-between items-center">
        <div>
          <h2
            onClick={() => navigate(`/question/${question.id}`)}
            className="text-xl font-semibold cursor-pointer hover:text-blue-400"
          >
            {question.title}
          </h2>
          <p
            className="text-sm text-gray-400"
            dangerouslySetInnerHTML={{ __html: question.body }}
          />
        </div>
        <div className="flex flex-col items-center space-y-1">
          <button className="text-green-400 hover:text-green-500">
            <FaArrowUp />
          </button>
          <span>{question.votes || 0}</span>
          <button className="text-red-400 hover:text-red-500">
            <FaArrowDown />
          </button>
        </div>
      </div>
    </div>
  );
};

export default QuestionCard;
