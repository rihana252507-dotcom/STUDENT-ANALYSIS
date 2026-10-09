"""
CampusIQ – AI-Powered Student Analytics and Success Platform
Unified Flask Application & Role-Based Controller
KPMG in India Hackathon Challenge

Features:
- Three Authenticated Roles: Admin, Faculty, Student
- SQLite Database Integration with Auto-Seeding
- Secure Password Hashing & Flask Session Management
- Role-Protected Views & Server-Enforced API Permissions
- 5-Pillar Explainable Multi-Factor Scoring & Risk Analytics
- Dynamic Chart.js API Feeds, Live Search, What-If Simulation, and CSV Export
"""

import os
import csv
import io
from pathlib import Path
from flask import (
    Flask, render_template, request, redirect, url_for,
    session, jsonify, flash, Response
)

from database.db import get_db, init_db
from werkzeug.security import generate_password_hash
from services.auth import (
    authenticate_user, login_user, logout_user,
    get_current_user, login_required, role_required
)
from services.analytics import analytics_engine

# Initialize Flask App
BASE_DIR = Path(__file__).resolve().parent
app = Flask(
    __name__,
    template_folder=str(BASE_DIR / "templates"),
    static_folder=str(BASE_DIR / "static")
)
app.secret_key = os.environ.get("SECRET_KEY", "campusiq-kpmg-hackathon-production-key-2026")

# Auto-initialize SQLite database on launch
init_db(force=False)

# ==============================================================================
# 1. CORE AUTHENTICATION & NAVIGATION ROUTES
# ==============================================================================

@app.route("/")
def index():
    """Root route: Redirects authenticated users to their dashboard, else to /login."""
    if "user_id" in session:
        role = session.get("role")
        if role == "admin":
            return redirect(url_for("admin_dashboard"))
        elif role == "faculty":
            return redirect(url_for("faculty_dashboard"))
        elif role == "student":
            return redirect(url_for("student_dashboard"))
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    """Login view: Supports Admin, Faculty, and Student authentication (Form & JSON)."""
    if request.method == "POST":
        data = request.get_json(silent=True) or {}
        username = (data.get("user_id") or data.get("username") or request.form.get("username") or "").strip()
        password = (data.get("password") or request.form.get("password") or "").strip()

        user = authenticate_user(username, password)
        if user:
            login_user(user)
            if request.is_json:
                return jsonify({
                    "success": True,
                    "user_id": user["user_id"],
                    "name": user["name"],
                    "role": user["role"],
                    "department": user.get("department", "")
                }), 200

            flash(f"Welcome back, {user['name']}!", "success")
            
            # Redirect to respective authorized dashboard
            if user["role"] == "admin":
                return redirect(url_for("admin_dashboard"))
            elif user["role"] == "faculty":
                return redirect(url_for("faculty_dashboard"))
            elif user["role"] == "student":
                return redirect(url_for("student_dashboard"))
            return redirect(url_for("index"))
        else:
            if request.is_json:
                return jsonify({"error": "Unauthorized", "message": "Invalid User ID or Password"}), 401
            flash("Invalid User ID or Password. Please check credentials or use Quick Demo Sign-In.", "danger")

    # If already logged in, redirect to respective dashboard
    if "user_id" in session:
        return redirect(url_for("index"))

    return render_template("login.html")


@app.route("/logout")
def logout():
    """Terminates user session and redirects to login."""
    logout_user()
    flash("You have been signed out safely.", "warning")
    return redirect(url_for("login"))


# ==============================================================================
# 2. ROLE-PROTECTED DASHBOARD PAGES
# ==============================================================================

@app.route("/admin")
@login_required
@role_required("admin")
def admin_dashboard():
    """Institutional Governance View for University Dean and Administrators."""
    user = get_current_user()
    return render_template("admin_dashboard.html", user=user)


@app.route("/faculty")
@login_required
@role_required("faculty")
def faculty_dashboard():
    """Department Mentorship Caseload View for Faculty Mentors."""
    user = get_current_user()
    return render_template("faculty_dashboard.html", user=user)


