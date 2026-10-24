import sys

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Shared helpers block to put at line ~900 (before export routes)
shared_helpers_code = '''

# ==============================================================================
# UNIFIED EXPORT HELPERS (EXCEL & CSV COMPLIANT WITH BOM & FORMULA PROTECTION)
# ==============================================================================

def _sanitize_csv_cell(val):
    """
    Sanitizes cell values to prevent CSV/Excel Formula Injection vulnerabilities
    while accurately preserving valid numeric values and ordinary text.
    """
    if val is None:
        return ""
    if isinstance(val, bool):
        return "Yes" if val else "No"
    if isinstance(val, (int, float)):
        return val
    s = str(val).strip()
    if not s:
        return ""
    try:
        float(s)
        return s
    except ValueError:
        pass
    if s[0] in ("=", "+", "-", "@", "\\t", "\\r"):
        return "'" + s
    return s


def _make_csv_response(output_str, filename):
    """
    Wraps CSV string output in a UTF-8 BOM response (\\ufeff) for native,
    flawless Microsoft Excel compatibility across Windows and macOS.
    """
    bom_content = "\\ufeff" + output_str
    return Response(
        bom_content,
        mimetype="text/csv; charset=utf-8",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Cache-Control": "no-cache, no-store, must-revalidate"
        }
    )


def _make_excel_response(wb, filename):
    """Saves openpyxl Workbook to memory BytesIO and returns streaming Excel response."""
    out = io.BytesIO()
    wb.save(out)
    out.seek(0)
    return Response(
        out.getvalue(),
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Cache-Control": "no-cache, no-store, must-revalidate"
        }
    )


def _style_excel_sheet(ws, title_text, columns):
    """
    Applies Enterprise Blue + Teal styling, text formatting on identifiers,
    and automatic column widths to an openpyxl worksheet.
    """
    ws.insert_rows(1)
    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=len(columns))
    title_cell = ws.cell(row=1, column=1, value=title_text)
    title_cell.font = Font(name="Calibri", size=14, bold=True, color="FFFFFF")
    title_cell.fill = PatternFill(start_color="123B66", end_color="123B66", fill_type="solid")
    title_cell.alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[1].height = 28

    ws.insert_rows(2)
    ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=len(columns))
    sub_cell = ws.cell(row=2, column=1, value=f"Generated on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Confidential CampusIQ Institutional Report")
    sub_cell.font = Font(name="Calibri", size=9, italic=True, color="5B6B82")
    sub_cell.fill = PatternFill(start_color="F4F7FB", end_color="F4F7FB", fill_type="solid")
    sub_cell.alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[2].height = 18

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
            if isinstance(cell.value, (int, float)) and not isinstance(cell.value, bool):
                cell.alignment = Alignment(horizontal="right", vertical="center")
            else:
                cell.number_format = '@'
                cell.alignment = Alignment(horizontal="left", vertical="center")

    for col_idx, col_name in enumerate(columns, 1):
        max_len = len(str(col_name))
        for row in range(header_row, ws.max_row + 1):
            val = ws.cell(row=row, column=col_idx).value
            if val is not None:
                max_len = max(max_len, len(str(val)))
        col_letter = get_column_letter(col_idx)
        ws.column_dimensions[col_letter].width = min(max(max_len + 4, 12), 40)


def _get_student_cohort_data(current_role, current_user_id, current_dept, dept_filter="ALL", risk_filter="ALL"):
    """Fetches and structures student records according to role and security scope."""
    conn = get_db()
    cursor = conn.cursor()

    if current_role == "hod":
        cursor.execute("SELECT * FROM students WHERE department = ? COLLATE NOCASE ORDER BY name ASC", (current_dept,))
    elif current_role == "faculty":
        cursor.execute("SELECT * FROM students WHERE faculty_id = ? OR department = ? ORDER BY name ASC", (current_user_id, current_dept))
    else:
        cursor.execute("SELECT * FROM students ORDER BY name ASC")

    students = [dict(r) for r in cursor.fetchall()]
    conn.close()

    if current_role == "hod":
        dept_filter = current_dept
    if dept_filter != "ALL":
        students = [s for s in students if (s.get("department") or "").upper() == dept_filter.upper()]
    if risk_filter != "ALL":
        students = [s for s in students if (s.get("risk_level") or "").lower() == risk_filter.lower()]

    today_str = datetime.date.today().strftime("%Y-%m-%d")
    risk_part = f"_{risk_filter.capitalize()}_Risk" if risk_filter != "ALL" else ""
    dept_part = f"_{dept_filter.upper()}" if dept_filter != "ALL" else ""
    filename_base = f"Student_Report{dept_part}{risk_part}_{today_str}"

    headers = [
        "Student ID", "Name", "Email", "Department", "Semester", "Section", "Advisor",
        "CGPA", "Exam Marks %", "Attendance %", "Backlogs", "LMS Weekly Hours",
        "Assignment Rate %", "Aptitude Score", "Tech Skills", "Success Score", "Risk Category"
    ]

    rows = []
    for s in students:
        rows.append([
            _sanitize_csv_cell(s.get("student_id", "")),
            _sanitize_csv_cell(s.get("name", "")),
            _sanitize_csv_cell(s.get("email", "")),
            _sanitize_csv_cell(s.get("department", "")),
            _sanitize_csv_cell(s.get("semester", "")),
            _sanitize_csv_cell(s.get("section", "")),
            _sanitize_csv_cell(s.get("mentor_name", "Unassigned")),
            s.get("cgpa", 0.0),
            s.get("academic_marks_pct", 0),
            s.get("attendance_pct", 0),
            s.get("backlogs", 0),
            s.get("lms_weekly_hours", 0),
            s.get("assignment_completion_pct", 0),
            s.get("placement_aptitude_score", 0),
            s.get("technical_skills_score", 0),
            s.get("success_score", 0),
            _sanitize_csv_cell(s.get("risk_level", "Low"))
        ])

    return headers, rows, filename_base
'''

