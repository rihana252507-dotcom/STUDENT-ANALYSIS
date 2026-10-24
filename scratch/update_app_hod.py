with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update index()
target_index = '''        elif role == "student":
            return redirect(url_for("student_dashboard"))'''

repl_index = '''        elif role == "hod":
            return redirect(url_for("hod_dashboard"))
        elif role == "student":
            return redirect(url_for("student_dashboard"))'''

if target_index in content:
    content = content.replace(target_index, repl_index, 1)
    print("Updated index() for HOD redirect")

# 2. Update login()
target_login = '''            elif user["role"] == "student":
                return redirect(url_for("student_dashboard"))'''

repl_login = '''            elif user["role"] == "hod":
                return redirect(url_for("hod_dashboard"))
            elif user["role"] == "student":
                return redirect(url_for("student_dashboard"))'''

if target_login in content:
    content = content.replace(target_login, repl_login, 1)
    print("Updated login() for HOD redirect")

# 3. Add HOD dashboard routes
target_dashboards = '''@app.route("/faculty")
@login_required
@role_required("faculty")
def faculty_dashboard():'''

hod_dash_route = '''@app.route("/hod")
@app.route("/hod/dashboard")
@login_required
@role_required("hod")
def hod_dashboard():
    """Departmental Governance and Monitoring View for Head of Department (HOD)."""
    user = get_current_user()
    dept_code = (user.get("department") or "").strip().upper()
    
    dept_info = None
    if dept_code:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM departments WHERE code = ? COLLATE NOCASE", (dept_code,))
        row = cursor.fetchone()
        dept_info = dict(row) if row else None
        conn.close()

    return render_template("hod_dashboard.html", user=user, dept_code=dept_code, dept_info=dept_info)


@app.route("/faculty")
@login_required
@role_required("faculty")
def faculty_dashboard():'''

if target_dashboards in content:
    content = content.replace(target_dashboards, hod_dash_route, 1)
    print("Added /hod and /hod/dashboard routes")

# 4. Update /api/students
target_students = '''    # Query with role filter
    if current_role == "faculty":'''

repl_students = '''    # Query with role filter
    if current_role == "hod":
        if not current_dept:
            return jsonify({"error": "Forbidden", "message": "No department assigned to HOD account"}), 403
        cursor.execute("SELECT * FROM students WHERE department = ? COLLATE NOCASE", (current_dept,))
    elif current_role == "faculty":'''

if target_students in content:
    content = content.replace(target_students, repl_students, 1)
    print("Updated /api/students for HOD department restriction")

# 5. Update /api/students/<student_id>
target_detail = '''    # Strict permission check for students: can view by user_id ('student001') or student_id ('CIQ-2026-001')
    if current_role == "student":'''

repl_detail = '''    # Strict permission check for HOD: can only view students in their assigned department
    if current_role == "hod":
        current_dept = session.get("department", "")
        if not current_dept:
            return jsonify({"error": "Forbidden", "message": "No department assigned to HOD account"}), 403
        conn_check = get_db()
        c_check = conn_check.cursor()
        c_check.execute("SELECT department FROM students WHERE student_id = ? COLLATE NOCASE OR user_id = ? COLLATE NOCASE", (student_id, student_id))
        s_dept_row = c_check.fetchone()
        conn_check.close()
        if not s_dept_row or (s_dept_row["department"] or "").strip().upper() != current_dept.strip().upper():
            return jsonify({"error": "Forbidden", "message": "Access denied: student does not belong to your department"}), 403

    # Strict permission check for students: can view by user_id ('student001') or student_id ('CIQ-2026-001')
    if current_role == "student":'''

if target_detail in content:
    content = content.replace(target_detail, repl_detail, 1)
    print("Updated /api/students/<student_id> for HOD department check")

# 6. Update /api/admin/faculty
target_admin_fac = '''@app.route("/api/admin/faculty", methods=["GET"])
@login_required
@role_required("admin")
def get_admin_faculty():'''

