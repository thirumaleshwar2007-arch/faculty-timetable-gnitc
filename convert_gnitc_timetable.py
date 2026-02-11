import pandas as pd
import json

# Your timetable data from the image
# Monday to Saturday, Periods 1-4
timetable_matrix = {
    'Monday': ['BEFA', 'SE', 'COI', 'DM'],
    'Tuesday': ['DM', 'SE', 'RTRP/CN', 'FSD/RTRP'],
    'Wednesday': ['OS', 'CN', 'FSD Lab(Batch-1) & RTRP (Batch-2)', 'BEFA'],
    'Thursday': ['SE', 'BEFA', 'DM', 'OS'],
    'Friday': ['CN', 'BEFA', 'FSD Lab(Batch-2) & RTRP (Batch-1)', 'DM'],
    'Saturday': ['OS', 'CN', 'COI', 'DM']
}

# Faculty mapping from your table
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

# Full subject names
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

# Class info
class_name = "CSE-CYBER-II-B"
room_no = "RD026"

# Convert matrix to rows
rows = []

for day, subjects in timetable_matrix.items():
    for period_idx, subject_code in enumerate(subjects, start=1):
        # Handle combined subjects (like "RTRP/CN")
        if '/' in subject_code:
            # Split combined subjects
            sub_codes = [s.strip() for s in subject_code.split('/')]
            for sub_code in sub_codes:
                if sub_code in faculty_mapping:
                    rows.append({
                        'Faculty': faculty_mapping[sub_code],
                        'Day': day,
                        'Period': period_idx,
                        'Class': class_name,
                        'Subject': subject_names.get(sub_code, sub_code),
                        'Room': room_no
                    })
        # Handle lab sessions
        elif 'Lab' in subject_code or 'Batch' in subject_code:
            # Extract subject code (e.g., "FSD" from "FSD Lab(Batch-1)")
            for code in faculty_mapping.keys():
                if code in subject_code:
                    rows.append({
                        'Faculty': faculty_mapping[code],
                        'Day': day,
                        'Period': period_idx,
                        'Class': f"{class_name} ({subject_code})",
                        'Subject': subject_names.get(code, code),
                        'Room': room_no
                    })
                    break
        # Normal subject
        else:
            if subject_code in faculty_mapping:
                rows.append({
                    'Faculty': faculty_mapping[subject_code],
                    'Day': day,
                    'Period': period_idx,
                    'Class': class_name,
                    'Subject': subject_names.get(subject_code, subject_code),
                    'Room': room_no
                })

# Create DataFrame
df = pd.DataFrame(rows)

# Save to Excel
output_file = 'GNITC_CSE_CYBER_II_B_Timetable.xlsx'
df.to_excel(output_file, index=False)

print("✅ GNITC Timetable Converted Successfully!")
print(f"📁 File: {output_file}")
print(f"📊 Total entries: {len(df)}")
print(f"👥 Faculty members: {df['Faculty'].nunique()}")
print(f"📚 Subjects: {df['Subject'].nunique()}")

# Show sample
print("\n📋 SAMPLE DATA:")
print(df.head(10).to_string(index=False))

# Show faculty list
print("\n👥 FACULTY LIST:")
for faculty in sorted(df['Faculty'].unique()):
    count = len(df[df['Faculty'] == faculty])
    print(f"  • {faculty} ({count} classes)")