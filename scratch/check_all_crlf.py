import glob

files = [
    "STUDENT-ANALYSIS/app.py",
    "STUDENT-ANALYSIS/static/js/app.js",
    "STUDENT-ANALYSIS/templates/hod_dashboard.html",
    "STUDENT-ANALYSIS/templates/admin_dashboard.html",
    "STUDENT-ANALYSIS/templates/faculty_dashboard.html",
    "STUDENT-ANALYSIS/templates/student_dashboard.html",
]

for p in files:
    with open(p, "rb") as f:
        data = f.read()
    crcrlf = data.count(b"\r\r\n")
    if crcrlf > 0:
        fixed = data.replace(b"\r\r\n", b"\r\n")
        with open(p, "wb") as f:
            f.write(fixed)
        print(f"Fixed {crcrlf} CRCRLF in {p}")
    else:
        print(f"Clean: {p}")
