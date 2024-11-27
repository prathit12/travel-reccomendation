
from elasticsearch import Elasticsearch
from utils.es_utils import wait_for_elasticsearch

class SearchService:
    def __init__(self):
        self.es = wait_for_elasticsearch()

    def search_destinations(self, query_params):
        must_conditions = []
        
        if 'type' in query_params:
            must_conditions.append({"match": {"type": query_params['type']}})
            
        if 'price_range' in query_params:
            must_conditions.append({
                "range": {
                    "price": {
                        "gte": query_params['price_range'][0],
                        "lte": query_params['price_range'][1]
                    }
                }
            })
            
        if 'rating' in query_params:
            must_conditions.append({
                "range": {
                    "rating": {"gte": query_params['rating']}
                }
            })

        body = {
            "query": {
                "bool": {
                    "must": must_conditions
                }
            },
            "sort": [
                {"rating": {"order": "desc"}},
                {"reviews_count": {"order": "desc"}}
            ]
        }

        return self.es.search(index="destinations", body=body)

    def get_destination_reviews(self, destination_name, page=1, size=10):
        body = {
            "query": {
                "match": {"destination": destination_name}
            },
            "sort": [
                {"helpful_votes": {"order": "desc"}},
                {"date": {"order": "desc"}}
            ],
            "from": (page - 1) * size,
            "size": size
        }
        
        return self.es.search(index="destination_reviews", body=body)