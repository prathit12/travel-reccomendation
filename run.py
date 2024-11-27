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
    query = request.args.get('q', '')
    if not query:
        return jsonify([])

    response = app.elasticsearch.search(
        index="destinations",
        body={
            "query": {
                "bool": {
                    "should": [
                        {
                            "multi_match": {
                                "query": query,
                                "fields": [
                                    "destination^3",
                                    "type^2",
                                    "activities^2",
                                    "season"
                                ],
                                "fuzziness": "AUTO",
                                "operator": "or"
                            }
                        },
                        {
                            "match_phrase_prefix": {
                                "destination": {
                                    "query": query,
                                    "boost": 4
                                }
                            }
                        }
                    ],
                    "minimum_should_match": 1
                }
            },
            "size": 10,
            "_source": ["destination", "type", "activities", "price", "season"],
            "sort": [
                "_score"
            ]
        }
    )
    
    # Format the response to include more details
    results = []
    for hit in response['hits']['hits']:
        results.append({
            'score': hit['_score'],
            **hit['_source']
        })
    
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