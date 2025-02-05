import sys
import os

# Ajouter le répertoire parent au PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from EchoWize.api.main import app


def test_get_restaurant_reviews(restaurant_name: str):
    response = app.test_client().get(f'http://localhost:5000/restaurant/{restaurant_name}/reviews')
    response_data = response.get_json()
    print(response_data)
if __name__ == '__main__':
    test_get_restaurant_reviews("Mangez moi Le Fred's")