@app.route("/student")
@login_required
@role_required("student")
def student_dashboard():
    """Personalized Academic Radar & Success View for Logged-In Student."""
    user = get_current_user()
    student_id = user["user_id"]

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM students WHERE student_id = ? OR user_id = ? OR email = ?", (student_id, student_id, user.get("email", "")))
    student_row = cursor.fetchone()

    if not student_row:
        conn.close()
        flash("Student profile not found in database records.", "danger")
        return redirect(url_for("logout"))

    student = dict(student_row)

    # Compute live explainable metrics
    metrics = analytics_engine.compute_student_metrics(student)

    # Fetch recorded counseling interventions
    cursor.execute("""
    SELECT * FROM interventions WHERE student_id = ? ORDER BY created_at DESC
    """, (student["student_id"],))
    interventions = [dict(row) for row in cursor.fetchall()]

    # Fetch student notifications
    cursor.execute("""
    SELECT * FROM notifications WHERE user_id = ? OR user_id = ? OR user_id = 'all' ORDER BY created_at DESC
    """, (student_id, student["student_id"]))
    notifications = [dict(row) for row in cursor.fetchall()]
    conn.close()

    return render_template(
        "student_dashboard.html",
        user=user,
        student=student,
        metrics=metrics,
        interventions=interventions,
        notifications=notifications
    )


# ==============================================================================
# 3. REST API ENDPOINTS (DATA & ANALYTICS)
# ==============================================================================

