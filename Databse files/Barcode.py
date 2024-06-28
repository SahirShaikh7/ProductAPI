import psycopg2
from tabulate import tabulate

def retrieve_products_and_ingredients(barcode_number):
    # Connection parameters, adjust as needed
    conn_params = {
        'dbname': 'FoodDemo',
        'user': 'postgres',
        'password': 'Anayah@134',
        'host': 'localhost',
        # 'port': 'your_port'
    }
    
    # Establish the connection
    try:
        conn = psycopg2.connect(**conn_params)
        print("Database connection established.")
    except Exception as e:
        print(f"Error connecting to the database: {e}")
        return

    cur = conn.cursor()
    
    try:
        # Execute the function
        print("Executing function...")
        cur.execute("SELECT * FROM retrieve_products_and_ingredients(%s)", (barcode_number,))
        
        # Fetch all results
        results = cur.fetchall()
        print(f"Fetched {len(results)} rows.")
        
        if results:
            # Print the product name once
            product_name = results[0][0]
            print(f"Product Name: {product_name}")
            print()
            
            # Prepare the table data
            table_data = []
            for row in results:
                _, ingredient_name, component, hazard, allergy = row[1], row[2], row[3], row[4], row[5]
                component = component if component else "Not specified"
                hazard = hazard if hazard else "None"
                allergy = allergy if allergy else "None"
                
                table_data.append([ingredient_name, component, hazard, allergy])
            
            # Define the table headers
            headers = ["Ingredient Name", "Component", "Hazard", "Allergy"]
            
            # Print the table
            print(tabulate(table_data, headers, tablefmt="grid"))
        else:
            print("No data found for the given barcode number.")
    except Exception as e:
        print(f"Error executing query: {e}")
    finally:
        cur.close()
        conn.close()
        print("Database connection closed.")

# Example usage
barcode_number = '1234567890'
retrieve_products_and_ingredients(barcode_number)
