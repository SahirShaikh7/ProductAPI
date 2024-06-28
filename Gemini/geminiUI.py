from tkinter import *
import requests
import google
import cv2
import google.generativeai as genai
from PIL import Image as im, ImageTk 
import pandas as pd
from tkinter import *
from tkinter import messagebox
from pandastable import Table, TableModel
import warnings
warnings.filterwarnings("ignore")
from pyzbar.pyzbar import decode 



root = Tk()
root.geometry('640x575') 
root.title('Gemini Food API')
root.configure(bg='#365E32')

foodVar = StringVar()
barcodeVar = StringVar()
classVar = StringVar()
classVar.set('INGREDIENTS:')

GOOGLE_API_KEY = "AIzaSyC81hsbRz79lDZ9Y-4gMrzz_cDhBYh-uTU"
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')
prompt = """Give name of %s after 'Food:' and specify all 'Raw Material:' 'Spices:', 'Acidity Regulators:', 'Oils:', 'Emulsifiers:', 'Flavour Enhancers:', 'Colors:' sperately under 'Ingredeints:' in new lines it has in the next line with commas starting with 'Ingredients:' and then in a new line gives all the allergies this food item can give infront of 'Allergies:'. In the next line, state the nutrients with their percentages in front of 'Nutrients:'. In New Line state if it's Veg or Non-Veg staring with 'Classification'. with no empty lines or white spaces
EXAMPLE:

Food: <Food Name>
Ingredients:
Raw Material: <raw material, name all sperately and not in brackets>
Spices: <spices>
Acidity Regulators: <acidity regulators>
Oils: <Diffrent oils>
Emulsifiers: <emulsifiers>
Flavour Enhancers: <Flavour Enhancers>
Colors:  <Added Colours>
Allergies:  <allergies names only>
Nutrients: <Nutrient with percentage or unit in brackets don't use ':'>
Classification: <Veg or Non-Veg>
"""
#for camera
camera_open = False
placeholder_image = im.open('Gemini/images/CameraPlaceholder.png')
placeholder_image = placeholder_image.resize((275,225))
placeholder_photo = ImageTk.PhotoImage(placeholder_image)
placeholder_photo_Og = placeholder_photo
capturedImage = None
captured = None
label_widget = Label(root,image=placeholder_photo)
label_widget.place(x=340, y=20)


#Table
Canvas(root,bg='#81A263',width=600, height=225).place(x=20, y=330)
tables_frame = Frame(root,bg='#81A263')
tables_frame.place(x=22, y=332, width=600, height=225)

temp = {'Raw Material': ['', '', '', '', '', '', '', '', '', ''], 'Spices': ['', '', '', '', '', '', '', '', '', ''], 'Acidity Regulators': ['', '', '', '', '', '', '', '', '', ''], 'Oils': ['', '', '', '', '', '', '', '', '', ''], 'Emulsifiers': ['', '', '', '', '', '', '', '', '', ''], 'Flavour Enhancers': ['', '', '', '', '', '', '', '', '', ''], 'Colors': ['', '', '', '', '', '', '', '', '', ''], 'Nutrients': ['', '', '', '', '', '', '', '', '', '']}
df1 = pd.DataFrame(temp)
table_frame1 = Frame(tables_frame)
table_frame1.place(x=20, y=10, width=450, height=200)  # Set the size and position
ingredientTable = Table(table_frame1, dataframe=df1, width=500, height=200)
ingredientTable.show()
ingredientTable.hideRowHeader()

ingredientTable.zoomOut()
ingredientTable.zoomOut()
ingredientTable.zoomOut()
ingredientTable.zoomOut()

temp = {'Allergies': ['', '', '', '', '', '', '', '', '', '']}
df1 = pd.DataFrame(temp)
table_frame2 = Frame(tables_frame)
table_frame2.place(x=480, y=10, width=100, height=200)  # Set the size and position
allergyTable = Table(table_frame2, dataframe=df1, showindex=False, width=300, height=200)
allergyTable.show()
allergyTable.hideRowHeader()