@app.route("/api/admin/overview", methods=["GET"])
@login_required
@role_required("admin")
def get_admin_overview():
    """Returns macro-level institutional metrics for admin KPI scorecards."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM students")
    students = [dict(row) for row in cursor.fetchall()]

    cursor.execute("SELECT COUNT(*) FROM faculty")
    faculty_cnt = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM departments")
    dept_cnt = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM courses")
    course_cnt = cursor.fetchone()[0]
    conn.close()

    total = len(students)
    if total == 0:
        return jsonify({"total_students": 0, "faculty_count": faculty_cnt, "department_count": dept_cnt, "course_count": course_cnt})

    high_risk = sum(1 for s in students if s["risk_level"] == "High")
    med_risk = sum(1 for s in students if s["risk_level"] == "Medium")
    low_risk = sum(1 for s in students if s["risk_level"] == "Low")
    avg_cgpa = round(sum(s["cgpa"] for s in students) / total, 2)
    avg_attendance = round(sum(s["attendance_pct"] for s in students) / total, 1)
    avg_success = round(sum(s["success_score"] for s in students) / total, 1)
    compliant = sum(1 for s in students if s["attendance_pct"] >= 75.0)
    placement_ready = sum(1 for s in students if s["technical_skills_score"] >= 75 and s["placement_aptitude_score"] >= 70)

    return jsonify({
        "total_students": total,
        "faculty_count": faculty_cnt,
        "department_count": dept_cnt,
        "course_count": course_cnt,
        "avg_cgpa": avg_cgpa,
        "avg_attendance": avg_attendance,
        "avg_success_score": avg_success,
        "risk_counts": { "high": high_risk, "medium": med_risk, "low": low_risk },
        "risk_percentages": {
            "high": round((high_risk / total) * 100, 1),
            "medium": round((med_risk / total) * 100, 1),
            "low": round((low_risk / total) * 100, 1)
        },
        "attendance_compliance_rate": round((compliant / total) * 100, 1),
        "placement_ready_rate": round((placement_ready / total) * 100, 1),
        "placement_ready_count": placement_ready
    })


@app.route("/api/admin/charts", methods=["GET"])
@login_required
@role_required("admin")
def get_admin_charts():
    """Aggregates Chart.js datasets: Risk Doughnut, Dept Bar, Scatter, Systemic Drivers."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM students")
    students = [dict(row) for row in cursor.fetchall()]
    conn.close()

    total = len(students)
    if total == 0:
        return jsonify({})

    # 1. Risk Breakdown
    high_cnt = sum(1 for s in students if s["risk_level"] == "High")
    med_cnt = sum(1 for s in students if s["risk_level"] == "Medium")
    low_cnt = sum(1 for s in students if s["risk_level"] == "Low")

    risk_breakdown = {
        "labels": ["High Risk", "Medium Risk", "Low Risk"],
        "counts": [high_cnt, med_cnt, low_cnt],
        "percentages": [
            round((high_cnt / total) * 100, 1),
            round((med_cnt / total) * 100, 1),
            round((low_cnt / total) * 100, 1)
        ],
        "colors": ["#EF4444", "#F59E0B", "#10B981"]
    }

    # 2. Department Benchmarks
    dept_groups = {}
    for s in students:
        d = s["department"]
        if d not in dept_groups:
            dept_groups[d] = {"cgpa_sum": 0, "success_sum": 0, "count": 0}
        dept_groups[d]["cgpa_sum"] += s["cgpa"]
        dept_groups[d]["success_sum"] += s["success_score"]
        dept_groups[d]["count"] += 1

    dept_labels = sorted(list(dept_groups.keys()))
    dept_cgpa = [round(dept_groups[d]["cgpa_sum"] / dept_groups[d]["count"], 2) for d in dept_labels]
    dept_success = [round(dept_groups[d]["success_sum"] / dept_groups[d]["count"], 1) for d in dept_labels]

    department_chart = {
        "labels": dept_labels,
        "avg_cgpa": dept_cgpa,
        "avg_success": dept_success
    }

    # 3. Attendance vs CGPA Scatter
    scatter_data = [{
        "x": s["attendance_pct"],
        "y": s["cgpa"],
        "name": s["name"],
        "id": s["student_id"],
        "dept": s["department"],
        "risk": s["risk_level"]
    } for s in students]

    # 4. Systemic Risk Bottlenecks
    factor_counts = {
        "Attendance < 75%": sum(1 for s in students if s["attendance_pct"] < 75.0),
        "Active Backlogs": sum(1 for s in students if s["backlogs"] > 0),
        "CGPA < 6.5": sum(1 for s in students if s["cgpa"] < 6.5),
        "Low LMS Activity (<6 hrs/wk)": sum(1 for s in students if s["lms_weekly_hours"] < 6.0),
        "Low Assignment Submission (<70%)": sum(1 for s in students if s["assignment_completion_pct"] < 70.0),
        "Placement Aptitude Deficit (<65)": sum(1 for s in students if s["placement_aptitude_score"] < 65.0),
        "Elevated Stress (Feedback < 3.0)": sum(1 for s in students if s["student_feedback_score"] < 3.0)
    }
    sorted_factors = sorted(factor_counts.items(), key=lambda x: x[1], reverse=True)

    systemic_risk_chart = {
        "labels": [f[0] for f in sorted_factors],
        "counts": [f[1] for f in sorted_factors]
    }

    # 5. Placement Readiness Chart
    tier1_ready = sum(1 for s in students if s["technical_skills_score"] >= 75 and s["placement_aptitude_score"] >= 70)
    apt_gap = sum(1 for s in students if s["technical_skills_score"] >= 75 and s["placement_aptitude_score"] < 70)
    tech_gap = sum(1 for s in students if s["technical_skills_score"] < 75 and s["placement_aptitude_score"] >= 70)
    early_prep = max(0, total - (tier1_ready + apt_gap + tech_gap))

    placement_readiness_chart = {
        "labels": ["Tier-1 Ready (DSA & Aptitude)", "Aptitude Skills Gap", "Technical Coding Gap", "Foundation Stage"],
        "counts": [tier1_ready, apt_gap, tech_gap, early_prep],
        "colors": ["#10B981", "#F59E0B", "#EC4899", "#8B5CF6"]
    }

    # 6. Success Score Distribution Histogram
    dist_excellent = sum(1 for s in students if s["success_score"] >= 80.0)
    dist_proficient = sum(1 for s in students if 65.0 <= s["success_score"] < 80.0)
    dist_moderate = sum(1 for s in students if 50.0 <= s["success_score"] < 65.0)
    dist_critical = sum(1 for s in students if s["success_score"] < 50.0)

    score_distribution_chart = {
        "labels": ["80-100 (Exemplary)", "65-79 (Proficient)", "50-64 (Watchlist)", "<50 (Critical Risk)"],
        "counts": [dist_excellent, dist_proficient, dist_moderate, dist_critical],
        "colors": ["#10B981", "#3B82F6", "#F59E0B", "#F43F5E"]
    }

    return jsonify({
        "risk_breakdown": risk_breakdown,
        "department_chart": department_chart,
        "scatter_data": scatter_data,
        "systemic_risk_chart": systemic_risk_chart,
        "placement_readiness_chart": placement_readiness_chart,
        "score_distribution_chart": score_distribution_chart
    })


