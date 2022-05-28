from flask import Flask, redirect, url_for, render_template, request, flash
from forms import EditProfileForm, RegistrationForm, LoginForm

app = Flask(__name__)
app.config["SECRET_KEY"] = "383ed93c7f5c33627fb4bf56036c7493"


@app.route("/")
@app.route("/index")
def home():
    return render_template("client/index.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm()
    if(request.method == "POST"):
        if form.validate_on_submit():
            flash(f"Account created for {form.username.data}!", "success")
        else:
            flash(f"Please fix the errors first.", "failed")

    return render_template("auth/register.html", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if(request.method == "POST"):
        if form.validate_on_submit():
            if form.email.data == 'admin@admin.com' and form.password.data == 'password':
                flash(f"Successful login!", "success")
                return redirect(url_for("home"))
            else:
                flash(f"Login Unsuccessful!", 'failed')
    return render_template("auth/login.html", form=form)


@app.route("/edit-profile", methods=["GET", "POST"])
def edit_profile():
    form = EditProfileForm()
    if(request.method == "POST"):
        if form.validate_on_submit():
            flash(f"Profile updated successfully.", "success")
        else:
            flash(f"There were some errors.", "failure")
    return render_template("client/edit_profile.html", form=form)


if __name__ == "__main__":
    app.run(debug=True)
