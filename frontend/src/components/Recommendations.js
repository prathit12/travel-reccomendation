import React, { useState } from 'react';
import axios from 'axios';

function Recommendations() {
  const [userId, setUserId] = useState('');
  const [recommendations, setRecommendations] = useState([]);

  const handleGetRecommendations = async () => {
    try {
      const response = await axios.get('/recommendations', { params: { user_id: userId } });
      setRecommendations(response.data);
    } catch (error) {
      console.error('Error fetching recommendations:', error);
    }
  };

  const saveRecommendation = async (recommendation) => {
    try {
      await axios.post('/save-recommendation', { user_id: userId, recommendation });
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
      <ul>
        {recommendations.map((recommendation, index) => (
          <li key={index}>
            {recommendation._source.destination}
            <button onClick={() => saveRecommendation(recommendation)}>Save</button>
          </li>
        ))}
      </ul>
    </div>
  );
}

export default Recommendations;