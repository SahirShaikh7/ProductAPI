from PIL import Image, ImageTk
import tkinter as tk
from tkinter.filedialog import askopenfilename
import cv2 
from pyzbar.pyzbar import decode 
import requests

root = tk.Tk()
root.geometry("525x440")
root.title("Text Extractor")
slide = 0
buffer = {'OpenFoodFacts':0,'Nutritionix':0,'Edamam':0}

tk.Canvas(root,width=510,height=210,bg="#2e2c27").place(x=5,y=210)
frame = tk.Frame(root, width=394, height=189)
canvas = tk.Canvas(frame, width=394, height=189, bg='white')

displayText = tk.StringVar()
def finddirectory():
    global image_path
    image_path = askopenfilename()
    
    img = Image.open(image_path)
    img = img.resize((170, 135))
    pic = ImageTk.PhotoImage(img)
    
    imgLabel = tk.Label(root, image=pic).place(x=325,y=20)
    imgLabel.image = pic
    
def displayIngredients(APIName,ingredients,allergyPresent=False,allergens=[]):
    canvas.delete("all")
    label = tk.Label(canvas, text=f"{APIName}", bg='white',font=("Arial",12,"bold"))
    window = canvas.create_window(50, (1)*25, window=label, anchor=tk.NW)
    canvas.itemconfigure(window, anchor=tk.W)
    count = 0
    for i,ingredient in enumerate(ingredients):
        count += 1
        print(f"- {ingredient}")
        label = tk.Label(canvas, text=str(i+1)+"."+str(ingredient), bg='white',font=("Arial",11))
        window = canvas.create_window(60, 8+(i+2)*21, window=label, anchor=tk.NW)
        canvas.itemconfigure(window, anchor=tk.W)

        
    if allergyPresent:
        label = tk.Label(canvas, text="Allergies", bg='white',font=("Arial",11,"bold"))
        window = canvas.create_window(50, 12+(count+2)*21, window=label, anchor=tk.NW)
        canvas.itemconfigure(window, anchor=tk.W)
        for i,allergen in enumerate(allergens):
            print(f"- {allergen}")
            label = tk.Label(canvas, text=str(i+1)+"."+str(allergen.replace("en:","")), bg='white',font=("Arial",11))
            window = canvas.create_window(60, 12+(count+i+3)*21, window=label, anchor=tk.NW)
            canvas.itemconfigure(window, anchor=tk.W)
    
    update_scrollregion(None)
       
def simplify(string,type = ""):
    while('(' in string and ')' in string):
                start = string.rfind('(')
                end = string.rfind(')')
                string = string[0:start]+string[end:-1]
                
    ingredients_list = string.split(',')
    
    if type == "edamam": ingredients_list = string.split(';')
                
    for i,v in enumerate(ingredients_list):
            ingredients_list[i] = v.strip()
            if '.' in v:
                ingredients_list[i] = v.replace('.',"").strip()
            if ')' in v:
                ingredients_list[i] = v.replace(')',"").strip()
                
    return ingredients_list
    
            
def get_food_ingredients_openfoodfacts(barcode):
    global buffer
    api_url = f'https://world.openfoodfacts.org/api/v0/product/{barcode}.json'
    
    response = requests.get(api_url)
    
    if response.status_code == 200:
        data = response.json()
        if data['status'] == 1:
            product = data['product']
            ingredients_list = product.get('ingredients', [])
            ingredients = [ingredient.get('text', 'Unknown') for ingredient in ingredients_list]
            allergens=product.get('allergens_tags',[])
            if isinstance(ingredients, list):
                    print("Ingredients:")
            else:
                print(ingredients)
            if allergens:
                displayIngredients("OpenFoodFacts",ingredients,True,allergens)
                buffer['OpenFoodFacts'] = ["OpenFoodFacts",ingredients,True,allergens]
                print("Allergens:")
            else:
                displayIngredients("OpenFoodFacts",ingredients)
                buffer['OpenFoodFacts'] = ["OpenFoodFacts",ingredients]
                print("No allergens found or not specified.")
            
        else:
            print('OpenFoodFacts Product not found')
    else:
        print('Error in API request:: ',response)
    
    
def get_nutritionix_ingredients(barcode):
    api_url = f'https://trackapi.nutritionix.com/v2/search/item/?upc={barcode}'
    response = requests.get(api_url,headers={'x-app-id':f'627a2e20','x-app-key':f'f24f17f1ad152bac28fb66af2c2fae34'})
    data = response.json()
    
    if response.status_code == 200:
        product = data['foods'][0]
        ingredients_list = simplify(product.get('nf_ingredient_statement'))
        
        displayIngredients("Nutritionix",ingredients_list)
        buffer['Nutritionix'] = ["Nutritionix",ingredients_list]
    else:
        print("Error: ",response)
        
        
