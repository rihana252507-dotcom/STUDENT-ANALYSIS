with open('static/js/app.js', encoding='utf-8') as f:
    text = f.read()

import re
print("Occurrences of faculty or advisee or modal in app.js:")
matches = re.findall(r'(function\s+[a-zA-Z0-9_]*faculty[a-zA-Z0-9_]*|function\s+[a-zA-Z0-9_]*student[a-zA-Z0-9_]*|function\s+[a-zA-Z0-9_]*modal[a-zA-Z0-9_]*|function\s+[a-zA-Z0-9_]*profile[a-zA-Z0-9_]*)', text, re.IGNORECASE)
print("Functions:", set(matches))

# Look for where students are rendered in faculty dashboard
for m in re.finditer(r'([^\n]*facultyStudentsTable[^\n]*)', text):
    print("facultyStudentsTable line:", m.group(1))

# Look for student profile inspection modal
for m in re.finditer(r'([^\n]*openStudentDetailModal[^\n]*|[^\n]*inspectStudent[^\n]*)', text):
    print("modal trigger line:", m.group(1)[:120])
