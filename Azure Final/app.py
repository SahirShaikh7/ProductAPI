from flask import Flask, request, jsonify
from flask_swagger_ui import get_swaggerui_blueprint
import requests
import google
import json
import cv2
import google.generativeai as genai
import numpy
import base64
from PIL import Image
from io import BytesIO
import psycopg2
from psycopg2 import Error
from pyzbar.pyzbar import decode 

# Set the URL for the Flask API
url = "http://localhost:5000/product-and-ingredients"

# Define the headers
headers = {'Content-Type': 'application/json'}

GOOGLE_API_KEY = "AIzaSyC81hsbRz79lDZ9Y-4gMrzz_cDhBYh-uTU"
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# PostgreSQL database connection parameters
db_params = {
    'dbname': 'DatabaseAPI',
    'user': 'postgres',
    'password': 'Anayah@134',
    'host': 'localhost',
    # 'port': 'your_port'
}

prompt = """Give the name of %s after 'Food:' and specify all 'Raw Material:', Ingredients -> Components (contains materials that make up the raw mmaterials or displays 'None') separately under 'ingredients:' in new lines. Start each list with commas. In the next line, state 'hazards:', followed by the health hazards this food item can cause. Then, in the next line, state 'allergies:', followed by all the allergies this food item can cause. Ensure there are no empty lines or extra white spaces and also give the classification like Veg or Non-Veg.

Example:

Food: <Food Name>
ingredients:
Raw Material: <raw material, name all separately, and include spices, flavors, oils, colors, if raw materials consist of more components that are used to make it, display theses components it inside of brackets after the raw material, else DISPLAY (None) after the raw material> eg: Chocolate (mill, cocoa), Salt (None), Sunflower Oil (None)
hazards: <hazards caused from any of the components that make up the raw material raw material, names only,display theses hazards inside of brackets after the raw material name, else if ingredients do not have any components that cause a health problem DISPLAY (None) after the raw material> eg: Chocolate (Migraines,Swelling), Sugar (Obesity), Oil (asthma,coughing)
allergies: <allergies caused from any of the components that make up the raw material raw material, names only,display theses allergies inside of brackets after the raw material name, else if ingredients do not have any components that cause an allergic reaction DISPLAY (None) after the raw material> eg: Chocolate (milk,soy), Salt (None), Oil (Protien)
classification:<Classification>

NOTE: THERE HAS TO BE EITHER 'NONE' OR COMPONENTS THAT MAKE UP THE RAW MATERIALS IN A BRACKET AFTER ANY RAW MATERIAL NAME AND ALSO SAME IN HAZARDS AND ALLERGIES, DO NOT LEAVE ANYTHING EMPTY
eg <raw material name> (componatents used to make it), <raw material name> (NONE) ,<health hazards> (NONE), <allergies> (NONE)
"""
def display(response):
    lists = response.split('\n')
    biggest = 0
    for i, list in enumerate(lists):
        st = list.find(':')
        lists[i] = [list[0:st], list[st+1:]]
        if lists[i][0] == '':
            lists.pop(i)
            continue
        li = lists[i][1]
        split = True
        pos = 0
        temp = []
        for j, let in enumerate(li):
            if let == '(': split = False
            elif let == ')': split = True
            if split and let == ',' or j == len(li)-1:
                t = li[pos:j+1]
                if t[-1] == ',': temp.append(t[0:-1].strip())
                else: temp.append(t.strip())
                pos = j+1
        if len(temp) > biggest: biggest = len(temp)
        lists[i][1] = temp

    print("INITIATING RESULT SEPERATION")
    dic = dict(lists)
    dic['ingredients'] = []
    if len(dic["Raw Material"]) <= 3: raise(AttributeError)
    for i, raw in enumerate(dic["Raw Material"]):
        if raw.find('(') != -1:
            st = raw.find('(')
            dic['ingredients'].append(raw[0:st])
            dic['Raw Material'][i] = raw[st+1:-1].split(',')
        else:
            dic['ingredients'].append(raw)
            dic['Raw Material'][i] = ['None']
            
    for i, al in enumerate(dic["allergies"]):
        if al.find('(') != -1:
            st = al.find('(')
            dic['allergies'][i] = al[st+1:-1].split(',')
        else:
            dic['allergies'][i] = ['None']
            
    for i, haz in enumerate(dic["hazards"]):
        if haz.find('(') != -1:
            st = haz.find('(')
            dic['hazards'][i] = haz[st+1:-1].split(',')
        else:
            dic['hazards'][i] = ['None']

    dic['components'] = dic['Raw Material']
    del dic['Raw Material']

    print(len(dic['allergies']),len(dic['hazards']), len(dic['ingredients']))
    
    if len(dic['allergies']) == len(dic['hazards']) == len(dic['ingredients']):print('positive response')
    else: raise AttributeError
        
    return dic
    
