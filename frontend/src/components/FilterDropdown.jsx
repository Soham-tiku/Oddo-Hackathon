import React, { useState } from 'react';

const FilterDropdown = () => {
  const [selected, setSelected] = useState('Newest');

  return (
    <div className="flex justify-end mb-2">
      <select
        value={selected}
        onChange={(e) => setSelected(e.target.value)}
        className="bg-gray-800 border border-gray-600 text-white px-3 py-2 rounded"
      >
        <option>Newest</option>
        <option>Unanswered</option>
        <option>Most Voted</option>
      </select>
    </div>
  );
};

export default FilterDropdown;
