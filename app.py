from flask import Flask, render_template, request, redirect, url_for, session
import pandas as pd
import os

app = Flask(__name__)
app.secret_key = "test123"

UPLOAD_FOLDER = "uploads"
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
ADMIN_PASSWORD = "gnit123"

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/search", methods=["POST"])
def search():
    name = request.form["faculty"]
    return f"Searching for: {name} (Feature will work after upload)"

@app.route("/admin")
def admin():
    return render_template("admin_login.html")

@app.route("/admin_login", methods=["POST"])
def admin_login():
    password = request.form["password"]
    if password == ADMIN_PASSWORD:
        session["admin"] = True
        return redirect("/dashboard")
    return "Wrong password. <a href='/admin'>Try again</a>"

@app.route("/dashboard")
def dashboard():
    if not session.get("admin"):
        return redirect("/admin")
    return render_template("dashboard.html")

@app.route("/upload_page")
def upload_page():
    if not session.get("admin"):
        return redirect("/admin")
    return render_template("upload.html")

@app.route("/upload", methods=["POST"])
def upload():
    if not session.get("admin"):
        return redirect("/admin")
    
    file = request.files["file"]
    if file.filename == "":
        return "No file selected"
    
    # Save file
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], "timetable.xlsx")
    file.save(filepath)
    
    return "✅ File uploaded! <a href='/'>Go to Home</a>"

@app.route("/logout")
def logout():
    session.pop("admin", None)
    return redirect("/")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)