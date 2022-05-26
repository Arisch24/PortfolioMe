from flask import Flask, redirect, url_for

app = Flask(__name__)

@app.route("/")
def home():
    return "Hello, Flask haah"

if __name__ == "__name__":
    app.run()