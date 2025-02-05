from flask import Blueprint, jsonify
from api.services.serapi_service import SerapiService
from api.services.data_transformer import DataTransformer
from api.integration_open_ia import integrationOpenIA

restaurant_routes = Blueprint('restaurant_routes', __name__)

@restaurant_routes.route('/restaurant/<restaurant_name>/reviews', methods=['GET'])
def get_restaurant_reviews(restaurant_name: str):
    serapi_service = SerapiService()
    data_transformer = DataTransformer()
    data_id = serapi_service.get_data_id(restaurant_name)
    reviews = serapi_service.get_reviews(data_id)
    serapi_service.upload_reviews_to_csv(reviews, restaurant_name)
    data_transformer.transform_reviews()
    integration = integrationOpenIA()
    integration.process_negative_reviews()
    
    return jsonify({
        'message': f"Reviews uploaded to MinIO for restaurant {restaurant_name}",
        'status': 'success'
    })

