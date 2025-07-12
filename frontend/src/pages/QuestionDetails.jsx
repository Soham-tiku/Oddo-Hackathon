import React from 'react';

const QuestionDetails = () => {
  // TODO: fetch question & answers
  return (
    <div className="max-w-4xl mx-auto p-6 text-white">
      <h2 className="text-2xl font-bold mb-2">Question Title Goes Here</h2>
      <p className="mb-4 text-gray-300">Asked by John Doe · 2 hours ago</p>
      <div className="bg-gray-800 p-4 rounded mb-6">
        <p>Question body and rich content goes here...</p>
      </div>

      <h3 className="text-xl font-semibold mb-2">Answers</h3>
      <div className="space-y-4">
        <div className="bg-gray-700 p-4 rounded">
          <p>Sample answer content here...</p>
        </div>
      </div>
    </div>
  );
};

export default QuestionDetails;
