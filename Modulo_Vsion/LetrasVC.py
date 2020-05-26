import pytesseract
import cv2
from PIL import Image
import numpy as np

def get_grayscale(image):
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
 
def thresholding(image):
    return cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
	
def remove_noise(image):
    return cv2.medianBlur(image,5)
	
def opening(image):
    kernel = np.ones((5,5),np.uint8)
    return cv2.morphologyEx(image, cv2.MORPH_OPEN, kernel)

def deskew(image):
    coords = np.column_stack(np.where(image > 0))
    angle = cv2.minAreaRect(coords)[-1]
    if angle < -45:
        angle = -(90 + angle)
    else:
        angle = -angle
    (h, w) = image.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    return rotated
value=Image.open(r"C:\Users\Ayoub\Desktop\vision_v3\imagen_vision.jpg")
#value=cv2.imread(r"C:\Users\Ayoub\Desktop\vision_v3\1.jpg")

#value= deskew(value)
#gray = get_grayscale(value)
#value = opening(gray)
#value= thresholding(gray)

text=pytesseract.image_to_string(value,config='--tessdata-dir "C://Program Files//Tesseract-OCR//tessdata"')
print("text present in images: \n",text)
