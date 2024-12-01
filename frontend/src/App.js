import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import Search from './components/Search';
import Recommendations from './components/Recommendations';
import DestinationDetails from './components/DestinationDetails';

function App() {
  return (
    <Router>
      <div className="App">
        <Routes>
          <Route path="/" element={<Search />} />
          <Route path="/search" element={<Search />} />
          <Route path="/recommendations" element={<Recommendations />} />
          <Route path="/destination/:id" element={<DestinationDetails />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;