@app.route("/api/admin/departments", methods=["GET"])
@login_required
@role_required("admin")
def get_admin_departments():
    """Department-wise performance table for Dean View."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM students")
    students = [dict(row) for row in cursor.fetchall()]
    conn.close()

    dept_stats = {}
    for s in students:
        d = s["department"]
        if d not in dept_stats:
            dept_stats[d] = {
                "department": d,
                "department_name": s["department_name"],
                "total_students": 0,
                "high_risk": 0,
                "medium_risk": 0,
                "low_risk": 0,
                "cgpa_sum": 0,
                "attendance_sum": 0,
                "success_sum": 0,
                "placement_ready": 0
            }
        st = dept_stats[d]
        st["total_students"] += 1
        if s["risk_level"] == "High":
            st["high_risk"] += 1
        elif s["risk_level"] == "Medium":
            st["medium_risk"] += 1
        else:
            st["low_risk"] += 1
        st["cgpa_sum"] += s["cgpa"]
        st["attendance_sum"] += s["attendance_pct"]
        st["success_sum"] += s["success_score"]
        if s["technical_skills_score"] >= 75 and s["placement_aptitude_score"] >= 70:
            st["placement_ready"] += 1

    summary = []
    for d, st in sorted(dept_stats.items()):
        cnt = st["total_students"]
        summary.append({
            "department": d,
            "department_name": st["department_name"],
            "total_students": cnt,
            "high_risk_count": st["high_risk"],
            "high_risk_pct": round((st["high_risk"] / cnt) * 100, 1),
            "medium_risk_count": st["medium_risk"],
            "low_risk_count": st["low_risk"],
            "avg_cgpa": round(st["cgpa_sum"] / cnt, 2),
            "avg_attendance": round(st["attendance_sum"] / cnt, 1),
            "avg_success_score": round(st["success_sum"] / cnt, 1),
            "placement_ready_rate": round((st["placement_ready"] / cnt) * 100, 1)
        })

    return jsonify({"departments": summary})


@app.route("/api/students", methods=["GET"])
@login_required
def get_students():
    """
    Search, filter, and sort student directory.
    Enforces server-side role permissions:
    - Admin: access all students
    - Faculty: access only assigned students (department / mentor)
    - Student: forbidden (must use /api/students/<id>)
    """
    current_role = session.get("role")
    current_user_id = session.get("user_id")
    current_dept = session.get("department", "")

    if current_role == "student":
        return jsonify({"error": "Forbidden", "message": "Students can only access personal records"}), 403

    conn = get_db()
    cursor = conn.cursor()

    # Query with role filter
    if current_role == "faculty":
        cursor.execute("SELECT * FROM students WHERE faculty_id = ? OR department = ?", (current_user_id, current_dept))
    else:
        cursor.execute("SELECT * FROM students")
    
    rows = cursor.fetchall()
    conn.close()

    students = [dict(r) for r in rows]

    # Filters
    search = request.args.get("search", "").strip().lower()
    dept = request.args.get("department", "ALL").strip()
    risk = request.args.get("risk_level", "ALL").strip()
    sem = request.args.get("semester", "ALL").strip()
    sort_by = request.args.get("sort_by", "risk_level")
    order = request.args.get("order", "asc")

    filtered = []
    for s in students:
        if dept != "ALL" and s["department"].upper() != dept.upper():
            continue
        if risk != "ALL" and s["risk_level"].lower() != risk.lower():
            continue
        if sem != "ALL" and str(s["semester"]) != str(sem):
            continue
        if search:
            match_name = search in s["name"].lower()
            match_id = search in s["student_id"].lower()
            match_mentor = search in s.get("mentor_name", "").lower()
            if not (match_name or match_id or match_mentor):
                continue
        filtered.append(s)

    # Sorting
    risk_rank = {"High": 1, "Medium": 2, "Low": 3}
    reverse = (order.lower() == "desc")

    if sort_by == "risk_level":
        filtered.sort(key=lambda x: risk_rank.get(x["risk_level"], 99), reverse=reverse)
    elif sort_by in ["success_score", "cgpa", "attendance_pct", "backlogs", "academic_marks_pct"]:
        filtered.sort(key=lambda x: x.get(sort_by, 0), reverse=reverse)
    elif sort_by == "name":
        filtered.sort(key=lambda x: x["name"].lower(), reverse=reverse)

    return jsonify({
        "students": filtered,
        "total_count": len(students),
        "filtered_count": len(filtered)
    })


@app.route("/api/students/<student_id>", methods=["GET"])
@login_required
def get_student_detail(student_id):
    """
    Returns full deep-dive profile of a student.
    Strictly enforces access permissions:
    - Student: can only view own record
    - Faculty: can view advisees in their department
    - Admin: can view all
    """
    current_role = session.get("role")
    current_user_id = session.get("user_id", "")

    # Strict permission check for students: can view by user_id ('student001') or student_id ('CIQ-2026-001')
    if current_role == "student":
        allowed_ids = {current_user_id.upper(), session.get("student_id", "").upper()}
        # If student_id requested is not directly in allowed_ids, check if it maps to this user's student record
        if student_id.upper() not in allowed_ids:
            conn_check = get_db()
            c_check = conn_check.cursor()
            c_check.execute("SELECT student_id, user_id FROM students WHERE user_id = ? COLLATE NOCASE OR student_id = ? COLLATE NOCASE", (current_user_id, current_user_id))
            own_row = c_check.fetchone()
            conn_check.close()
            if not own_row or student_id.upper() not in [own_row["student_id"].upper(), own_row["user_id"].upper()]:
                return jsonify({"error": "Forbidden", "message": "Access denied to unauthorized student record"}), 403

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM students WHERE student_id = ? COLLATE NOCASE OR user_id = ? COLLATE NOCASE", (student_id, student_id))
    row = cursor.fetchone()

    if not row:
        conn.close()
        return jsonify({"error": "Not Found", "message": f"Student '{student_id}' not found"}), 404

    student = dict(row)

    # Strict check for faculty: must belong to their department or caseload
    if current_role == "faculty":
        current_dept = session.get("department", "")
        if student["faculty_id"] != current_user_id and student["department"] != current_dept:
            conn.close()
            return jsonify({"error": "Forbidden", "message": "Student is outside your faculty mentorship caseload"}), 403

    # Calculate explainable metrics
    metrics = analytics_engine.compute_student_metrics(student)
    student.update(metrics)

    # Fetch recorded counseling interventions
    cursor.execute("""
    SELECT * FROM interventions WHERE student_id = ? ORDER BY created_at DESC
    """, (student["student_id"],))
    interventions = [dict(r) for r in cursor.fetchall()]
    conn.close()

    student["logged_interventions"] = interventions
    return jsonify(student)


@app.route("/api/students/<student_id>/intervention", methods=["POST"])
@login_required
@role_required("admin", "faculty")
def log_intervention(student_id):
    """Records faculty counseling minutes and intervention protocol in SQLite."""
    data = request.get_json(silent=True) or {}
    action_type = data.get("action_type", "General Academic Counseling")
    priority = data.get("priority", "High")
    faculty_name = data.get("faculty_name", session.get("name", "Faculty Mentor"))
    notes = data.get("notes", "Counseling session conducted.")
    faculty_id = session.get("user_id")

    conn = get_db()
    cursor = conn.cursor()

    # Verify student exists
    cursor.execute("SELECT * FROM students WHERE student_id = ? COLLATE NOCASE OR user_id = ? COLLATE NOCASE", (student_id, student_id))
    student = cursor.fetchone()
    if not student:
        conn.close()
        return jsonify({"error": "Not Found", "message": "Student not found"}), 404

    cursor.execute("""
    INSERT INTO interventions (student_id, faculty_id, faculty_name, action_type, priority, notes)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (student["student_id"], faculty_id, faculty_name, action_type, priority, notes))
    conn.commit()
    conn.close()

    return jsonify({
        "success": True,
        "message": f"Intervention logged successfully for {student['name']}"
    }), 201