repl_admin_fac = '''@app.route("/api/admin/faculty", methods=["GET"])
@login_required
@role_required("admin", "hod")
def get_admin_faculty():
    current_role = session.get("role")
    current_dept = session.get("department", "")
    conn = get_db()
    cursor = conn.cursor()
    if current_role == "hod":
        if not current_dept:
            return jsonify({"error": "Forbidden", "message": "No department assigned to HOD account"}), 403
        cursor.execute("SELECT * FROM faculty WHERE department = ? COLLATE NOCASE ORDER BY name ASC", (current_dept,))
    else:
        cursor.execute("SELECT * FROM faculty ORDER BY name ASC")
    faculty_list = [dict(r) for r in cursor.fetchall()]
    
    # Enrich with active advisee counts
    for f in faculty_list:
        cursor.execute("SELECT COUNT(*) as cnt FROM students WHERE faculty_id = ? OR department = ?", (f["faculty_id"], f["department"]))
        f["advisee_count"] = cursor.fetchone()["cnt"]
    conn.close()

    return jsonify({"faculty": faculty_list})


def _old_get_admin_faculty():'''

if target_admin_fac in content:
    content = content.replace(target_admin_fac, repl_admin_fac, 1)
    print("Updated /api/admin/faculty for HOD department restriction")

# 7. Update /api/interventions
target_intv = '''@app.route("/api/interventions", methods=["GET"])
@login_required
@role_required("admin", "faculty")
def get_interventions():'''

repl_intv = '''@app.route("/api/interventions", methods=["GET"])
@login_required
@role_required("admin", "faculty", "hod")
def get_interventions():'''

if target_intv in content:
    content = content.replace(target_intv, repl_intv, 1)
    print("Updated /api/interventions decorator for HOD")

target_intv_body = '''    if current_role == "admin":
        cursor.execute("""
        SELECT i.*, s.name as student_name, s.department as student_dept, s.risk_level as student_risk,
               n.is_read as notif_is_read, n.read_at as notif_read_at
        FROM interventions i
        LEFT JOIN students s ON i.student_id = s.student_id
        LEFT JOIN notifications n ON n.intervention_id = i.id
        ORDER BY i.created_at DESC
        """)
    else:'''

repl_intv_body = '''    if current_role == "admin":
        cursor.execute("""
        SELECT i.*, s.name as student_name, s.department as student_dept, s.risk_level as student_risk,
               n.is_read as notif_is_read, n.read_at as notif_read_at
        FROM interventions i
        LEFT JOIN students s ON i.student_id = s.student_id
        LEFT JOIN notifications n ON n.intervention_id = i.id
        ORDER BY i.created_at DESC
        """)
    elif current_role == "hod":
        current_dept = session.get("department", "")
        if not current_dept:
            return jsonify({"error": "Forbidden", "message": "No department assigned to HOD account"}), 403
        cursor.execute("""
        SELECT i.*, s.name as student_name, s.department as student_dept, s.risk_level as student_risk,
               n.is_read as notif_is_read, n.read_at as notif_read_at
        FROM interventions i
        JOIN students s ON i.student_id = s.student_id
        LEFT JOIN notifications n ON n.intervention_id = i.id
        WHERE s.department = ? COLLATE NOCASE
        ORDER BY i.created_at DESC
        """, (current_dept,))
    else:'''

if target_intv_body in content:
    content = content.replace(target_intv_body, repl_intv_body, 1)
    print("Updated /api/interventions query for HOD department restriction")

