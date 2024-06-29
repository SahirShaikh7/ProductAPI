from flask import jsonify, request
from dataMethods.get_db_params import *
import psycopg2
from psycopg2 import Error
def insert_product_and_ingredients_by_barcode():
    try:
        print('\nInserting product in database:')
        connection = psycopg2.connect(**get_db_params())
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