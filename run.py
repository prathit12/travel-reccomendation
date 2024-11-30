from flask import Flask, send_from_directory, request, jsonify
from flask_cors import CORS
from config import Config
import os
from utils.es_utils import wait_for_elasticsearch
from recommendation_engine import RecommendationEngine

app = Flask(__name__, static_folder='frontend/build', static_url_path='')
CORS(app)

try:
    # Configure Elasticsearch with connection verification
    app.elasticsearch = wait_for_elasticsearch()
except ConnectionError as e:
    print(f"Failed to connect to Elasticsearch: {e}")
    exit(1)

recommendation_engine = RecommendationEngine()


@app.route('/search', methods=['GET'])
def search():
    # Extract query and filters from the request
    query = request.args.get('q', '').strip()
    filters = {
        'type': request.args.get('type', None),
        'season': request.args.get('season', None),
        'maxPrice': request.args.get('maxPrice', None),
        'rating': request.args.get('rating', None),
        'timezone': request.args.get('timezone', None),  # Add timezone filter
    }
    sort = request.args.get('sort', 'price')

    if not query:
        return jsonify([])  # Return an empty list if query is missing

    # Build Elasticsearch filters dynamically
    must_filters = []

    if filters['type']:
        must_filters.append({"match": {"type": filters['type']}})
    if filters['season']:
        must_filters.append({"match": {"season": filters['season']}})
    if filters['maxPrice']:
        must_filters.append({"range": {"price": {"lte": int(filters['maxPrice'])}}})
    if filters['rating']:
        must_filters.append({"term": {"rating": int(filters['rating'])}})  # Exact match for numeric rating
    if filters['timezone']:
        must_filters.append({"match": {"timezone": filters['timezone']}})  # Add timezone filter

    # Elasticsearch query
    response = app.elasticsearch.search(
        index="destinations",
        body={
            "query": {
                "bool": {
                    "must": must_filters,
                    "should": [
                        {
                            "multi_match": {
                                "query": query,
                                "fields": [
                                    "destination^3",
                                    "type^2",
                                    "activities",
                                    "season"
                                ],
                                "fuzziness": "AUTO",
                                "operator": "or"
                            }
                        }
                    ],
                    "minimum_should_match": 1
                }
            },
            "sort": [
                {sort: {"order": "asc"}},  # Sort dynamically based on user input
                "_score"
            ]
        }
    )

    # Format the response
    results = [
        {
            'score': hit['_score'],
            **hit['_source']
        }
        for hit in response['hits']['hits']
    ]

    return jsonify(results)





@app.route('/recommendations', methods=['GET'])
def recommendations():
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({"error": "User ID is required"}), 400

    response = recommendation_engine.get_personalized_recommendations(user_id)
    results = [hit['_source'] for hit in response['hits']['hits']]
    return jsonify(results)

@app.route('/save-recommendation', methods=['POST'])
def save_recommendation():
    data = request.get_json()
    user_id = data.get('user_id')
    recommendation = data.get('recommendation')
    
    if not user_id or not recommendation:
        return jsonify({"error": "User ID and recommendation are required"}), 400
    
    # Save the recommendation to the user's profile
    app.elasticsearch.index(index="user_recommendations", body={
        "user_id": user_id,
        "recommendation": recommendation,
        "timestamp": "now"
    })
    
    return jsonify({"message": "Recommendation saved successfully"})

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path and path != "" and os.path.exists(app.static_folder + '/' + path):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')

if __name__ == "__main__":
    app.run(debug=Config.DEBUG)