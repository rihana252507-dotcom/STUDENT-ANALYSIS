"""
CampusIQ – AI-Powered Student Analytics and Success Platform
Backend Application (Flask)
KPMG in India Hackathon Challenge

Architecture:
- Modular Explainable AI Analytics Engine (Rule-based multi-factor scoring & risk classification)
- Scikit-learn / XGBoost ML Pipeline Extension Interface
- RESTful API with dynamic aggregation, filtering, search, and intervention logging
- Dynamic Chart.js-ready analytics endpoints
- Static file serving for single-command hackathon evaluation
"""

import os
import csv
import json
from pathlib import Path
from datetime import datetime
from flask import Flask, jsonify, request, send_from_directory, abort

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "data" / "students.csv"
FRONTEND_DIR = BASE_DIR / "frontend"

app = Flask(__name__, static_folder=str(FRONTEND_DIR), static_url_path="")

# ==============================================================================
# 1. EXPLAINABLE AI RISK & SUCCESS ANALYTICS ENGINE
# ==============================================================================

class MLRiskPredictorInterface:
    """
    Extensible Machine Learning Interface.
    Acts as an abstraction boundary: allows drop-in replacement with a serialized
    Scikit-learn / XGBoost pipeline (e.g., joblib.load('models/student_risk_xgb.pkl'))
    without changing frontend API contracts.
    """
    def __init__(self):
        self.model_loaded = False
        self.model_version = "v1.0-explainable-rules"
        self.model_architecture = "Multi-Pillar Weighted Heuristic + Explainable Attribution Engine"

    def predict(self, feature_dict):
        """Placeholder for ML model inference; returns None when no pickled model exists."""
        return None


