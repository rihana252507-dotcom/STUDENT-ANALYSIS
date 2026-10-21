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
from services.chatbot import generate_multilingual_chat_reply

# Initialize Flask App
BASE_DIR = Path(__file__).resolve().parent
app = Flask(
    __name__,
    template_folder=str(BASE_DIR / "templates"),
    static_folder=str(BASE_DIR / "static")
)
app.secret_key = os.environ.get("SECRET_KEY", "campusiq-kpmg-hackathon-production-key-2026")
app.json.ensure_ascii = False

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

    # Fetch complete academic records across all semesters
    cursor.execute("""
    SELECT * FROM academic_records WHERE student_id = ? ORDER BY semester ASC, id ASC
    """, (student["student_id"],))
    academic_rows = [dict(row) for row in cursor.fetchall()]

    semesters_data = {}
    total_courses = len(academic_rows)
    total_passed = sum(1 for r in academic_rows if r["status"] == "Passed")
    backlog_subjects = [r["course_name"] for r in academic_rows if r["status"] == "Backlog"]

    for r in academic_rows:
        label = r["semester_label"]
        if label not in semesters_data:
            semesters_data[label] = {
                "year": r["year"],
                "semester": r["semester"],
                "semester_label": label,
                "academic_year": r["academic_year"],
                "sgpa": r["sgpa"],
                "courses": [],
                "has_backlog": False,
                "backlog_count": 0
            }
        semesters_data[label]["courses"].append(r)
        if r["status"] == "Backlog":
            semesters_data[label]["has_backlog"] = True
            semesters_data[label]["backlog_count"] += 1

    current_academic_year = f"Year {(student['semester'] + 1) // 2}"

    # Fetch semester fee records
    cursor.execute("""
    SELECT * FROM student_fees WHERE student_id = ? ORDER BY year ASC, semester ASC
    """, (student["student_id"],))
    fee_rows = [dict(row) for row in cursor.fetchall()]

    from datetime import date
    today_str = date.today().isoformat()

    total_fees = 0.0
    total_paid = 0.0
    total_due = 0.0
    next_due_date = None

    for fr in fee_rows:
        t_fee = float(fr.get("total_fee") or 0.0)
        a_paid = float(fr.get("amount_paid") or 0.0)
        rem_due = max(0.0, round(t_fee - a_paid, 2))
        fr["remaining_due"] = rem_due

        d_date = fr.get("due_date")
        if rem_due <= 0.0:
            fr["status"] = "Paid"
        elif d_date and d_date < today_str:
            fr["status"] = "Overdue"
        elif a_paid > 0.0:
            fr["status"] = "Partially Paid"
        else:
            fr["status"] = "Due"

        total_fees += t_fee
        total_paid += a_paid
        total_due += rem_due

        # Track next upcoming due date among records with remaining due > 0
        if rem_due > 0 and d_date and d_date >= today_str:
            if next_due_date is None or d_date < next_due_date:
                next_due_date = d_date

    fee_summary = {
        "total_fees": round(total_fees, 2),
        "total_paid": round(total_paid, 2),
        "total_due": round(total_due, 2),
        "next_due_date": next_due_date or ("Not available" if total_due > 0 else "None pending")
    }

    # Fetch saved student skills
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS student_skills (
        student_id TEXT PRIMARY KEY,
        skills TEXT NOT NULL DEFAULT '[]',
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (student_id) REFERENCES students(student_id)
    );
    """)
    cursor.execute("SELECT skills FROM student_skills WHERE student_id = ?", (student["student_id"],))
    skill_row = cursor.fetchone()
    import json
    saved_skills = []
    if skill_row and skill_row["skills"]:
        try:
            saved_skills = json.loads(skill_row["skills"])
        except Exception:
            saved_skills = [s.strip() for s in skill_row["skills"].split(",") if s.strip()]

    from services.placement import match_companies_for_student
    placement_data = match_companies_for_student(saved_skills, student)

    conn.close()

    return render_template(
        "student_dashboard.html",
        user=user,
        student=student,
        metrics=metrics,
        interventions=interventions,
        notifications=notifications,
        academic_records=academic_rows,
        semesters_data=semesters_data,
        total_courses=total_courses,
        total_passed=total_passed,
        backlog_subjects=backlog_subjects,
        current_academic_year=current_academic_year,
        fee_records=fee_rows,
        fee_summary=fee_summary,
        saved_skills=saved_skills,
        placement_data=placement_data
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
        faculty_name = session.get("name", "")
        cursor.execute("""
            SELECT * FROM students 
            WHERE faculty_id = ? 
               OR department = ? 
               OR mentor_name = ?
               OR student_id IN (SELECT student_id FROM interventions WHERE faculty_id = ?)
        """, (current_user_id, current_dept, faculty_name, current_user_id))
    else:
        cursor.execute("SELECT * FROM students")
    
    rows = cursor.fetchall()

    # Query academic_records to accurately attach backlog subjects and count
    cursor.execute("""
        SELECT student_id, GROUP_CONCAT(course_name, ', ') AS backlog_subjects, COUNT(*) AS backlog_records_count
        FROM academic_records
        WHERE LOWER(status) NOT IN ('passed', 'pass', 'completed', 'clear')
        GROUP BY student_id
    """)
    backlogs_map = {
        r["student_id"]: {
            "subjects": r["backlog_subjects"],
            "count": r["backlog_records_count"]
        }
        for r in cursor.fetchall()
    }
    conn.close()

    students = []
    for r in rows:
        s = dict(r)
        b_info = backlogs_map.get(s["student_id"], {})
        rec_count = b_info.get("count", 0)
        raw_subjects = b_info.get("subjects") or ""
        
        actual_backlogs = max(s.get("backlogs") or 0, rec_count)
        s["backlogs"] = actual_backlogs
        if raw_subjects:
            s["backlog_subjects"] = raw_subjects
        elif actual_backlogs > 0:
            s["backlog_subjects"] = "1 Active Backlog" if actual_backlogs == 1 else f"{actual_backlogs} Active Backlogs"
        else:
            s["backlog_subjects"] = ""
            
        s["academic_year"] = (s.get("semester", 1) + 1) // 2
        students.append(s)

    # Filters
    search = request.args.get("search", "").strip().lower()
    dept = request.args.get("department", "ALL").strip()
    risk = request.args.get("risk_level", "ALL").strip()
    sem = request.args.get("semester", "ALL").strip()
    sort_by = request.args.get("sort_by", "department").strip()
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
            match_id = search in s["student_id"].lower() or search in s.get("user_id", "").lower()
            match_mentor = search in s.get("mentor_name", "").lower()
            if not (match_name or match_id or match_mentor):
                continue
        filtered.append(s)

    # Department custom priority sorting order:
    # 1. CSE, 2. AIML, 3. AIDS (including AI&DS), 4. Remaining departments alphabetically, 5. Missing at end
    def dept_sort_priority(dept_val):
        if not dept_val:
            return (2, "ZZZZ")
        d = str(dept_val).strip().upper().replace("&", "")
        if d == "CSE":
            return (0, 1)
        elif d == "AIML":
            return (0, 2)
        elif d == "AIDS":
            return (0, 3)
        else:
            return (1, str(dept_val).strip().upper())

    # Sorting
    risk_rank = {"High": 1, "Medium": 2, "Low": 3}
    reverse = (order.lower() == "desc")

    if sort_by == "department":
        filtered.sort(key=lambda s: (
            dept_sort_priority(s.get("department")),
            str(s.get("student_id") or "").strip().lower(),
            str(s.get("name") or "").strip().lower()
        ), reverse=reverse)
    elif sort_by == "risk_level":
        filtered.sort(key=lambda x: risk_rank.get(x["risk_level"], 99), reverse=reverse)
    elif sort_by in ["success_score", "cgpa", "attendance_pct", "backlogs", "academic_marks_pct"]:
        filtered.sort(key=lambda x: x.get(sort_by, 0), reverse=reverse)
    elif sort_by == "name":
        filtered.sort(key=lambda x: x["name"].lower(), reverse=reverse)
    else:
        filtered.sort(key=lambda s: (
            dept_sort_priority(s.get("department")),
            str(s.get("student_id") or "").strip().lower(),
            str(s.get("name") or "").strip().lower()
        ))

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

    # Fetch recorded academic records
    cursor.execute("""
    SELECT * FROM academic_records WHERE student_id = ? ORDER BY semester ASC, id ASC
    """, (student["student_id"],))
    academic_records = [dict(r) for r in cursor.fetchall()]
    conn.close()

    student["logged_interventions"] = interventions
    student["academic_records"] = academic_records
    return jsonify(student)


@app.route("/api/students/<student_id>/intervention", methods=["POST"])
@login_required
@role_required("admin", "faculty")
def log_intervention(student_id):
    """Records faculty counseling minutes and intervention protocol in SQLite."""
    data = request.get_json(silent=True) or {}
    action_type = (data.get("action_type") or data.get("title") or "General Academic Counseling").strip()
    title = (data.get("title") or action_type).strip()
    priority = (data.get("priority") or "High").strip()
    instructions = (data.get("instructions") or "").strip()
    due_date = (data.get("due_date") or "").strip()
    notes = (data.get("notes") or instructions or "Intervention assigned.").strip()

    current_role = session.get("role")
    current_user_id = session.get("user_id")

    conn = get_db()
    cursor = conn.cursor()

    # 1. Verify student exists
    cursor.execute("SELECT * FROM students WHERE student_id = ? COLLATE NOCASE OR user_id = ? COLLATE NOCASE", (student_id, student_id))
    student = cursor.fetchone()
    if not student:
        conn.close()
        return jsonify({"error": "Not Found", "message": "Student not found"}), 404

    # 2. Determine and verify assigned faculty
    target_faculty_id = data.get("faculty_id") or data.get("assigned_faculty")
    faculty_row = None

    if target_faculty_id:
        cursor.execute("SELECT * FROM faculty WHERE faculty_id = ? COLLATE NOCASE OR user_id = ? COLLATE NOCASE", (target_faculty_id, target_faculty_id))
        faculty_row = cursor.fetchone()

    if not faculty_row and data.get("faculty_name"):
        cursor.execute("SELECT * FROM faculty WHERE name = ? COLLATE NOCASE", (data.get("faculty_name").strip(),))
        faculty_row = cursor.fetchone()

    # Fallback to student's assigned faculty mentor
    if not faculty_row and student["faculty_id"]:
        cursor.execute("SELECT * FROM faculty WHERE faculty_id = ? COLLATE NOCASE OR user_id = ? COLLATE NOCASE", (student["faculty_id"], student["faculty_id"]))
        faculty_row = cursor.fetchone()

    if faculty_row:
        faculty_id = faculty_row["user_id"]
        faculty_name = faculty_row["name"]
    else:
        if current_role == "faculty":
            faculty_id = current_user_id
            faculty_name = session.get("name", "Faculty Mentor")
        else:
            conn.close()
            return jsonify({"error": "Bad Request", "message": "A valid faculty member must be selected."}), 400

    # 3. Transactional insert of intervention and faculty notification
    try:
        cursor.execute("BEGIN TRANSACTION")
        cursor.execute("""
        INSERT INTO interventions (
            student_id, faculty_id, faculty_name, action_type, title,
            priority, instructions, notes, due_date, status
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            student["student_id"], faculty_id, faculty_name, action_type, title,
            priority, instructions, notes, due_date, "Assigned" if current_role == "admin" else "In Progress"
        ))
        intervention_id = cursor.lastrowid

        # Create notification for assigned faculty member
        notif_msg = f"Admin assigned intervention '{title}' for {student['name']} ({student['student_id']}). Priority: {priority}."
        if due_date:
            notif_msg += f" Due: {due_date}."
        if instructions:
            notif_msg += f" Instructions: {instructions}"

        cursor.execute("""
        INSERT INTO notifications (user_id, title, message, type, is_read, intervention_id)
        VALUES (?, ?, ?, ?, 0, ?)
        """, (faculty_id, f"Intervention: {title}", notif_msg, "intervention", intervention_id))

        conn.commit()
    except Exception as e:
        conn.rollback()
        conn.close()
        return jsonify({"error": "Database Error", "message": str(e)}), 500

    conn.close()

    return jsonify({
        "success": True,
        "message": f"Intervention assigned successfully for {student['name']}",
        "intervention_id": intervention_id
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
    """
    Adds a new faculty mentor and provisions user authentication credentials.
    Permanently persists record in SQLite with transactional integrity.
    """
    data = request.get_json(silent=True) or request.form.to_dict() or {}
    faculty_id = (data.get("faculty_id") or data.get("user_id") or data.get("username") or "").strip()
    name = data.get("name", "").strip()
    email = data.get("email", "").strip() or f"{faculty_id.lower()}@campusiq.edu"
    dept = data.get("department", "CSE").strip().upper()
    designation = data.get("designation", "Assistant Professor").strip()
    phone = data.get("phone", "+91 9811223344").strip()
    specialization = data.get("specialization", "Computer Science").strip()
    password = (data.get("password") or "Faculty@123").strip()

    # Server-side validation of mandatory fields
    if not faculty_id:
        return jsonify({"error": "Bad Request", "message": "Faculty ID / Username is required."}), 400
    if not name:
        return jsonify({"error": "Bad Request", "message": "Faculty full name is required."}), 400
    if not dept:
        return jsonify({"error": "Bad Request", "message": "Department is required."}), 400

    conn = get_db()
    cursor = conn.cursor()

    try:
        # 1. Enforce uniqueness against users and faculty tables
        cursor.execute("SELECT user_id FROM users WHERE user_id = ? OR email = ?", (faculty_id, email))
        if cursor.fetchone():
            return jsonify({
                "error": "Conflict",
                "message": f"User ID '{faculty_id}' or Email '{email}' is already registered in the system."
            }), 409

        cursor.execute("SELECT faculty_id FROM faculty WHERE faculty_id = ? OR user_id = ?", (faculty_id, faculty_id))
        if cursor.fetchone():
            return jsonify({
                "error": "Conflict",
                "message": f"Faculty record with ID '{faculty_id}' already exists."
            }), 409

        # 2. Hash password securely using PBKDF2 (never plain text)
        hashed = generate_password_hash(password)

        # 3. Parameterized INSERT into users table for authentication
        cursor.execute("""
        INSERT INTO users (user_id, password_hash, role, name, email, department)
        VALUES (?, ?, 'faculty', ?, ?, ?)
        """, (faculty_id, hashed, name, email, dept))

        # 4. Parameterized INSERT into faculty table
        cursor.execute("""
        INSERT INTO faculty (faculty_id, user_id, name, email, department, designation, phone, specialization)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (faculty_id, faculty_id, name, email, dept, designation, phone, specialization))

        # 5. Update department faculty count
        cursor.execute("UPDATE departments SET faculty_count = faculty_count + 1 WHERE code = ?", (dept,))

        # 6. Commit transaction to permanently persist in SQLite
        conn.commit()

    except Exception as e:
        conn.rollback()
        return jsonify({"error": "Database Error", "message": f"Failed to save faculty record: {str(e)}"}), 500
    finally:
        conn.close()

    return jsonify({
        "success": True,
        "message": f"Faculty member '{name}' ({faculty_id}) created and saved permanently.",
        "faculty_id": faculty_id,
        "user_id": faculty_id
    }), 201


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
        SELECT i.*, s.name as student_name, s.department as student_dept, s.risk_level as student_risk,
               n.is_read as notif_is_read, n.read_at as notif_read_at
        FROM interventions i
        LEFT JOIN students s ON i.student_id = s.student_id
        LEFT JOIN notifications n ON n.intervention_id = i.id
        ORDER BY i.created_at DESC
        """)
    else:
        cursor.execute("""
        SELECT i.*, s.name as student_name, s.department as student_dept, s.risk_level as student_risk,
               n.is_read as notif_is_read, n.read_at as notif_read_at
        FROM interventions i
        LEFT JOIN students s ON i.student_id = s.student_id
        LEFT JOIN notifications n ON n.intervention_id = i.id
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
    """Updates progress status, action taken, and implementation notes of an active intervention."""
    data = request.get_json(silent=True) or {}
    new_status = data.get("status")
    action_taken = data.get("action_taken")
    implementation_notes = data.get("implementation_notes") or data.get("notes")

    current_role = session.get("role")
    current_user_id = session.get("user_id")

    conn = get_db()
    cursor = conn.cursor()

    # Check permission: Faculty can update only their own assigned interventions
    cursor.execute("SELECT * FROM interventions WHERE id = ?", (id,))
    intv = cursor.fetchone()
    if not intv:
        conn.close()
        return jsonify({"error": "Not Found", "message": "Intervention not found"}), 404

    if current_role == "faculty" and intv["faculty_id"] != current_user_id:
        conn.close()
        return jsonify({"error": "Forbidden", "message": "You can only update interventions assigned to you"}), 403

    status_val = new_status if new_status else intv["status"]
    action_val = action_taken if action_taken is not None else intv["action_taken"]
    notes_val = implementation_notes if implementation_notes is not None else intv["implementation_notes"]

    completed_at = intv["completed_at"]
    if status_val == "Completed" and not completed_at:
        import datetime
        completed_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("""
    UPDATE interventions
    SET status = ?, action_taken = ?, implementation_notes = ?, completed_at = ?
    WHERE id = ?
    """, (status_val, action_val, notes_val, completed_at, id))
    conn.commit()
    conn.close()
    return jsonify({
        "success": True,
        "message": f"Intervention updated successfully to {status_val}"
    })


@app.route("/api/students", methods=["POST"])
@login_required
@role_required("admin")
def add_student():
    """
    Provisions a new student, computes explainable metrics, and creates user login.
    Permanently persists record in SQLite with transactional integrity.
    """
    data = request.get_json(silent=True) or request.form.to_dict() or {}
    s_id = (data.get("student_id") or data.get("roll_number") or data.get("username") or "").strip()
    name = data.get("name", "").strip()
    email = data.get("email", "").strip() or f"{s_id.lower()}@campusiq.edu"
    dept = data.get("department", "CSE").strip().upper()
    password = (data.get("password") or "Student@123").strip()
    section = data.get("section", "A").strip()
    phone = data.get("phone", "+91 9800000000").strip()
    gender = data.get("gender", "Not Specified").strip()

    # Server-side validation of mandatory fields
    if not s_id:
        return jsonify({"error": "Bad Request", "message": "Student ID / Roll number is required."}), 400
    if not name:
        return jsonify({"error": "Bad Request", "message": "Student full name is required."}), 400
    if not dept:
        return jsonify({"error": "Bad Request", "message": "Department is required."}), 400

    # Safe numerical parsing & range validation
    try:
        sem = int(data.get("semester", 6))
        if sem < 1 or sem > 8:
            sem = 6
    except (ValueError, TypeError):
        sem = 6

    try:
        cgpa = float(data.get("cgpa", 7.5))
        if cgpa < 0.0 or cgpa > 10.0:
            return jsonify({"error": "Bad Request", "message": "CGPA must be between 0.0 and 10.0."}), 400
    except (ValueError, TypeError):
        return jsonify({"error": "Bad Request", "message": "Invalid numeric format for CGPA."}), 400

    try:
        attendance = float(data.get("attendance_pct", 80.0))
        if attendance < 0.0 or attendance > 100.0:
            return jsonify({"error": "Bad Request", "message": "Attendance percentage must be between 0 and 100."}), 400
    except (ValueError, TypeError):
        return jsonify({"error": "Bad Request", "message": "Invalid numeric format for Attendance percentage."}), 400

    try:
        backlogs = int(data.get("backlogs", 0))
        if backlogs < 0:
            return jsonify({"error": "Bad Request", "message": "Backlogs cannot be negative."}), 400
    except (ValueError, TypeError):
        return jsonify({"error": "Bad Request", "message": "Invalid numeric format for Backlogs."}), 400

    try:
        aptitude = float(data.get("placement_aptitude_score", 70.0))
    except (ValueError, TypeError):
        aptitude = 70.0

    try:
        tech = float(data.get("technical_skills_score", 75.0))
    except (ValueError, TypeError):
        tech = 75.0

    academic_marks = float(data.get("academic_marks_pct", round(min(100.0, cgpa * 9.5), 1)))
    lms_hours = float(data.get("lms_weekly_hours", 10.0))
    lms_score = float(data.get("lms_engagement_score", 75.0))
    assignment_pct = float(data.get("assignment_completion_pct", 80.0))
    extracurricular = float(data.get("extracurricular_score", 70.0))
    feedback = float(data.get("student_feedback_score", 4.0))

    conn = get_db()
    cursor = conn.cursor()

    try:
        # 1. Enforce uniqueness against users and students tables
        cursor.execute("SELECT user_id FROM users WHERE user_id = ? OR email = ?", (s_id, email))
        if cursor.fetchone():
            return jsonify({
                "error": "Conflict",
                "message": f"User ID '{s_id}' or Email '{email}' is already registered in the system."
            }), 409

        cursor.execute("SELECT student_id FROM students WHERE student_id = ? OR user_id = ?", (s_id, s_id))
        if cursor.fetchone():
            return jsonify({
                "error": "Conflict",
                "message": f"Student record with ID '{s_id}' already exists."
            }), 409

        # 2. Enrich department metadata & faculty mentor
        cursor.execute("SELECT name, hod_name FROM departments WHERE code = ?", (dept,))
        dept_row = cursor.fetchone()
        dept_name = dept_row["name"] if dept_row else dept
        mentor = data.get("mentor_name") or (dept_row["hod_name"] if dept_row else "Dr. Sunita Rao")
        fac_id = data.get("faculty_id", "faculty001")

        # 3. Compute explainable metrics
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

        # 4. Hash password securely (PBKDF2)
        hashed = generate_password_hash(password)

        # 5. Parameterized INSERT into users table for student authentication
        cursor.execute("""
        INSERT INTO users (user_id, password_hash, role, name, email, department)
        VALUES (?, ?, 'student', ?, ?, ?)
        """, (s_id, hashed, name, email, dept))

        # 6. Parameterized INSERT into students table
        cursor.execute("""
        INSERT INTO students (
            student_id, user_id, name, email, gender, department, department_name,
            semester, section, faculty_id, mentor_name, cgpa, academic_marks_pct,
            attendance_pct, backlogs, lms_weekly_hours, lms_engagement_score,
            assignment_completion_pct, extracurricular_score, placement_aptitude_score,
            technical_skills_score, student_feedback_score, phone, success_score, risk_level, segment
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            s_id, s_id, name, email, gender, dept, dept_name, sem, section,
            fac_id, mentor, cgpa, academic_marks, attendance, backlogs,
            lms_hours, lms_score, assignment_pct, extracurricular,
            aptitude, tech, feedback, phone, metrics["success_score"], metrics["risk_level"], metrics["segment"]
        ))

        # 7. Update department student count
        cursor.execute("UPDATE departments SET student_count = student_count + 1 WHERE code = ?", (dept,))

        # 8. Seed default fee record for current semester
        acad_yr_num = (sem + 1) // 2
        sem_label = f"{acad_yr_num}-{1 if sem % 2 != 0 else 2}"
        cursor.execute("""
        INSERT INTO student_fees (
            student_id, academic_year, year, semester, semester_label, total_fee, amount_paid, due_date
        ) VALUES (?, ?, ?, ?, ?, 65000.0, 65000.0, '2026-06-30')
        """, (s_id, f"2025-2026", acad_yr_num, sem, sem_label))

        # 9. Commit transaction to permanently persist in SQLite
        conn.commit()

    except Exception as e:
        conn.rollback()
        return jsonify({"error": "Database Error", "message": f"Failed to save student record: {str(e)}"}), 500
    finally:
        conn.close()

    return jsonify({
        "success": True,
        "message": f"Student '{name}' ({s_id}) successfully created and saved permanently.",
        "student_id": s_id,
        "user_id": s_id
    }), 201


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
    """Returns alerts and interventions for logged-in user with unread count."""
    user_id = session.get("user_id")
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT n.*, i.student_id as intv_student_id, i.title as intv_title,
           i.priority as intv_priority, i.instructions as intv_instructions,
           i.notes as intv_notes, i.due_date as intv_due_date,
           i.status as intv_status, i.action_taken as intv_action_taken,
           i.implementation_notes as intv_impl_notes,
           s.name as student_name, s.department as student_dept
    FROM notifications n
    LEFT JOIN interventions i ON n.intervention_id = i.id
    LEFT JOIN students s ON i.student_id = s.student_id
    WHERE n.user_id = ? OR n.user_id = 'all'
    ORDER BY n.created_at DESC
    """, (user_id,))
    rows = [dict(r) for r in cursor.fetchall()]

    # Compute unread count for logged-in user
    cursor.execute("""
    SELECT COUNT(*) as unread_count
    FROM notifications
    WHERE (user_id = ? OR user_id = 'all') AND (is_read = 0 OR is_read IS NULL)
    """, (user_id,))
    unread_count = cursor.fetchone()["unread_count"]

    conn.close()
    return jsonify({
        "notifications": rows,
        "unread_count": unread_count
    })


@app.route("/api/notifications/<int:id>/read", methods=["POST", "PUT"])
@login_required
def mark_notification_read(id):
    """Marks a notification as read for authorized recipient and updates read timestamp."""
    user_id = session.get("user_id")
    role = session.get("role")

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM notifications WHERE id = ?", (id,))
    notif = cursor.fetchone()
    if not notif:
        conn.close()
        return jsonify({"error": "Not Found", "message": "Notification not found"}), 404

    # Recipient verification: user must be the intended recipient or 'all' or admin
    if notif["user_id"] != user_id and notif["user_id"] != "all" and role != "admin":
        conn.close()
        return jsonify({"error": "Forbidden", "message": "Unauthorized to access this notification"}), 403

    import datetime
    now_ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("UPDATE notifications SET is_read = 1, read_at = ? WHERE id = ?", (now_ts, id))
    conn.commit()

    # Remaining unread count
    cursor.execute("""
    SELECT COUNT(*) as unread_count
    FROM notifications
    WHERE (user_id = ? OR user_id = 'all') AND (is_read = 0 OR is_read IS NULL)
    """, (user_id,))
    remaining_unread = cursor.fetchone()["unread_count"]
    conn.close()

    return jsonify({
        "success": True,
        "message": "Notification marked as read",
        "unread_count": remaining_unread
    })


# ==============================================================================
# 5.1 ACADEMIC RECORDS API (Student Dashboard)
# ==============================================================================

@app.route("/api/student/academic-records", methods=["GET"])
@login_required
@role_required("student")
def get_student_academic_records():
    """Returns the authenticated student's complete multi-year and multi-semester academic records.
    
    Supports optional query filters:
    - year: int or str (1, 2, 3, 4)
    - semester: str ('1-1', '1-2', etc.)
    - search: str (matches course_code or course_name)
    """
    current_user_id = session.get("user_id")
    if not current_user_id:
        return jsonify({"error": "Unauthorized", "message": "Please log in"}), 401

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM students WHERE student_id = ? OR user_id = ?", (current_user_id, current_user_id))
    student_row = cursor.fetchone()
    if not student_row:
        conn.close()
        return jsonify({"error": "Not Found", "message": "Student profile not found"}), 404

    s = dict(student_row)
    canonical_id = s["student_id"]

    # Optional query parameters
    filter_year = request.args.get("year", "").strip()
    filter_sem = request.args.get("semester", "").strip()
    search_q = request.args.get("search", "").strip().lower()

    # Query academic records for this student
    query = "SELECT * FROM academic_records WHERE student_id = ?"
    params = [canonical_id]

    if filter_year:
        try:
            query += " AND year = ?"
            params.append(int(filter_year))
        except ValueError:
            pass

    if filter_sem:
        query += " AND (semester_label = ? OR semester = ?)"
        params.extend([filter_sem, filter_sem])

    query += " ORDER BY year ASC, semester ASC, course_code ASC"

    cursor.execute(query, params)
    records = [dict(r) for r in cursor.fetchall()]

    # If search filter is provided, filter records by course_code or course_name
    if search_q:
        records = [r for r in records if search_q in (r.get("course_code") or "").lower() or search_q in (r.get("course_name") or "").lower()]

    # Query summary metrics across all records
    cursor.execute("""
    SELECT 
        COUNT(*) as total_courses,
        SUM(CASE WHEN status = 'Passed' THEN 1 ELSE 0 END) as passed_courses,
        SUM(CASE WHEN status != 'Passed' THEN 1 ELSE 0 END) as backlog_count,
        SUM(classes_conducted) as total_conducted,
        SUM(classes_attended) as total_attended
    FROM academic_records
    WHERE student_id = ?
    """, (canonical_id,))
    summary_row = cursor.fetchone()

    cursor.execute("""
    SELECT course_name FROM academic_records
    WHERE student_id = ? AND status != 'Passed'
    ORDER BY year ASC, semester ASC
    """, (canonical_id,))
    backlog_subjects = [r["course_name"] for r in cursor.fetchall()]

    conn.close()

    total_courses = summary_row["total_courses"] if summary_row and summary_row["total_courses"] else 0
    passed_courses = summary_row["passed_courses"] if summary_row and summary_row["passed_courses"] else 0
    backlog_count = summary_row["backlog_count"] if summary_row and summary_row["backlog_count"] is not None else int(s.get("backlogs", 0))
    tot_cond = summary_row["total_conducted"] if summary_row and summary_row["total_conducted"] else 0
    tot_att = summary_row["total_attended"] if summary_row and summary_row["total_attended"] else 0
    overall_attendance = round((tot_att / tot_cond * 100), 1) if tot_cond > 0 else float(s.get("attendance_pct", 0.0))

    # Group records by semester for structured hierarchy
    semesters_dict = {}
    for r in records:
        sem_key = r.get("semester_label") or str(r["semester"])
        if sem_key not in semesters_dict:
            semesters_dict[sem_key] = {
                "semester": sem_key,
                "semester_num": r["semester"],
                "year": r["year"],
                "academic_year": r["academic_year"],
                "sgpa": r["sgpa"],
                "courses": []
            }
        semesters_dict[sem_key]["courses"].append(r)

    # Compute current academic year
    current_year_num = (int(s.get("semester", 6)) + 1) // 2 if s.get("semester") else 3

    return jsonify({
        "student": {
            "name": s.get("name", "Not available"),
            "student_id": s.get("student_id", "Not available"),
            "department": s.get("department", "Not available"),
            "current_year": f"Year {current_year_num}",
            "current_semester": f"Semester {s.get('semester', 'Not available')}",
            "cgpa": float(s.get("cgpa", 0.0)) if s.get("cgpa") is not None else None,
            "risk_level": s.get("risk_level", "Medium"),
            "mentor_name": s.get("mentor_name", "Not available")
        },
        "summary": {
            "total_courses": total_courses,
            "passed_courses": passed_courses,
            "backlog_count": backlog_count,
            "backlog_subjects": backlog_subjects,
            "overall_attendance_pct": overall_attendance,
            "attendance_shortage": overall_attendance < 75.0,
            "cgpa": float(s.get("cgpa", 0.0)) if s.get("cgpa") is not None else None
        },
        "records": records,
        "semesters": list(semesters_dict.values()),
        "total_results": len(records)
    })


# ==============================================================================
# 5.2 SEMESTER FEE DETAILS API (Student Dashboard)
# ==============================================================================

@app.route("/student/fee-details")
@app.route("/student/fees")
@login_required
@role_required("student")
def student_fee_details_page():
    """Direct URL access to the student's Fee Details section."""
    return redirect(url_for("student_dashboard") + "#section-fee-details")


@app.route("/api/student/fee-details", methods=["GET"])
@login_required
@role_required("student")
def get_student_fee_details():
    """Returns the authenticated student's semester-wise fee records and summary metrics.
    Strictly server-side isolated to current session student.
    """
    current_user_id = session.get("user_id")
    if not current_user_id:
        return jsonify({"error": "Unauthorized", "message": "Please log in"}), 401

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM students WHERE student_id = ? OR user_id = ?", (current_user_id, current_user_id))
    student_row = cursor.fetchone()
    if not student_row:
        conn.close()
        return jsonify({"error": "Not Found", "message": "Student profile not found"}), 404

    s = dict(student_row)
    canonical_id = s["student_id"]

    cursor.execute("""
    SELECT * FROM student_fees WHERE student_id = ? ORDER BY year ASC, semester ASC
    """, (canonical_id,))
    fee_rows = [dict(r) for r in cursor.fetchall()]
    conn.close()

    from datetime import date
    today_str = date.today().isoformat()

    total_fees = 0.0
    total_paid = 0.0
    total_due = 0.0
    next_due_date = None

    for fr in fee_rows:
        t_fee = float(fr.get("total_fee") or 0.0)
        a_paid = float(fr.get("amount_paid") or 0.0)
        rem_due = max(0.0, round(t_fee - a_paid, 2))
        fr["remaining_due"] = rem_due

        d_date = fr.get("due_date")
        if rem_due <= 0.0:
            fr["status"] = "Paid"
        elif d_date and d_date < today_str:
            fr["status"] = "Overdue"
        elif a_paid > 0.0:
            fr["status"] = "Partially Paid"
        else:
            fr["status"] = "Due"

        total_fees += t_fee
        total_paid += a_paid
        total_due += rem_due

        if rem_due > 0 and d_date and d_date >= today_str:
            if next_due_date is None or d_date < next_due_date:
                next_due_date = d_date

    current_year_num = (int(s.get("semester", 6)) + 1) // 2 if s.get("semester") else 3

    return jsonify({
        "student": {
            "name": s.get("name", "Not available"),
            "student_id": s.get("student_id", "Not available"),
            "department": s.get("department", "Not available"),
            "current_year": f"Year {current_year_num}",
            "current_semester": f"Semester {s.get('semester', 'Not available')}",
            "mentor_name": s.get("mentor_name", "Not available")
        },
        "summary": {
            "total_fees": round(total_fees, 2),
            "total_paid": round(total_paid, 2),
            "total_due": round(total_due, 2),
            "next_due_date": next_due_date or ("Not available" if total_due > 0 else "None pending")
        },
        "records": fee_rows,
        "total_results": len(fee_rows)
    })


# ==============================================================================
# 5B. STUDENT PLACEMENT & SKILLS API (Dynamic Matching)
# ==============================================================================

@app.route("/api/student/skills", methods=["GET"])
@login_required
@role_required("student")
def get_student_skills():
    """Returns saved skills for authenticated student, strictly isolated by session."""
    user_id = session.get("user_id")
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT student_id FROM students WHERE student_id = ? OR user_id = ?", (user_id, user_id))
    s_row = cursor.fetchone()
    canonical_id = s_row["student_id"] if s_row else user_id

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS student_skills (
        student_id TEXT PRIMARY KEY,
        skills TEXT NOT NULL DEFAULT '[]',
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (student_id) REFERENCES students(student_id)
    );
    """)
    cursor.execute("SELECT skills FROM student_skills WHERE student_id = ?", (canonical_id,))
    row = cursor.fetchone()
    conn.close()

    import json
    skills = []
    if row and row["skills"]:
        try:
            skills = json.loads(row["skills"])
        except Exception:
            skills = [s.strip() for s in row["skills"].split(",") if s.strip()]
    return jsonify({"success": True, "skills": skills})


@app.route("/api/student/skills", methods=["POST"])
@login_required
@role_required("student")
def save_student_skills():
    """Saves updated skill list for authenticated student strictly isolated by session."""
    user_id = session.get("user_id")
    data = request.get_json(silent=True) or {}
    raw_skills = data.get("skills", [])
    if not isinstance(raw_skills, list):
        return jsonify({"error": "Bad Request", "message": "Skills must be an array of strings."}), 400

    clean_skills = []
    seen = set()
    for s in raw_skills:
        if isinstance(s, str):
            trimmed = s.strip()
            if trimmed and len(trimmed) <= 60 and trimmed.lower() not in seen:
                seen.add(trimmed.lower())
                clean_skills.append(trimmed)
        if len(clean_skills) >= 50:
            break

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT student_id FROM students WHERE student_id = ? OR user_id = ?", (user_id, user_id))
    s_row = cursor.fetchone()
    canonical_id = s_row["student_id"] if s_row else user_id

    import json
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS student_skills (
        student_id TEXT PRIMARY KEY,
        skills TEXT NOT NULL DEFAULT '[]',
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (student_id) REFERENCES students(student_id)
    );
    """)
    cursor.execute("""
    INSERT INTO student_skills (student_id, skills, updated_at)
    VALUES (?, ?, CURRENT_TIMESTAMP)
    ON CONFLICT(student_id) DO UPDATE SET
        skills = excluded.skills,
        updated_at = CURRENT_TIMESTAMP
    """, (canonical_id, json.dumps(clean_skills)))
    conn.commit()
    conn.close()

    return jsonify({"success": True, "skills": clean_skills, "message": "Skills saved successfully."})


@app.route("/api/student/placement/match", methods=["POST"])
@login_required
@role_required("student")
def match_placement_opportunities():
    """Computes dynamic company match and eligibility for authenticated student based on entered/saved skills."""
    user_id = session.get("user_id")
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM students WHERE student_id = ? OR user_id = ?", (user_id, user_id))
    s_row = cursor.fetchone()
    if not s_row:
        conn.close()
        return jsonify({"error": "Not Found", "message": "Student profile not found"}), 404

    student = dict(s_row)
    canonical_id = student["student_id"]

    data = request.get_json(silent=True) or {}
    raw_skills = data.get("skills")

    import json
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS student_skills (
        student_id TEXT PRIMARY KEY,
        skills TEXT NOT NULL DEFAULT '[]',
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (student_id) REFERENCES students(student_id)
    );
    """)

    if raw_skills is None:
        cursor.execute("SELECT skills FROM student_skills WHERE student_id = ?", (canonical_id,))
        skill_row = cursor.fetchone()
        if skill_row and skill_row["skills"]:
            try:
                raw_skills = json.loads(skill_row["skills"])
            except Exception:
                raw_skills = [s.strip() for s in skill_row["skills"].split(",") if s.strip()]
        else:
            raw_skills = []
    elif isinstance(raw_skills, list) and data.get("save_skills", False):
        clean_skills = []
        seen = set()
        for s in raw_skills:
            if isinstance(s, str):
                trimmed = s.strip()
                if trimmed and len(trimmed) <= 60 and trimmed.lower() not in seen:
                    seen.add(trimmed.lower())
                    clean_skills.append(trimmed)
            if len(clean_skills) >= 50:
                break
        cursor.execute("""
        INSERT INTO student_skills (student_id, skills, updated_at)
        VALUES (?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(student_id) DO UPDATE SET
            skills = excluded.skills,
            updated_at = CURRENT_TIMESTAMP
        """, (canonical_id, json.dumps(clean_skills)))
        conn.commit()
        raw_skills = clean_skills

    conn.close()

    from services.placement import match_companies_for_student
    result = match_companies_for_student(raw_skills, student)
    result["success"] = True
    return jsonify(result)


# ==============================================================================
# 5C. STUDENT CAREER ROADMAP & JOB PREPARATION API
# ==============================================================================

@app.route("/api/student/roadmap", methods=["GET"])
@login_required
@role_required("student")
def get_student_career_roadmap():
    """Returns the authenticated student's saved career plan and target role roadmap data."""
    user_id = session.get("user_id")
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM students WHERE student_id = ? OR user_id = ?", (user_id, user_id))
    s_row = cursor.fetchone()
    if not s_row:
        conn.close()
        return jsonify({"error": "Not Found", "message": "Student record not found"}), 404

    student = dict(s_row)
    canonical_id = student["student_id"]

    # Ensure career roadmap table exists
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS student_career_plan (
        student_id TEXT PRIMARY KEY,
        target_role TEXT NOT NULL DEFAULT 'Software Developer',
        timeline_days INTEGER NOT NULL DEFAULT 60,
        daily_hours INTEGER NOT NULL DEFAULT 2,
        skill_level TEXT NOT NULL DEFAULT 'Beginner',
        preferred_language TEXT NOT NULL DEFAULT 'Python',
        skill_assessments TEXT NOT NULL DEFAULT '{}',
        completed_tasks TEXT NOT NULL DEFAULT '[]',
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (student_id) REFERENCES students(student_id)
    );
    """)

    cursor.execute("SELECT * FROM student_career_plan WHERE student_id = ?", (canonical_id,))
    plan_row = cursor.fetchone()

    # Also fetch any saved skills from student_skills table for baseline integration
    cursor.execute("SELECT skills FROM student_skills WHERE student_id = ?", (canonical_id,))
    skill_row = cursor.fetchone()
    conn.close()

    import json
    from services.roadmap import get_role_data, CAREER_ROLES, INTERVIEW_PREP_BANK

    saved_skills = []
    if skill_row and skill_row["skills"]:
        try:
            saved_skills = json.loads(skill_row["skills"])
        except Exception:
            saved_skills = [s.strip() for s in skill_row["skills"].split(",") if s.strip()]

    target_role = "Software Developer"
    timeline_days = 60
    daily_hours = 2
    skill_level = "Beginner"
    preferred_language = "Python"
    skill_assessments = {}
    completed_tasks = []

    if plan_row:
        target_role = plan_row["target_role"] or "Software Developer"
        timeline_days = plan_row["timeline_days"] or 60
        daily_hours = plan_row["daily_hours"] or 2
        skill_level = plan_row["skill_level"] or "Beginner"
        preferred_language = plan_row["preferred_language"] or "Python"
        try:
            skill_assessments = json.loads(plan_row["skill_assessments"] or "{}")
        except Exception:
            skill_assessments = {}
        try:
            completed_tasks = json.loads(plan_row["completed_tasks"] or "[]")
        except Exception:
            completed_tasks = []

    # If student has skills in student_skills but not assessed yet, pre-populate as 'Practiced'
    for sk in saved_skills:
        if sk not in skill_assessments:
            skill_assessments[sk] = "Practiced"

    role_data = get_role_data(target_role)

    # Calculate skill gaps
    all_role_skills = role_data.get("core_skills", []) + role_data.get("optional_skills", [])
    skills_known = []
    skills_learning = []
    skills_needed = []

    for sk in all_role_skills:
        status = skill_assessments.get(sk, "Not Started")
        if status in ["Practiced", "Confident"]:
            skills_known.append({"skill": sk, "status": status, "is_core": sk in role_data.get("core_skills", [])})
        elif status == "Learning":
            skills_learning.append({"skill": sk, "status": status, "is_core": sk in role_data.get("core_skills", [])})
        else:
            skills_needed.append({"skill": sk, "status": "Not Started", "is_core": sk in role_data.get("core_skills", [])})

    # Total roadmap tasks count
    all_tasks = []
    for stage in role_data.get("stages", []):
        for task in stage.get("practical_tasks", []):
            task_key = f"s{stage['stage_num']}_{task[:30]}"
            all_tasks.append(task_key)

    total_tasks_count = len(all_tasks)
    completed_tasks_count = sum(1 for t in all_tasks if t in completed_tasks)

    # Compute Readiness percentage:
    # 50% weight from Core Skills (Known = 100%, Learning = 50%), 50% weight from Roadmap Tasks completed
    core_skills_list = role_data.get("core_skills", [])
    core_score = 0
    if core_skills_list:
        for cs in core_skills_list:
            st = skill_assessments.get(cs, "Not Started")
            if st in ["Practiced", "Confident"]:
                core_score += 1.0
            elif st == "Learning":
                core_score += 0.5
        core_pct = (core_score / len(core_skills_list)) * 100.0
    else:
        core_pct = 0.0

    task_pct = (completed_tasks_count / total_tasks_count * 100.0) if total_tasks_count > 0 else 0.0
    readiness_percentage = round((core_pct * 0.5) + (task_pct * 0.5), 1)

    return jsonify({
        "success": True,
        "student": {
            "name": student.get("name"),
            "student_id": student.get("student_id"),
            "department": student.get("department"),
            "semester": student.get("semester"),
            "academic_year": ((student.get("semester", 6) - 1) // 2) + 1,
            "cgpa": student.get("cgpa")
        },
        "plan": {
            "target_role": target_role,
            "timeline_days": timeline_days,
            "daily_hours": daily_hours,
            "skill_level": skill_level,
            "preferred_language": preferred_language,
            "skill_assessments": skill_assessments,
            "completed_tasks": completed_tasks
        },
        "role_data": role_data,
        "available_roles": list(CAREER_ROLES.keys()),
        "skill_gap": {
            "skills_known": skills_known,
            "skills_learning": skills_learning,
            "skills_needed": skills_needed,
            "known_count": len(skills_known),
            "learning_count": len(skills_learning),
            "needed_count": len(skills_needed)
        },
        "progress": {
            "readiness_percentage": readiness_percentage,
            "core_skills_coverage_pct": round(core_pct, 1),
            "roadmap_tasks_completed": completed_tasks_count,
            "roadmap_tasks_total": total_tasks_count,
            "calculation_basis": "50% weighted core skill assessments (Practiced/Confident) + 50% weighted roadmap stage practical task completions."
        },
        "interview_prep": INTERVIEW_PREP_BANK
    })


@app.route("/api/student/roadmap", methods=["POST"])
@login_required
@role_required("student")
def save_student_career_roadmap():
    """Saves updated career plan, target role, skill assessments, and completed roadmap tasks."""
    user_id = session.get("user_id")
    data = request.get_json(silent=True) or {}

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT student_id FROM students WHERE student_id = ? OR user_id = ?", (user_id, user_id))
    s_row = cursor.fetchone()
    if not s_row:
        conn.close()
        return jsonify({"error": "Not Found", "message": "Student profile not found"}), 404

    canonical_id = s_row["student_id"]

    target_role = (data.get("target_role") or "Software Developer").strip()
    timeline_days_raw = str(data.get("timeline_days") or "60").strip()
    try:
        timeline_days = int("".join(filter(str.isdigit, timeline_days_raw)) or 60)
    except Exception:
        timeline_days = 60
    daily_hours = str(data.get("daily_hours") or "2-3").strip()
    skill_level = (data.get("skill_level") or "Beginner").strip()
    preferred_language = (data.get("preferred_language") or "Python").strip()

    raw_assessments = data.get("skill_assessments") or {}
    raw_tasks = data.get("completed_tasks") or []

    import json
    clean_assessments = {}
    valid_statuses = {"Not Started", "Learning", "Practiced", "Confident"}
    for k, v in raw_assessments.items():
        if isinstance(k, str) and len(k) <= 80 and v in valid_statuses:
            clean_assessments[k.strip()] = v

    clean_tasks = [str(t).strip() for t in raw_tasks if isinstance(t, str) and len(str(t).strip()) <= 100]

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS student_career_plan (
        student_id TEXT PRIMARY KEY,
        target_role TEXT NOT NULL DEFAULT 'Software Developer',
        timeline_days INTEGER NOT NULL DEFAULT 60,
        daily_hours INTEGER NOT NULL DEFAULT 2,
        skill_level TEXT NOT NULL DEFAULT 'Beginner',
        preferred_language TEXT NOT NULL DEFAULT 'Python',
        skill_assessments TEXT NOT NULL DEFAULT '{}',
        completed_tasks TEXT NOT NULL DEFAULT '[]',
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (student_id) REFERENCES students(student_id)
    );
    """)

    cursor.execute("""
    INSERT INTO student_career_plan (
        student_id, target_role, timeline_days, daily_hours, skill_level,
        preferred_language, skill_assessments, completed_tasks, updated_at
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
    ON CONFLICT(student_id) DO UPDATE SET
        target_role = excluded.target_role,
        timeline_days = excluded.timeline_days,
        daily_hours = excluded.daily_hours,
        skill_level = excluded.skill_level,
        preferred_language = excluded.preferred_language,
        skill_assessments = excluded.skill_assessments,
        completed_tasks = excluded.completed_tasks,
        updated_at = CURRENT_TIMESTAMP
    """, (
        canonical_id, target_role, timeline_days, daily_hours, skill_level,
        preferred_language, json.dumps(clean_assessments), json.dumps(clean_tasks)
    ))

    # Also keep student_skills table synced with skills marked Practiced or Confident
    confident_skills = [sk for sk, st in clean_assessments.items() if st in ["Practiced", "Confident"]]
    if confident_skills:
        cursor.execute("""
        INSERT INTO student_skills (student_id, skills, updated_at)
        VALUES (?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(student_id) DO UPDATE SET
            skills = excluded.skills,
            updated_at = CURRENT_TIMESTAMP
        """, (canonical_id, json.dumps(confident_skills)))

    conn.commit()
    conn.close()

    # Return refreshed roadmap state for the student
    return get_student_career_roadmap()



# ==============================================================================
# 6. CHATBOT STUDY ASSISTANT API (Student Dashboard)
# ==============================================================================

@app.route("/api/student/chat", methods=["POST"])
@login_required
@role_required("student")
def student_chat():
    """Multilingual Study Assistant chatbot endpoint for the Student Dashboard."""
    data = request.get_json(silent=True) or {}
    message = (data.get("message") or "").strip()

    if not message or len(message) > 1000:
        return jsonify({"error": "Invalid message", "reply": "Please enter a valid message (1-1000 characters)."}), 400

    # Load the authenticated student's real data
    student_id = session.get("user_id")
    canonical_id = session.get("student_id") or student_id
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM students 
        WHERE student_id = ? OR user_id = ? OR student_id = ?
    """, (canonical_id, student_id, student_id))
    student_row = cursor.fetchone()

    # Query active backlog subjects from academic_records if present
    backlog_subjects = ""
    if student_row:
        cursor.execute("""
            SELECT GROUP_CONCAT(course_name, ', ') AS subjects 
            FROM academic_records 
            WHERE student_id = ? AND LOWER(status) != 'passed'
        """, (student_row["student_id"],))
        b_row = cursor.fetchone()
        if b_row and b_row["subjects"]:
            backlog_subjects = b_row["subjects"]
    conn.close()

    if not student_row:
        return jsonify({"reply": "I couldn't find your student profile. Please try logging in again."})

    s = dict(student_row)
    if backlog_subjects:
        s["backlog_subjects"] = backlog_subjects
    metrics = analytics_engine.compute_student_metrics(s)

    result = generate_multilingual_chat_reply(message, s, metrics, session)
    return jsonify(result)


def _generate_chat_reply(msg, s, metrics):
    """Generates a personalized rule-based response using the student's actual data."""
    name = s.get("name", "").split()[0]
    cgpa = float(s.get("cgpa", 0))
    attendance = float(s.get("attendance_pct", 0))
    backlogs = int(s.get("backlogs", 0))
    success_score = float(s.get("success_score", 0))
    risk_level = s.get("risk_level", "Medium")
    lms_hours = float(s.get("lms_weekly_hours", 0))
    assignment_pct = float(s.get("assignment_completion_pct", 0))
    aptitude = float(s.get("placement_aptitude_score", 0))
    tech = float(s.get("technical_skills_score", 0))
    department = s.get("department", "")
    semester = s.get("semester", "")

    # --- Pattern matching for common topics ---

    # Risk / how to reduce risk (checked before general academic keywords)
    if any(k in msg for k in ["risk", "reduce risk", "lower risk", "improve risk", "high risk", "medium risk", "low risk", "debarment"]):
        lines = [f"Your current risk level is {risk_level}, {name} (Success Score: {success_score}/100)."]
        if risk_level == "Low":
            lines.append("You're in great standing! To maintain Low Risk:")
            lines.append("• Keep your attendance above 80% and CGPA above 8.0.")
            lines.append("• Stay consistent with LMS assignments and placement prep.")
        elif risk_level == "Medium":
            lines.append("To move from Medium to Low Risk, focus on:")
            if attendance < 78:
                lines.append(f"• Boost your attendance from {attendance}% to above 80%.")
            if backlogs > 0:
                lines.append(f"• Clear your {backlogs} active backlog(s) in the next exam cycle.")
            if assignment_pct < 70:
                lines.append(f"• Improve assignment submission rate from {assignment_pct}% to above 80%.")
            if aptitude < 65 or tech < 70:
                lines.append(f"• Work on placement skills — your aptitude is {aptitude}/100 and tech skills are {tech}/100.")
            lines.append("• Use the What-If Simulator on your dashboard to see how specific improvements affect your score.")
        else:
            lines.append("Here's an urgent action plan to reduce your risk level:")
            if attendance < 75:
                lines.append(f"• 🚨 CRITICAL: Improve attendance from {attendance}% — attend every class from now on.")
            if backlogs >= 2:
                lines.append(f"• 🚨 CRITICAL: You have {backlogs} backlogs — request peer tutoring support from your department.")
            if cgpa < 6.0:
                lines.append(f"• Focus on improving your CGPA ({cgpa}) — prioritize core subjects.")
            lines.append("• Meet your faculty advisor immediately for a personalized recovery plan.")
            lines.append("• The What-If Simulator can show you exactly how much each improvement helps.")
        return "\n".join(lines)

    # Study plan / schedule (checked before generic help)
    if any(k in msg for k in ["study plan", "study schedule", "timetable", "revision", "how to study", "plan my"]):
        plan_lines = [f"Here's a personalized study plan suggestion for you, {name} ({department} Sem {semester}):"]
        if backlogs > 0:
            plan_lines.append(f"\n📌 Priority: Clear {backlogs} backlog(s)")
            plan_lines.append("• Dedicate 1.5 hours daily specifically to backlog subjects.")
            plan_lines.append("• Solve at least 3 previous year question papers per backlog subject.")
        if attendance < 75:
            plan_lines.append("\n📌 Attendance Recovery:")
            plan_lines.append("• Mark all remaining class slots as non-negotiable in your calendar.")
        plan_lines.append("\n📅 Suggested Daily Routine:")
        if cgpa < 7.0:
            plan_lines.append("• Morning (1.5 hrs): Revise yesterday's lecture notes and core concepts.")
            plan_lines.append("• Afternoon (1 hr): Solve practice problems from your weakest subject.")
            plan_lines.append("• Evening (1 hr): Complete pending LMS assignments and lab work.")
            plan_lines.append("• Night (30 min): Quick review of tomorrow's lecture topics.")
        else:
            plan_lines.append("• Morning (1 hr): Advanced problem solving and competitive coding practice.")
            plan_lines.append("• Afternoon (45 min): Review lecture material and take LMS quizzes.")
            plan_lines.append("• Evening (1 hr): Work on projects, assignments, or placement preparation.")
        if lms_hours < 8:
            plan_lines.append(f"\n💡 Tip: Your LMS study time is {lms_hours} hrs/week. Try to increase it to at least 10 hrs/week for better results.")
        return "\n".join(plan_lines)

    # Recommendations / explain recommendations
    if any(k in msg for k in ["recommendation", "my recommendation", "explain my", "what should i", "action plan", "roadmap"]):
        recs = []
        recs.append(f"Here's a summary of your personalized recommendations, {name}:")
        recs.append(f"\n📊 Your Success Score: {success_score}/100 ({risk_level} Risk)")
        if metrics.get("recommended_interventions"):
            for i, intv in enumerate(metrics["recommended_interventions"], 1):
                recs.append(f"\n{i}. {intv['action']}")
                recs.append(f"   Why: {intv['rationale']}")
                recs.append(f"   Timeline: {intv['timeline']} | Priority: {intv['urgency']}")
        if metrics.get("risk_factors"):
            recs.append("\n⚠️ Key areas needing attention:")
            for rf in metrics["risk_factors"]:
                recs.append(f"  • {rf['title']} ({rf['impact']})")
        if metrics.get("positive_factors"):
            recs.append("\n✅ Your strengths:")
            for pf in metrics["positive_factors"]:
                recs.append(f"  • {pf['title']} ({pf['impact']})")
        return "\n".join(recs)

    # Academic performance / GPA / marks
    if any(k in msg for k in ["academic", "performance", "cgpa", "gpa", "marks", "grades"]):
        tips = []
        if cgpa >= 8.5:
            tips.append(f"Your CGPA of {cgpa} is excellent, {name}! You're in the top tier.")
            tips.append("To maintain this, consider mentoring peers and exploring research opportunities.")
        elif cgpa >= 7.0:
            tips.append(f"Your CGPA is {cgpa}, which is good, {name}. Here's how to push higher:")
            tips.append("• Focus on weaker subjects — revise previous semester topics for 30 min daily.")
            tips.append("• Solve past exam papers to identify recurring question patterns.")
            tips.append("• Attend faculty office hours for subjects where you scored below 80%.")
        else:
            tips.append(f"Your CGPA is currently {cgpa}, {name}. Let's work on improving it:")
            tips.append("• Prioritize clearing fundamentals — revise core concepts 1 hour daily.")
            tips.append("• Create a subject-wise study schedule and stick to it consistently.")
            tips.append("• Form or join a study group with classmates who score well.")
            tips.append("• Use your LMS resources — video lectures and practice quizzes can help.")
        if backlogs > 0:
            tips.append(f"• Important: You have {backlogs} active backlog(s). Focus on clearing these first in the next supplementary exam cycle.")
        return "\n".join(tips)

    # Attendance
    if any(k in msg for k in ["attendance", "absent", "debarment", "classes"]):
        if attendance >= 85:
            return (f"Great news, {name}! Your attendance is {attendance}%, well above the 75% statutory requirement. "
                    f"Keep up the consistency. Regular attendance correlates strongly with better exam performance.")
        elif attendance >= 75:
            return (f"Your attendance is {attendance}%, {name} — you meet the minimum 75% threshold, but there isn't much buffer. "
                    f"Try not to miss any more classes. Here are some tips:\n"
                    f"• Set daily reminders for your class schedule.\n"
                    f"• If you're feeling unwell, inform your faculty advisor so it can be documented.\n"
                    f"• Attend at least the first and last lectures of each day — these often cover key exam material.")
        else:
            deficit = round(75.0 - attendance, 1)
            return (f"⚠️ {name}, your attendance is {attendance}%, which is {deficit}% below the mandatory 75% cutoff. "
                    f"This puts you at risk of exam debarment. Here's what to do immediately:\n"
                    f"• Attend every remaining class without exception.\n"
                    f"• Meet your faculty advisor ({s.get('mentor_name', 'your mentor')}) within the next 2 days to discuss a recovery plan.\n"
                    f"• Some universities allow condonation for medical reasons — check with your department office.\n"
                    f"• Prioritize lab sessions, as missing those has a bigger penalty.")

    # Placement / career
    if any(k in msg for k in ["placement", "career", "job", "internship", "interview", "company", "recruit"]):
        lines = [f"Here's your placement readiness summary, {name}:"]
        lines.append(f"• Aptitude Score: {aptitude}/100")
        lines.append(f"• Technical Skills: {tech}/100")
        if cgpa >= 7.0 and backlogs == 0 and aptitude >= 70:
            lines.append(f"\n✅ You meet the basic eligibility criteria for Tier-1 campus placements!")
            lines.append("To stand out further:")
            lines.append("• Practice competitive coding daily (LeetCode, CodeForces).")
            lines.append("• Build 2-3 solid projects showcasing your skills.")
            lines.append("• Prepare for behavioral interviews with the STAR method.")
        else:
            lines.append("\n📋 To become placement-ready:")
            if cgpa < 7.0:
                lines.append(f"• Raise your CGPA above 7.0 (currently {cgpa}).")
            if backlogs > 0:
                lines.append(f"• Clear all {backlogs} backlog(s) — most companies require zero backlogs.")
            if aptitude < 70:
                lines.append(f"• Improve aptitude score — practice logical reasoning and quantitative problems daily.")
            if tech < 75:
                lines.append(f"• Boost technical skills — solve 2-3 coding problems daily on online platforms.")
        return "\n".join(lines)

    # LMS / assignments / learning
    if any(k in msg for k in ["lms", "assignment", "learning", "submission", "online", "coursework"]):
        lines = [f"Your LMS & assignment statistics, {name}:"]
        lines.append(f"• Weekly LMS Study Hours: {lms_hours} hrs/week")
        lines.append(f"• Assignment Completion Rate: {assignment_pct}%")
        if lms_hours >= 12 and assignment_pct >= 85:
            lines.append("\n✅ Excellent digital engagement! Keep up the consistent effort.")
        else:
            lines.append("\nTips to improve:")
            if lms_hours < 10:
                lines.append(f"• Try to increase your weekly study hours from {lms_hours} to at least 10-12 hours.")
            if assignment_pct < 80:
                lines.append(f"• Submit all pending assignments — even late submissions are better than missing ones.")
            lines.append("• Set a daily 1-hour LMS session right after classes end.")
            lines.append("• Use the LMS discussion forums to ask questions — it boosts your engagement score.")
        return "\n".join(lines)

    # Backlogs
    if any(k in msg for k in ["backlog", "arrear", "supplementary", "re-exam", "clear subject"]):
        if backlogs == 0:
            return f"Great news, {name}! You have no active backlogs. Keep up the strong academic performance!"
        else:
            return (f"You currently have {backlogs} active backlog(s), {name}. Here's how to tackle them:\n\n"
                    f"• Dedicate 1.5 hours daily specifically to backlog subjects.\n"
                    f"• Get previous year question papers — most supplementary exams follow similar patterns.\n"
                    f"• Request peer tutoring from your department.\n"
                    f"• Meet your faculty advisor ({s.get('mentor_name', 'your mentor')}) to discuss a recovery plan.\n"
                    f"• Each cleared backlog improves your success score by approximately 12 points!")

    # Score / success score
    if any(k in msg for k in ["score", "success score", "my score", "how am i doing", "my status"]):
        return (f"Your current Student Success Score is {success_score}/100, {name}.\n"
                f"Risk Level: {risk_level}\n\n"
                f"Pillar Breakdown:\n"
                f"• Academic Mastery: {metrics['pillars']['academic']}/100 (30% weight)\n"
                f"• Attendance: {metrics['pillars']['attendance']}/100 (20% weight)\n"
                f"• LMS Engagement: {metrics['pillars']['lms']}/100 (15% weight)\n"
                f"• Placement Readiness: {metrics['pillars']['placement']}/100 (20% weight)\n"
                f"• Wellbeing: {metrics['pillars']['wellbeing']}/100 (15% weight)\n\n"
                f"Use the What-If Simulator to see how improving specific areas affects your projected score!")

    # Greeting
    if any(k in msg for k in ["hello", "hi", "hey", "good morning", "good evening", "howdy"]):
        return (f"Hello {name}! 👋 I'm your CampusIQ Study Assistant. "
                f"Your current success score is {success_score}/100 ({risk_level} Risk). "
                f"How can I help you today? You can ask me about your academics, attendance, study planning, "
                f"recommendations, placement readiness, or ways to reduce your academic risk.")

    # Thank you
    if any(k in msg for k in ["thank", "thanks", "thx", "appreciate"]):
        return f"You're welcome, {name}! 😊 I'm always here to help. Keep working hard — consistency is the key to success!"

    # Wellbeing / stress (checked before generic help)
    if any(k in msg for k in ["stress", "wellbeing", "mental health", "anxious", "burnout", "overwhelm", "tired"]):
        return (f"Your wellbeing matters, {name}. Here are some suggestions:\n\n"
                f"• Take regular breaks — use the Pomodoro technique (25 min study, 5 min break).\n"
                f"• Physical exercise, even a 20-minute walk, reduces academic stress significantly.\n"
                f"• Talk to your faculty advisor ({s.get('mentor_name', 'your mentor')}) if you're feeling overwhelmed.\n"
                f"• Your campus wellness counselor is available for confidential support sessions.\n"
                f"• Maintain a sleep schedule — 7-8 hours helps memory and concentration.\n"
                f"• Remember: it's okay to ask for help. You're not alone in this journey! 💪")

    # Help / what can you do
    if any(k in msg for k in ["help", "what can you", "options", "features", "what do you"]):
        return (f"I can help you with the following, {name}:\n\n"
                f"📚 **Academic Performance** — CGPA analysis and improvement tips\n"
                f"📅 **Attendance** — Compliance status and recovery strategies\n"
                f"📝 **Study Planning** — Personalized daily study schedules\n"
                f"📊 **Recommendations** — Explain your dashboard recommendations\n"
                f"⚠️ **Risk Reduction** — Steps to lower your academic risk level\n"
                f"💼 **Placement Prep** — Career readiness and eligibility\n"
                f"📖 **LMS & Assignments** — Engagement tips\n"
                f"🏆 **Success Score** — Detailed pillar breakdown\n\n"
                f"Just type your question!")

    # Fallback
    return (f"I'm not sure I fully understood your question, {name}. "
            f"I can help you with topics like:\n"
            f"• Academic performance & CGPA\n"
            f"• Attendance improvement\n"
            f"• Study planning & schedules\n"
            f"• Your dashboard recommendations\n"
            f"• Risk level reduction\n"
            f"• Placement readiness\n"
            f"• LMS and assignments\n\n"
            f"Try asking something like \"How can I improve my attendance?\" or \"Help me make a study plan.\"")


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