# New endpoints for /api/export/csv and /api/export/xlsx
updated_student_export_endpoints = '''
@app.route("/api/export/csv", methods=["GET"])
@login_required
def export_csv():
    """Generates and downloads Excel-compatible CSV report with UTF-8 BOM based on caller's role and filters."""
    current_role = session.get("role")
    current_user_id = session.get("user_id")
    current_dept = session.get("department", "")

    if current_role == "student":
        return jsonify({"error": "Forbidden"}), 403

    if current_role == "hod" and not current_dept:
        return jsonify({"error": "Forbidden", "message": "No department assigned"}), 403

    dept = request.args.get("department", "ALL")
    risk = request.args.get("risk_level", "ALL")

    headers, rows, filename_base = _get_student_cohort_data(current_role, current_user_id, current_dept, dept, risk)

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(headers)
    for r in rows:
        writer.writerow(r)

    return _make_csv_response(output.getvalue(), f"{filename_base}.csv")


@app.route("/api/export/xlsx", methods=["GET"])
@login_required
def export_xlsx():
    """Generates and downloads genuine Microsoft Excel (.xlsx) workbook for student cohort records."""
    current_role = session.get("role")
    current_user_id = session.get("user_id")
    current_dept = session.get("department", "")

    if current_role == "student":
        return jsonify({"error": "Forbidden"}), 403

    if current_role == "hod" and not current_dept:
        return jsonify({"error": "Forbidden", "message": "No department assigned"}), 403

    dept = request.args.get("department", "ALL")
    risk = request.args.get("risk_level", "ALL")

    headers, rows, filename_base = _get_student_cohort_data(current_role, current_user_id, current_dept, dept, risk)

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Student Cohort"
    for r in rows:
        ws.append(r)

    title = f"CampusIQ Institutional Student Cohort Performance Report"
    if dept != "ALL":
        title += f" ({dept})"
    if risk != "ALL":
        title += f" - {risk.capitalize()} Risk"

    _style_excel_sheet(ws, title, headers)
    return _make_excel_response(wb, f"{filename_base}.xlsx")


@app.route("/api/interventions/export/csv", methods=["GET"])
@login_required
@role_required("admin", "faculty", "hod")
def export_interventions_csv():
    """Generates and downloads Excel-compatible CSV of student interventions within authorized scope."""
    current_role = session.get("role")
    current_user_id = session.get("user_id")
    current_dept = session.get("department", "")

    conn = get_db()
    cursor = conn.cursor()
    if current_role == "hod":
        cursor.execute("""
            SELECT i.*, s.name as student_name, s.department as student_dept
            FROM interventions i
            JOIN students s ON s.student_id = i.student_id
            WHERE s.department = ? COLLATE NOCASE
            ORDER BY i.id DESC
        """, (current_dept,))
    elif current_role == "faculty":
        cursor.execute("""
            SELECT i.*, s.name as student_name, s.department as student_dept
            FROM interventions i
            JOIN students s ON s.student_id = i.student_id
            WHERE i.faculty_id = ? OR s.department = ?
            ORDER BY i.id DESC
        """, (current_user_id, current_dept))
    else:
        cursor.execute("""
            SELECT i.*, s.name as student_name, s.department as student_dept
            FROM interventions i
            LEFT JOIN students s ON s.student_id = i.student_id
            ORDER BY i.id DESC
        """)

    rows_data = [dict(r) for r in cursor.fetchall()]
    conn.close()

    headers = [
        "Intervention ID", "Student ID", "Student Name", "Department",
        "Faculty Mentor", "Action Type", "Priority", "Title",
        "Instructions & Notes", "Status", "Created Date", "Completed Date"
    ]

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(headers)

    for i in rows_data:
        writer.writerow([
            f"#INT-{i['id']}",
            _sanitize_csv_cell(i.get("student_id", "")),
            _sanitize_csv_cell(i.get("student_name", "")),
            _sanitize_csv_cell(i.get("student_dept", "")),
            _sanitize_csv_cell(i.get("faculty_name", "")),
            _sanitize_csv_cell(i.get("action_type", "")),
            _sanitize_csv_cell(i.get("priority", "Medium")),
            _sanitize_csv_cell(i.get("title", "")),
            _sanitize_csv_cell(i.get("instructions") or i.get("notes") or ""),
            _sanitize_csv_cell(i.get("status", "Assigned")),
            _sanitize_csv_cell(i.get("created_at", "")),
            _sanitize_csv_cell(i.get("completed_at", "") or "In Progress")
        ])

    today_str = datetime.date.today().strftime("%Y-%m-%d")
    dept_prefix = f"{current_dept}_" if current_dept else ""
    filename = f"{dept_prefix}Intervention_Report_{today_str}.csv"
    return _make_csv_response(output.getvalue(), filename)


@app.route("/api/interventions/export/xlsx", methods=["GET"])
@login_required
@role_required("admin", "faculty", "hod")
def export_interventions_xlsx():
    """Generates and downloads genuine Excel (.xlsx) workbook of student interventions within authorized scope."""
    current_role = session.get("role")
    current_user_id = session.get("user_id")
    current_dept = session.get("department", "")

    conn = get_db()
    cursor = conn.cursor()
    if current_role == "hod":
        cursor.execute("""
            SELECT i.*, s.name as student_name, s.department as student_dept
            FROM interventions i
            JOIN students s ON s.student_id = i.student_id
            WHERE s.department = ? COLLATE NOCASE
            ORDER BY i.id DESC
        """, (current_dept,))
    elif current_role == "faculty":
        cursor.execute("""
            SELECT i.*, s.name as student_name, s.department as student_dept
            FROM interventions i
            JOIN students s ON s.student_id = i.student_id
            WHERE i.faculty_id = ? OR s.department = ?
            ORDER BY i.id DESC
        """, (current_user_id, current_dept))
    else:
        cursor.execute("""
            SELECT i.*, s.name as student_name, s.department as student_dept
            FROM interventions i
            LEFT JOIN students s ON s.student_id = i.student_id
            ORDER BY i.id DESC
        """)

    rows_data = [dict(r) for r in cursor.fetchall()]
    conn.close()

    headers = [
        "Intervention ID", "Student ID", "Student Name", "Department",
        "Faculty Mentor", "Action Type", "Priority", "Title",
        "Instructions & Notes", "Status", "Created Date", "Completed Date"
    ]

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Interventions"

    for i in rows_data:
        ws.append([
            f"#INT-{i['id']}",
            _sanitize_csv_cell(i.get("student_id", "")),
            _sanitize_csv_cell(i.get("student_name", "")),
            _sanitize_csv_cell(i.get("student_dept", "")),
            _sanitize_csv_cell(i.get("faculty_name", "")),
            _sanitize_csv_cell(i.get("action_type", "")),
            _sanitize_csv_cell(i.get("priority", "Medium")),
            _sanitize_csv_cell(i.get("title", "")),
            _sanitize_csv_cell(i.get("instructions") or i.get("notes") or ""),
            _sanitize_csv_cell(i.get("status", "Assigned")),
            _sanitize_csv_cell(i.get("created_at", "")),
            _sanitize_csv_cell(i.get("completed_at", "") or "In Progress")
        ])

    _style_excel_sheet(ws, "CampusIQ Student Success Interventions & Advising Log", headers)
    today_str = datetime.date.today().strftime("%Y-%m-%d")
    dept_prefix = f"{current_dept}_" if current_dept else ""
    filename = f"{dept_prefix}Intervention_Report_{today_str}.xlsx"
    return _make_excel_response(wb, filename)


@app.route("/api/faculty/export/csv", methods=["GET"])
@login_required
@role_required("admin", "hod")
def export_faculty_csv():
    """Generates and downloads Excel-compatible CSV directory of faculty members."""
    current_role = session.get("role")
    current_dept = session.get("department", "")

    conn = get_db()
    cursor = conn.cursor()
    if current_role == "hod":
        cursor.execute("SELECT * FROM faculty WHERE department = ? COLLATE NOCASE ORDER BY name ASC", (current_dept,))
    else:
        cursor.execute("SELECT * FROM faculty ORDER BY department ASC, name ASC")
    faculty = [dict(r) for r in cursor.fetchall()]

    for f in faculty:
        cursor.execute("SELECT COUNT(*) as cnt FROM students WHERE faculty_id = ? OR department = ?", (f["faculty_id"], f["department"]))
        f["advisee_count"] = cursor.fetchone()["cnt"]
    conn.close()

    headers = [
        "Faculty ID", "Full Name", "Designation", "Department", "Email Address", "Phone",
        "Specialization", "Courses Count", "Assigned Advisees", "Attendance Tracking Status"
    ]

    output = io.StringIO()
    writer = csv.writer(output)
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
    dept_prefix = f"{current_dept}_" if current_role == "hod" else ""
    filename = f"{dept_prefix}Faculty_Report_{today_str}.csv"
    return _make_csv_response(output.getvalue(), filename)


@app.route("/api/faculty/export/xlsx", methods=["GET"])
@login_required
@role_required("admin", "hod")
def export_faculty_xlsx():
    """Generates and downloads genuine Excel (.xlsx) directory of faculty members."""
    current_role = session.get("role")
    current_dept = session.get("department", "")

    conn = get_db()
    cursor = conn.cursor()
    if current_role == "hod":
        cursor.execute("SELECT * FROM faculty WHERE department = ? COLLATE NOCASE ORDER BY name ASC", (current_dept,))
    else:
        cursor.execute("SELECT * FROM faculty ORDER BY department ASC, name ASC")
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
    ws.title = "Faculty Directory"

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

    _style_excel_sheet(ws, "CampusIQ Institutional Faculty Directory & Workload Report", headers)
    today_str = datetime.date.today().strftime("%Y-%m-%d")
    dept_prefix = f"{current_dept}_" if current_role == "hod" else ""
    filename = f"{dept_prefix}Faculty_Report_{today_str}.xlsx"
    return _make_excel_response(wb, filename)


@app.route("/api/student/transcript/export/csv", methods=["GET"])
@login_required
@role_required("student")
def export_student_transcript_csv():
    """Generates and downloads Excel-compatible CSV of the authenticated student's academic transcript."""
    current_user = get_current_user()
    student_id = session.get("student_id") or current_user["user_id"]

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM academic_records
        WHERE student_id = ? COLLATE NOCASE
        ORDER BY year ASC, semester ASC, course_code ASC
    """, (student_id,))
    records = [dict(r) for r in cursor.fetchall()]
    conn.close()

    headers = [
        "Year", "Semester", "Academic Year", "Course Code", "Course Name",
        "Credits", "Mid 1 Marks", "Mid 2 Marks", "Internal Marks",
        "External Marks", "Total Marks", "Max Marks", "Grade",
        "Attendance (%)", "SGPA", "Status"
    ]

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(headers)

    for r in records:
        writer.writerow([
            r.get("year", 1),
            _sanitize_csv_cell(r.get("semester_label") or r.get("semester", "")),
            _sanitize_csv_cell(r.get("academic_year", "")),
            _sanitize_csv_cell(r.get("course_code", "")),
            _sanitize_csv_cell(r.get("course_name", "")),
            r.get("credits", 0),
            r.get("mid1_marks", 0),
            r.get("mid2_marks", 0),
            r.get("internal_marks", 0),
            r.get("external_marks", 0),
            r.get("total_marks", 0),
            r.get("total_max", 100),
            _sanitize_csv_cell(r.get("grade", "P")),
            r.get("attendance_pct", 0),
            r.get("sgpa", 0.0),
            _sanitize_csv_cell(r.get("status", "Completed"))
        ])

    today_str = datetime.date.today().strftime("%Y-%m-%d")
    filename = f"Student_Transcript_{student_id}_{today_str}.csv"
    return _make_csv_response(output.getvalue(), filename)


@app.route("/api/student/transcript/export/xlsx", methods=["GET"])
@login_required
@role_required("student")
def export_student_transcript_xlsx():
    """Generates and downloads genuine Excel (.xlsx) workbook of the authenticated student's academic transcript."""
    current_user = get_current_user()
    student_id = session.get("student_id") or current_user["user_id"]

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM academic_records
        WHERE student_id = ? COLLATE NOCASE
        ORDER BY year ASC, semester ASC, course_code ASC
    """, (student_id,))
    records = [dict(r) for r in cursor.fetchall()]
    conn.close()

    headers = [
        "Year", "Semester", "Academic Year", "Course Code", "Course Name",
        "Credits", "Mid 1 Marks", "Mid 2 Marks", "Internal Marks",
        "External Marks", "Total Marks", "Max Marks", "Grade",
        "Attendance (%)", "SGPA", "Status"
    ]

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Academic Transcript"

    for r in records:
        ws.append([
            r.get("year", 1),
            _sanitize_csv_cell(r.get("semester_label") or r.get("semester", "")),
            _sanitize_csv_cell(r.get("academic_year", "")),
            _sanitize_csv_cell(r.get("course_code", "")),
            _sanitize_csv_cell(r.get("course_name", "")),
            r.get("credits", 0),
            r.get("mid1_marks", 0),
            r.get("mid2_marks", 0),
            r.get("internal_marks", 0),
            r.get("external_marks", 0),
            r.get("total_marks", 0),
            r.get("total_max", 100),
            _sanitize_csv_cell(r.get("grade", "P")),
            r.get("attendance_pct", 0),
            r.get("sgpa", 0.0),
            _sanitize_csv_cell(r.get("status", "Completed"))
        ])

    _style_excel_sheet(ws, f"Official Student Academic Transcript & Grades ({student_id})", headers)
    today_str = datetime.date.today().strftime("%Y-%m-%d")
    filename = f"Student_Transcript_{student_id}_{today_str}.xlsx"
    return _make_excel_response(wb, filename)
'''