@app.route("/api/simulate", methods=["POST"])
@login_required
def simulate():
    """Recalculates hypothetical projected score for What-If scenario simulations."""
    data = request.get_json(silent=True) or {}
    student_id = data.get("student_id")

    current_role = session.get("role")
    current_user_id = session.get("user_id")

    # Enforce student permission
    if current_role == "student" and current_user_id.upper() != str(student_id).upper():
        return jsonify({"error": "Forbidden", "message": "Unauthorized simulation"}), 403

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM students WHERE student_id = ? COLLATE NOCASE OR user_id = ? COLLATE NOCASE", (str(student_id), str(student_id)))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return jsonify({"error": "Not Found", "message": "Student not found"}), 404

    student = dict(row)
    result = analytics_engine.simulate_scenario(
        student,
        attendance_boost=data.get("attendance_boost", 0),
        clear_backlogs=data.get("clear_backlogs", 0),
        lms_hours_boost=data.get("lms_hours_boost", 0),
        assignment_boost=data.get("assignment_boost", 0)
    )

    return jsonify(result)


@app.route("/api/export/csv", methods=["GET"])
@login_required
def export_csv():
    """Generates and downloads dynamic CSV report based on caller's role and filters."""
    current_role = session.get("role")
    current_user_id = session.get("user_id")
    current_dept = session.get("department", "")

    if current_role == "student":
        return jsonify({"error": "Forbidden"}), 403

    conn = get_db()
    cursor = conn.cursor()

    if current_role == "faculty":
        cursor.execute("SELECT * FROM students WHERE faculty_id = ? OR department = ?", (current_user_id, current_dept))
    else:
        cursor.execute("SELECT * FROM students")

    students = [dict(r) for r in cursor.fetchall()]
    conn.close()

    # Optional department & risk filters
    dept = request.args.get("department", "ALL")
    risk = request.args.get("risk_level", "ALL")

    if dept != "ALL":
        students = [s for s in students if s["department"].upper() == dept.upper()]
    if risk != "ALL":
        students = [s for s in students if s["risk_level"].lower() == risk.lower()]

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "Student ID", "Name", "Email", "Department", "Semester", "Section", "Advisor",
        "CGPA", "Exam Marks %", "Attendance %", "Backlogs", "LMS Weekly Hours",
        "Assignment Rate %", "Aptitude Score", "Tech Skills", "Success Score", "Risk Category"
    ])

    for s in students:
        writer.writerow([
            s["student_id"], s["name"], s["email"], s["department"], s["semester"], s["section"],
            s.get("mentor_name", ""), s["cgpa"], s["academic_marks_pct"], s["attendance_pct"],
            s["backlogs"], s["lms_weekly_hours"], s["assignment_completion_pct"],
            s["placement_aptitude_score"], s["technical_skills_score"],
            s["success_score"], s["risk_level"]
        ])

    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=CampusIQ_Student_Report.csv"}
    )