class StudentAnalyticsEngine:
    """
    Explainable Multi-Pillar Student Success and Risk Scoring Engine.
    
    Pillars:
    1. Academic Mastery (30%): CGPA (scale 0-10) and exam marks, adjusted for active backlogs.
    2. Attendance & Discipline (20%): Percentage compliance with UGC/NAAC regulatory 75% bar.
    3. Digital Learning Engagement (15%): LMS weekly hours and assignment completion rate.
    4. Placement & Employability (20%): Technical coding proficiency and placement aptitude.
    5. Holistic Wellbeing & Extracurriculars (15%): Activity participation & wellbeing sentiment.
    """

    WEIGHTS = {
        "academic": 0.30,
        "attendance": 0.20,
        "lms": 0.15,
        "placement": 0.20,
        "wellbeing": 0.15
    }

    def __init__(self):
        self.ml_interface = MLRiskPredictorInterface()

    def compute_student_metrics(self, s):
        """
        Calculates normalized pillar scores, composite success score, risk category,
        explainable factors, and recommended mentor interventions for a student record.
        """
        cgpa = float(s.get("cgpa", 0))
        marks = float(s.get("academic_marks_pct", 0))
        attendance = float(s.get("attendance_pct", 0))
        backlogs = int(s.get("backlogs", 0))
        lms_hours = float(s.get("lms_weekly_hours", 0))
        lms_score_raw = float(s.get("lms_engagement_score", 0))
        assignment_pct = float(s.get("assignment_completion_pct", 0))
        extra_score = float(s.get("extracurricular_score", 0))
        aptitude = float(s.get("placement_aptitude_score", 0))
        tech = float(s.get("technical_skills_score", 0))
        feedback = float(s.get("student_feedback_score", 0))

        # --- Pillar 1: Academic Mastery (0-100) ---
        # CGPA (scaled 0-100) and marks average, penalized by backlogs
        cgpa_norm = min(100.0, max(0.0, (cgpa / 10.0) * 100.0))
        academic_base = (cgpa_norm * 0.6) + (marks * 0.4)
        backlog_penalty = backlogs * 12.0  # -12 per backlog
        academic_pillar = max(10.0, min(100.0, academic_base - backlog_penalty))

        # --- Pillar 2: Attendance & Discipline (0-100) ---
        # Strict regulatory penalty below 75%
        if attendance >= 75.0:
            attendance_pillar = min(100.0, attendance)
        else:
            shortfall = 75.0 - attendance
            attendance_pillar = max(0.0, attendance - (shortfall * 1.5))

        # --- Pillar 3: LMS & Engagement (0-100) ---
        hours_norm = min(100.0, (lms_hours / 18.0) * 100.0)
        lms_pillar = (hours_norm * 0.3) + (lms_score_raw * 0.35) + (assignment_pct * 0.35)
        lms_pillar = max(10.0, min(100.0, lms_pillar))

        # --- Pillar 4: Placement Readiness (0-100) ---
        placement_pillar = (tech * 0.55) + (aptitude * 0.45)
        placement_pillar = max(10.0, min(100.0, placement_pillar))

        # --- Pillar 5: Holistic Wellbeing (0-100) ---
        feedback_norm = min(100.0, (feedback / 5.0) * 100.0)
        wellbeing_pillar = (feedback_norm * 0.55) + (extra_score * 0.45)
        wellbeing_pillar = max(10.0, min(100.0, wellbeing_pillar))

        # Composite Success Score (0-100)
        composite_score = round(
            (academic_pillar * self.WEIGHTS["academic"]) +
            (attendance_pillar * self.WEIGHTS["attendance"]) +
            (lms_pillar * self.WEIGHTS["lms"]) +
            (placement_pillar * self.WEIGHTS["placement"]) +
            (wellbeing_pillar * self.WEIGHTS["wellbeing"]),
            1
        )
        composite_score = max(5.0, min(99.5, composite_score))

        # Risk Classification (Explainable Decision Tree / Rules)
        # Low, Medium, High Risk
        is_high_risk = (
            composite_score < 60.0 or
            attendance < 70.0 or
            backlogs >= 2 or
            (cgpa < 5.8 and backlogs >= 1)
        )
        
        is_medium_risk = (
            not is_high_risk and (
                composite_score < 74.0 or
                attendance < 78.0 or
                backlogs == 1 or
                assignment_pct < 68.0 or
                placement_pillar < 62.0
            )
        )

        if is_high_risk:
            risk_level = "High"
            risk_badge = "high"
        elif is_medium_risk:
            risk_level = "Medium"
            risk_badge = "medium"
        else:
            risk_level = "Low"
            risk_badge = "low"

        # Explainable Risk Factors (Feature Impact Attribution)
        risk_factors = []
        positive_factors = []

        # Attendance factor
        if attendance < 75.0:
            impact_val = round((75.0 - attendance) * 0.9, 1)
            risk_factors.append({
                "category": "Regulatory Attendance",
                "severity": "danger" if attendance < 68.0 else "warning",
                "impact": f"-{impact_val} pts",
                "title": f"Attendance Shortfall ({attendance}%)",
                "description": f"Falls below mandatory 75% threshold. Risk of exam debarment."
            })
        else:
            positive_factors.append({
                "category": "Attendance",
                "impact": "+8 pts",
                "title": f"Consistent Attendance ({attendance}%)",
                "description": "Meets academic discipline and institutional compliance standards."
            })

        # Backlogs factor
        if backlogs > 0:
            risk_factors.append({
                "category": "Academic Velocity",
                "severity": "danger" if backlogs >= 2 else "warning",
                "impact": f"-{backlogs * 12} pts",
                "title": f"{backlogs} Active Backlog{'s' if backlogs > 1 else ''}",
                "description": f"Clearing outstanding credits is urgent to preserve degree timeline."
            })

        # Academic marks / CGPA factor
        if cgpa < 6.5:
            risk_factors.append({
                "category": "Cumulative GPA",
                "severity": "danger" if cgpa < 5.8 else "warning",
                "impact": "-10 pts",
                "title": f"CGPA Below 6.5 Benchmark ({cgpa})",
                "description": "Restricts eligibility for tier-1 campus placement drives."
            })
        elif cgpa >= 8.5:
            positive_factors.append({
                "category": "Academic Excellence",
                "impact": "+15 pts",
                "title": f"Top Tier CGPA ({cgpa})",
                "description": "Consistent first-class performance across evaluation cycles."
            })

        # LMS / Assignment engagement
        if assignment_pct < 65.0 or lms_hours < 5.0:
            risk_factors.append({
                "category": "Learning Management Engagement",
                "severity": "warning",
                "impact": "-6 pts",
                "title": f"Subdued LMS Activity ({lms_hours} hrs/wk, {assignment_pct}% submissions)",
                "description": "Signal of low continuous self-study and learning friction."
            })
        elif lms_hours >= 14.0 and assignment_pct >= 90.0:
            positive_factors.append({
                "category": "Digital Engagement",
                "impact": "+10 pts",
                "title": f"Proactive Self-Study ({lms_hours} hrs/wk)",
                "description": "High continuous engagement with course materials and assessments."
            })

        # Placement Readiness factor
        if placement_pillar < 60.0:
            risk_factors.append({
                "category": "Placement Readiness",
                "severity": "warning",
                "impact": "-8 pts",
                "title": f"Aptitude/Tech Skills Deficit ({int(placement_pillar)}/100)",
                "description": "Requires targeted coding labs and reasoning workshops."
            })
        elif placement_pillar >= 85.0:
            positive_factors.append({
                "category": "Placement Ready",
                "impact": "+12 pts",
                "title": f"Strong Technical Profile ({int(placement_pillar)}/100)",
                "description": "High coding aptitude, project depth, and recruitment readiness."
            })

        # Wellbeing & Sentiment
        if feedback < 2.5:
            risk_factors.append({
                "category": "Student Wellbeing",
                "severity": "danger" if feedback < 2.0 else "warning",
                "impact": "-5 pts",
                "title": f"Low Wellness/Sentiment Index ({feedback}/5.0)",
                "description": "Potential academic burnout, isolation, or personal stress reported."
            })

        # Suggested Faculty Interventions
        interventions = []
        if attendance < 75.0:
            interventions.append({
                "id": "INT-ATT-01",
                "category": "Attendance Advisory",
                "urgency": "Immediate" if attendance < 68.0 else "High",
                "action": "Issue Statutory Attendance Warning & Schedule Dean Counseling",
                "timeline": "Within 48 hours",
                "rationale": f"Current attendance is {attendance}%, below UGC 75% minimum requirement."
            })
        if backlogs > 0:
            interventions.append({
                "id": "INT-ACAD-02",
                "category": "Remedial Academics",
                "urgency": "High",
                "action": f"Assign Department Peer Tutor for {backlogs} Outstanding Subject(s)",
                "timeline": "Next 7 days",
                "rationale": "Clear backlogs in upcoming supplementary examination cycle."
            })
        if placement_pillar < 65.0:
            interventions.append({
                "id": "INT-CAREER-03",
                "category": "Career Accelerator",
                "urgency": "Moderate",
                "action": "Enroll in KPMG Aptitude & Data Structures Weekend Bootcamp",
                "timeline": "Next cohort (2 weeks)",
                "rationale": f"Placement score is {int(placement_pillar)}/100. Target score is >= 75."
            })
        if assignment_pct < 70.0 or lms_hours < 6.0:
            interventions.append({
                "id": "INT-LMS-04",
                "category": "Academic Mentorship",
                "urgency": "Moderate",
                "action": "Mentor 1-on-1 Check-in for Assignment Catch-up & LMS Remediation",
                "timeline": "Within 10 days",
                "rationale": f"Assignment completion is {assignment_pct}%; resolve learning roadblocks."
            })
        if feedback < 3.0:
            interventions.append({
                "id": "INT-WELL-05",
                "category": "Student Wellbeing",
                "urgency": "High",
                "action": "Refer to Campus Student Wellness Counselor for Stress Support",
                "timeline": "Within 3 days",
                "rationale": "Sentiment indicator indicates elevated stress or low motivation."
            })

        # If student has 0 risks, recommend honors/mentorship role
        if not interventions:
            interventions.append({
                "id": "INT-HONOR-01",
                "category": "Peer Mentorship",
                "urgency": "Low",
                "action": "Nominate for Department Peer Mentor Program & Research Internship",
                "timeline": "Next semester",
                "rationale": "Exemplary academic and technical track record across all pillars."
            })

        pillars = {
            "academic": round(academic_pillar, 1),
            "attendance": round(attendance_pillar, 1),
            "lms": round(lms_pillar, 1),
            "placement": round(placement_pillar, 1),
            "wellbeing": round(wellbeing_pillar, 1)
        }

        return {
            "success_score": composite_score,
            "risk_level": risk_level,
            "risk_badge": risk_badge,
            "pillars": pillars,
            "risk_factors": risk_factors,
            "positive_factors": positive_factors,
            "recommended_interventions": interventions
        }