# Replace old /api/export/csv block in app.py
idx_old_export = content.find('@app.route("/api/export/csv", methods=["GET"])')
idx_next_sec = content.find('# ==============================================================================\n# 4. CRUD & EXTENDED MANAGEMENT APIS', idx_old_export)

if idx_old_export != -1 and idx_next_sec != -1:
    new_app_content = (
        content[:idx_old_export]
        + shared_helpers_code
        + "\n\n"
        + updated_student_export_endpoints
        + "\n\n"
        + content[idx_next_sec:]
    )
    print("Replaced /api/export/csv and injected unified helpers and new endpoints")
else:
    print(f"ERROR: could not locate export block indices: {idx_old_export}, {idx_next_sec}")
    sys.exit(1)

# Now, in the lower HOD section, update the CSV responses to use _make_csv_response
# Check if redundant _sanitize_csv_cell or _style_excel_sheet exists lower down
lower_helpers_tag = "# HOD EXPORT REPORT ENDPOINTS (CSV & EXCEL .XLSX)"
idx_lower = new_app_content.find(lower_helpers_tag)
if idx_lower != -1:
    # Remove redundant helper definitions in lower section if any
    old_lower_sanitize = "def _sanitize_csv_cell(val):"
    idx_s = new_app_content.find(old_lower_sanitize, idx_lower)
    idx_first_hod_route = new_app_content.find('@app.route("/api/hod/export/students/csv"', idx_lower)
    if idx_s != -1 and idx_first_hod_route != -1:
        new_app_content = (
            new_app_content[:idx_s]
            + new_app_content[idx_first_hod_route:]
        )
        print("Cleaned up redundant lower helpers before HOD routes")

