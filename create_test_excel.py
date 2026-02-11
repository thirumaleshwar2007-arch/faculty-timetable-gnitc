import pandas as pd

# Simple test data for GNITC CSE-CYBER
data = {
    'Faculty': [
        'Mr. MD. Saleem',
        'Mr. MD. Saleem', 
        'Mr. MD. Saleem',
        'Mrs. Y.Sindhura',
        'Mrs. Y.Sindhura',
        'Mr. N. Srikanth',
        'Mr. N. Srikanth',
        'Mr. V. Saravanakumar',
        'Mr. V. Saravanakumar',
        'Mr. K. Mathivanan',
        'Mr. P.Prasanna'
    ],
    'Day': [
        'Monday', 'Wednesday', 'Friday',
        'Monday', 'Tuesday',
        'Monday', 'Wednesday',
        'Monday', 'Thursday',
        'Tuesday', 'Monday'
    ],
    'Period': [1, 3, 2, 4, 1, 1, 4, 2, 1, 3, 3],
    'Class': [
        'CSE-CYBER-II-B', 'CSE-CYBER-II-B', 'CSE-CYBER-II-B',
        'CSE-CYBER-II-B', 'CSE-CYBER-II-B',
        'CSE-CYBER-II-B', 'CSE-CYBER-II-B',
        'CSE-CYBER-II-B', 'CSE-CYBER-II-B',
        'CSE-CYBER-II-B', 'CSE-CYBER-II-B'
    ],
    'Subject': [
        'Operating Systems',
        'OS Lab',
        'Operating Systems',
        'Discrete Mathematics',
        'Discrete Mathematics',
        'Business Economics & Financial Analysis',
        'Business Economics & Financial Analysis',
        'Software Engineering',
        'Software Engineering',
        'Computer Networks',
        'Constitution of India'
    ]
}

# Create DataFrame
df = pd.DataFrame(data)

# Save to Excel
df.to_excel('GNITC_Simple_Test.xlsx', index=False)

print("✅ SIMPLE TEST FILE CREATED!")
print("📁 File: GNITC_Simple_Test.xlsx")
print(f"📊 Total classes: {len(df)}")
print(f"👥 Faculty: {df['Faculty'].nunique()}")

print("\n👥 FACULTY IN THIS FILE:")
for faculty in sorted(df['Faculty'].unique()):
    count = len(df[df['Faculty'] == faculty])
    print(f"  • {faculty} ({count} classes)")

print("\n🔍 TEST THESE SEARCHES:")
print("  • 'Saleem' - Should show 3 classes")
print("  • 'Sindhura' - Should show 2 classes") 
print("  • 'Srikanth' - Should show 2 classes")