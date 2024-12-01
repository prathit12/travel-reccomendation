import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import './Search.css';

function DestinationDetails() {
  const { id } = useParams();
  const [destination, setDestination] = useState(null);
  const [reviews, setReviews] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`/destination/${id}`)
      .then(response => {
        if (!response.ok) {
          throw new Error('Destination not found');
        }
        return response.json();
      })
      .then(data => {
        setDestination(data.destination);
        setReviews(data.reviews);
        setLoading(false);
      })
      .catch(error => {
        console.error('Error:', error);
        setLoading(false);
      });
  }, [id]);

  if (loading) return <div>Loading...</div>;
  if (!destination) return <div>Destination not found</div>;

  return (
    <div className="destination-details">
      <h1>{destination.destination}</h1>
      
      <div className="details-section">
        <h2>Details</h2>
        <p><strong>Type:</strong> {destination.type}</p>
        <p><strong>Activities:</strong> {destination.activities}</p>
        <p><strong>Season:</strong> {destination.season}</p>
        <p><strong>Price:</strong> ${destination.price}</p>
        <p><strong>Rating:</strong> {destination.rating}/5</p>
        <p><strong>Reviews Count:</strong> {destination.reviews_count}</p>
        <p><strong>Timezone:</strong> {destination.timezone}</p>
      </div>

      <div className="reviews-section">
        <h2>Reviews</h2>
        {reviews.map((review, index) => (
          <div key={index} className="review-card">
            <p className="reviewer">{review.reviewer_name}</p>
            <p className="review-text">{review.review_statement}</p>
            <p className="review-date">{review.date}</p>
          </div>
        ))}
      </div>
    </div>
  );
}

export default DestinationDetails;