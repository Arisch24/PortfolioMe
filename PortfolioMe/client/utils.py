import secrets
import os
from flask import current_app, url_for
from PIL import Image
import cv2
import pytesseract


def save_resume(form_resume):
    # Function to save the resume image
    random_hex = secrets.token_hex(8)
    _, file_extension = os.path.splitext(form_resume.filename)
    resume_name = random_hex + file_extension
    resume_path = os.path.join(
        current_app.root_path, 'static/resumes', resume_name)

    # Resizing image
    output_size = (1080, 1920)  # size of image
    image = Image.open(form_resume)
    image.thumbnail(output_size)
    image.save(resume_path)

    return resume_name


def parse_resume(resume_image):
    path = r"c:\Users\arisc\OneDrive\Documents\VS Code\FYP\PortfolioMe\static\resumes"
    img = cv2.imread(path + f"\{resume_image}")

    # Adding custom options
    custom_config = r'--oem 3 --psm 6'
    pytesseract.pytesseract.tesseract_cmd = 'C:\\Users\\arisc\\AppData\\Local\\Programs\\Tesseract-OCR\\tesseract.exe'

    text = pytesseract.image_to_string(img, lang='eng')
    return text