# ==============================================================================
# 4. CRUD & EXTENDED MANAGEMENT APIS (STUDENTS, FACULTY, COURSES, INTERVENTIONS)
# ==============================================================================

@app.route("/api/admin/faculty", methods=["GET"])
@login_required
@role_required("admin")
def get_admin_faculty():
    """Returns directory of faculty members with caseload statistics."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM faculty ORDER BY name ASC")
    faculty_list = [dict(r) for r in cursor.fetchall()]
    
    # Enrich with active advisee counts
    for f in faculty_list:
        cursor.execute("SELECT COUNT(*) as cnt FROM students WHERE faculty_id = ? OR department = ?", (f["faculty_id"], f["department"]))
        f["advisee_count"] = cursor.fetchone()["cnt"]
    conn.close()

    return jsonify({"faculty": faculty_list})


@app.route("/api/faculty", methods=["POST"])
@login_required
@role_required("admin")
def add_faculty():
    """Adds a new faculty mentor and provisions user authentication credentials."""
    data = request.get_json(silent=True) or {}
    faculty_id = data.get("faculty_id", "").strip()
    name = data.get("name", "").strip()
    email = data.get("email", "").strip()
    dept = data.get("department", "CSE").strip()
    designation = data.get("designation", "Assistant Professor").strip()
    phone = data.get("phone", "+91 9811223344").strip()
    specialization = data.get("specialization", "Computer Science").strip()
    password = data.get("password", "Faculty@123").strip()

    if not faculty_id or not name or not dept:
        return jsonify({"error": "Bad Request", "message": "Faculty ID, Name, and Department are required"}), 400

    conn = get_db()
    cursor = conn.cursor()
    try:
        hashed = generate_password_hash(password)
        cursor.execute("""
        INSERT INTO users (user_id, password_hash, role, name, email, department)
        VALUES (?, ?, 'faculty', ?, ?, ?)
        """, (faculty_id, hashed, name, email, dept))

        cursor.execute("""
        INSERT INTO faculty (faculty_id, user_id, name, email, department, designation, phone, specialization)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (faculty_id, faculty_id, name, email, dept, designation, phone, specialization))
        conn.commit()
    except Exception as e:
        conn.close()
        return jsonify({"error": "Database Error", "message": str(e)}), 400
    conn.close()

    return jsonify({"success": True, "message": f"Faculty {name} created with ID {faculty_id}"}), 201