analytics_engine = StudentAnalyticsEngine()

# ==============================================================================
# 2. IN-MEMORY DATA STORE & CSV PARSER
# ==============================================================================

STUDENTS_CACHE = []
INTERVENTIONS_LOG = {}  # student_id -> list of logged actions

def load_and_enrich_students():
    """Loads student records from data/students.csv and pre-computes analytics."""
    global STUDENTS_CACHE
    if not DATA_PATH.exists():
        raise FileNotFoundError(f"Dataset not found at {DATA_PATH}")

    loaded = []
    with open(DATA_PATH, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Parse numerical fields
            student = {
                "student_id": row["student_id"],
                "name": row["name"],
                "email": row["email"],
                "gender": row.get("gender", "Unspecified"),
                "department": row["department"],
                "department_name": row.get("department_name", row["department"]),
                "semester": int(row["semester"]),
                "section": row.get("section", "A"),
                "mentor": row.get("mentor", "Academic Advisor"),
                "cgpa": float(row["cgpa"]),
                "academic_marks_pct": float(row["academic_marks_pct"]),
                "attendance_pct": float(row["attendance_pct"]),
                "backlogs": int(row["backlogs"]),
                "lms_weekly_hours": float(row["lms_weekly_hours"]),
                "lms_engagement_score": float(row["lms_engagement_score"]),
                "assignment_completion_pct": float(row["assignment_completion_pct"]),
                "extracurricular_score": float(row["extracurricular_score"]),
                "placement_aptitude_score": float(row["placement_aptitude_score"]),
                "technical_skills_score": float(row["technical_skills_score"]),
                "student_feedback_score": float(row["student_feedback_score"]),
                "phone": row.get("phone", "+91 9800000000")
            }

            # Enrich with analytics
            analytics = analytics_engine.compute_student_metrics(student)
            student.update(analytics)
            loaded.append(student)

    STUDENTS_CACHE = loaded
    print(f"[CampusIQ] Loaded and analyzed {len(STUDENTS_CACHE)} students from {DATA_PATH}")

# Initialize on import
load_and_enrich_students()

# ==============================================================================
# 3. CORS & SECURITY HEADERS
# ==============================================================================

@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    return response

# ==============================================================================
# 4. STATIC FRONTEND ROUTES
# ==============================================================================

@app.route("/")
def index():
    return send_from_directory(FRONTEND_DIR, "index.html")

@app.route("/<path:path>")
def static_files(path):
    if (FRONTEND_DIR / path).exists():
        return send_from_directory(FRONTEND_DIR, path)
    return send_from_directory(FRONTEND_DIR, "index.html")

# ==============================================================================
# 5. REST API ENDPOINTS
# ==============================================================================

@app.route("/api/health", methods=["GET"])
def health_check():
    """Health check endpoint displaying system readiness and AI pipeline status."""
    return jsonify({
        "status": "healthy",
        "service": "CampusIQ - AI-Powered Student Analytics",
        "records_loaded": len(STUDENTS_CACHE),
        "ai_engine": {
            "type": "Explainable Rule-Based Multi-Pillar Scoring Engine",
            "model_version": "v1.0-explainable-rules",
            "ml_model_status": "Ready for Scikit-Learn/XGBoost weights drop-in",
            "pillars_evaluated": 5,
            "timestamp": datetime.now().isoformat()
        }
    })


@app.route("/api/overview", methods=["GET"])
def get_overview():
    """
    Returns executive metrics for dashboard scorecards.
    Supports optional department filtering (?department=CSE).
    """
    dept_filter = request.args.get("department", "ALL").upper()
    students = STUDENTS_CACHE
    if dept_filter != "ALL":
        students = [s for s in students if s["department"] == dept_filter]

    total = len(students)
    if total == 0:
        return jsonify({
            "total_students": 0,
            "avg_cgpa": 0,
            "avg_attendance": 0,
            "avg_success_score": 0,
            "risk_counts": {"high": 0, "medium": 0, "low": 0},
            "risk_percentages": {"high": 0, "medium": 0, "low": 0},
            "placement_ready_rate": 0,
            "attendance_compliance_rate": 0,
            "total_backlogs": 0
        })

    avg_cgpa = round(sum(s["cgpa"] for s in students) / total, 2)
    avg_attendance = round(sum(s["attendance_pct"] for s in students) / total, 1)
    avg_success = round(sum(s["success_score"] for s in students) / total, 1)

    high_risk = sum(1 for s in students if s["risk_level"] == "High")
    med_risk = sum(1 for s in students if s["risk_level"] == "Medium")
    low_risk = sum(1 for s in students if s["risk_level"] == "Low")

    placement_ready = sum(1 for s in students if s["pillars"]["placement"] >= 75.0)
    attendance_compliant = sum(1 for s in students if s["attendance_pct"] >= 75.0)
    total_backlogs = sum(s["backlogs"] for s in students)

    return jsonify({
        "total_students": total,
        "avg_cgpa": avg_cgpa,
        "avg_attendance": avg_attendance,
        "avg_success_score": avg_success,
        "risk_counts": {
            "high": high_risk,
            "medium": med_risk,
            "low": low_risk
        },
        "risk_percentages": {
            "high": round((high_risk / total) * 100, 1),
            "medium": round((med_risk / total) * 100, 1),
            "low": round((low_risk / total) * 100, 1)
        },
        "placement_ready_count": placement_ready,
        "placement_ready_rate": round((placement_ready / total) * 100, 1),
        "attendance_compliant_count": attendance_compliant,
        "attendance_compliance_rate": round((attendance_compliant / total) * 100, 1),
        "total_backlogs": total_backlogs
    })


@app.route("/api/students", methods=["GET"])
def get_students():
    """
    Search, filter, and sort student roster.
    Query parameters:
    - search: string (name, student_id, mentor)
    - department: string (CSE, IT, AI&DS, ECE, ME, EEE, or ALL)
    - risk_level: string (High, Medium, Low, or ALL)
    - semester: integer (4, 6, 8, or ALL)
    - sort_by: string (success_score, cgpa, attendance_pct, backlogs, name)
    - order: asc | desc
    """
    search = request.args.get("search", "").strip().lower()
    dept = request.args.get("department", "ALL").strip()
    risk = request.args.get("risk_level", "ALL").strip()
    sem = request.args.get("semester", "ALL").strip()
    sort_by = request.args.get("sort_by", "risk_level")
    order = request.args.get("order", "asc")

    results = []
    for s in STUDENTS_CACHE:
        # Department filter
        if dept != "ALL" and s["department"].upper() != dept.upper():
            continue
        # Risk level filter
        if risk != "ALL" and s["risk_level"].lower() != risk.lower():
            continue
        # Semester filter
        if sem != "ALL" and str(s["semester"]) != str(sem):
            continue
        # Search query
        if search:
            match_name = search in s["name"].lower()
            match_id = search in s["student_id"].lower()
            match_mentor = search in s["mentor"].lower()
            match_email = search in s["email"].lower()
            if not (match_name or match_id or match_mentor or match_email):
                continue

        results.append(s)

    # Sorting logic
    risk_rank = {"High": 1, "Medium": 2, "Low": 3}
    reverse = (order.lower() == "desc")

    if sort_by == "risk_level":
        # When order is asc, High risk comes first
        results.sort(key=lambda x: risk_rank.get(x["risk_level"], 99), reverse=reverse)
    elif sort_by in ["success_score", "cgpa", "attendance_pct", "backlogs", "academic_marks_pct"]:
        results.sort(key=lambda x: x.get(sort_by, 0), reverse=reverse)
    elif sort_by == "name":
        results.sort(key=lambda x: x["name"].lower(), reverse=reverse)

    return jsonify({
        "count": len(results),
        "total_dataset": len(STUDENTS_CACHE),
        "students": results
    })


@app.route("/api/students/<student_id>", methods=["GET"])
def get_student_detail(student_id):
    """
    Returns full deep-dive profile of a student, including explainable factor breakdown,
    suggested interventions, and real-time logged intervention history.
    """
    student = next((s for s in STUDENTS_CACHE if s["student_id"].upper() == student_id.upper()), None)
    if not student:
        return jsonify({"error": f"Student with ID '{student_id}' not found"}), 404

    # Copy student and attach recorded intervention log
    detail = dict(student)
    detail["logged_interventions"] = INTERVENTIONS_LOG.get(student["student_id"], [])
    return jsonify(detail)


@app.route("/api/students/<student_id>/intervention", methods=["POST"])
def log_student_intervention(student_id):
    """
    Allows faculty or administrators to log an action/counseling intervention.
    Payload: { action_type, notes, mentor_name, priority }
    """
    student = next((s for s in STUDENTS_CACHE if s["student_id"].upper() == student_id.upper()), None)
    if not student:
        return jsonify({"error": f"Student with ID '{student_id}' not found"}), 404

    data = request.get_json(silent=True) or {}
    action_type = data.get("action_type", "General Academic Counseling")
    notes = data.get("notes", "Counseling session conducted with student.")
    mentor_name = data.get("mentor_name", student.get("mentor", "Faculty Advisor"))
    priority = data.get("priority", "Medium")

    new_log = {
        "intervention_id": f"LOG-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "action_type": action_type,
        "notes": notes,
        "mentor_name": mentor_name,
        "priority": priority,
        "timestamp": datetime.now().strftime("%d %b %Y, %I:%M %p"),
        "status": "In Progress"
    }

    if student_id not in INTERVENTIONS_LOG:
        INTERVENTIONS_LOG[student_id] = []
    INTERVENTIONS_LOG[student_id].insert(0, new_log)

    return jsonify({
        "success": True,
        "message": f"Intervention successfully logged for {student['name']}",
        "logged_intervention": new_log,
        "total_interventions": len(INTERVENTIONS_LOG[student_id])
    }), 201


@app.route("/api/analytics/charts", methods=["GET"])
def get_chart_data():
    """
    Aggregates data specifically structured for Chart.js interactive visualizations:
    1. Risk Breakdown (Doughnut)
    2. Department Performance Comparison (Bar)
    3. Attendance vs CGPA Scatter (Scatter with risk classification)
    4. Top Systemic Risk Drivers (Horizontal Bar)
    5. Average Pillar Radar (Radar of institutional averages)
    """
    dept_filter = request.args.get("department", "ALL").upper()
    students = STUDENTS_CACHE
    if dept_filter != "ALL":
        students = [s for s in students if s["department"] == dept_filter]

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

    # 2. Department Performance
    dept_groups = {}
    for s in STUDENTS_CACHE:  # Always include all depts for comparison
        d = s["department"]
        if d not in dept_groups:
            dept_groups[d] = {"cgpa_sum": 0, "success_sum": 0, "attendance_sum": 0, "count": 0}
        dept_groups[d]["cgpa_sum"] += s["cgpa"]
        dept_groups[d]["success_sum"] += s["success_score"]
        dept_groups[d]["attendance_sum"] += s["attendance_pct"]
        dept_groups[d]["count"] += 1

    dept_labels = sorted(list(dept_groups.keys()))
    dept_cgpa = [round(dept_groups[d]["cgpa_sum"] / dept_groups[d]["count"], 2) for d in dept_labels]
    dept_success = [round(dept_groups[d]["success_sum"] / dept_groups[d]["count"], 1) for d in dept_labels]
    dept_attendance = [round(dept_groups[d]["attendance_sum"] / dept_groups[d]["count"], 1) for d in dept_labels]

    department_chart = {
        "labels": dept_labels,
        "avg_cgpa": dept_cgpa,
        "avg_success": dept_success,
        "avg_attendance": dept_attendance
    }

    # 3. Attendance vs CGPA Scatter
    scatter_data = []
    for s in students:
        scatter_data.append({
            "x": s["attendance_pct"],
            "y": s["cgpa"],
            "name": s["name"],
            "id": s["student_id"],
            "dept": s["department"],
            "risk": s["risk_level"],
            "score": s["success_score"]
        })

    # 4. Top Systemic Risk Drivers
    # Count frequency of each risk condition
    factor_counts = {
        "Attendance < 75%": sum(1 for s in students if s["attendance_pct"] < 75.0),
        "Active Backlogs": sum(1 for s in students if s["backlogs"] > 0),
        "CGPA < 6.5": sum(1 for s in students if s["cgpa"] < 6.5),
        "Low LMS Activity (<6 hrs/wk)": sum(1 for s in students if s["lms_weekly_hours"] < 6.0),
        "Low Assignment Submission (<70%)": sum(1 for s in students if s["assignment_completion_pct"] < 70.0),
        "Placement Aptitude Deficit (<65)": sum(1 for s in students if s["placement_aptitude_score"] < 65.0),
        "Reported High Stress (Feedback < 3.0)": sum(1 for s in students if s["student_feedback_score"] < 3.0)
    }

    sorted_factors = sorted(factor_counts.items(), key=lambda x: x[1], reverse=True)
    systemic_risk_chart = {
        "labels": [f[0] for f in sorted_factors],
        "counts": [f[1] for f in sorted_factors]
    }

    # 5. Average Pillar Radar
    radar_data = {
        "labels": [
            "Academic Mastery",
            "Attendance Compliance",
            "LMS Engagement",
            "Placement Readiness",
            "Holistic Wellbeing"
        ],
        "institutional_avg": [
            round(sum(s["pillars"]["academic"] for s in students) / total, 1),
            round(sum(s["pillars"]["attendance"] for s in students) / total, 1),
            round(sum(s["pillars"]["lms"] for s in students) / total, 1),
            round(sum(s["pillars"]["placement"] for s in students) / total, 1),
            round(sum(s["pillars"]["wellbeing"] for s in students) / total, 1)
        ]
    }

    return jsonify({
        "risk_breakdown": risk_breakdown,
        "department_chart": department_chart,
        "scatter_data": scatter_data,
        "systemic_risk_chart": systemic_risk_chart,
        "radar_data": radar_data
    })


@app.route("/api/departments", methods=["GET"])
def get_departments():
    """Returns department-level benchmarking data for the Dean/Administrator view."""
    dept_stats = {}
    for s in STUDENTS_CACHE:
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
                "backlogs_sum": 0,
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
        st["backlogs_sum"] += s["backlogs"]
        if s["pillars"]["placement"] >= 75.0:
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
            "total_backlogs": st["backlogs_sum"],
            "placement_ready_rate": round((st["placement_ready"] / cnt) * 100, 1)
        })

    return jsonify({"departments": summary})


