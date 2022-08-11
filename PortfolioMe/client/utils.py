import secrets
import os
import cv2
import pytesseract
import numpy as np
import pdf2image
import difflib
import re
import nltk
import spacy
from flask_login import current_user
from flask import current_app


def save_resume(form_resume):
    '''
    Function to save the resume image
    *
    @param (form_resume): to save the resume in the filesystem
    '''
    random_hex = secrets.token_hex(8)
    _, file_extension = os.path.splitext(form_resume.filename)

    resume_name = random_hex + file_extension
    resume_path = os.path.join(
        current_app.root_path, 'static/resumes', resume_name)

    form_resume.save(resume_path)

    return resume_name


def save_multiple_documents(docs):
    all_docs_name = []
    for doc in docs:
        random_hex = secrets.token_hex(8)
        _, file_extension = os.path.splitext(doc.filename)
        doc_name = random_hex + file_extension
        doc_path = os.path.join(
            current_app.root_path, f'static/resumes', doc_name)

        all_docs_name.append(doc_name)
        doc.save(doc_path)

    return all_docs_name


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


def parse_resume(resume_image):
    '''
    Parse resume function
    @param(resume_image): resume_image to parse
    '''
    text = ""
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

        text += pytesseract.image_to_string(
            filtered_image, lang='eng', config=custom_config) + "\n"

    return text