def text(TEXT):
    try: 
        response = model.generate_content(prompt % TEXT)
        res = response.text.replace('*',"").replace('#','')
        print(res)
        dic = display(res)
        return dic
    except google.api_core.exceptions.InternalServerError: return text(TEXT)
    except AttributeError: return text(TEXT)
    except IndexError: return text(TEXT)
def img(IMAGE):
    try:
        response = model.generate_content([prompt % 'this food item', IMAGE], stream=True)
        response.resolve()
        res = response.text.replace('*',"")
        print(res)
        print('IMAGE DONE PROCESSING')
        dic = display(res)
        return  dic
    except google.api_core.exceptions.InternalServerError: return img(IMAGE)
    except AttributeError: return img(IMAGE)
    except IndexError: return img(IMAGE)
    
def get_food_name_openfoodfacts(barcode):
    api_url = f'https://world.openfoodfacts.org/api/v0/product/{barcode}.json'
    
    response = requests.get(api_url)
    
    if response.status_code == 200:
        data = response.json()
        if data['status'] == 1:
            product = data['product']
            name = product.get('product_name')
            company = product.get('brand_owner')
            print('From OpenFoodFacts:',name)
            print('From Company:',company)
            if company != None:
                t = name,company
            else: t = name
            data = text(str(t))
            return data
        else: return "Product Not Found"
    
def BarcodeReader(IMAGE): 
    img = numpy.array(IMAGE)
    detectedBarcodes = decode(IMAGE) 
       
    if not detectedBarcodes: 
        print("Barcode Not Detected") 
    else:
        for barcode in detectedBarcodes:   
            (x, y, w, h) = barcode.rect 
            
            cv2.rectangle(img, (x-10, y-10), 
                          (x + w+10, y + h+10),  
                          (255, 0, 0), 2) 
              
            if barcode.data!="": 
                print('Barcode Reader:',barcode.data)
                return str(barcode.data)[2:-1]

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
        "action": "insert_by_barcode",
        "barcode_number": input_data['barcode_number'],
        "product_name": input_data['product_name'],
        "classification": input_data['classification'][0],  # Assume it's Vegetarian
        "ingredients": input_data["ingredients"],
        "components": ["" if comp == ["None"] else ", ".join(comp) for comp in input_data["components"]],
        "hazards": [hazard[0] if hazard else "None" for hazard in input_data["hazards"]],
        "allergies": [allergy[0] if allergy else "None" for allergy in input_data["allergies"]]
    }
    return output_data

def insert_product_and_ingredients_by_barcode():
    try:
        print('\nInserting product in database:')
        connection = psycopg2.connect(**db_params)
        cursor = connection.cursor()

        barcode_number = request.json.get('barcode_number')
        product_name = request.json.get('product_name')
        classification = request.json.get('classification')
        ingredients = request.json.get('ingredients', [])
        components = request.json.get('components', [])
        hazards = request.json.get('hazards', [])
        allergies = request.json.get('allergies', [])

        sql_command = """
            CALL insert_product_and_ingredients(
                %s::varchar, %s::varchar, %s::varchar, %s::varchar[], %s::varchar[], %s::varchar[], %s::varchar[]
            )
        """

        cursor.execute(sql_command, (
            barcode_number,
            product_name,
            classification,
            ingredients,
            components,
            hazards,
            allergies
        ))

        connection.commit()

        response = {
            'message': 'Stored procedure successfully called.'
        }

    except (Exception, Error) as error:
        response = {
            'error': f'Error while calling stored procedure: {error}'
        }
        return jsonify(response), 201

    finally:
        if 'connection' in locals():
            cursor.close()
            connection.close()
            print("PostgreSQL connection is closed.")

    return jsonify(response)

