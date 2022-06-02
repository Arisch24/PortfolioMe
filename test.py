import cv2 
import pytesseract

img = cv2.imread('test.png')

# Adding custom options
# custom_config = r'--oem 3 --psm 6'
pytesseract.pytesseract.tesseract_cmd = 'C:\\Users\\arisc\\AppData\\Local\\Programs\\Tesseract-OCR\\tesseract.exe'

text = pytesseract.image_to_string(img, lang='eng')
print(text)