# 8. Add /api/hod/overview
hod_overview_code = '''
# ==============================================================================
# HOD (HEAD OF DEPARTMENT) API ENDPOINTS
# ==============================================================================

@app.route("/api/hod/overview", methods=["GET"])
@login_required
@role_required("hod")
def hod_overview():
    """
    Returns verified department-level metrics, faculty overview,
    risk monitoring statistics, and active interventions for the authenticated HOD.
    Enforces strict backend isolation to session department.
    """
    current_user = get_current_user()
    dept_code = (current_user.get("department") or "").strip().upper()
    if not dept_code:
        return jsonify({"error": "Forbidden", "message": "No department assigned to HOD account"}), 403

    conn = get_db()
    cursor = conn.cursor()

    # Department metadata
    cursor.execute("SELECT * FROM departments WHERE code = ? COLLATE NOCASE", (dept_code,))
    dept_row = cursor.fetchone()
    dept_name = dept_row["name"] if dept_row else dept_code
    hod_name = dept_row["hod_name"] if dept_row else current_user.get("name", "")

    # Student aggregated metrics
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
    s_stats = cursor.fetchone()

    # Faculty members for this department
    cursor.execute("""
        SELECT faculty_id, name, email, department, designation, specialization, phone, courses_count
        FROM faculty
        WHERE department = ? COLLATE NOCASE
        ORDER BY name ASC
    """, (dept_code,))
    faculty_list = [dict(f) for f in cursor.fetchall()]

    # Interventions for students of this department
    cursor.execute("""
        SELECT i.*, s.name as student_name, s.department as student_dept, s.risk_level as student_risk,
               n.is_read as notif_is_read, n.read_at as notif_read_at
        FROM interventions i
        JOIN students s ON i.student_id = s.student_id
        LEFT JOIN notifications n ON n.intervention_id = i.id
        WHERE s.department = ? COLLATE NOCASE
        ORDER BY i.created_at DESC
    """, (dept_code,))
    intv_rows = [dict(r) for r in cursor.fetchall()]

    active_intvs = [i for i in intv_rows if (i.get("status") or "").lower() != "completed"]
    completed_intvs = [i for i in intv_rows if (i.get("status") or "").lower() == "completed"]

    # Student records list
    cursor.execute("""
        SELECT * FROM students
        WHERE department = ? COLLATE NOCASE
        ORDER BY 
            CASE LOWER(risk_level) 
                WHEN 'high' THEN 1 
                WHEN 'medium' THEN 2 
                WHEN 'low' THEN 3 
                ELSE 4 
            END, name ASC
    """, (dept_code,))
    students_list = [dict(s) for s in cursor.fetchall()]

    # Query academic_records to attach backlog subjects
    cursor.execute("""
        SELECT student_id, GROUP_CONCAT(course_name, ', ') AS backlog_subjects, COUNT(*) AS backlog_records_count
        FROM academic_records
        WHERE LOWER(status) NOT IN ('passed', 'pass', 'completed', 'clear')
        GROUP BY student_id
    """)
    backlogs_map = {r["student_id"]: {"subjects": r["backlog_subjects"], "count": r["backlog_records_count"]} for r in cursor.fetchall()}
    for s in students_list:
        sid = s.get("student_id")
        b_info = backlogs_map.get(sid, {})
        s["backlog_subjects"] = b_info.get("subjects") or ""
        if not s.get("backlogs") and b_info.get("count"):
            s["backlogs"] = b_info["count"]

    conn.close()

    return jsonify({
        "success": True,
        "department": {
            "code": dept_code,
            "name": dept_name,
            "hod_name": hod_name
        },
        "metrics": {
            "total_students": s_stats["total_students"] or 0,
            "total_faculty": len(faculty_list),
            "at_risk_students": (s_stats["high_risk_count"] or 0) + (s_stats["med_risk_count"] or 0),
            "high_risk_count": s_stats["high_risk_count"] or 0,
            "med_risk_count": s_stats["med_risk_count"] or 0,
            "low_risk_count": s_stats["low_risk_count"] or 0,
            "avg_attendance": round(s_stats["avg_attendance"] or 0.0, 1),
            "avg_cgpa": round(s_stats["avg_cgpa"] or 0.0, 2),
            "avg_marks": round(s_stats["avg_marks"] or 0.0, 1),
            "avg_success_score": round(s_stats["avg_success_score"] or 0.0, 1),
            "total_backlogs": s_stats["total_backlogs"] or 0,
            "active_interventions": len(active_intvs),
            "completed_interventions": len(completed_intvs),
            "total_interventions": len(intv_rows)
        },
        "faculty": {
            "list": faculty_list,
            "attendance_notice": "Faculty attendance data is not available in the current system."
        },
        "students": students_list,
        "interventions": intv_rows
    }), 200
'''

if 'def hod_overview():' not in content:
    content += "\n" + hod_overview_code
    print("Added hod_overview API route to app.py")

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated app.py successfully!")
