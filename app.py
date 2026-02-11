from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import pandas as pd
import os
import json
import tempfile
import traceback

app = Flask(__name__)
app.secret_key = "test123"  # Change this in production!

# ============= RAILWAY CONFIGURATION =============
# Get port from Railway environment
port = int(os.environ.get("PORT", 5001))

# Handle uploads for Railway vs Local
if os.environ.get('RAILWAY_ENVIRONMENT'):
    # On Railway - use temp directory (files are temporary)
    UPLOAD_FOLDER = tempfile.gettempdir()
    print(f"🚂 Running on Railway - using temp folder: {UPLOAD_FOLDER}")
else:
    # On local computer - use uploads folder
    UPLOAD_FOLDER = "uploads"
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    print(f"💻 Running locally - using folder: {UPLOAD_FOLDER}")

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# ============= YOUR EXISTING CODE (PRESERVED) =============
ADMIN_PASSWORD = "gnit123"

def convert_college_excel(filepath):
    """
    Automatically convert college Excel format to app format
    Supports both formats:
    1. College matrix format (with separate faculty sheet)
    2. Already converted app format
    """
    try:
        # Try to read as app format first (columns: Faculty, Day, Period, Class, Subject)
        df = pd.read_excel(filepath)
        
        # Check if already in app format
        required_columns = ['Faculty', 'Day', 'Period', 'Class', 'Subject']
        if all(col in df.columns for col in required_columns):
            print("✅ File already in app format")
            return df
        
        # If not, try to convert from college format
        print("🔄 Converting from college format...")
        
        # Try to detect college format
        xl = pd.ExcelFile(filepath)
        
        # Check for multiple sheets
        if len(xl.sheet_names) >= 2:
            # College format with Timetable and Faculty sheets
            return convert_from_college_format(filepath)
        else:
            # Single sheet - try to detect matrix format
            return convert_from_matrix_format(filepath)
            
    except Exception as e:
        print(f"❌ Conversion error: {e}")
        return None

def convert_from_college_format(filepath):
    """Convert from GNITC college format (multiple sheets)"""
    try:
        # Read both sheets
        xl = pd.ExcelFile(filepath)
        timetable_df = pd.read_excel(filepath, sheet_name=0)  # Timetable sheet
        
        # ===== 1. CREATE FACULTY MAPPING =====
        # Map subject codes to faculty (simplified mapping)
        mapping = {
            'DM': 'Mrs. Y.Sindhura',
            'BEFA': 'Mr. N. Srikanth', 
            'OS': 'Mr. MD. Saleem',
            'CN': 'Mr. K. Mathivanan',
            'SE': 'Mr. V. Saravanakumar',
            'COI': 'Mr. P.Prasanna',
            'RTRP': 'Mr. G. Vijay Kumar',
            'FSD': 'Mr. V. Saravanakumar'
        }
        
        # ===== 2. PARSE TIMETABLE MATRIX =====
        rows = []
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
        day_codes = ['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT']
        
        # Find the timetable data (skip headers)
        for idx, row in timetable_df.iterrows():
            if len(row) > 0:
                first_cell = str(row.iloc[0]).strip().upper() if pd.notna(row.iloc[0]) else ""
                
                if first_cell in day_codes:
                    day_index = day_codes.index(first_cell)
                    day_name = days[day_index]
                    
                    # Get subjects for periods 1-6
                    for period in range(1, 7):  # Periods 1-6
                        if period < len(row):
                            cell_value = row.iloc[period]
                            if pd.notna(cell_value):
                                subject_code = str(cell_value).strip()
                                
                                if subject_code and subject_code != 'nan':
                                    # Map subject code to faculty
                                    faculty = None
                                    for code, fac in mapping.items():
                                        if code in subject_code:
                                            faculty = fac
                                            break
                                    
                                    if faculty:
                                        rows.append({
                                            'Faculty': faculty,
                                            'Day': day_name,
                                            'Period': period,
                                            'Class': 'CSE-CYBER-II-B',
                                            'Subject': get_subject_name(subject_code)
                                        })
        
        if rows:
            return pd.DataFrame(rows)
        else:
            return None
        
    except Exception as e:
        print(f"Error converting college format: {e}")
        return None

