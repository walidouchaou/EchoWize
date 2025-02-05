from flask import Flask
from api.routes.restaurant_routes import restaurant_routes

app = Flask(__name__)
app.register_blueprint(restaurant_routes)

if __name__ == '__main__':
    app.run(debug=True)
    
