from flask import Flask, render_template, request, redirect, url_for, session
import pandas as pd
import os
import json

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
    name = request.form["faculty"].strip()
    
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], "timetable.xlsx")
    
    if not os.path.exists(filepath):
        return render_template("result.html", 
                             error="📭 No timetable uploaded yet. Contact HOD.",
                             name=name,
                             has_timetable=False)
    
    try:
        df = pd.read_excel(filepath)
        df["Faculty"] = df["Faculty"].astype(str).str.strip()
        
        # GNITC specific: Handle different name formats
        # Search for partial matches (e.g., "Saleem" finds "Mr. MD. Saleem")
        search_name_lower = name.lower()
        
        # Try different search patterns
        filtered = df[
            df["Faculty"].str.lower().str.contains(search_name_lower) |
            df["Faculty"].str.lower().str.replace(".", "").str.replace(" ", "").str.contains(search_name_lower.replace(" ", ""))
        ]
        
        if len(filtered) == 0:
            # Get suggestions
            all_faculty = df["Faculty"].unique()
            suggestions = []
            for faculty in all_faculty:
                faculty_lower = faculty.lower()
                if (search_name_lower in faculty_lower or 
                    search_name_lower in faculty_lower.replace(".", "").replace(" ", "")):
                    suggestions.append(faculty)
            
            return render_template("result.html",
                                 error=f"❌ No timetable found for '{name}'",
                                 suggestions=suggestions[:5],
                                 name=name,
                                 has_timetable=True)
        
        data = filtered.to_dict(orient="records")
        
        # Add period times for GNITC
        period_times = {
            1: "9:10-10:10",
            2: "10:10-11:10", 
            3: "11:10-12:10",
            4: "12:10-1:10",
            5: "2:00-3:00",
            6: "3:00-4:00"
        }
        
        for row in data:
            row['Time'] = period_times.get(row['Period'], 'N/A')
        
        return render_template("result.html",
                             data=data,
                             name=name,
                             count=len(data),
                             has_timetable=True)
        
    except Exception as e:
        return render_template("result.html",
                             error=f"⚠️ Error: {str(e)}",
                             name=name,
                             has_timetable=True)

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

# Add this route - place it after your other routes
@app.route("/api/faculty_list")
def get_faculty_list():
    """API endpoint to get all faculty names for autocomplete"""
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], "timetable.xlsx")
    
    if not os.path.exists(filepath):
        return json.dumps([])
    
    try:
        df = pd.read_excel(filepath)
        # Get unique faculty names, remove NaN, sort alphabetically
        faculty_list = df['Faculty'].dropna().unique()
        faculty_list = [str(name).strip() for name in faculty_list if str(name).strip()]
        faculty_list.sort()
        
        return json.dumps(faculty_list[:50])  # Limit to 50 names
        
    except Exception as e:
        print(f"Error in faculty_list API: {e}")
        return json.dumps([])


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)