# Scale down the first table
allergyTable.zoomOut()
allergyTable.zoomOut()
allergyTable.zoomOut()
allergyTable.zoomOut()


def display(response):
    lists = response.split('\n')
    biggest = 0
    for i,list in enumerate(lists):
        lists[i] = list.split(':')
        if lists[i][0] == '':
            lists.pop(i)
            continue
        li = lists[i][1]
        split = True
        pos = 0
        temp = []
        for j,let in enumerate(li):
            if let == '(': split = False
            elif let == ')': split = True
            if split and let == ',' or j == len(li)-1:
                t = li[pos:j+1]
                if t[-1] == ',':temp.append(t[0:-1].strip())
                else: temp.append(t.strip())
                pos = j+1
        if len(temp) > biggest: biggest = len(temp)
        lists[i][1] = temp
    
    for i,list in enumerate(lists):
        if list[0] == 'Allergies': continue
        for j in range(biggest-len(list[1])):
            list[1].append('')
        #print(list)
    
    data = dict(lists)
    if data['Nutrients'][0] == '': 
        print('Retrying...')
        raise AttributeError
    allergy = {'Allergies':data['Allergies']}
    clas = data['Classification'][0]
    print('Food Item:',data['Food'][0])
    foodVar.set(data['Food'][0])
    del data['Food'], data['Ingredients'], data['Allergies'], data['Classification']
    print('Ingredients:')
    IT = pd.DataFrame(data)
    print(IT)
    ingredientTable.updateModel(TableModel(IT))
    ingredientTable.redraw()
    print('Allergies:')
    AT = pd.DataFrame(allergy)
    print(AT)
    allergyTable.updateModel(TableModel(AT))
    allergyTable.redraw()
    print('Food Classification:',clas)
    t = "INGREDIENTS:",clas
    classVar.set(t)

def text():
    TEXT = foodVar.get()
    try:
        response = model.generate_content(prompt % TEXT)
        res = response.text.replace('*',"").replace('#','')
        print(res)
        if res.count('\n') >= 12 or res.count(':') > 12:
            display(res)
    except google.api_core.exceptions.InternalServerError: text()
    except AttributeError: text()
    except IndexError: text()
    
def img(image):
    try:
        response = model.generate_content([prompt % 'this food item', image], stream=True)
        response.resolve()
        res = response.text.replace('*',"")
        print(res)
        if res.count('\n') >= 12 or res.count(':') > 12:
            display(res)
        else: messagebox.showinfo("Error", "Please Enter Valid Food Image") 
    except google.api_core.exceptions.InternalServerError: img(image)
    except AttributeError: img(image)
    except IndexError: img(image)
    
def get_food_name_openfoodfacts():
    barcode = barcodeVar.get()
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
            foodVar.set(t)
            text()
            
def open_camera(STRING): 
    global vid, camera_open
    if not camera_open:
        # Define new video capture object
        vid = cv2.VideoCapture(0)
        # Set the width and height 
        vid.set(cv2.CAP_PROP_FRAME_WIDTH, 300) 
        vid.set(cv2.CAP_PROP_FRAME_HEIGHT, 300)
        camera_open = True
        # Repeat the same process after every 100 milliseconds (increase delay)
        update_frame(STRING)
    
def close_camera():
    global vid, camera_open
    if camera_open:
        # Release the camera
        vid.release()
        camera_open = False   
        
def capture_image():
    global capturedImage, placeholder_photo, captured
    placeholder_photo = capturedImage
    close_camera()
    img(captured)

closeButton = Button(root,text="X",command=close_camera,width=3, bg='#365E32', fg='white')
closeButton.place(x=342,y=22)
capture = Button(root,text='CAPTURE', command=capture_image, bg='white', fg='black',width=34,font=('Arial',10,'bold'),state='disabled')
capture.place(x=339,y=255)