def convert_from_matrix_format(filepath):
    """Convert from simple matrix format (days × periods)"""
    try:
        df = pd.read_excel(filepath)
        rows = []
        
        # Find day column (contains MON, TUE, etc.)
        day_column = None
        for col in df.columns:
            first_val = df[col].iloc[0] if len(df) > 0 else ""
            if pd.notna(first_val):
                if any(day in str(first_val).upper() for day in ['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT']):
                    day_column = col
                    break
        
        if not day_column:
            return None
        
        days_map = {
            'MON': 'Monday', 'TUE': 'Tuesday', 'WED': 'Wednesday',
            'THU': 'Thursday', 'FRI': 'Friday', 'SAT': 'Saturday'
        }
        
        # Faculty mapping
        faculty_mapping = {
            'DM': 'Mrs. Y.Sindhura',
            'BEFA': 'Mr. N. Srikanth',
            'OS': 'Mr. MD. Saleem',
            'CN': 'Mr. K. Mathivanan',
            'SE': 'Mr. V. Saravanakumar',
            'COI': 'Mr. P.Prasanna',
            'RTRP': 'Mr. G. Vijay Kumar',
            'FSD': 'Mr. V. Saravanakumar'
        }
        
        # Process each row
        for idx, row in df.iterrows():
            day_code = str(row[day_column]).strip().upper() if pd.notna(row[day_column]) else ""
            if day_code in days_map:
                day_name = days_map[day_code]
                
                # Check each column for subject codes
                for col in df.columns:
                    if col != day_column:
                        cell_value = row[col]
                        if pd.notna(cell_value):
                            subject_code = str(cell_value).strip()
                            if subject_code and subject_code != 'nan':
                                # Get period from column name or position
                                period = 1  # Default
                                col_str = str(col)
                                if '1' in col_str:
                                    period = 1
                                elif '2' in col_str:
                                    period = 2
                                elif '3' in col_str:
                                    period = 3
                                elif '4' in col_str:
                                    period = 4
                                elif '5' in col_str:
                                    period = 5
                                elif '6' in col_str:
                                    period = 6
                                
                                # Map to faculty
                                for code, faculty in faculty_mapping.items():
                                    if code in subject_code:
                                        rows.append({
                                            'Faculty': faculty,
                                            'Day': day_name,
                                            'Period': period,
                                            'Class': 'CSE-CYBER-II-B',
                                            'Subject': get_subject_name(subject_code)
                                        })
                                        break
        
        if rows:
            return pd.DataFrame(rows)
        else:
            return None
        
    except Exception as e:
        print(f"Error converting matrix format: {e}")
        return None

