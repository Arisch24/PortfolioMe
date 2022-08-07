# PortfolioMe

---

## Features

- Register/Login
- Edit Profile
- Reset Password
- Blocking/Unblock Account
- Unactive Account user not logged in for > 3 months
- Apply for jobs
- Job searching and filtering
- Upload resume and additional documents
- Resume converted to image and parsed with OCR
- Parsed text is segmented and processed with NLP algorithm

## Samples

## Cloning the repo

1. Install python if you don't have it on your machine with `sudo apt install python3.8` for Linux/Mac and [click here](https://www.python.org/downloads/) for Windows. Make sure you have the latest installation on your machine.
2. Next, create a new virtual environment `$ virtualenv .venv` and activate it. The steps for activating are [here](#virtual-environment-activation).
3. Download the requirements of this repo with `pip install -r requirements.txt` command.
4. Then run `python run.py` in the terminal and navigate to your browser and go to `localhost:5000`

### Virtual Environment Activation

Windows

```console
source .venv/Scripts/activate
```

Mac/Linux

```console
source .venv/bin/activate
```

## App Structure

```text
.
|-- LICENSE
|-- PortfolioMe
|   |-- __init__.py
|   |-- admin_forms.py
|   |-- admin_routes.py
|   |-- auth
|   |   |-- __init__.py
|   |   |-- forms.py
|   |   |-- routes.py
|   |   `-- utils.py
|   |-- client
|   |   |-- __init__.py
|   |   |-- forms.py
|   |   |-- routes.py
|   |   `-- utils.py
|   |-- config.py
|   |-- constants.py
|   |-- errors
|   |   |-- __init__.py
|   |   `-- handlers.py
|   |-- main
|   |   |-- __init__.py
|   |   `-- routes.py
|   |-- models.py
|   |-- site.db
|   |-- static
|   |   |-- css
|   |   |   |-- admin
|   |   |   |   |-- base.css
|   |   |   |   |-- index.css
|   |   |   |   |-- login.css
|   |   |   |   `-- manage_admin.css
|   |   |   |-- auth
|   |   |   |   |-- login.css
|   |   |   |   |-- register.css
|   |   |   |   |-- reset_password_request.css
|   |   |   |   `-- reset_token.css
|   |   |   |-- client
|   |   |   |   |-- edit_profile.css
|   |   |   |   |-- job_board.css
|   |   |   |   |-- job_detail.css
|   |   |   |   |-- resume_status.css
|   |   |   |   `-- upload_resume_details.css
|   |   |   |-- custom
|   |   |   |   |-- create.css
|   |   |   |   |-- details.css
|   |   |   |   |-- edit.css
|   |   |   |   `-- list.css
|   |   |   |-- errors
|   |   |   |   `-- errors.css
|   |   |   |-- layout
|   |   |   |   |-- base.css
|   |   |   |   |-- base_errors.css
|   |   |   |   |-- base_form.css
|   |   |   |   `-- reset.css
|   |   |   `-- main
|   |   |       `-- index.css
|   |   |-- images
|   |   |   |-- Eye_Icon_UIA.svg
|   |   |   |-- Eye_slash_Icon_UIA.svg
|   |   |   |-- Hamburger.png
|   |   |   |-- favicon.ico
|   |   |   |-- folder.png
|   |   |   |-- folder.svg
|   |   |   |-- github.svg
|   |   |   |-- instagram.svg
|   |   |   |-- medal.svg
|   |   |   |-- photo.png
|   |   |   |-- profile-circle.svg
|   |   |   |-- resume image.png
|   |   |   |-- save-2.svg
|   |   |   |-- search-normal.svg
|   |   |   `-- youtube.svg
|   |   `-- js
|   |       `-- extras.js
|   `-- templates
|       |-- admin
|       |   |-- base.html
|       |   |-- index.html
|       |   |-- login.html
|       |   |-- manage_admin.html
|       |   |-- master.html
|       |   `-- temp.html
|       |-- auth
|       |   |-- login.html
|       |   |-- register.html
|       |   |-- reset_password_request.html
|       |   `-- reset_token.html
|       |-- client
|       |   |-- edit_profile.html
|       |   |-- job_board.html
|       |   |-- job_detail.html
|       |   |-- resume_status.html
|       |   `-- upload_resume_details.html
|       |-- custom
|       |   |-- create.html
|       |   |-- details.html
|       |   |-- edit.html
|       |   |-- email_body.html
|       |   `-- list.html
|       |-- errors
|       |   |-- 403.html
|       |   |-- 404.html
|       |   `-- 500.html
|       |-- layout
|       |   |-- base.html
|       |   |-- base_errors.html
|       |   `-- base_form.html
|       `-- main
|           `-- index.html
|-- README.md
|-- example.env
|-- requirements.txt
|-- run.py
`-- tree.txt

24 directories, 91 files


```