def update_frame(STRING):
    global vid, camera_open, capturedImage, placeholder_photo_Og, placeholder_photo, captured
    
    try:
        # Capture the video frame by frame 
        _, frame = vid.read() 
        frame = cv2.flip(frame, 1)
        
        if camera_open and frame is not None:
            opencv_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA) 

            captured_image = im.fromarray(opencv_image)
            captured = captured_image
            captured_image = captured_image.resize((275,225))
            # Convert captured image to photoimage 
            photo_image = ImageTk.PhotoImage(image=captured_image) 

            label_widget.photo_image = photo_image 

            label_widget.configure(image=photo_image) 
            label_widget.lift()
            closeButton.lift()
            
            if STRING == 'Barcode':
                detect_barcode = decode(frame)
                if not detect_barcode: 
                    print("Barcode Not Detected") 
                else:
                    for barcode in detect_barcode:   
                        (x, y, w, h) = barcode.rect 
                        
                        cv2.rectangle(frame, (x-10, y-10), (x + w+10, y + h+10), (255, 0, 0), 2) 
                        
                        if barcode.data!="":
                            print('Barcode Reader:',barcode.data)
                            barcodeVar.set(str(barcode.data))
                            get_food_name_openfoodfacts()
                            close_camera()
                            break
            elif STRING == 'Food':
                capture.configure(state='active')
                capturedImage = photo_image
            else:
                capture.configure(state='disabled')
                capturedImage = photo_image
                captured = None
        elif not camera_open:
            # Display placeholder image when the camera is closed
            label_widget.configure(image=placeholder_photo)
            placeholder_photo = placeholder_photo_Og
            capture.configure(state='disabled')
                    
    except Exception as e:
        print(f"An error occurred: {e}")
    
    # Repeat the same process after every 100 milliseconds (increase delay)
    if camera_open:
        label_widget.after(10, update_frame,STRING)


    
Canvas(root,width=300, height=260, bg='#81A263',borderwidth=-1).place(x=20,y=20)
#Food Item Name
Label(root,text='FOOD ITEM:', bg='#FD9B63', fg='white',width=20,font=('Arial',10,'bold')).place(x=40,y=40)
Label(root,text='Name:', bg='#365E32', fg='white',width=8).place(x=40,y=66)
Entry(root, textvariable=foodVar, bg='#E7D37F').place(x=108,y=67)
Button(root,text='Submit', command=text, bg='#365E32', fg='white').place(x=235,y=63)
Label(root,text='OR:', bg='#81A263', fg='#365E32').place(x=40,y=87)
Button(root,text='Take Picture', command=lambda: open_camera('Food'), bg='#365E32', fg='white').place(x=40,y=107)

Label(root,text='BARCODE:', bg='#FD9B63', fg='white',width=20,font=('Arial',10,'bold')).place(x=40,y=150)
Label(root,text='Code:', bg='#365E32', fg='white',width=8).place(x=40,y=176)
Entry(root, textvariable=barcodeVar, bg='#E7D37F').place(x=108,y=177)
Button(root,text='Submit', command=get_food_name_openfoodfacts, bg='#365E32', fg='white').place(x=235,y=173)
Label(root,text='OR:', bg='#81A263', fg='#365E32').place(x=40,y=197)
Button(root,text='Take Picture', command=lambda: open_camera('Barcode'), bg='#365E32', fg='white').place(x=40,y=217)

Canvas(root,width=275, height=225, bg='#81A263',borderwidth=-1).place(x=340,y=20)
label_widget.lift()
capture.lift()
closeButton.lift()

Label(root,text='INGREDIENTS:',textvariable=classVar, bg='#FD9B63', fg='white',width=50,font=('Arial',14,'bold')).place(x=19, y=295)
root.mainloop()


#8992760221028
#0071464306502