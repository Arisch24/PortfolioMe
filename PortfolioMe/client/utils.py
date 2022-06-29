import secrets
import os
from PortfolioMe import app
from PIL import Image


def save_resume(form_resume):
    # Function to save the resume image
    random_hex = secrets.token_hex(8)
    _, file_extension = os.path.splitext(form_resume.filename)
    resume_name = random_hex + file_extension
    resume_path = os.path.join(app.root_path, 'static/resumes', resume_name)

    # Resizing image
    output_size = (1080, 1920)  # size of image
    image = Image.open(form_resume)
    image.thumbnail(output_size)
    image.save(resume_path)

    return resume_name
