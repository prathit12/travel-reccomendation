import React, { useState } from 'react';
import axios from 'axios';
import './Search.css';
import defaultImage from '../assets/images/default.jpg';

function Search() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);
  const [filtersVisible, setFiltersVisible] = useState(false);
  const [filters, setFilters] = useState({
    type: '',
    season: '',
    maxPrice: '',
    activities: '',
    rating: '',
    language: '',
    currency: '',
    timezone: ''
  });
  const [sortBy, setSortBy] = useState('price');
  const [favorites, setFavorites] = useState([]);

  // Updated image mapping with local assets
  const getImageUrl = (type) => {
    try {
      return require(`../assets/images/${type.toLowerCase()}.jpg`);
    } catch (e) {
      return defaultImage;
    }
  };

  const handleSearch = async (filtersOverride = filters) => {
    if (!query.trim()) return;

    setLoading(true);
    setError(null);
    setFiltersVisible(true); // Show filters after the first search

    try {
      const response = await axios.get('/search', { 
        params: { 
          q: query,
          ...filtersOverride,
          sort: sortBy
        } 
      });

      const resultsWithImages = response.data.map(result => ({
        ...result,
        image: result.imageUrl || getImageUrl(result.type)
      }));
      setResults(resultsWithImages);
    } catch (err) {
      setError('Failed to fetch results');
      console.error('Search error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleFilterChange = (filterKey, value) => {
    const updatedFilters = { ...filters, [filterKey]: value };
    setFilters(updatedFilters);
    handleSearch(updatedFilters);
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleSearch();
    }
  };

  const toggleFavorite = (destination) => {
    setFavorites(prev => 
      prev.includes(destination.id) 
        ? prev.filter(id => id !== destination.id)
        : [...prev, destination.id]
    );
  };

  return (
    <div className="search-container">
      <h1>Discover Your Next Adventure</h1>

      <div className="search-box">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Where would you like to go?"
          aria-label="Search destinations"
        />
        <button 
          onClick={() => handleSearch()} 
          disabled={!query.trim()}
          aria-label="Search button"
        >
          {loading ? 'Searching...' : 'Explore'}
        </button>
      </div>

      {filtersVisible && (
        <div className="filters">
          <select value={filters.type} onChange={(e) => handleFilterChange('type', e.target.value)}>
            <option value="">All Types</option>
            <option value="beach">Beach</option>
            <option value="mountain">Mountain</option>
            <option value="adventure">Adventure</option>
            <option value="nature">Nature</option>
            <option value="urban">Urban</option>
          </select>

          <select value={filters.season} onChange={(e) => handleFilterChange('season', e.target.value)}>
            <option value="">All Seasons</option>
            <option value="summer">Summer</option>
            <option value="winter">Winter</option>
            <option value="spring">Spring</option>
            <option value="fall">Fall</option>
          </select>

          <input
            type="number"
            placeholder="Max Price"
            value={filters.maxPrice}
            onChange={(e) => handleFilterChange('maxPrice', e.target.value)}
          />

          <select value={filters.rating} onChange={(e) => handleFilterChange('rating', e.target.value)}>
            <option value="">Rating</option>
            <option value="1">1</option>
            <option value="2">2</option>
            <option value="3">3</option>
            <option value="4">4</option>
            <option value="5">5</option>
          </select>

          <select value={filters.timezone} onChange={(e) => handleFilterChange('timezone', e.target.value)}>
            <option value="">Select Timezone</option>
            <option value="GMT">GMT</option>
            <option value="EST">EST</option>
            <option value="UTC">UTC</option>
            <option value="IST">IST</option>
          </select>

        </div>
      )}

      {error && <div className="error" role="alert">{error}</div>}

      {results.length > 0 ? (
        <div className="results">
          {results.map((result, index) => (
            <div key={index} className="result-card">
              {/* <button 
                className={`favorite-btn ${favorites.includes(result.id) ? 'active' : ''}`}
                onClick={() => toggleFavorite(result)}
              >
                ❤
              </button> */}
              <img 
                src={result.image} 
                alt={result.destination}
                onError={(e) => {
                  e.target.onerror = null;
                  e.target.src = defaultImage;
                }}
              />
              <h3>{result.destination}</h3>
              <p><strong>Type:</strong> {result.type}</p>
              <p><strong>Activities:</strong> {result.activities}</p>
              <p><strong>Season:</strong> {result.season}</p>
              <p><strong>Price:</strong> ${result.price}</p>
              <div className="additional-info">
                <p><strong>Rating:</strong> {result.rating}/5</p>
                {/* <p><strong>Popular Times:</strong> {result.popularTimes}</p>
                <p><strong>Local Weather:</strong> {result.weather}</p> */}
              </div>
            </div>
          ))}
        </div>
      ) : (
        <p className="no-results">{!loading && query && 'No destinations found'}</p>
        
      )}
    </div>
  );
}

export default Search;


