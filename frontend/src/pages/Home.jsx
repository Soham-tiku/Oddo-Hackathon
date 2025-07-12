import { Link } from 'react-router-dom';

const Home = () => {
  return (
    <div className="p-6 text-white">
      <div className="flex justify-between items-center mb-4">
        <input type="text" placeholder="Search" className="px-3 py-1 rounded text-black" />
        <select className="text-black px-2 py-1 rounded">
          <option>Newest</option>
          <option>Unanswered</option>
        </select>
      </div>

      <div className="space-y-4">
        {[1, 2].map((q, i) => (
          <Link to={`/question/${q}`} key={i} className="block bg-gray-800 p-4 rounded hover:bg-gray-700">
            <h2 className="text-lg font-semibold">How to join 2 columns in SQL</h2>
            <p className="text-sm mt-1">I want to combine First Name and Last Name into one column...</p>
          </Link>
        ))}
      </div>

      <div className="mt-6 flex justify-center gap-2">
        {[1, 2, 3, 4, 5, 6, 7].map(num => (
          <button key={num} className="px-3 py-1 bg-gray-700 hover:bg-gray-600 rounded">{num}</button>
        ))}
      </div>
    </div>
  );
};

export default Home;