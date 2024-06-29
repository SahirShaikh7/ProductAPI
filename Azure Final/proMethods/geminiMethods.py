from proMethods import display
import google
import google.generativeai as genai

GOOGLE_API_KEY = "AIzaSyC81hsbRz79lDZ9Y-4gMrzz_cDhBYh-uTU"
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

prompt = """Give the name of '%s' after 'Food:' and specify all 'Raw Material:', Ingredients -> Components (contains materials that make up the raw mmaterials or displays 'None') separately under 'ingredients:' in new lines. Start each list with commas. In the next line, state 'hazards:', followed by the health hazards this food item can cause. Then, in the next line, state 'allergies:', followed by all the allergies this food item can cause. Ensure there are no empty lines or extra white spaces and also give the classification like Veg or Non-Veg.

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
    
def text(TEXT):
    try: 
        response = model.generate_content(prompt % TEXT)
        res = response.text.replace('*',"").replace('#','')
        dic = display.display(res)
        return dic
    except google.api_core.exceptions.InternalServerError: return text(TEXT)
    except google.api_core.exceptions.ResourceExhausted: return 'Product Not Found'
    except AttributeError: return text(TEXT)
    except IndexError: return text(TEXT)
    
def img(IMAGE):
    response = model.generate_content(['Give only the name of the Food item/product shown in the image in lowercase', IMAGE], stream=True)
    response.resolve()
    res = response.text.replace('*',"").replace('#','').replace('\n','').strip()
    print('Retrieved Food Image:',res)
    return res