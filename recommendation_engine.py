
from elasticsearch import Elasticsearch
from utils.es_utils import wait_for_elasticsearch

class RecommendationEngine:
    def __init__(self):
        self.es = wait_for_elasticsearch()

    def get_personalized_recommendations(self, user_id):
        # Get user profile
        user = self.es.get(index="user_profiles", id=user_id)
        preferences = user['_source']['preferences']

        # Build recommendation query based on user preferences
        should_conditions = []
        
        for activity in preferences['activities']:
            should_conditions.append({"match": {"activities": activity}})
        
        should_conditions.append({
            "range": {
                "price": {
                    "gte": 0,
                    "lte": self._get_budget_range(preferences['budget_range'])
                }
            }
        })

        body = {
            "query": {
                "bool": {
                    "should": should_conditions,
                    "minimum_should_match": 1
                }
            },
            "sort": [
                {"rating": {"order": "desc"}}
            ]
        }

        return self.es.search(index="destinations", body=body)

    def _get_budget_range(self, budget_range):
        ranges = {
            "low": 1500,
            "medium": 2500,
            "high": 5000
        }
        return ranges.get(budget_range, 5000)

    def track_user_interaction(self, user_id, destination, interaction_type):
        interaction = {
            "user_id": user_id,
            "destination": destination,
            "interaction_type": interaction_type,
            "timestamp": "now"
        }
        
        return self.es.index(index="user_interactions", body=interaction)