def get_subject_name(code):
    """Convert subject code to full name"""
    subject_names = {
        'DM': 'Discrete Mathematics',
        'BEFA': 'Business Economics & Financial Analysis',
        'OS': 'Operating Systems',
        'CN': 'Computer Networks',
        'SE': 'Software Engineering',
        'COI': 'Constitution of India',
        'RTRP': 'Real-Time Research Project',
        'FSD': 'Full Stack Development'
    }
    
    for short, full in subject_names.items():
        if short in code:
            return full
    
    return code  # Return as-is if not found

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
        
        # Check if Faculty column exists
        if 'Faculty' not in df.columns:
            return render_template("result.html",
                                 error="❌ Invalid timetable format. Please upload a valid timetable.",
                                 name=name,
                                 has_timetable=True)
        
        df["Faculty"] = df["Faculty"].astype(str).str.strip()
        
        # GNITC specific: Handle different name formats
        # Search for partial matches (e.g., "Saleem" finds "Mr. MD. Saleem")
        search_name_lower = name.lower()
        
        # Try different search patterns
        mask = df["Faculty"].str.lower().str.contains(search_name_lower, na=False)
        
        filtered = df[mask]
        
        if len(filtered) == 0:
            # Get suggestions
            all_faculty = df["Faculty"].unique()
            suggestions = []
            for faculty in all_faculty:
                if pd.notna(faculty):
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
        print(f"Search error: {traceback.format_exc()}")
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
    
    if 'file' not in request.files:
        return "No file selected"
    
    file = request.files['file']
    
    if file.filename == '':
        return "Please choose a file"
    
    # Check file extension
    if not (file.filename.endswith('.xlsx') or file.filename.endswith('.xls')):
        return "Please upload Excel file only (.xlsx or .xls)"
    
    try:
        # Save the file
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], "timetable.xlsx")
        file.save(filepath)
        
        # Read the file to get stats
        df = pd.read_excel(filepath)
        
        # Check if it's already in app format
        required_columns = ['Faculty', 'Day', 'Period', 'Class', 'Subject']
        
        # Check if columns exist - FIXED VERSION
        columns_exist = []
        for col in required_columns:
            columns_exist.append(col in df.columns)
        
        if all(columns_exist):  # This works because it's a list of booleans
            # Already in correct format
            stats = {
                'faculty_count': int(df['Faculty'].nunique()),
                'total_classes': len(df),
                'classes': int(df['Class'].nunique()),
                'subjects': int(df['Subject'].nunique())
            }
            faculty_list = df['Faculty'].dropna().unique()[:10]
            faculty_list = [str(name) for name in faculty_list if pd.notna(name) and str(name).strip()]
        else:
            # Try to auto-convert
            converted_df = convert_college_excel(filepath)
            if converted_df is not None and len(converted_df) > 0:
                # Save the converted version
                converted_df.to_excel(filepath, index=False)
                stats = {
                    'faculty_count': int(converted_df['Faculty'].nunique()),
                    'total_classes': len(converted_df),
                    'classes': int(converted_df['Class'].nunique()),
                    'subjects': int(converted_df['Subject'].nunique())
                }
                faculty_list = converted_df['Faculty'].dropna().unique()[:10]
                faculty_list = [str(name) for name in faculty_list if pd.notna(name) and str(name).strip()]
            else:
                stats = {
                    'faculty_count': 0,
                    'total_classes': len(df),
                    'classes': 0,
                    'subjects': 0
                }
                faculty_list = ['Format not recognized - using basic upload']
        
        return render_template("upload_success.html", 
                             stats=stats,
                             faculty_list=faculty_list)
        
    except Exception as e:
        error_details = traceback.format_exc()
        print(f"Error in upload: {error_details}")
        return f"Error processing file: {str(e)}"

@app.route("/logout")
def logout():
    session.pop("admin", None)
    return redirect("/")

@app.route("/api/faculty_list")
def get_faculty_list():
    """API endpoint to get all faculty names for autocomplete"""
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], "timetable.xlsx")
    
    if not os.path.exists(filepath):
        return json.dumps([])
    
    try:
        df = pd.read_excel(filepath)
        
        # Check if Faculty column exists
        if 'Faculty' not in df.columns:
            return json.dumps([])
        
        # Get unique faculty names, remove NaN, sort alphabetically
        faculty_series = df['Faculty'].dropna()
        faculty_list = []
        
        for name in faculty_series:
            if pd.notna(name):
                faculty_list.append(str(name).strip())
        
        # Remove duplicates by converting to set then back to list
        faculty_list = list(set(faculty_list))
        faculty_list.sort()
        
        return json.dumps(faculty_list[:50])  # Limit to 50 names
        
    except Exception as e:
        print(f"Error in faculty_list API: {e}")
        return json.dumps([])

# ============= RAILWAY COMPATIBILITY =============
@app.route('/health')
def health():
    """Health check endpoint for Railway"""
    return jsonify({"status": "healthy"}), 200

if __name__ == "__main__":
    print(f"🚀 Starting Faculty Scheduler on port {port}")
    print(f"📁 Upload folder: {UPLOAD_FOLDER}")
    print(f"🔑 Admin login: /admin")
    app.run(host="0.0.0.0", port=port, debug=False)