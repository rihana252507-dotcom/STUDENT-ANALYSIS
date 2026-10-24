import os
import sys

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Check if openpyxl import is present
if 'import openpyxl' not in content:
    content = content.replace(
        'import io\n',
        'import io\nimport datetime\nimport openpyxl\nfrom openpyxl.styles import Font, PatternFill, Alignment, Border, Side\nfrom openpyxl.utils import get_column_letter\n'
    )
    print("Added openpyxl & datetime imports")

# 2. Remove _old_get_admin_faculty
old_func_start = "def _old_get_admin_faculty():"
if old_func_start in content:
    # Find start and end of that function
    idx1 = content.find(old_func_start)
    idx2 = content.find("@app.route(\"/api/faculty\", methods=[\"POST\"])", idx1)
    if idx1 != -1 and idx2 != -1:
        content = content[:idx1] + content[idx2:]
        print("Removed _old_get_admin_faculty")

# 3. Find if __name__ == "__main__": block
runner_block = """# ==============================================================================
# RUNNER
# ==============================================================================

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"\\n========================================================")
    print(f" CampusIQ \u2014 AI-Powered Student Analytics & Success Platform ")
    print(f" Full-Stack Single-Project Application Running ")
    print(f" URL: http://127.0.0.1:{port}")
    print(f"========================================================\\n")
    app.run(host="0.0.0.0", port=port, debug=True)"""

# Check if runner block is in content and not at the end
if 'if __name__ == "__main__":' in content:
    idx_runner = content.find('if __name__ == "__main__":')
    # Check if there are @app.route after this
    if '@app.route' in content[idx_runner:]:
        print("Found runner before some routes, extracting runner...")
        # Find start of runner section
        r_start = content.rfind('# RUNNER', 0, idx_runner)
        if r_start == -1:
            r_start = idx_runner
        else:
            # find preceding comment line
            c_line = content.rfind('# ==', 0, r_start)
            if c_line != -1:
                r_start = c_line
        
        # Find end of app.run block
        r_end = content.find('app.run(', idx_runner)
        r_end = content.find('\n', r_end) + 1
        
        extracted_runner = content[r_start:r_end].strip()
        content = content[:r_start] + content[r_end:]
        print("Extracted runner block, will append at end")
    else:
        extracted_runner = None
else:
    extracted_runner = None