# Update HOD CSV return statements to use _make_csv_response
# 1. hod_export_students_csv
old_hod_stu_resp = '''    today_str = datetime.date.today().strftime("%Y-%m-%d")
    filename = f"{dept_code}_Student_Report_{today_str}.csv"
    return Response(
        output.getvalue(),
        mimetype="text/csv; charset=utf-8",
        headers={"Content-Disposition": f\'attachment; filename="{filename}"\'}
    )'''
new_hod_stu_resp = '''    today_str = datetime.date.today().strftime("%Y-%m-%d")
    filename = f"{dept_code}_Student_Report_{today_str}.csv"
    return _make_csv_response(output.getvalue(), filename)'''
new_app_content = new_app_content.replace(old_hod_stu_resp, new_hod_stu_resp)

# 2. hod_export_faculty_csv
old_hod_fac_resp = '''    today_str = datetime.date.today().strftime("%Y-%m-%d")
    filename = f"{dept_code}_Faculty_Report_{today_str}.csv"
    return Response(
        output.getvalue(),
        mimetype="text/csv; charset=utf-8",
        headers={"Content-Disposition": f\'attachment; filename="{filename}"\'}
    )'''
new_hod_fac_resp = '''    today_str = datetime.date.today().strftime("%Y-%m-%d")
    filename = f"{dept_code}_Faculty_Report_{today_str}.csv"
    return _make_csv_response(output.getvalue(), filename)'''