@app.route("/api/admin/courses", methods=["GET"])
@login_required
def get_admin_courses():
    """Returns curriculum course catalog."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM courses ORDER BY course_code ASC")
    courses = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return jsonify({"courses": courses})


@app.route("/api/admin/courses", methods=["POST"])
@login_required
@role_required("admin")
def add_course():
    """Registers a new course in curriculum database."""
    data = request.get_json(silent=True) or {}
    c_code = data.get("course_code", "").strip()
    c_name = data.get("course_name", "").strip()
    dept = data.get("department", "CSE").strip()
    semester = int(data.get("semester", 6))
    credits = int(data.get("credits", 4))
    faculty_name = data.get("faculty_name", "Department Faculty").strip()
    pass_rate = float(data.get("pass_rate", 88.0))

    if not c_code or not c_name or not dept:
        return jsonify({"error": "Bad Request", "message": "Course code, name, and department are required"}), 400

    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute("""
        INSERT INTO courses (course_code, course_name, department, semester, credits, faculty_name, pass_rate)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (c_code, c_name, dept, semester, credits, faculty_name, pass_rate))
        conn.commit()
    except Exception as e:
        conn.close()
        return jsonify({"error": "Database Error", "message": str(e)}), 400
    conn.close()

    return jsonify({"success": True, "message": f"Course {c_code} registered successfully!"}), 201


@app.route("/api/interventions", methods=["GET"])
@login_required
@role_required("admin", "faculty")
def get_interventions():
    """Returns recorded counseling interventions based on caller's role."""
    current_role = session.get("role")
    current_user_id = session.get("user_id")

    conn = get_db()
    cursor = conn.cursor()
    if current_role == "admin":
        cursor.execute("""
        SELECT i.*, s.name as student_name, s.department as student_dept, s.risk_level as student_risk
        FROM interventions i
        LEFT JOIN students s ON i.student_id = s.student_id
        ORDER BY i.created_at DESC
        """)
    else:
        cursor.execute("""
        SELECT i.*, s.name as student_name, s.department as student_dept, s.risk_level as student_risk
        FROM interventions i
        LEFT JOIN students s ON i.student_id = s.student_id
        WHERE i.faculty_id = ? OR s.department = ?
        ORDER BY i.created_at DESC
        """, (current_user_id, session.get("department", "")))

    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return jsonify({"interventions": rows})


@app.route("/api/interventions/<int:id>", methods=["PUT"])
@login_required
@role_required("admin", "faculty")
def update_intervention_status(id):
    """Updates progress status of an active counseling intervention."""
    data = request.get_json(silent=True) or {}
    new_status = data.get("status", "In Progress")

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE interventions SET status = ? WHERE id = ?", (new_status, id))
    conn.commit()
    conn.close()
    return jsonify({"success": True, "message": f"Intervention updated to {new_status}"})