# New HOD export endpoints to add
hod_export_endpoints = '''

# ==============================================================================
# HOD EXPORT REPORT ENDPOINTS (CSV & EXCEL .XLSX)
# ==============================================================================

def _sanitize_csv_cell(val):
    """Sanitizes cell values to prevent CSV/Excel Formula Injection vulnerabilities."""
    if val is None:
        return ""
    if isinstance(val, (int, float)) and not isinstance(val, bool):
        return val
    s = str(val).strip()
    if s and s[0] in ("=", "+", "-", "@", "\\t", "\\r"):
        return "'" + s
    return s


def _style_excel_sheet(ws, title_text, columns):
    """Applies Enterprise Blue + Teal styling and auto column widths to an openpyxl worksheet."""
    # Title row
    ws.insert_rows(1)
    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=len(columns))
    title_cell = ws.cell(row=1, column=1, value=title_text)
    title_cell.font = Font(name="Calibri", size=14, bold=True, color="FFFFFF")
    title_cell.fill = PatternFill(start_color="123B66", end_color="123B66", fill_type="solid")
    title_cell.alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[1].height = 28

    # Subtitle / Generated info
    ws.insert_rows(2)
    ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=len(columns))
    sub_cell = ws.cell(row=2, column=1, value=f"Generated on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Confidential CampusIQ Institutional Report")
    sub_cell.font = Font(name="Calibri", size=9, italic=True, color="5B6B82")
    sub_cell.fill = PatternFill(start_color="F4F7FB", end_color="F4F7FB", fill_type="solid")
    sub_cell.alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[2].height = 18

    # Table Header row (now row 4 because of empty row 3)
    ws.insert_rows(3)
    ws.row_dimensions[3].height = 6

    header_row = 4
    ws.row_dimensions[header_row].height = 24
    header_fill = PatternFill(start_color="123B66", end_color="123B66", fill_type="solid")
    header_font = Font(name="Calibri", size=10, bold=True, color="FFFFFF")
    thin_border = Border(
        left=Side(style='thin', color='DCE4EE'),
        right=Side(style='thin', color='DCE4EE'),
        top=Side(style='thin', color='DCE4EE'),
        bottom=Side(style='thin', color='DCE4EE')
    )

    for col_idx, col_name in enumerate(columns, 1):
        cell = ws.cell(row=header_row, column=col_idx, value=col_name)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

    # Style data rows
    data_font = Font(name="Calibri", size=10, color="172B4D")
    alt_fill = PatternFill(start_color="F8FBFF", end_color="F8FBFF", fill_type="solid")
    white_fill = PatternFill(start_color="FFFFFF", end_color="FFFFFF", fill_type="solid")

    for row_idx in range(header_row + 1, ws.max_row + 1):
        ws.row_dimensions[row_idx].height = 20
        row_fill = alt_fill if row_idx % 2 == 0 else white_fill
        for col_idx in range(1, len(columns) + 1):
            cell = ws.cell(row=row_idx, column=col_idx)
            cell.font = data_font
            cell.fill = row_fill
            cell.border = thin_border
            if isinstance(cell.value, (int, float)):
                cell.alignment = Alignment(horizontal="right", vertical="center")
            else:
                cell.alignment = Alignment(horizontal="left", vertical="center")

    # Auto-adjust column widths
    for col_idx, col_name in enumerate(columns, 1):
        max_len = len(str(col_name))
        for row in range(header_row, ws.max_row + 1):
            val = ws.cell(row=row, column=col_idx).value
            if val is not None:
                max_len = max(max_len, len(str(val)))
        col_letter = get_column_letter(col_idx)
        ws.column_dimensions[col_letter].width = min(max(max_len + 4, 12), 40)


@app.route("/api/hod/export/students/csv", methods=["GET"])
@login_required
@role_required("hod")
def hod_export_students_csv():
    """Exports CSV roster of students strictly filtered to authenticated HOD's department."""
    current_user = get_current_user()
    dept_code = (current_user.get("department") or session.get("department") or "").strip().upper()
    if not dept_code:
        return jsonify({"error": "Forbidden", "message": "No department assigned"}), 403

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT student_id, name, department, semester, section, mentor_name,
               attendance_pct, cgpa, academic_marks_pct, backlogs,
               success_score, risk_level
        FROM students
        WHERE department = ? COLLATE NOCASE
        ORDER BY name ASC
    """, (dept_code,))
    students = [dict(r) for r in cursor.fetchall()]

    # Fetch active interventions to populate intervention status
    cursor.execute("SELECT student_id, status FROM interventions")
    intv_map = {}
    for row in cursor.fetchall():
        s_id = row["student_id"]
        if s_id not in intv_map or row["status"] in ("In Progress", "Assigned", "Active"):
            intv_map[s_id] = row["status"]
    conn.close()

    output = io.StringIO()
    writer = csv.writer(output)
    headers = [
        "Student ID", "Full Name", "Department", "Semester", "Section", "Faculty Advisor",
        "Attendance (%)", "CGPA", "Exam Marks (%)", "Active Backlogs",
        "Success Score", "Risk Level", "Intervention Status"
    ]
    writer.writerow(headers)

    for s in students:
        s_id = s["student_id"]
        status = intv_map.get(s_id, "None")
        writer.writerow([
            _sanitize_csv_cell(s["student_id"]),
            _sanitize_csv_cell(s["name"]),
            _sanitize_csv_cell(s["department"]),
            _sanitize_csv_cell(s.get("semester", "")),
            _sanitize_csv_cell(s.get("section", "")),
            _sanitize_csv_cell(s.get("mentor_name", "Unassigned")),
            s.get("attendance_pct", 0),
            s.get("cgpa", 0.0),
            s.get("academic_marks_pct", 0),
            s.get("backlogs", 0),
            s.get("success_score", 0),
            _sanitize_csv_cell(s.get("risk_level", "Low")),
            _sanitize_csv_cell(status)
        ])

    today_str = datetime.date.today().strftime("%Y-%m-%d")
    filename = f"{dept_code}_Student_Report_{today_str}.csv"
    return Response(
        output.getvalue(),
        mimetype="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )


@app.route("/api/hod/export/students/xlsx", methods=["GET"])
@login_required
@role_required("hod")
def hod_export_students_xlsx():
    """Exports formatted Excel (.xlsx) roster of students strictly filtered to authenticated HOD's department."""
    current_user = get_current_user()
    dept_code = (current_user.get("department") or session.get("department") or "").strip().upper()
    if not dept_code:
        return jsonify({"error": "Forbidden", "message": "No department assigned"}), 403

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT student_id, name, department, semester, section, mentor_name,
               attendance_pct, cgpa, academic_marks_pct, backlogs,
               success_score, risk_level
        FROM students
        WHERE department = ? COLLATE NOCASE
        ORDER BY name ASC
    """, (dept_code,))
    students = [dict(r) for r in cursor.fetchall()]

    cursor.execute("SELECT student_id, status FROM interventions")
    intv_map = {}
    for row in cursor.fetchall():
        s_id = row["student_id"]
        if s_id not in intv_map or row["status"] in ("In Progress", "Assigned", "Active"):
            intv_map[s_id] = row["status"]
    conn.close()

    headers = [
        "Student ID", "Full Name", "Department", "Semester", "Section", "Faculty Advisor",
        "Attendance (%)", "CGPA", "Exam Marks (%)", "Active Backlogs",
        "Success Score", "Risk Level", "Intervention Status"
    ]

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = f"{dept_code} Students"

    for s in students:
        s_id = s["student_id"]
        status = intv_map.get(s_id, "None")
        ws.append([
            _sanitize_csv_cell(s["student_id"]),
            _sanitize_csv_cell(s["name"]),
            _sanitize_csv_cell(s["department"]),
            _sanitize_csv_cell(s.get("semester", "")),
            _sanitize_csv_cell(s.get("section", "")),
            _sanitize_csv_cell(s.get("mentor_name", "Unassigned")),
            s.get("attendance_pct", 0),
            s.get("cgpa", 0.0),
            s.get("academic_marks_pct", 0),
            s.get("backlogs", 0),
            s.get("success_score", 0),
            _sanitize_csv_cell(s.get("risk_level", "Low")),
            _sanitize_csv_cell(status)
        ])

    _style_excel_sheet(ws, f"{dept_code} Department - Student Cohort Performance & Risk Report", headers)

    out = io.BytesIO()
    wb.save(out)
    out.seek(0)
    today_str = datetime.date.today().strftime("%Y-%m-%d")
    filename = f"{dept_code}_Student_Report_{today_str}.xlsx"
    return Response(
        out.getvalue(),
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )


@app.route("/api/hod/export/faculty/csv", methods=["GET"])
@login_required
@role_required("hod")
def hod_export_faculty_csv():
    """Exports CSV directory of faculty members in the authenticated HOD's department."""
    current_user = get_current_user()
    dept_code = (current_user.get("department") or session.get("department") or "").strip().upper()
    if not dept_code:
        return jsonify({"error": "Forbidden", "message": "No department assigned"}), 403

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT faculty_id, name, email, phone, department, designation, specialization, courses_count
        FROM faculty
        WHERE department = ? COLLATE NOCASE
        ORDER BY name ASC
    """, (dept_code,))
    faculty = [dict(r) for r in cursor.fetchall()]

    for f in faculty:
        cursor.execute("SELECT COUNT(*) as cnt FROM students WHERE faculty_id = ? OR department = ?", (f["faculty_id"], f["department"]))
        f["advisee_count"] = cursor.fetchone()["cnt"]
    conn.close()

    output = io.StringIO()
    writer = csv.writer(output)
    headers = [
        "Faculty ID", "Full Name", "Designation", "Department", "Email Address", "Phone",
        "Specialization", "Courses Count", "Assigned Advisees", "Attendance Tracking Status"
    ]
    writer.writerow(headers)

    for f in faculty:
        writer.writerow([
            _sanitize_csv_cell(f["faculty_id"]),
            _sanitize_csv_cell(f["name"]),
            _sanitize_csv_cell(f.get("designation", "Faculty Mentor")),
            _sanitize_csv_cell(f["department"]),
            _sanitize_csv_cell(f.get("email", "")),
            _sanitize_csv_cell(f.get("phone", "")),
            _sanitize_csv_cell(f.get("specialization", "General")),
            f.get("courses_count", 0),
            f.get("advisee_count", 0),
            "Attendance tracking not active in current system"
        ])

    today_str = datetime.date.today().strftime("%Y-%m-%d")
    filename = f"{dept_code}_Faculty_Report_{today_str}.csv"
    return Response(
        output.getvalue(),
        mimetype="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )


@app.route("/api/hod/export/faculty/xlsx", methods=["GET"])
@login_required
@role_required("hod")
def hod_export_faculty_xlsx():
    """Exports formatted Excel (.xlsx) directory of faculty members in the authenticated HOD's department."""
    current_user = get_current_user()
    dept_code = (current_user.get("department") or session.get("department") or "").strip().upper()
    if not dept_code:
        return jsonify({"error": "Forbidden", "message": "No department assigned"}), 403

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT faculty_id, name, email, phone, department, designation, specialization, courses_count
        FROM faculty
        WHERE department = ? COLLATE NOCASE
        ORDER BY name ASC
    """, (dept_code,))
    faculty = [dict(r) for r in cursor.fetchall()]

    for f in faculty:
        cursor.execute("SELECT COUNT(*) as cnt FROM students WHERE faculty_id = ? OR department = ?", (f["faculty_id"], f["department"]))
        f["advisee_count"] = cursor.fetchone()["cnt"]
    conn.close()

    headers = [
        "Faculty ID", "Full Name", "Designation", "Department", "Email Address", "Phone",
        "Specialization", "Courses Count", "Assigned Advisees", "Attendance Tracking Status"
    ]

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = f"{dept_code} Faculty"

    for f in faculty:
        ws.append([
            _sanitize_csv_cell(f["faculty_id"]),
            _sanitize_csv_cell(f["name"]),
            _sanitize_csv_cell(f.get("designation", "Faculty Mentor")),
            _sanitize_csv_cell(f["department"]),
            _sanitize_csv_cell(f.get("email", "")),
            _sanitize_csv_cell(f.get("phone", "")),
            _sanitize_csv_cell(f.get("specialization", "General")),
            f.get("courses_count", 0),
            f.get("advisee_count", 0),
            "Attendance tracking not active in current system"
        ])

    _style_excel_sheet(ws, f"{dept_code} Department - Faculty Directory & Workload Report", headers)

    out = io.BytesIO()
    wb.save(out)
    out.seek(0)
    today_str = datetime.date.today().strftime("%Y-%m-%d")
    filename = f"{dept_code}_Faculty_Report_{today_str}.xlsx"
    return Response(
        out.getvalue(),
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )


@app.route("/api/hod/export/summary/csv", methods=["GET"])
@login_required
@role_required("hod")
def hod_export_summary_csv():
    """Exports departmental executive summary KPIs in CSV format."""
    current_user = get_current_user()
    dept_code = (current_user.get("department") or session.get("department") or "").strip().upper()
    if not dept_code:
        return jsonify({"error": "Forbidden", "message": "No department assigned"}), 403

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM departments WHERE code = ? COLLATE NOCASE", (dept_code,))
    dept_row = cursor.fetchone()
    dept_name = dept_row["name"] if dept_row else dept_code
    hod_name = dept_row["hod_name"] if dept_row else current_user.get("name", "")

    cursor.execute("""
        SELECT 
            COUNT(*) as total_students,
            AVG(CASE WHEN cgpa IS NOT NULL THEN cgpa END) as avg_cgpa,
            AVG(CASE WHEN attendance_pct IS NOT NULL THEN attendance_pct END) as avg_attendance,
            AVG(CASE WHEN academic_marks_pct IS NOT NULL THEN academic_marks_pct END) as avg_marks,
            AVG(CASE WHEN success_score IS NOT NULL THEN success_score END) as avg_success_score,
            SUM(CASE WHEN backlogs > 0 THEN backlogs ELSE 0 END) as total_backlogs,
            SUM(CASE WHEN LOWER(risk_level) = 'high' THEN 1 ELSE 0 END) as high_risk_count,
            SUM(CASE WHEN LOWER(risk_level) = 'medium' THEN 1 ELSE 0 END) as med_risk_count,
            SUM(CASE WHEN LOWER(risk_level) = 'low' THEN 1 ELSE 0 END) as low_risk_count
        FROM students
        WHERE department = ? COLLATE NOCASE
    """, (dept_code,))
    stats = dict(cursor.fetchone())

    cursor.execute("SELECT COUNT(*) as cnt FROM faculty WHERE department = ? COLLATE NOCASE", (dept_code,))
    total_faculty = cursor.fetchone()["cnt"]

    cursor.execute("""
        SELECT COUNT(*) as total_intv,
               SUM(CASE WHEN status IN ('Active', 'In Progress', 'Assigned') THEN 1 ELSE 0 END) as active_intv,
               SUM(CASE WHEN status = 'Completed' THEN 1 ELSE 0 END) as completed_intv
        FROM interventions
        WHERE student_id IN (SELECT student_id FROM students WHERE department = ? COLLATE NOCASE)
    """, (dept_code,))
    intv_stats = dict(cursor.fetchone())
    conn.close()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Metric Category", "Metric Name", "Value", "Operational Description"])

    metrics_rows = [
        ("Institutional Profile", "Department Code", dept_code, "Official department acronym"),
        ("Institutional Profile", "Department Name", dept_name, "Full department name"),
        ("Institutional Profile", "Head of Department (HOD)", hod_name, "Designated department administrator"),
        ("Institutional Profile", "Report Date", datetime.date.today().strftime("%Y-%m-%d"), "Snapshot generation date"),
        ("Student Cohort", "Total Enrolled Students", stats.get("total_students", 0), "Total student records in department"),
        ("Student Risk", "High Risk Students", stats.get("high_risk_count", 0) or 0, "Attendance < 75% or CGPA < 6.0 or severe backlogs"),
        ("Student Risk", "Medium Risk Students", stats.get("med_risk_count", 0) or 0, "Moderate academic or attendance risk flags"),
        ("Student Risk", "Low Risk Students", stats.get("low_risk_count", 0) or 0, "Good standing across attendance and academics"),
        ("Academic Performance", "Average Attendance (%)", round(stats.get("avg_attendance") or 0.0, 1), "Mean class attendance percentage"),
        ("Academic Performance", "Average CGPA", round(stats.get("avg_cgpa") or 0.0, 2), "Cumulative Grade Point Average across cohort"),
        ("Academic Performance", "Average Exam Marks (%)", round(stats.get("avg_marks") or 0.0, 1), "Mean internal and external marks"),
        ("Academic Performance", "Average Success Score", round(stats.get("avg_success_score") or 0.0, 1), "Weighted predictive success index (0-100)"),
        ("Academic Performance", "Total Active Backlogs", stats.get("total_backlogs", 0) or 0, "Sum of active backlogs across all students"),
        ("Faculty & Advising", "Total Department Faculty", total_faculty, "Faculty members allocated to department"),
        ("Faculty & Advising", "Faculty Attendance Tracking", "Data not available", "Faculty attendance module is not tracked in system"),
        ("Interventions", "Total Interventions", intv_stats.get("total_intv", 0) or 0, "Cumulative logged interventions"),
        ("Interventions", "Active / Pending Interventions", intv_stats.get("active_intv", 0) or 0, "Interventions currently in progress"),
        ("Interventions", "Completed Interventions", intv_stats.get("completed_intv", 0) or 0, "Interventions successfully closed")
    ]

    for cat, name, val, desc in metrics_rows:
        writer.writerow([
            _sanitize_csv_cell(cat),
            _sanitize_csv_cell(name),
            val if isinstance(val, (int, float)) else _sanitize_csv_cell(val),
            _sanitize_csv_cell(desc)
        ])

    today_str = datetime.date.today().strftime("%Y-%m-%d")
    filename = f"{dept_code}_Department_Summary_{today_str}.csv"
    return Response(
        output.getvalue(),
        mimetype="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )


@app.route("/api/hod/export/summary/xlsx", methods=["GET"])
@login_required
@role_required("hod")
def hod_export_summary_xlsx():
    """Exports departmental executive summary KPIs in formatted Excel (.xlsx) format."""
    current_user = get_current_user()
    dept_code = (current_user.get("department") or session.get("department") or "").strip().upper()
    if not dept_code:
        return jsonify({"error": "Forbidden", "message": "No department assigned"}), 403

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM departments WHERE code = ? COLLATE NOCASE", (dept_code,))
    dept_row = cursor.fetchone()
    dept_name = dept_row["name"] if dept_row else dept_code
    hod_name = dept_row["hod_name"] if dept_row else current_user.get("name", "")

    cursor.execute("""
        SELECT 
            COUNT(*) as total_students,
            AVG(CASE WHEN cgpa IS NOT NULL THEN cgpa END) as avg_cgpa,
            AVG(CASE WHEN attendance_pct IS NOT NULL THEN attendance_pct END) as avg_attendance,
            AVG(CASE WHEN academic_marks_pct IS NOT NULL THEN academic_marks_pct END) as avg_marks,
            AVG(CASE WHEN success_score IS NOT NULL THEN success_score END) as avg_success_score,
            SUM(CASE WHEN backlogs > 0 THEN backlogs ELSE 0 END) as total_backlogs,
            SUM(CASE WHEN LOWER(risk_level) = 'high' THEN 1 ELSE 0 END) as high_risk_count,
            SUM(CASE WHEN LOWER(risk_level) = 'medium' THEN 1 ELSE 0 END) as med_risk_count,
            SUM(CASE WHEN LOWER(risk_level) = 'low' THEN 1 ELSE 0 END) as low_risk_count
        FROM students
        WHERE department = ? COLLATE NOCASE
    """, (dept_code,))
    stats = dict(cursor.fetchone())

    cursor.execute("SELECT COUNT(*) as cnt FROM faculty WHERE department = ? COLLATE NOCASE", (dept_code,))
    total_faculty = cursor.fetchone()["cnt"]

    cursor.execute("""
        SELECT COUNT(*) as total_intv,
               SUM(CASE WHEN status IN ('Active', 'In Progress', 'Assigned') THEN 1 ELSE 0 END) as active_intv,
               SUM(CASE WHEN status = 'Completed' THEN 1 ELSE 0 END) as completed_intv
        FROM interventions
        WHERE student_id IN (SELECT student_id FROM students WHERE department = ? COLLATE NOCASE)
    """, (dept_code,))
    intv_stats = dict(cursor.fetchone())
    conn.close()

    headers = ["Metric Category", "Metric Name", "Value", "Operational Description"]

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = f"{dept_code} Executive Summary"

    metrics_rows = [
        ("Institutional Profile", "Department Code", dept_code, "Official department acronym"),
        ("Institutional Profile", "Department Name", dept_name, "Full department name"),
        ("Institutional Profile", "Head of Department (HOD)", hod_name, "Designated department administrator"),
        ("Institutional Profile", "Report Date", datetime.date.today().strftime("%Y-%m-%d"), "Snapshot generation date"),
        ("Student Cohort", "Total Enrolled Students", stats.get("total_students", 0), "Total student records in department"),
        ("Student Risk", "High Risk Students", stats.get("high_risk_count", 0) or 0, "Attendance < 75% or CGPA < 6.0 or severe backlogs"),
        ("Student Risk", "Medium Risk Students", stats.get("med_risk_count", 0) or 0, "Moderate academic or attendance risk flags"),
        ("Student Risk", "Low Risk Students", stats.get("low_risk_count", 0) or 0, "Good standing across attendance and academics"),
        ("Academic Performance", "Average Attendance (%)", round(stats.get("avg_attendance") or 0.0, 1), "Mean class attendance percentage"),
        ("Academic Performance", "Average CGPA", round(stats.get("avg_cgpa") or 0.0, 2), "Cumulative Grade Point Average across cohort"),
        ("Academic Performance", "Average Exam Marks (%)", round(stats.get("avg_marks") or 0.0, 1), "Mean internal and external marks"),
        ("Academic Performance", "Average Success Score", round(stats.get("avg_success_score") or 0.0, 1), "Weighted predictive success index (0-100)"),
        ("Academic Performance", "Total Active Backlogs", stats.get("total_backlogs", 0) or 0, "Sum of active backlogs across all students"),
        ("Faculty & Advising", "Total Department Faculty", total_faculty, "Faculty members allocated to department"),
        ("Faculty & Advising", "Faculty Attendance Tracking", "Data not available", "Faculty attendance module is not tracked in system"),
        ("Interventions", "Total Interventions", intv_stats.get("total_intv", 0) or 0, "Cumulative logged interventions"),
        ("Interventions", "Active / Pending Interventions", intv_stats.get("active_intv", 0) or 0, "Interventions currently in progress"),
        ("Interventions", "Completed Interventions", intv_stats.get("completed_intv", 0) or 0, "Interventions successfully closed")
    ]

    for cat, name, val, desc in metrics_rows:
        ws.append([
            _sanitize_csv_cell(cat),
            _sanitize_csv_cell(name),
            val if isinstance(val, (int, float)) else _sanitize_csv_cell(val),
            _sanitize_csv_cell(desc)
        ])

    _style_excel_sheet(ws, f"{dept_code} Department - Executive Summary & Institutional Metrics", headers)

    out = io.BytesIO()
    wb.save(out)
    out.seek(0)
    today_str = datetime.date.today().strftime("%Y-%m-%d")
    filename = f"{dept_code}_Department_Summary_{today_str}.xlsx"
    return Response(
        out.getvalue(),
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )
'''

# Append export endpoints before runner or at the end
if extracted_runner:
    final_content = content.rstrip() + "\n\n" + hod_export_endpoints + "\n\n" + extracted_runner + "\n"
else:
    final_content = content.rstrip() + "\n\n" + hod_export_endpoints + "\n"

# Verify syntax before writing
import ast
try:
    ast.parse(final_content)
    print("AST verification passed!")
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(final_content)
    print("SUCCESS: app.py successfully updated and written!")
except Exception as e:
    print(f"ERROR validating AST: {e}")