def retrieve_products_and_ingredients_by_barcode():
    try:
        barcode_number = request.json.get('barcode_number')
        if not barcode_number:
            return jsonify({"error": "Barcode number is required"}), 400

        conn = psycopg2.connect(**db_params)
        cur = conn.cursor()

        cur.execute("SELECT * FROM retrieve_products_and_ingredients(%s)", (barcode_number,))

        results = cur.fetchall()

        if results:
            product_name = results[0][0]
            classification = results[0][1]
            table_data = []
            for row in results:
                ingredient_id = row[2]
                ingredient_name = row[3]
                component = row[4] if row[4] else "Not specified"
                hazard = row[5] if row[5] else "None"
                allergy = row[6] if row[6] else "None"

                table_data.append({
                    "ingredient_id": ingredient_id,
                    "ingredient_name": ingredient_name,
                    "component": component,
                    "hazard": hazard,
                    "allergy": allergy
                })

            response = {
                "product_name": product_name,
                "classification": classification,
                "ingredients": table_data
            }
        else:
            response = {"message": "No data found for the given barcode number."}
            return jsonify(response), 201

        cur.close()
        conn.close()

        return jsonify(response)
    except Exception as e:
        return jsonify({"error": f"Error retrieving data: {e}"}), 500
    
# Function to insert product and ingredients
def insert_product_and_ingredients(payload):
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    if response.status_code == 200:
        print("Insert Response:", response.json())
    else:
        print("Insert Failed:", response.status_code, response.text)

# Function to retrieve product and ingredients
def retrieve_product_and_ingredients(payload):
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    if response.status_code == 200:
        print("Retrieve Response:", response.json())
    else:
        print("Retrieve Failed:", response.status_code, response.text)
    
#DATABASE ROUTE
@app.route('/product-and-ingredients', methods=['POST'])
def handle_product_and_ingredients():
    action = request.json.get('action')

    if action == 'insert_by_barcode':
        return insert_product_and_ingredients_by_barcode()
    elif action == 'retrieve_by_barcode':
        return retrieve_products_and_ingredients_by_barcode()
    
    else:
        return jsonify({"error": "Invalid action specified"}), 400

#FOODAPI ROUTE
@app.route("/food-name",methods=["POST"])
def using_name():
    if request.method == "POST":
        data = request.get_json()
        data = text(data['foodItem'])
        return jsonify(data), 200
    
@app.route("/barcode",methods=["POST"])
def using_barcode():
    if request.method == "POST":
        data = request.get_json()
        barcode = data['barcode']
        print('Recieved Barcode: ',barcode)
        output_data = 'Error Occured'
        response = requests.post('http://127.0.0.1:5000/product-and-ingredients',json={'action':'retrieve_by_barcode', 'barcode_number':barcode})
        if response.status_code == 200:
            output_data = response.json()
        else:
            data = get_food_name_openfoodfacts(barcode)
            data['barcode_number'] = barcode
            data['action'] = "insert_by_barcode"
            data['product_name'] = data['Food']
            
            output_data = convert_format(data)
            print('INSERTING')
            output_data = insert_product_and_ingredients(output_data)
            

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
        response = requests.post('http://127.0.0.1:5000/product-and-ingredients',json={'action':'retrieve_by_barcode', 'barcode_number':barcode})
        if response.status_code == 200:
            output_data = response.json()
        else:
            data = get_food_name_openfoodfacts(barcode)
            data['barcode_number'] = barcode
            data['action'] = "insert_by_barcode"
            data['product_name'] = data['Food']
            
            output_data = convert_format(data)
            
            output_data = insert_product_and_ingredients(output_data)
            print(output_data)
        
        j=(json.dumps(output_data, indent=4))
        return (j), 200
    
@app.route("/food-image",methods=["POST"])
def using_foodImage():
    if request.method == "POST":
        data = request.get_json()
        im = Image.open(BytesIO(base64.b64decode(data['encodedImage'])))
        dic = img(im)
        return jsonify(dic), 200

if __name__ == "__main__":
    app.run(debug=True)
    
