import numpy
from pyzbar.pyzbar import decode 
import cv2

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