new_app_content = new_app_content.replace(old_hod_fac_resp, new_hod_fac_resp)

# 3. hod_export_summary_csv
old_hod_sum_resp = '''    today_str = datetime.date.today().strftime("%Y-%m-%d")
    filename = f"{dept_code}_Department_Summary_{today_str}.csv"
    return Response(
        output.getvalue(),
        mimetype="text/csv; charset=utf-8",
        headers={"Content-Disposition": f\'attachment; filename="{filename}"\'}
    )'''
new_hod_sum_resp = '''    today_str = datetime.date.today().strftime("%Y-%m-%d")
    filename = f"{dept_code}_Department_Summary_{today_str}.csv"
    return _make_csv_response(output.getvalue(), filename)'''
new_app_content = new_app_content.replace(old_hod_sum_resp, new_hod_sum_resp)

# 4. Also use _make_excel_response in hod xlsx endpoints:
old_hod_stu_xlsx = '''    out = io.BytesIO()
    wb.save(out)
    out.seek(0)
    today_str = datetime.date.today().strftime("%Y-%m-%d")
    filename = f"{dept_code}_Student_Report_{today_str}.xlsx"
    return Response(
        out.getvalue(),
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f\'attachment; filename="{filename}"\'}
    )'''
new_hod_stu_xlsx = '''    today_str = datetime.date.today().strftime("%Y-%m-%d")
    filename = f"{dept_code}_Student_Report_{today_str}.xlsx"
    return _make_excel_response(wb, filename)'''