def get_edamam_ingredients(barcode):
    api_id = '259015ba'  # Replace with your Edamam API ID
    api_key = '29ca21b47b39e970115ef263ecebe1a3'  # Replace with your Edamam API Key
    url = f'https://api.edamam.com/api/food-database/v2/parser?upc={barcode}&app_id={api_id}&app_key={api_key}'
    
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        products = data.get('hints')[0].get('food')
        ingredients_list = products.get('foodContentsLabel')
        
        ingredients_list = simplify(ingredients_list.replace('INGREDIENTS:',""),"edamam")

        for i,v in enumerate(ingredients_list):
            ingredients_list[i] = v.lower().capitalize()
        displayIngredients("Edamam",ingredients_list)
        buffer['Edamam'] = ["Edamam",ingredients_list]
    else:
        pass
    
# Function to update the scroll region of the canvas
def update_scrollregion(event):
    canvas.configure(scrollregion=canvas.bbox("all"))
        
def BarcodeReader(): 
    image = image_path
    img = cv2.imread(image) 
       
    # Decode the barcode image 
    detectedBarcodes = decode(img) 
       
    # If not detected then print the message 
    if not detectedBarcodes: 
        print("Barcode Not Detected or your barcode is blank/corrupted!") 
    else:
        for barcode in detectedBarcodes:   
            # Locate the barcode position in image 
            (x, y, w, h) = barcode.rect 
            
            cv2.rectangle(img, (x-10, y-10), 
                          (x + w+10, y + h+10),  
                          (255, 0, 0), 2) 
              
            if barcode.data!="": 
                print(barcode.data) 
                print(barcode.type)
                displayText.set(barcode.data)
                global barcoded 
                barcoded = barcode.data
                
            # Get food ingredients from the OpenFoodFacts API
            global slide,buffer
            buffer = {'OpenFoodFacts':0,'Nutritionix':0,'Edamam':0}
            get_food_ingredients_openfoodfacts(barcode.data)
            slide = 0
def incORdec(string):
    global slide, buffer
    if string == "inc":
        slide += 1
        if slide == 3: slide = 0
    elif string == "dec":
        slide -= 1
        if slide == -1: slide = 2  
        
    if(slide == 0):
        if buffer['OpenFoodFacts'] != 0:
            temp = buffer["OpenFoodFacts"]
            if len(temp) == 4:
                displayIngredients(temp[0],temp[1],temp[2],temp[3])
            else:
                displayIngredients(temp[0],temp[1])
        else:
            get_food_ingredients_openfoodfacts(barcoded)
    elif(slide == 1):
        if buffer['Nutritionix'] != 0:
            temp = buffer["Nutritionix"]
            displayIngredients(temp[0],temp[1])
        else:
            get_nutritionix_ingredients(str(barcoded)[2:-1])
    elif(slide == 2):
        if buffer['Edamam'] != 0:
            temp = buffer["Edamam"]
            displayIngredients(temp[0],temp[1])
        else:
            get_edamam_ingredients(barcoded)
    else:
        canvas.delete("all")
             
imageButton = tk.Button(root, text = "Choose Image",command=finddirectory, bg="#2e2c27", fg="white").place(x=10,y=10)
findText = tk.Button(root,text="Search", command=BarcodeReader, bg="#2e2c27", fg="white").place(x=100,y=10)
tk.Label(root,text = "Extrated Text/Barcode: ").place(x=10,y=40)
display = tk.Label(root,textvariable=displayText,bg="gray",width=18,height=3,font=("Arial",20)).place(x=10,y=60)
tk.Canvas(root,width=180,height=145, bg="#2e2c27").place(x=320,y=15)

tk.Canvas(root, width=510,height=5, bg="#2e2c27").place(x=5,y=175)
tk.Label(root, text = "Ingredients: ").place(x=10,y=182)
tk.Canvas(root, width=510,height=5, bg="#2e2c27").place(x=5,y=200)

#ingredientArea = tk.Frame(root,width=394,height=189,bg="white").place(x=65,y=220)
frame.place(x=65, y=220)
canvas.place(x=0, y=0)

# Add a vertical scrollbar to the frame, next to the canvas
scrollbar = tk.Scrollbar(frame, orient=tk.VERTICAL, command=canvas.yview)
scrollbar.place(x=374, y=0, height=189)

# Configure the canvas to use the scrollbar
canvas.configure(yscrollcommand=scrollbar.set)

# Bind the configure event of the canvas to update the scroll region
canvas.bind("<Configure>", update_scrollregion)

tk.Button(root,text="<",width=5,height=12,bg="gray",command=lambda: incORdec('dec')).place(x=15,y=220)
tk.Button(root,text=">",width=5,height=12,bg="gray",command=lambda: incORdec('inc')).place(x=465,y=220)

tk.mainloop()