from elasticsearch import Elasticsearch
from elastic_transport import ConnectionError
from config import Config
from utils.es_utils import wait_for_elasticsearch
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def populate_data():
    # Real-world travel destinations data
    destinations = [
        {
            "destination": "Bali, Indonesia",
            "price": 1200,
            "type": "beach",
            "activities": "surfing, temples, diving, yoga",
            "season": "dry_season",
            "rating": 4.5,
            "reviews_count": 1250,
            "amenities": ["wifi", "restaurants", "shopping"],
            "language": "Indonesian",
            "currency": "IDR",
            "timezone": "UTC+8"
        },
        {"destination": "Queenstown, New Zealand", "price": 2000, "type": "adventure", "activities": "skiing, bungee jumping, hiking", "season": "winter"},
        {"destination": "Paris, France", "price": 1800, "type": "cultural", "activities": "museums, dining, architecture", "season": "spring"},
        {"destination": "Tokyo, Japan", "price": 2200, "type": "urban", "activities": "shopping, temples, dining, cherry blossoms", "season": "spring"},
        {"destination": "Maldives", "price": 3000, "type": "luxury", "activities": "snorkeling, diving, spa, overwater villas", "season": "winter"},
        {"destination": "Machu Picchu, Peru", "price": 1500, "type": "historical", "activities": "hiking, archaeology, photography", "season": "dry_season"},
        {"destination": "Safari, Tanzania", "price": 4000, "type": "adventure", "activities": "wildlife viewing, photography, camping", "season": "dry_season"},
        {"destination": "Santorini, Greece", "price": 1700, "type": "romantic", "activities": "beaches, wine tasting, sunset viewing", "season": "summer"},
        {"destination": "Swiss Alps", "price": 2500, "type": "mountains", "activities": "skiing, hiking, mountain biking", "season": "winter"},
        {"destination": "Great Barrier Reef", "price": 2300, "type": "nature", "activities": "diving, snorkeling, boat tours", "season": "summer"},
        {"destination": "Grand Canyon, USA", "price": 1500, "type": "nature", "activities": "hiking, sightseeing, photography, rafting", "season": "spring"},
        {"destination": "Bangkok, Thailand", "price": 1000, "type": "cultural", "activities": "temples, street food, shopping, nightlife", "season": "winter"},
        {"destination": "Dubai, UAE", "price": 2800, "type": "luxury", "activities": "shopping, desert safari, architecture, beaches", "season": "winter"},
        {"destination": "Banff, Canada", "price": 2200, "type": "mountains", "activities": "skiing, hiking, lake activities, wildlife viewing", "season": "winter"},
        {"destination": "Barcelona, Spain", "price": 1600, "type": "cultural", "activities": "architecture, beaches, dining, art", "season": "summer"},
        {"destination": "Cape Town, South Africa", "price": 1800, "type": "diverse", "activities": "beaches, wine tasting, hiking, cultural tours", "season": "spring"}
    ]

    # Add destination reviews
    destination_reviews = [
        {
            "destination": "Bali, Indonesia",
            "user_id": "user123",
            "rating": 5,
            "review": "Amazing experience!",
            "date": "2023-01-15",
            "helpful_votes": 45
        },

    ]

    # Current travel trends data
    travel_trends = [
        {"trend": "sustainable tourism", "popularity": 92, "season": "all"},
        {"trend": "digital nomad destinations", "popularity": 88, "season": "all"},
        {"trend": "wellness retreats", "popularity": 85, "season": "all"},
        {"trend": "adventure sports", "popularity": 80, "season": "summer"},
        {"trend": "cultural immersion", "popularity": 78, "season": "spring"},
        {"trend": "luxury escapes", "popularity": 75, "season": "winter"},
        {"trend": "food tourism", "popularity": 82, "season": "all"},
        {"trend": "eco-friendly stays", "popularity": 87, "season": "all"}
    ]

    # Sample user profiles for testing
    user_profiles = [
        {
            "user_id": "user123",
            "preferences": {
                "activities": ["beach", "diving", "luxury"],
                "budget_range": "high",
                "preferred_seasons": ["summer", "winter"]
            },
            "past_searches": ["Maldives", "luxury resorts", "beach destinations"]
        },
        {
            "user_id": "user456",
            "preferences": {
                "activities": ["hiking", "adventure", "photography"],
                "budget_range": "medium",
                "preferred_seasons": ["spring", "fall"]
            },
            "past_searches": ["hiking trails", "adventure sports", "mountain destinations"]
        }
    ]

    try:
        es = wait_for_elasticsearch()
        
        # Delete existing indices
        if es.indices.exists(index="destinations"):
            es.indices.delete(index="destinations")
        
        # Create index with mapping
        es.indices.create(
            index="destinations",
            body={
                "mappings": {
                    "properties": {
                        "destination": {"type": "text", "analyzer": "standard"},
                        "type": {"type": "text", "analyzer": "standard"},
                        "activities": {"type": "text", "analyzer": "standard"},
                        "season": {"type": "keyword"},
                        "price": {"type": "integer"},
                        "rating": {"type": "float"},
                        "reviews_count": {"type": "integer"},
                        "amenities": {"type": "keyword"},
                        "language": {"type": "keyword"},
                        "currency": {"type": "keyword"},
                        "timezone": {"type": "keyword"}
                    }
                }
            }
        )

        # Create reviews index
        es.indices.create(
            index="destination_reviews",
            body={
                "mappings": {
                    "properties": {
                        "destination": {"type": "keyword"},
                        "user_id": {"type": "keyword"},
                        "rating": {"type": "float"},
                        "review": {"type": "text"},
                        "date": {"type": "date"},
                        "helpful_votes": {"type": "integer"}
                    }
                }
            }
        )
        
        # Index destinations
        for destination in destinations:
            try:
                es.index(index="destinations", body=destination)
            except Exception as e:
                print(f"Error indexing destination {destination['destination']}: {e}")

        # Index travel trends
        for trend in travel_trends:
            try:
                es.index(index="travel_trends", body=trend)
            except Exception as e:
                print(f"Error indexing trend {trend['trend']}: {e}")

        # Index user profiles
        for profile in user_profiles:
            try:
                es.index(index="user_profiles", body=profile)
            except Exception as e:
                print(f"Error indexing user profile {profile['user_id']}: {e}")

        # Index reviews
        for review in destination_reviews:
            try:
                es.index(index="destination_reviews", body=review)
            except Exception as e:
                print(f"Error indexing review: {e}")

        print("Data population completed successfully!")
        
    except Exception as e:
        print(f"Error during data population: {e}")
        raise

if __name__ == "__main__":
    populate_data()
