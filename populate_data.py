import pgeocode
import json
from elasticsearch import Elasticsearch
from config import Config

def fetch_popular_destinations(country_codes, num_cities_per_country=20):
    """
    Fetch popular travel destinations using `pgeocode` filtered by known cities.
    :param country_codes: List of ISO country codes (e.g., ['US', 'CA', 'IN']).
    :param num_cities_per_country: Number of cities to fetch per country.
    :return: List of unique popular city names across all countries.
    """
    # Extended predefined list of popular cities per country
    popular_cities = {
        "US": ["New York", "Los Angeles", "San Francisco", "Miami", "Las Vegas",
               "Chicago", "Orlando", "Boston", "Seattle", "Houston"],
        "CA": ["Toronto", "Vancouver", "Montreal", "Calgary", "Ottawa",
               "Quebec City", "Edmonton", "Halifax", "Victoria", "Winnipeg"],
        "IN": ["Mumbai", "Delhi", "Goa", "Jaipur", "Bengaluru",
               "Chennai", "Hyderabad", "Kolkata", "Agra", "Varanasi"],
        "DE": ["Berlin", "Munich", "Frankfurt", "Hamburg", "Cologne",
               "Stuttgart", "Dresden", "Leipzig", "Dusseldorf", "Nuremberg"],
        "AU": ["Sydney", "Melbourne", "Brisbane", "Perth", "Adelaide",
               "Gold Coast", "Cairns", "Hobart", "Canberra", "Darwin"]
    }

    all_destinations = set()
    for country_code in country_codes:
        try:
            # Predefined cities
            predefined_cities = popular_cities.get(country_code, [])
            all_destinations.update(predefined_cities)

            # Fallback: Use pgeocode for additional cities
            if len(predefined_cities) < num_cities_per_country:
                nomi = pgeocode.Nominatim(country_code)
                postal_data = nomi._data[['place_name', 'latitude', 'longitude']].drop_duplicates()
                additional_cities = postal_data['place_name'].dropna().unique()[:num_cities_per_country]
                all_destinations.update(additional_cities)
        except Exception as e:
            print(f"Failed to fetch cities for {country_code}: {e}")

    return list(all_destinations)

def generate_destination_data(cities):
    """
    Generate synthetic destination data for a list of cities.
    :param cities: List of city names.
    :return: List of destination dictionaries.
    """
    destinations = []
    for city in cities:
        destination = {
            "destination": city,
            "price": 1000 + (len(city) * 50),  # Example price logic
            "type": "cultural",
            "activities": "museums, dining, architecture",
            "season": "spring",
            "rating": round(3.5 + (len(city) % 2) * 0.5, 1),
            "reviews_count": 100 + len(city),
            "amenities": ["wifi", "restaurants", "shopping"],
            "language": "English",
            "currency": "USD",
            "timezone": "UTC-5"  # Simplified example
        }
        destinations.append(destination)
    return destinations

# def upload_to_elasticsearch(destinations, index_name="travel_destinations"):
#     """
#     Upload destination data to Elasticsearch.
#     :param destinations: List of destination dictionaries.
#     :param index_name: Elasticsearch index name.
#     """
#     es = Elasticsearch(
#         Config.get_elasticsearch_url(),
#         basic_auth=(Config.ELASTICSEARCH_USER, Config.ELASTICSEARCH_PASSWORD),
#         verify_certs=Config.ELASTICSEARCH_VERIFY_CERTS
#     )

#     # Create the index if it doesn't exist
#     if not es.indices.exists(index=index_name):
#         es.indices.create(index=index_name)
#         print(f"Index '{index_name}' created.")

#     # Upload data
#     for i, destination in enumerate(destinations):
#         try:
#             es.index(index=index_name, id=i, body=destination)
#             print(f"Uploaded: {destination['destination']}")
#         except Exception as e:
#             print(f"Failed to upload {destination['destination']}: {e}")

def upload_to_elasticsearch(file_path, index_name="travel_destinations"):
    """
    Upload destination data from a JSON file to Elasticsearch.
    :param file_path: Path to the JSON file containing destination data.
    :param index_name: Elasticsearch index name.
    """
    # Load the dataset from the JSON file
    with open(file_path, 'r') as file:
        destinations = json.load(file)

    # Connect to Elasticsearch
    es = Elasticsearch(
        Config.get_elasticsearch_url(),
        basic_auth=(Config.ELASTICSEARCH_USER, Config.ELASTICSEARCH_PASSWORD),
        verify_certs=Config.ELASTICSEARCH_VERIFY_CERTS
    )

    # Create the index if it doesn't exist
    if not es.indices.exists(index=index_name):
        es.indices.create(index=index_name)
        print(f"Index '{index_name}' created.")

    # Upload data
    for i, destination in enumerate(destinations):
        try:
            es.index(index=index_name, id=i, body=destination)
            print(f"Uploaded: {destination['destination']}")
        except Exception as e:
            print(f"Failed to upload {destination['destination']}: {e}")

if __name__ == "__main__":
    upload_to_elasticsearch('dataset.json')
    # country_codes = ["US", "CA", "IN", "DE", "AU"]  # Add more country codes for additional destinations
    # cities = fetch_popular_destinations(country_codes)
    # if cities:
    #     print(f"Fetched Cities: {len(cities)} cities")
    #     destinations = generate_destination_data(cities)
    #     print(f"Generated Destinations: {len(destinations)} destinations")
    #     upload_to_elasticsearch(destinations)
    # else:
    #     print("No cities found. Ensure `pgeocode` data is available.")
