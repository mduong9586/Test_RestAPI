import os
import psycopg2
from dotenv import load_dotenv
from flask import Flask, request, jsonify

load_dotenv()
#create flask app
app = Flask(__name__)

#get url for database and connect using psycopg2 
url = os.getenv("DATABASE_URL")
connection = psycopg2.connect(url)

#create a new table using SQL command
CREATE_INVENTORY_TABLE = "CREATE TABLE IF NOT EXISTS ims (id SERIAL PRIMARY KEY, product TEXT, quantity INT);"

with connection:
    with connection.cursor() as cursor:
        cursor.execute(CREATE_INVENTORY_TABLE)

#insert data into table
INSERT_PRODUCT_RETURN_ID = "INSERT INTO ims (product, quantity) VALUES (%s, %s) RETURNING id;"

@app.route("/api/product", methods=["POST"])
def create_product():
    data = request.get_json()
    product = data[0]["product"]
    quantity = data[1]["quantity"]
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(INSERT_PRODUCT_RETURN_ID, (product, quantity,))
            product_id = cursor.fetchone()[0]
    
    return {"id": product_id, "product": product, "quantity": quantity, "message": f"{quantity} {product} added"}, 201      

#get all data from table
SELECT_ALL_PRODUCTS = "SELECT * FROM ims"

@app.route("/api/product", methods=["GET"])
def get_all_products():
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(SELECT_ALL_PRODUCTS)
            products = cursor.fetchall()
            if products:
                result  = []
                for product in products:
                    result.append({"id": product[0], "product": product[1], "quantity": product[2]})
                return jsonify(result)
            else:
                return jsonify({"error": f"No products found."}), 404

#get product by their ID
SELECT_PRODUCTS_BY_ID = "SELECT * FROM ims WHERE id = %s;"

@app.route("/api/product/<int:product_id>", methods=["GET"])
def get_product(product_id):
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(SELECT_PRODUCTS_BY_ID, (product_id,))
            product = cursor.fetchone()
            if product:
                return jsonify({"id": product[0], "product": product[1], "quantity": product[2]})
            else:
                return jsonify({"error": f"Product with ID {product_id} not found."}), 404

#update product by their ID
UPDATE_PRODUCTS_BY_ID = "UPDATE ims SET product = %s, quantity = %s WHERE id = %s;"
            
@app.route("/api/product/<int:product_id>", methods=["PUT"])
def update_product(product_id):
    data = request.get_json()
    product = data["product"]
    quantity = data["quantity"]
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(UPDATE_PRODUCTS_BY_ID, (product, quantity, product_id))
            if cursor.rowcount == 0:
                return jsonify({"error": f"Product with ID {product_id} not found."}), 404
    return jsonify({"id": product_id, "product": product, "quantity": quantity, "message": f"Product with ID {product_id} updated."})

#delete product by their id
DELETE_PRODUCTS_BY_ID = "DELETE FROM ims WHERE id = %s;"

@app.route("/api/product/<int:product_id>", methods=["DELETE"])
def delete_product(product_id):
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(DELETE_PRODUCTS_BY_ID, (product_id,))
            if cursor.rowcount == 0:
                return jsonify({"error": f"Product with ID {product_id} not found."}), 404
    return jsonify({"message": f"Product with ID {product_id} deleted."})