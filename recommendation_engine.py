from elasticsearch import Elasticsearch
from utils.es_utils import wait_for_elasticsearch, index_exists
import urllib3

# Suppress InsecureRequestWarning
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class RecommendationEngine:
    def __init__(self):
        self.es = wait_for_elasticsearch()
        self.required_indices = ["user_profiles", "travel_trends", "destinations"]
        self.check_indices()

    def check_indices(self):
        for index in self.required_indices:
            if not index_exists(self.es, index):
                raise Exception(f"Required index '{index}' does not exist in Elasticsearch.")

    def get_personalized_recommendations(self, user_id):
        try:
            # Fetch user profile by querying `user_id` field
            user_response = self.es.search(index="user_profiles", body={
                "query": {
                    "term": {
                        "user_id": user_id  # Ensure `.keyword` is used for exact match
                    }
                }
            })
            
            #Check if any documents were found
            if user_response['hits']['total']['value'] == 0:
                print(f"User profile not found for user {user_id}")
                return {"hits": {"hits": []}}
            
            user = user_response['hits']['hits'][0]
            print(f"User profile found: {user}")
            preferences = user['_source']['preferences']
        except Exception as e:
            print(f"Error fetching user profile for user {user_id}: {e}")
            return {"hits": {"hits": []}}

        # Get travel trends
        trends_response = self.es.search(index="travel_trends", body={
            "query": {
                "match_all": {}
            },
            "size": 10000  # Fetch all trends
        })
        trends = trends_response['hits']['hits']

        # Build recommendation query based on user preferences and trends
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

        for season in preferences['preferred_seasons']:
            should_conditions.append({"match": {"season": season}})

        for trend in trends:
            should_conditions.append({"match": {"activities": trend['_source']['trend']}})
            should_conditions.append({"match": {"season": trend['_source']['season']}})

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