# -*- coding: utf-8 -*-

from flask import current_app as app, request, jsonify
from recommendation_engine import RecommendationEngine

recommendation_engine = RecommendationEngine()

# @app.route('/search', methods=['GET'])
# def search():
#     query = request.args.get('q')
#     response = app.elasticsearch.search(
#         index="destinations",
#         body={
#             "query": {
#                 "multi_match": {
#                     "query": query,
#                     "fields": ["destination", "activities"]
#                 }
#             }
#         }
#     )
#     return jsonify(response['hits']['hits'])



@app.route('/search', methods=['GET'])
def search():
    # Extract query and filters from the request
    query = request.args.get('q', '').strip()
    filters = {
        'type': request.args.get('type', None),
        'season': request.args.get('season', None),
        'maxPrice': request.args.get('maxPrice', None),
        'activities': request.args.get('activities', None),
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
    if filters['activities']:
        must_filters.append({"match": {"activities": filters['activities']}})

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