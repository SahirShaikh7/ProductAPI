from flask import Flask, request, jsonify
from flask_swagger_ui import get_swaggerui_blueprint
import requests
import json
import base64
from PIL import Image
from io import BytesIO

from proMethods import get_food_name_openfoodfacts, BarcodeReader, text, img
from dataMethods import *

url = "http://localhost:5000/product-and-ingredients"
app = Flask(__name__)

#SWAGGER
SWAGGER_URL = '' 
#API_URL = 'http://petstore.swagger.io/v2/swagger.json'  # Our API url (can of course be a local resource)
API_URL = '/static/swagger.json'
swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={  # Swagger UI config overrides
        'app_name': "Test application"
    },
)

app.register_blueprint(swaggerui_blueprint)


#DATABASE
def convert_format(input_data):
    output_data = {
        "action": input_data['action'],
        "barcode_number": input_data['barcode_number'],
        "product_name": input_data['product_name'],
        "classification": input_data['classification'][0],  # Assume it's Vegetarian
        "ingredients": input_data["ingredients"],
        "components": ["" if comp == ["None"] else ", ".join(comp) for comp in input_data["components"]],
        "hazards": [hazard[0] if hazard else "None" for hazard in input_data["hazards"]],
        "allergies": [allergy[0] if allergy else "None" for allergy in input_data["allergies"]]
    }
    return output_data
#DATABASE ROUTE
@app.route('/product-and-ingredients', methods=['POST'])
def handle_product_and_ingredients():
    action = request.json.get('action')
    if action == 'insert_by_barcode':
        return insert_product_and_ingredients_by_barcode()
    elif action == 'retrieve_by_barcode':
        return retrieve_products_and_ingredients_by_barcode()
    elif action == 'insert_by_product':
        return insert_product_and_ingredients_by_product_name()
    elif action == 'retrieve_by_product':
        return retrieve_products_and_ingredients_by_product_name()
    
    else:
        return jsonify({"error": "Invalid action specified"}), 400

#FOODAPI ROUTE
@app.route("/food-name",methods=["POST"])
def using_name():
    if request.method == "POST":
        data = request.get_json()
        name = data['foodItem'].lower()
        print('Recieved Name:',name)
        output_data = 'Error Occured'
        
        response = requests.post(url,json={'action':'retrieve_by_product', 'product_name':name})
        if response.status_code == 200:
            output_data = response.json()
        else:
            data = text(name)
            if data == 'Product Not Found': return jsonify('Product Not Found'), 201
            data['barcode_number'] = ''
            data['action'] = "insert_by_product"
            data['product_name'] = name.lower()
            
            output_data = convert_format(data)
            print('INSERTING')
            requests.post(url,json=output_data).json()
            output_data = requests.post(url,json={'action':'retrieve_by_product', 'product_name':name}).json()

        j=(json.dumps(output_data, indent=4))
        return (j), 200
    
@app.route("/barcode",methods=["POST"])
def using_barcode():
    if request.method == "POST":
        data = request.get_json()
        barcode = data['barcode']
        print('Recieved Barcode: ',barcode)
        output_data = 'Error Occured'
        
        response = requests.post(url,json={'action':'retrieve_by_barcode', 'barcode_number':barcode})
        if response.status_code == 200:
            output_data = response.json()
        else:
            data = get_food_name_openfoodfacts(barcode)
            if data == 'Product Not Found': return jsonify('Product Not Found'), 201
            data['barcode_number'] = barcode
            data['action'] = "insert_by_barcode"
            data['product_name'] = data['Food']
            
            output_data = convert_format(data)
            print('INSERTING')
            requests.post(url,json=output_data).json()
            output_data = requests.post(url,json={'action':'retrieve_by_barcode', 'barcode_number':barcode}).json()

        output_data['product_name'] = output_data['product_name']
        j=(json.dumps(output_data, indent=4))
        return (j), 200
    
@app.route("/barcode-image",methods=["POST"])
def using_barcodeImage():
    if request.method == "POST":
        data = request.get_json()
        im = Image.open(BytesIO(base64.b64decode(data['encodedImage'])))
        barcode = BarcodeReader(im)
        print('Recieved Barcode: ',barcode)
        output_data = 'Error Occured'
        response = requests.post(url,json={'action':'retrieve_by_barcode', 'barcode_number':barcode})
        if response.status_code == 200:
            output_data = response.json()
        else:
            data = get_food_name_openfoodfacts(barcode)
            if data == 'Product Not Found': return jsonify({'message':data}), 201
            data['barcode_number'] = barcode
            data['action'] = "insert_by_barcode"
            data['product_name'] = data['Food']
            
            output_data = convert_format(data)
            requests.post(url,json=output_data).json()
            output_data = requests.post(url,json={'action':'retrieve_by_barcode', 'barcode_number':barcode}).json()
        
        
        j=(json.dumps(output_data, indent=4))
        return (j), 200
    
@app.route("/food-image",methods=["POST"])
def using_foodImage():
    if request.method == "POST":
        data = request.get_json()
        im = Image.open(BytesIO(base64.b64decode(data['encodedImage'])))
        name = img(im).lower()
        
        response = requests.post(url,json={'action':'retrieve_by_product', 'product_name':name})
        if response.status_code == 200:
            output_data = response.json()
        else:
            data = text(name)
            if data == 'Product Not Found': return jsonify('Product Not Found'), 201
            data['barcode_number'] = 'None'
            data['action'] = "insert_by_product"
            data['product_name'] = name.lower()
            
            output_data = convert_format(data)
            print('INSERTING')
            print(requests.post(url,json=output_data).json())
            output_data = requests.post(url,json={'action':'retrieve_by_product', 'product_name':name}).json()

        j=(json.dumps(output_data, indent=4))
        return (j), 200

if __name__ == "__main__":
    app.run(debug=True)
    
