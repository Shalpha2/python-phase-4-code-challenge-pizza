#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response
from flask_restful import Api, Resource
import os
from flask_cors import CORS

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)
CORS(app)

api = Api(app)


@app.route("/")
def index():
    return "<h1>Code challenge</h1>"

class Restaurants(Resource):
    def get(self):
        restaurants = [restaurant.to_dict(only=("id", "name", "address")) for restaurant in db.session.query(Restaurant).all()] 
        return make_response(restaurants, 200)
api.add_resource(Restaurants, "/restaurants")


class RestaurantById(Resource):
    def get(self, restaurant_id):
        restaurant = db.session.get(Restaurant,restaurant_id)
        if not restaurant:
            return make_response({"error": "Restaurant not found"}, 404)
        return make_response(restaurant.to_dict(), 200)
    

    def delete(self, restaurant_id):
        restaurant = db.session.get(Restaurant , restaurant_id)
        if not restaurant:
            return make_response({"error": "Restaurant not found"}, 404)
        db.session.delete(restaurant)
        db.session.commit()
        return make_response({"message": "Restaurant deleted successfully"}, 204)
    
api.add_resource(RestaurantById, "/restaurants/<int:restaurant_id>")



class Pizzas(Resource):
    def get(self):
        pizza= [pizza.to_dict(only=("id", "name", "ingredients")) for pizza in db.session.query(Pizza).all()]
        return make_response(pizza, 200)
api.add_resource(Pizzas, "/pizzas")


class RestaurantPizzas(Resource):
    def post(self):
        data = request.get_json()

        try:
            new_restaurant_pizza = RestaurantPizza(
                price=data.get("price"),
                pizza_id=data.get("pizza_id"),
                restaurant_id=data.get("restaurant_id")
            )

            db.session.add(new_restaurant_pizza)
            db.session.commit()

            
            response_data = {
                "id": new_restaurant_pizza.id,
                "price": new_restaurant_pizza.price,
                "pizza_id": new_restaurant_pizza.pizza_id,
                "restaurant_id": new_restaurant_pizza.restaurant_id,
                "pizza": new_restaurant_pizza.pizza.to_dict(),
                "restaurant": new_restaurant_pizza.restaurant.to_dict()
            }

            return make_response(response_data, 201)

        except Exception:
            return make_response({"errors": ["validation errors"]}, 400)

api.add_resource(RestaurantPizzas, "/restaurant_pizzas")



if __name__ == "__main__":
    app.run(port=5555, debug=True)



    
