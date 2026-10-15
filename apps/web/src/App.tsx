import { Link, Route, Routes } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import Generate from './pages/Generate';
import TimetableView from './pages/TimetableView';
import Inputs from './pages/Inputs';

export default function App() {
  return (
    <div className="min-h-screen bg-gray-50 text-gray-900">
      <nav className="border-b bg-white px-6 py-3 flex gap-4">
        <Link className="font-bold" to="/">TimetableGen</Link>
        <Link to="/inputs">Inputs</Link>
        <Link to="/generate">Generate</Link>
        <Link to="/view">View</Link>
      </nav>
      <main className="p-6 max-w-6xl mx-auto">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/inputs" element={<Inputs />} />
          <Route path="/generate" element={<Generate />} />
          <Route path="/view" element={<TimetableView />} />
        </Routes>
      </main>
    </div>
  );
}
