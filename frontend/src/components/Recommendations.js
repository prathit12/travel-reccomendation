import React, { useState } from 'react';
import axios from 'axios';

function Recommendations() {
  const [userId, setUserId] = useState('');
  const [recommendations, setRecommendations] = useState([]);
  const [error, setError] = useState(null);

  const handleGetRecommendations = async () => {
    if (!userId.trim()) {
      setError('User ID is required.');
      return;
    }

    try {
      const response = await axios.get('/recommendations', { params: { user_id: String(userId) } });
      setRecommendations(response.data);
      if (response.data.length === 0) {
        setError('No recommendations found for this user.');
      } else {
        setError(null);
      }
    } catch (error) {
      console.error('Error fetching recommendations:', error);
      setError('Failed to fetch recommendations.');
    }
  };

  const saveRecommendation = async (recommendation) => {
    try {
      await axios.post('/save-recommendation', { user_id: String(userId), recommendation });
      alert('Recommendation saved!');
    } catch (error) {
      console.error('Error saving recommendation:', error);
    }
  };

  return (
    <div>
      <h1>Get Recommendations</h1>
      <input
        type="text"
        value={userId}
        onChange={(e) => setUserId(e.target.value)}
        placeholder="Enter user ID..."
      />
      <button onClick={handleGetRecommendations}>Get Recommendations</button>
      {error && <p>{error}</p>}
      <ul>
        {recommendations.map((recommendation, index) => (
          <li key={index}>
            {recommendation.destination}
            <button onClick={() => saveRecommendation(recommendation)}>Save</button>
          </li>
        ))}
      </ul>
    </div>
  );
}

export default Recommendations;