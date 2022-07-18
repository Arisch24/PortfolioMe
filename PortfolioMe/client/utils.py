import secrets
import os
import cv2
import pytesseract
import numpy as np
import pdf2image
from PIL import Image
from flask import current_app, url_for
from turtle import width


def save_resume(form_resume):
    '''
    Function to save the resume image
    *
    @param (form_resume): to save the resume in the filesystem
    '''
    random_hex = secrets.token_hex(8)
    _, file_extension = os.path.splitext(form_resume.filename)
    if file_extension == ".pdf":
        form_resume = form_resume.read()
        pages = pdf2image.convert_from_bytes(
            form_resume,  fmt="png", poppler_path='C:\\Program Files\\poppler-0.68.0\\bin')

        resume_name = random_hex + ".png"
        resume_path = os.path.join(
            current_app.root_path, 'static/resumes')
        for page in pages:
            page.save(f'{resume_path}/{resume_name}')
    else:
        resume_name = random_hex + file_extension
        resume_path = os.path.join(
            current_app.root_path, 'static/resumes', resume_name)

        # Resizing image
        output_size = (1080, 1920)  # size of image
        image = Image.open(form_resume)
        image = image.convert("RGB")
        image.thumbnail(output_size)
        image.save(resume_path)

    return resume_name


def convert_pdf(pdf):
    # Convert pdf to image
    pages = pdf2image.convert_from_bytes(
        pdf,  fmt="png", poppler_path='C:\\Program Files\\poppler-0.68.0\\bin')
    return pages


''' 
=================================
All image processing functions
=================================
 '''


def grayscale(image):
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)


def remove_noise(image):
    # noise removal
    return cv2.medianBlur(image, 1)


def thresholding(image):
    # thresholding
    return cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]


def dilate(image):
    # dilation
    kernel = np.ones((5, 5), np.uint8)
    return cv2.dilate(image, kernel, iterations=1)


def erode(image):
    # erosion
    # opening - erosion followed by dilation
    kernel = np.ones((3, 3))
    return cv2.erode(image, kernel, iterations=1)


def opening(image):
    kernel = np.ones(3)
    return cv2.morphologyEx(image, cv2.MORPH_OPEN, kernel)


def canny(image):
    # canny edge detection
    return cv2.Canny(image, 10, 20)


def deskew(image):
    # skew correction
    coords = np.column_stack(np.where(image > 0))
    angle = cv2.minAreaRect(coords)[-1]
    if angle < -45:
        angle = -(90 + angle)
    else:
        angle = -angle
    (h, w) = image.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(
        image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    return rotated


def match_template(image, template):
    # template matching
    return cv2.matchTemplate(image, template, cv2.TM_CCOEFF_NORMED)


def resize(img, x, y):
    img = cv2.resize(img, None, fx=x, fy=y, interpolation=cv2.INTER_CUBIC)
    return img


def apply_filters(retouche):
    after_grayscale = grayscale(retouche)
    after_threshold = thresholding(after_grayscale)
    after_opening = opening(after_threshold)
    after_erode = erode(after_opening)
    after_remove_noise = remove_noise(after_erode)
    return after_remove_noise


def parse_resume(resume_image, bool):
    ''''
    Parse resume function
    @param(resume_image): resume_image to parse
    @param(bool): false if its converted from pdf to image and true if image is read from form
    '''
    if bool:
        # convert string data to numpy array
        npimg = np.fromstring(resume_image, np.uint8)
        # convert numpy array to image
        img = cv2.imdecode(npimg, cv2.IMREAD_COLOR)
        height, width, _ = img.shape
    else:
        for page in resume_image:
            # convert to img
            img = np.array(page)
        width, height, _ = img.shape

    # check if height and width are low
    if height < 1280 or width < 720:
        retouche = resize(img, 3.5, 3.5)
        filtered_image = apply_filters(retouche)
    elif height < 1920 or width < 1080:
        retouche = resize(img, 3, 3)
        filtered_image = apply_filters(retouche)
    else:
        filtered_image = img

    # Adding custom options
    custom_config = r'--oem 3'
    pytesseract.pytesseract.tesseract_cmd = 'C:\\Users\\arisc\\AppData\\Local\\Programs\\Tesseract-OCR\\tesseract.exe'

    text = pytesseract.image_to_string(
        filtered_image, lang='eng', config=custom_config)

    return text
