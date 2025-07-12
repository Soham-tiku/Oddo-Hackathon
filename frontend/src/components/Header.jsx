import { Link } from 'react-router-dom';

const Header = () => (
  <header className="bg-black text-white p-4 flex justify-between items-center shadow">
    <Link to="/" className="text-2xl font-bold">StackIt</Link>
    <div className="flex gap-4 items-center">
      <Link to="/ask" className="bg-blue-500 px-3 py-1 rounded">Ask New Question</Link>
      <button className="bg-gray-800 px-3 py-1 rounded">Login</button>
    </div>
  </header>
);

export default Header;