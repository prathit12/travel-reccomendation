from elasticsearch import Elasticsearch
from elastic_transport import ConnectionError
from config import Config

es = Elasticsearch(
    Config.get_elasticsearch_url(),
    basic_auth=(Config.ELASTICSEARCH_USER, Config.ELASTICSEARCH_PASSWORD),
    verify_certs=Config.ELASTICSEARCH_VERIFY_CERTS
)

def create_indices():
    # Destination index mapping
    destination_mapping = {
        "mappings": {
            "properties": {
                "destination": {"type": "text"},
                "price": {"type": "float"},
                "type": {"type": "keyword"},
                "activities": {"type": "text"},
                "season": {"type": "keyword"}
            }
        }
    }

    # User profile index mapping
    user_profile_mapping = {
        "mappings": {
            "properties": {
                "user_id": {"type": "keyword"},
                "preferences": {"type": "nested"},
                "past_searches": {"type": "text"}
            }
        }
    }

    # Travel trends index mapping
    travel_trends_mapping = {
        "mappings": {
            "properties": {
                "trend": {"type": "text"},
                "popularity": {"type": "integer"},
                "season": {"type": "keyword"}
            }
        }
    }

    try:
        if not es.indices.exists(index="destinations"):
            es.indices.create(index="destinations", body=destination_mapping)
        if not es.indices.exists(index="user_profiles"):
            es.indices.create(index="user_profiles", body=user_profile_mapping)
        if not es.indices.exists(index="travel_trends"):
            es.indices.create(index="travel_trends", body=travel_trends_mapping)
    except ConnectionError as e:
        print(f"Connection error: {e}")

if __name__ == "__main__":
    create_indices()
