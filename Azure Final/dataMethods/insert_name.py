from flask import jsonify, request
from dataMethods.get_db_params import *
import psycopg2
def retrieve_products_and_ingredients_by_product_name():
    try:
        print('\nRetrieving...')
        product_name = request.json.get('product_name')
        if not product_name:
            return jsonify({"error": "Product name is required"}), 400

        conn = psycopg2.connect(**get_db_params())
        cur = conn.cursor()

        cur.execute("SELECT * FROM retrieve_products_and_ingredients2(%s)", (product_name,))

        results = cur.fetchall()

        if results:
            barcode_number = results[0][0]
            classification = results[0][2]
            table_data = []
            for row in results:
                ingredient_id = row[3]
                ingredient_name = row[4]
                component = row[5] if row[5] else "Not specified"
                hazard = row[6] if row[6] else "None"
                allergy = row[7] if row[7] else "None"

                table_data.append({
                    "ingredient_id": ingredient_id,
                    "ingredient_name": ingredient_name,
                    "component": component,
                    "hazard": hazard,
                    "allergy": allergy
                })

            response = {
                "barcode_number": barcode_number,
                "product_name": product_name,
                "classification": classification,
                "ingredients": table_data
            }
        else:
            response = {"message": "No data found for the given product name."}
            return jsonify(response), 201

        cur.close()
        conn.close()

        return jsonify(response), 200
    except Exception as e:
        return jsonify({"error": f"Error retrieving data: {e}"}), 500
    