new_app_content = new_app_content.replace(old_hod_stu_xlsx, new_hod_stu_xlsx)

old_hod_fac_xlsx = '''    out = io.BytesIO()
    wb.save(out)
    out.seek(0)
    today_str = datetime.date.today().strftime("%Y-%m-%d")
    filename = f"{dept_code}_Faculty_Report_{today_str}.xlsx"
    return Response(
        out.getvalue(),
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f\'attachment; filename="{filename}"\'}
    )'''
new_hod_fac_xlsx = '''    today_str = datetime.date.today().strftime("%Y-%m-%d")
    filename = f"{dept_code}_Faculty_Report_{today_str}.xlsx"
    return _make_excel_response(wb, filename)'''
new_app_content = new_app_content.replace(old_hod_fac_xlsx, new_hod_fac_xlsx)

old_hod_sum_xlsx = '''    out = io.BytesIO()
    wb.save(out)
    out.seek(0)
    today_str = datetime.date.today().strftime("%Y-%m-%d")
    filename = f"{dept_code}_Department_Summary_{today_str}.xlsx"
    return Response(
        out.getvalue(),
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f\'attachment; filename="{filename}"\'}
    )'''
new_hod_sum_xlsx = '''    today_str = datetime.date.today().strftime("%Y-%m-%d")
    filename = f"{dept_code}_Department_Summary_{today_str}.xlsx"
    return _make_excel_response(wb, filename)'''
new_app_content = new_app_content.replace(old_hod_sum_xlsx, new_hod_sum_xlsx)

# Verify AST
import ast
try:
    ast.parse(new_app_content)
    print("AST verification passed for updated app.py!")
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(new_app_content)
    print("SUCCESS: app.py successfully updated!")
except Exception as e:
    print(f"AST Error: {e}")
    sys.exit(1)
