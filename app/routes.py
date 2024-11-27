# -*- coding: utf-8 -*-

from flask import current_app as app, request, jsonify
from recommendation_engine import RecommendationEngine

recommendation_engine = RecommendationEngine()

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('q')
    response = app.elasticsearch.search(
        index="destinations",
        body={
            "query": {
                "multi_match": {
                    "query": query,
                    "fields": ["destination", "activities"]
                }
            }
        }
    )
    return jsonify(response['hits']['hits'])

@app.route('/recommendations', methods=['GET'])
def recommendations():
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({"error": "User ID is required"}), 400

    response = recommendation_engine.get_personalized_recommendations(user_id)
    results = [hit['_source'] for hit in response['hits']['hits']]
    return jsonify(results)