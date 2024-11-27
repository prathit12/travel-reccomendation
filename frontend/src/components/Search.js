import React, { useState } from 'react';
import axios from 'axios';
import './Search.css';
import defaultImage from '../assets/images/default.jpg';

function Search() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);
  const [filters, setFilters] = useState({
    type: '',
    season: '',
    maxPrice: '',
    activities: '',
    amenities: '',
    language: '',
    currency: '',
    timezone: ''
  });
  const [sortBy, setSortBy] = useState('price');
  const [favorites, setFavorites] = useState([]);

  // Updated image mapping with local assets
  const getImageUrl = (type) => {
    try {
      // First try to load dynamic image
      return require(`../assets/images/${type.toLowerCase()}.jpg`);
    } catch (e) {
      // If type-specific image doesn't exist, use default
      return defaultImage;
    }
  };

  const handleSearch = async () => {
    if (!query.trim()) return;
    
    setLoading(true);
    setError(null);
    try {
      const response = await axios.get('/search', { 
        params: { 
          q: query,
          ...filters,
          sort: sortBy
        } 
      });
      // Enhanced image handling with error fallback
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
      
      <div className="filters">
        <select value={filters.type} onChange={(e) => setFilters(prev => ({ ...prev, type: e.target.value }))}>
          <option value="">All Types</option>
          <option value="beach">Beach</option>
          <option value="mountain">Mountain</option>
          <option value="city">City</option>
          <option value="countryside">Countryside</option>
        </select>

        <select value={filters.season} onChange={(e) => setFilters(prev => ({ ...prev, season: e.target.value }))}>
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
          onChange={(e) => setFilters(prev => ({ ...prev, maxPrice: e.target.value }))}
        />

        <select value={sortBy} onChange={(e) => setSortBy(e.target.value)}>
          <option value="price">Price</option>
          <option value="popularity">Popularity</option>
          <option value="rating">Rating</option>
        </select>

        <select value={filters.amenities} onChange={(e) => setFilters(prev => ({ ...prev, amenities: e.target.value }))}>
          <option value="">All Amenities</option>
          <option value="wifi">WiFi</option>
          <option value="restaurants">Restaurants</option>
          <option value="shopping">Shopping</option>
        </select>

        <select value={filters.language} onChange={(e) => setFilters(prev => ({ ...prev, language: e.target.value }))}>
          <option value="">All Languages</option>
          <option value="English">English</option>
          <option value="Spanish">Spanish</option>
          <option value="French">French</option>
        </select>

        <select value={filters.currency} onChange={(e) => setFilters(prev => ({ ...prev, currency: e.target.value }))}>
          <option value="">All Currencies</option>
          <option value="USD">USD</option>
          <option value="EUR">EUR</option>
          <option value="JPY">JPY</option>
        </select>

        <select value={filters.timezone} onChange={(e) => setFilters(prev => ({ ...prev, timezone: e.target.value }))}>
          <option value="">All Timezones</option>
          <option value="UTC-5">UTC-5</option>
          <option value="UTC+1">UTC+1</option>
          <option value="UTC+8">UTC+8</option>
        </select>
      </div>

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
          onClick={handleSearch} 
          disabled={loading}
          aria-label="Search button"
        >
          {loading ? 'Searching...' : 'Explore'}
        </button>
      </div>

      {error && <div className="error" role="alert">{error}</div>}

      {results.length > 0 ? (
        <div className="results">
          {results.map((result, index) => (
            <div key={index} className="result-card">
              <button 
                className={`favorite-btn ${favorites.includes(result.id) ? 'active' : ''}`}
                onClick={() => toggleFavorite(result)}
              >
                ❤
              </button>
              <img 
                src={result.image} 
                alt={result.destination}
                onError={(e) => {
                  e.target.onerror = null; // Prevent infinite loop
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
                <p><strong>Popular Times:</strong> {result.popularTimes}</p>
                <p><strong>Local Weather:</strong> {result.weather}</p>
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