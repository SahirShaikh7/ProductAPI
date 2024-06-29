from proMethods import geminiMethods
import requests

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
            data = geminiMethods.text(str(t))
            return data
        else: return "Product Not Found"