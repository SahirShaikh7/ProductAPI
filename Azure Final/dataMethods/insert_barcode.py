from flask import jsonify, request
from dataMethods.get_db_params import *
import psycopg2
def retrieve_products_and_ingredients_by_barcode():
    try:
        barcode_number = request.json.get('barcode_number')
        if not barcode_number:
            return jsonify({"error": "Barcode number is required"}), 400

        conn = psycopg2.connect(**get_db_params())
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