@app.route("/api/students", methods=["POST"])
@login_required
@role_required("admin")
def add_student():
    """Provisions a new student, computes explainable metrics, and creates user login."""
    data = request.get_json(silent=True) or {}
    s_id = data.get("student_id", "").strip()
    name = data.get("name", "").strip()
    email = data.get("email", "").strip() or f"{s_id.lower()}@campusiq.edu"
    dept = data.get("department", "CSE").strip()
    dept_name = data.get("department_name", dept)
    sem = int(data.get("semester", 6))
    section = data.get("section", "A").strip()
    cgpa = float(data.get("cgpa", 7.5))
    academic_marks = float(data.get("academic_marks_pct", 75.0))
    attendance = float(data.get("attendance_pct", 80.0))
    backlogs = int(data.get("backlogs", 0))
    lms_hours = float(data.get("lms_weekly_hours", 10.0))
    lms_score = float(data.get("lms_engagement_score", 75.0))
    assignment_pct = float(data.get("assignment_completion_pct", 80.0))
    extracurricular = float(data.get("extracurricular_score", 70.0))
    aptitude = float(data.get("placement_aptitude_score", 72.0))
    tech = float(data.get("technical_skills_score", 75.0))
    feedback = float(data.get("student_feedback_score", 4.0))
    mentor = data.get("mentor_name", "Dr. Sunita Rao").strip()
    fac_id = data.get("faculty_id", "faculty001").strip()
    phone = data.get("phone", "+91 9800000000").strip()

    if not s_id or not name or not dept:
        return jsonify({"error": "Bad Request", "message": "Student ID, Name, and Department are required"}), 400

    # Compute analytics
    calc_data = {
        "cgpa": cgpa,
        "academic_marks_pct": academic_marks,
        "attendance_pct": attendance,
        "backlogs": backlogs,
        "lms_weekly_hours": lms_hours,
        "lms_engagement_score": lms_score,
        "assignment_completion_pct": assignment_pct,
        "extracurricular_score": extracurricular,
        "placement_aptitude_score": aptitude,
        "technical_skills_score": tech,
        "student_feedback_score": feedback
    }
    metrics = analytics_engine.compute_student_metrics(calc_data)

    conn = get_db()
    cursor = conn.cursor()
    try:
        hashed = generate_password_hash("Student@123")

        # Insert User account
        cursor.execute("""
        INSERT INTO users (user_id, password_hash, role, name, email, department)
        VALUES (?, ?, 'student', ?, ?, ?)
        """, (s_id, hashed, name, email, dept))

        # Insert Student record
        cursor.execute("""
        INSERT INTO students (
            student_id, user_id, name, email, gender, department, department_name,
            semester, section, faculty_id, mentor_name, cgpa, academic_marks_pct,
            attendance_pct, backlogs, lms_weekly_hours, lms_engagement_score,
            assignment_completion_pct, extracurricular_score, placement_aptitude_score,
            technical_skills_score, student_feedback_score, phone, success_score, risk_level, segment
        ) VALUES (?, ?, ?, ?, 'Not Specified', ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            s_id, s_id, name, email, dept, dept_name, sem, section,
            fac_id, mentor, cgpa, academic_marks, attendance, backlogs,
            lms_hours, lms_score, assignment_pct, extracurricular,
            aptitude, tech, feedback, phone, metrics["success_score"], metrics["risk_level"], metrics["segment"]
        ))
        conn.commit()
    except Exception as e:
        conn.close()
        return jsonify({"error": "Database Error", "message": str(e)}), 400
    conn.close()

    return jsonify({"success": True, "message": f"Student {name} created successfully!", "student_id": s_id}), 201


@app.route("/api/students/<student_id>", methods=["PUT"])
@login_required
@role_required("admin")
def update_student(student_id):
    """Updates student records and recalculates success score & risk status."""
    data = request.get_json(silent=True) or {}
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM students WHERE student_id = ? COLLATE NOCASE OR user_id = ? COLLATE NOCASE", (student_id, student_id))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return jsonify({"error": "Not Found", "message": "Student not found"}), 404

    current = dict(row)
    for k, v in data.items():
        if k in current and k not in ["id", "student_id", "user_id"]:
            current[k] = v

    metrics = analytics_engine.compute_student_metrics(current)

    cursor.execute("""
    UPDATE students SET
        name = ?, email = ?, department = ?, semester = ?, section = ?,
        mentor_name = ?, cgpa = ?, academic_marks_pct = ?, attendance_pct = ?,
        backlogs = ?, lms_weekly_hours = ?, assignment_completion_pct = ?,
        placement_aptitude_score = ?, technical_skills_score = ?,
        success_score = ?, risk_level = ?, segment = ?
    WHERE student_id = ? COLLATE NOCASE
    """, (
        current["name"], current["email"], current["department"], current["semester"], current["section"],
        current["mentor_name"], current["cgpa"], current["academic_marks_pct"], current["attendance_pct"],
        current["backlogs"], current["lms_weekly_hours"], current["assignment_completion_pct"],
        current["placement_aptitude_score"], current["technical_skills_score"],
        metrics["success_score"], metrics["risk_level"], metrics["segment"],
        student_id
    ))
    conn.commit()
    conn.close()
    return jsonify({"success": True, "message": f"Student {student_id} updated successfully!"})


@app.route("/api/students/<student_id>", methods=["DELETE"])
@login_required
@role_required("admin")
def delete_student(student_id):
    """Deletes student record, interventions, and authentication account."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM students WHERE student_id = ? COLLATE NOCASE OR user_id = ? COLLATE NOCASE", (student_id, student_id))
    cursor.execute("DELETE FROM users WHERE user_id = ? COLLATE NOCASE", (student_id,))
    cursor.execute("DELETE FROM interventions WHERE student_id = ? COLLATE NOCASE", (student_id,))
    conn.commit()
    conn.close()
    return jsonify({"success": True, "message": f"Student {student_id} removed from system."})


@app.route("/api/notifications", methods=["GET"])
@login_required
def get_user_notifications():
    """Returns alerts for logged-in user."""
    user_id = session.get("user_id")
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM notifications WHERE user_id = ? OR user_id = 'all' ORDER BY created_at DESC", (user_id,))
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return jsonify({"notifications": rows})


# ==============================================================================
# RUNNER
# ==============================================================================

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"\n========================================================")
    print(f" CampusIQ – AI-Powered Student Analytics & Success Platform ")
    print(f" Full-Stack Single-Project Application Running ")
    print(f" URL: http://127.0.0.1:{port}")
    print(f"========================================================\n")
    app.run(host="0.0.0.0", port=port, debug=True)
