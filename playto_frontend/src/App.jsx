import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import Feed from './components/Feed';
import PostDetail from './components/PostDetail';
import Leaderboard from './components/Leaderboard';

function App() {
  const [currentUser, setCurrentUser] = useState(null);

  return (
    <Router>
      <div className="min-h-screen bg-gray-100">
        <Navbar currentUser={currentUser} setCurrentUser={setCurrentUser} />

        <div className="container mx-auto p-4 md:flex md:space-x-6">
          <main className="flex-1">
            <Routes>
              <Route path="/" element={<Feed currentUser={currentUser} />} />
              <Route path="/post/:id" element={<PostDetail currentUser={currentUser} />} />
            </Routes>
          </main>

          <aside className="mt-6 md:mt-0 md:w-80">
            <Leaderboard />
          </aside>
        </div>
      </div>
    </Router>
  );
}

export default App;