@app.route("/api/simulate", methods=["POST"])
def simulate_scenario():
    """
    Interactive 'What-If' Academic Scenario Simulator.
    Simulates the impact of faculty interventions on a student's risk category.
    Payload: { student_id, attendance_boost, clear_backlogs, lms_hours_boost, assignment_boost }
    """
    data = request.get_json(silent=True) or {}
    student_id = data.get("student_id")
    student = next((s for s in STUDENTS_CACHE if s["student_id"].upper() == str(student_id).upper()), None)
    if not student:
        return jsonify({"error": f"Student '{student_id}' not found"}), 404

    # Clone student and apply simulation parameters
    simulated = dict(student)
    simulated["attendance_pct"] = min(100.0, float(student["attendance_pct"]) + float(data.get("attendance_boost", 0)))
    simulated["backlogs"] = max(0, int(student["backlogs"]) - int(data.get("clear_backlogs", 0)))
    simulated["lms_weekly_hours"] = min(30.0, float(student["lms_weekly_hours"]) + float(data.get("lms_hours_boost", 0)))
    simulated["assignment_completion_pct"] = min(100.0, float(student["assignment_completion_pct"]) + float(data.get("assignment_boost", 0)))

    # Recalculate
    new_metrics = analytics_engine.compute_student_metrics(simulated)

    score_diff = round(new_metrics["success_score"] - student["success_score"], 1)

    return jsonify({
        "original": {
            "success_score": student["success_score"],
            "risk_level": student["risk_level"],
            "pillars": student["pillars"]
        },
        "simulated": {
            "success_score": new_metrics["success_score"],
            "risk_level": new_metrics["risk_level"],
            "pillars": new_metrics["pillars"]
        },
        "score_delta": f"+{score_diff}" if score_diff >= 0 else str(score_diff),
        "risk_improved": (student["risk_level"] != new_metrics["risk_level"])
    })


# ==============================================================================
# RUNNER
# ==============================================================================

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"\n========================================================")
    print(f" CampusIQ - AI-Powered Student Analytics & Success Platform ")
    print(f" KPMG in India Hackathon Challenge Prototype")
    print(f" Server running at: http://127.0.0.1:{port}")
    print(f"========================================================\n")
    app.run(host="0.0.0.0", port=port, debug=True)
