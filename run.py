from flask import Flask, send_from_directory, request, jsonify
from flask_cors import CORS
from config import Config
import os
from utils.es_utils import wait_for_elasticsearch
from recommendation_engine import RecommendationEngine
from elasticsearch import Elasticsearch, NotFoundError

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
    user_id = request.args.get("user_id")
    if not user_id:
        return jsonify({"error": "User ID is required"}), 400

    try:
        response = recommendation_engine.get_personalized_recommendations(user_id)
        results = [hit['_source'] for hit in response['hits']['hits']]
        return jsonify(results)
    except Exception as e:
        print(f"Error fetching recommendations for user {user_id}: {e}")
        return jsonify({"error": "Failed to fetch recommendations"}), 500

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





@app.route('/destination/<destination_id>', methods=['GET'])
def get_destination_details(destination_id):
    try:
        # Validate destination_id format
        if not destination_id.startswith("destination_"):
            return jsonify({"error": "Invalid destination ID format"}), 400

        # Fetch destination details by matching 'id' field
        result = app.elasticsearch.search(
            index="destinations",
            body={
                "query": {
                    "term": {
                        "id.keyword": destination_id  # Match the 'id' field exactly
                    }
                }
            }
        )

        # Check if the destination was found
        if result['hits']['total']['value'] == 0:
            return jsonify({"error": "Destination not found"}), 404

        # Get the destination details
        destination = result['hits']['hits'][0]['_source']

        # Fetch associated reviews
        reviews_result = app.elasticsearch.search(
            index="destination_reviews",
            body={
                "query": {
                    "term": {
                        "destination_id.keyword": destination_id  # Match exact destination_id
                    }
                }
            }
        )

        # Extract reviews
        reviews = [hit['_source'] for hit in reviews_result['hits']['hits']]

        return jsonify({
            "destination": destination,
            "reviews": reviews
        })

    except Exception as e:
        # Log error for debugging (optional)
        app.logger.error(f"Error fetching destination details for ID {destination_id}: {e}")
        return jsonify({"error": "Internal server error"}), 500


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path and path != "" and os.path.exists(app.static_folder + '/' + path):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')

if __name__ == "__main__":
    app.run(debug=Config.DEBUG)