def find_keywords(sentences, words, raw):
    '''
    Find keywords in raw resume data
    @param(data): data in list format
    '''

    # section to find the hireable criteria
    edu_keywords = ['education', 'edu', 'curriculum', 'educational history']
    cert_keywords = ['certification', 'certificate',
                     'certificates', 'cert', 'agency', 'other credentials']
    skills_keywords = ['technical', 'technical skills', 'technical skill']
    soft_skills_keywords = ['soft', 'soft skills', 'soft skill']
    work_experience_keywords = [
        'working experience', 'work experience']
    other_keywords = ['references', 'interests', 'contact me',
                      'personal information', 'personal profile']

    json_data = {}
    CLOSE_MATCHES = 1
    for i in range(len(sentences)):
        if difflib.get_close_matches(sentences[i].lower(), edu_keywords, CLOSE_MATCHES):
            j = i + 1
            text = ""
            while not (difflib.get_close_matches(sentences[j].lower(), cert_keywords, CLOSE_MATCHES)
                       or difflib.get_close_matches(sentences[j].lower(), skills_keywords, CLOSE_MATCHES)
                       or difflib.get_close_matches(sentences[j].lower(), soft_skills_keywords, CLOSE_MATCHES)
                       or difflib.get_close_matches(sentences[j].lower(), work_experience_keywords, CLOSE_MATCHES)
                       or difflib.get_close_matches(sentences[j].lower(), other_keywords, CLOSE_MATCHES)):
                text = text + sentences[j] + "\n"
                json_data.update({"education": text})
                j = j + 1
                if j >= len(sentences):
                    break
        if difflib.get_close_matches(sentences[i].lower(), cert_keywords, CLOSE_MATCHES):
            k = i + 1
            text = ""
            while not (difflib.get_close_matches(sentences[k].lower(), edu_keywords, CLOSE_MATCHES)
                       or difflib.get_close_matches(sentences[k].lower(), skills_keywords, CLOSE_MATCHES)
                       or difflib.get_close_matches(sentences[k].lower(), soft_skills_keywords, CLOSE_MATCHES)
                       or difflib.get_close_matches(sentences[k].lower(), work_experience_keywords, CLOSE_MATCHES)
                       or difflib.get_close_matches(sentences[k].lower(), other_keywords, CLOSE_MATCHES)):
                text = text + sentences[k] + "\n"
                json_data.update({"certification": text})
                k = k + 1
                if k >= len(sentences):
                    break
        if difflib.get_close_matches(sentences[i].lower(), skills_keywords, CLOSE_MATCHES):
            l = i + 1
            text = ""
            while not (difflib.get_close_matches(sentences[l].lower(), edu_keywords, CLOSE_MATCHES)
                       or difflib.get_close_matches(sentences[l].lower(), cert_keywords, CLOSE_MATCHES)
                       or difflib.get_close_matches(sentences[l].lower(), soft_skills_keywords, CLOSE_MATCHES)
                       or difflib.get_close_matches(sentences[l].lower(), work_experience_keywords, CLOSE_MATCHES)
                       or difflib.get_close_matches(sentences[l].lower(), other_keywords, CLOSE_MATCHES)):
                text = text + sentences[l] + "\n"
                json_data.update({"skills": text})
                l = l + 1
                if l >= len(sentences):
                    break
        if difflib.get_close_matches(sentences[i].lower(), soft_skills_keywords, CLOSE_MATCHES):
            m = i + 1
            text = ""
            while not (difflib.get_close_matches(sentences[m].lower(), edu_keywords, CLOSE_MATCHES)
                       or difflib.get_close_matches(sentences[m].lower(), skills_keywords, CLOSE_MATCHES)
                       or difflib.get_close_matches(sentences[m].lower(), cert_keywords, CLOSE_MATCHES)
                       or difflib.get_close_matches(sentences[m].lower(), work_experience_keywords, CLOSE_MATCHES)
                       or difflib.get_close_matches(sentences[m].lower(), other_keywords, CLOSE_MATCHES)):
                text = text + sentences[m] + "\n"
                json_data.update({"soft_skills": text})
                m = m + 1
                if m >= len(sentences):
                    break
        if difflib.get_close_matches(sentences[i].lower(), work_experience_keywords, CLOSE_MATCHES):
            n = i + 1
            text = ""
            while not (difflib.get_close_matches(sentences[n].lower(), edu_keywords, CLOSE_MATCHES)
                       or difflib.get_close_matches(sentences[n].lower(), skills_keywords, CLOSE_MATCHES)
                       or difflib.get_close_matches(sentences[n].lower(), soft_skills_keywords, CLOSE_MATCHES)
                       or difflib.get_close_matches(sentences[n].lower(), cert_keywords, CLOSE_MATCHES)
                       or difflib.get_close_matches(sentences[n].lower(), other_keywords, CLOSE_MATCHES)):
                text = text + sentences[n] + "\n"
                json_data.update({"work_experience": text})
                n = n + 1
                if n >= len(sentences):
                    break
        if difflib.get_close_matches(sentences[i].lower(), other_keywords, CLOSE_MATCHES):
            o = i + 1
            text = ""
            while not (difflib.get_close_matches(sentences[o].lower(), edu_keywords, CLOSE_MATCHES)
                       or difflib.get_close_matches(sentences[o].lower(), skills_keywords, CLOSE_MATCHES)
                       or difflib.get_close_matches(sentences[o].lower(), soft_skills_keywords, CLOSE_MATCHES)
                       or difflib.get_close_matches(sentences[o].lower(), cert_keywords, CLOSE_MATCHES)
                       or difflib.get_close_matches(sentences[o].lower(), work_experience_keywords, CLOSE_MATCHES)):
                text = text + sentences[o] + "\n"
                json_data.update({"others": text})
                o = o + 1
                if o >= len(sentences):
                    break

    # section to find the personal particulars from the data
    phone_number_pattern = r'\d{3}-\d{7,8}'
    linked_in_url_pattern = r'((http(s?)://)*([www])*\.|[linkedin])[linkedin/~\-]+\.[a-zA-Z0-9/~\-_,&=\?\.;]+[^\.,\s<]'
    postcode_pattern = r'\D(\d{5})\D'
    ic_pattern = r'\d{6}-\d{2}-\d{4}'
    address_pattern = r'[0-9]{1,3} .+, .+, [a-zA-Z]{2} [0-9]{5}'
    # Only Malaysian states
    state_pattern = r'Negeri Sembilan|Pahang|Perak|Perlis|Kedah|Selangor|Melaka|Sarawak|Penang|Terengganu|Kelantan|Sabah|Johor'

    for d in words:
        # search for phone number
        if re.search(phone_number_pattern, d.strip(), re.IGNORECASE):
            json_data.update(
                {"phone_number": re.search(phone_number_pattern, d.strip()).group()})
        # search for linked_in url
        elif re.search(linked_in_url_pattern, d.strip(), re.IGNORECASE):
            json_data.update(
                {"linked_in_url": re.search(linked_in_url_pattern, d.strip()).group()})
        # search for postcode
        elif re.search(postcode_pattern, " " + d.strip() + " "):
            json_data.update({"postcode": re.search(
                postcode_pattern, " " + d.strip() + " ").group().strip()})
        # search for ic
        elif re.search(ic_pattern, d.strip()):
            json_data.update({"ic": re.search(ic_pattern, d.strip()).group()})
        # search for address
        elif re.search(address_pattern, d.strip(), re.IGNORECASE):
            json_data.update({"address": re.search(
                address_pattern, d.strip()).group()})
        # search for address
        elif re.search(state_pattern, d.strip(), re.IGNORECASE):
            json_data.update({"state": re.search(
                state_pattern, d.strip()).group()})

    english_nlp = spacy.load('en_core_web_sm')
    spacy_parser = english_nlp(raw.lower())

    for entity in spacy_parser.ents:
        if entity.label_ == "PERSON":
            json_data.update({"name": entity.text})

    return json_data


def extract_resume_data(text):
    words = nltk.word_tokenize(text=text)
    sentences = nltk.line_tokenize(text=text)
    # pass data for keyword checking
    json_dict = find_keywords(sentences, words, text)

    # to store raw parsed text
    applicant_details = ""
    for index in sentences:
        if index == "":
            sentences.remove(index)
        else:
            applicant_details += "".join(index) + "\n"

    json_dict.update({"applicant_details": applicant_details})

    return json_dict
