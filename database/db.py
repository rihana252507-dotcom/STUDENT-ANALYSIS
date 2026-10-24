"""
CampusIQ – Database Module
SQLite Database Engine, Connection Manager, and Comprehensive Seed Generator
KPMG in India Hackathon Challenge Prototype (10-Student Calibrated Cohort)
"""

import sqlite3
import csv
from pathlib import Path
import os
from pathlib import Path
from werkzeug.security import generate_password_hash
from services.analytics import analytics_engine

BASE_DIR = Path(__file__).resolve().parent.parent

# Persistent SQLite database location:
# If DATABASE_PATH or RENDER_DISK_PATH is set (e.g. on Render with persistent disk), use that location.
# Otherwise, defaults to persistent file at database/campusiq.db.
_env_db = os.environ.get("DATABASE_PATH") or os.environ.get("RENDER_DISK_PATH")
if _env_db:
    _p = Path(_env_db)
    DB_PATH = _p if _p.suffix == ".db" else _p / "campusiq.db"
else:
    DB_PATH = BASE_DIR / "database" / "campusiq.db"

# Ensure target database directory exists
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

CSV_PATH = BASE_DIR / "data" / "students.csv"

def get_db():
    """Returns a thread-safe connection to the SQLite database with Row factory."""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn

def init_db(force=False):
    """
    Initializes the SQLite database tables and seeds demo accounts, departments, courses,
    faculty, and exactly 10 student records with explainable analytics.
    """
    conn = get_db()
    cursor = conn.cursor()

    if force:
        cursor.execute("DROP TABLE IF EXISTS users")
        cursor.execute("DROP TABLE IF EXISTS departments")
        cursor.execute("DROP TABLE IF EXISTS courses")
        cursor.execute("DROP TABLE IF EXISTS faculty")
        cursor.execute("DROP TABLE IF EXISTS students")
        cursor.execute("DROP TABLE IF EXISTS interventions")
        cursor.execute("DROP TABLE IF EXISTS notifications")
        cursor.execute("DROP TABLE IF EXISTS academic_records")
        cursor.execute("DROP TABLE IF EXISTS student_fees")
        cursor.execute("DROP TABLE IF EXISTS student_skills")
        conn.commit()

    # 1. Users Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL,
        name TEXT NOT NULL,
        email TEXT NOT NULL,
        department TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 2. Departments Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS departments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        code TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        hod_name TEXT NOT NULL,
        student_count INTEGER DEFAULT 0,
        faculty_count INTEGER DEFAULT 0
    );
    """)

    # 3. Courses Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS courses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        course_code TEXT UNIQUE NOT NULL,
        course_name TEXT NOT NULL,
        department TEXT NOT NULL,
        semester INTEGER NOT NULL,
        credits INTEGER NOT NULL,
        faculty_name TEXT NOT NULL,
        pass_rate REAL DEFAULT 85.0
    );
    """)

    # 4. Faculty Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS faculty (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        faculty_id TEXT UNIQUE NOT NULL,
        user_id TEXT NOT NULL,
        name TEXT NOT NULL,
        email TEXT NOT NULL,
        department TEXT NOT NULL,
        designation TEXT NOT NULL,
        phone TEXT,
        specialization TEXT,
        courses_count INTEGER DEFAULT 2
    );
    """)

    # 5. Students Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id TEXT UNIQUE NOT NULL,
        user_id TEXT NOT NULL,
        name TEXT NOT NULL,
        email TEXT NOT NULL,
        gender TEXT NOT NULL,
        department TEXT NOT NULL,
        department_name TEXT NOT NULL,
        semester INTEGER NOT NULL,
        section TEXT NOT NULL,
        faculty_id TEXT NOT NULL,
        mentor_name TEXT NOT NULL,
        cgpa REAL NOT NULL,
        academic_marks_pct REAL NOT NULL,
        attendance_pct REAL NOT NULL,
        backlogs INTEGER NOT NULL,
        lms_weekly_hours REAL NOT NULL,
        lms_engagement_score REAL NOT NULL,
        assignment_completion_pct REAL NOT NULL,
        extracurricular_score REAL NOT NULL,
        placement_aptitude_score REAL NOT NULL,
        technical_skills_score REAL NOT NULL,
        student_feedback_score REAL NOT NULL,
        phone TEXT,
        success_score REAL,
        risk_level TEXT,
        segment TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 6. Interventions Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS interventions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id TEXT NOT NULL,
        faculty_id TEXT NOT NULL,
        faculty_name TEXT NOT NULL,
        action_type TEXT NOT NULL,
        title TEXT,
        priority TEXT NOT NULL,
        instructions TEXT,
        notes TEXT NOT NULL,
        due_date TEXT,
        action_taken TEXT,
        implementation_notes TEXT,
        status TEXT DEFAULT 'Assigned',
        completed_at TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (student_id) REFERENCES students(student_id)
    );
    """)

    # 7. Notifications Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS notifications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT NOT NULL,
        title TEXT NOT NULL,
        message TEXT NOT NULL,
        type TEXT NOT NULL,
        is_read INTEGER DEFAULT 0,
        intervention_id INTEGER,
        read_at TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # Safe backward-compatible migrations for existing databases
    for col, col_type in [
        ("title", "TEXT"), ("instructions", "TEXT"), ("due_date", "TEXT"),
        ("action_taken", "TEXT"), ("implementation_notes", "TEXT"), ("completed_at", "TEXT")
    ]:
        try:
            cursor.execute(f"ALTER TABLE interventions ADD COLUMN {col} {col_type}")
        except Exception:
            pass

    for col, col_type in [("intervention_id", "INTEGER"), ("read_at", "TEXT")]:
        try:
            cursor.execute(f"ALTER TABLE notifications ADD COLUMN {col} {col_type}")
        except Exception:
            pass

    # 8. Academic Records Table (Complete Multi-Semester & Mid-Exam Telemetry)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS academic_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id TEXT NOT NULL,
        year INTEGER NOT NULL,
        semester INTEGER NOT NULL,
        semester_label TEXT NOT NULL,
        academic_year TEXT NOT NULL,
        course_code TEXT NOT NULL,
        course_name TEXT NOT NULL,
        credits REAL DEFAULT 3,
        mid1_marks REAL,
        mid1_max REAL DEFAULT 20.0,
        mid2_marks REAL,
        mid2_max REAL DEFAULT 20.0,
        internal_marks REAL,
        internal_max REAL DEFAULT 40.0,
        external_marks REAL,
        external_max REAL DEFAULT 60.0,
        total_marks REAL,
        total_max REAL DEFAULT 100.0,
        grade TEXT NOT NULL,
        status TEXT NOT NULL,
        classes_conducted INTEGER DEFAULT 45,
        classes_attended INTEGER DEFAULT 40,
        attendance_pct REAL DEFAULT 88.0,
        sgpa REAL,
        FOREIGN KEY (student_id) REFERENCES students(student_id)
    );
    """)

    # 9. Student Fees Table (Semester-Wise Fee Tracking)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS student_fees (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id TEXT NOT NULL,
        academic_year TEXT NOT NULL,
        year INTEGER NOT NULL,
        semester INTEGER NOT NULL,
        semester_label TEXT NOT NULL,
        total_fee REAL NOT NULL,
        amount_paid REAL NOT NULL DEFAULT 0.0,
        due_date TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (student_id) REFERENCES students(student_id)
    );
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_student_fees_student ON student_fees(student_id);")

    # 10. Student Skills Table (Placement Skill Profile)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS student_skills (
        student_id TEXT PRIMARY KEY,
        skills TEXT NOT NULL DEFAULT '[]',
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (student_id) REFERENCES students(student_id)
    );
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_student_skills_student ON student_skills(student_id);")

    conn.commit()

    # Check if admin001 exists; if not or if forced, re-seed
    cursor.execute("SELECT COUNT(*) as count FROM users WHERE user_id = 'admin001'")
    has_demo = cursor.fetchone()["count"] > 0

    if not has_demo or force:
        print("[CampusIQ DB] Initializing tables and seeding 10-student calibrated cohort...")

        # -------------------------------------------------------------
        # SEED 1: DEPARTMENTS (5 departments matching the 10 students)
        # -------------------------------------------------------------
        departments_data = [
            ("CSE", "Computer Science & Engineering", "Dr. Sunita Rao", 3, 2),
            ("IT", "Information Technology", "Dr. Meenakshi Sundaram", 3, 1),
            ("ECE", "Electronics & Communication Engineering", "Dr. Amit Verma", 2, 1),
            ("AI&DS", "Artificial Intelligence & Data Science", "Prof. Neha Gupta", 1, 1),
            ("ME", "Mechanical Engineering", "Dr. K. S. Pillai", 1, 1),
            ("AIML", "Artificial Intelligence & Machine Learning", "Dr. Priya Krishnaswamy", 0, 1),
        ]
        for code, name, hod, sc, fc in departments_data:
            cursor.execute("""
            INSERT OR REPLACE INTO departments (code, name, hod_name, student_count, faculty_count)
            VALUES (?, ?, ?, ?, ?)
            """, (code, name, hod, sc, fc))

        # -------------------------------------------------------------
        # SEED 2: COURSES
        # -------------------------------------------------------------
        courses_data = [
            ("CSE301", "Data Structures & Algorithmic Problem Solving", "CSE", 6, 4, "Dr. Sunita Rao", 88.5),
            ("CSE302", "Database Systems & Distributed Storage", "CSE", 6, 4, "Dr. Sunita Rao", 91.2),
            ("IT303", "Cloud Computing & DevOps Pipelines", "IT", 6, 3, "Dr. Meenakshi Sundaram", 84.0),
            ("AIDS401", "Machine Learning & Predictive Intelligence", "AI&DS", 4, 4, "Prof. Neha Gupta", 89.6),
            ("ECE304", "Digital Signal Processing & Microcontrollers", "ECE", 6, 4, "Dr. Amit Verma", 79.4),
            ("ME301", "Applied Thermodynamics & Fluid Mechanics", "ME", 6, 4, "Dr. K. S. Pillai", 76.8),
            ("T&P201", "KPMG Campus Placement Mock Aptitude & Coding", "CSE", 8, 2, "Dr. Sunita Rao", 93.0),
            ("AIML401", "Deep Learning & Neural Network Architectures", "AIML", 4, 4, "Dr. Priya Krishnaswamy", 87.3),
            ("AIML402", "Natural Language Processing & Generative AI", "AIML", 6, 4, "Dr. Priya Krishnaswamy", 85.0),
        ]
        for c_code, c_name, dept, sem, cred, fac, prate in courses_data:
            cursor.execute("""
            INSERT OR REPLACE INTO courses (course_code, course_name, department, semester, credits, faculty_name, pass_rate)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (c_code, c_name, dept, sem, cred, fac, prate))

        # -------------------------------------------------------------
        # SEED 3: ADMIN ACCOUNTS
        # admin001 / Admin@123 (exact request)
        # -------------------------------------------------------------
        p_admin123 = generate_password_hash("Admin@123")
        cursor.execute("""
        INSERT OR REPLACE INTO users (user_id, password_hash, role, name, email, department)
        VALUES (?, ?, ?, ?, ?, ?)
        """, ("admin001", p_admin123, "admin", "Dr. V. Ramanathan (Dean of Academics)", "dean@campusiq.edu", "Administration"))

        cursor.execute("""
        INSERT OR REPLACE INTO users (user_id, password_hash, role, name, email, department)
        VALUES (?, ?, ?, ?, ?, ?)
        """, ("admin", p_admin123, "admin", "Dr. V. Ramanathan (Dean of Academics)", "dean@campusiq.edu", "Administration"))

        # -------------------------------------------------------------
        # SEED 4: FACULTY ACCOUNTS
        # faculty001 / Faculty@123 (Dr. Sunita Rao)
        # faculty002..faculty005
        # -------------------------------------------------------------
        faculty_data = [
            ("faculty001", "FAC-CSE-01", "Dr. Sunita Rao", "sunita.rao@campusiq.edu", "CSE", "Professor & Head, CSE", "+91 9811223344", "Algorithms & AI Systems", "Faculty@123"),
            ("faculty002", "FAC-IT-01", "Dr. Meenakshi Sundaram", "meenakshi.s@campusiq.edu", "IT", "Professor & Head, IT", "+91 9811223346", "Cloud Computing & Cybersecurity", "Faculty@123"),
            ("faculty003", "FAC-AIDS-01", "Prof. Neha Gupta", "neha.gupta@campusiq.edu", "AI&DS", "Associate Professor, AI&DS", "+91 9811223347", "Deep Learning & Big Data", "Faculty@123"),
            ("faculty004", "FAC-ECE-01", "Dr. Amit Verma", "amit.verma@campusiq.edu", "ECE", "Professor & Head, ECE", "+91 9811223348", "Embedded IoT & VLSI", "Faculty@123"),
            ("faculty005", "FAC-ME-01", "Dr. K. S. Pillai", "ks.pillai@campusiq.edu", "ME", "Professor & Head, ME", "+91 9811223349", "Robotics & Thermal Systems", "Faculty@123"),
            ("faculty006", "FAC-AIML-01", "Dr. Priya Krishnaswamy", "priya.k@campusiq.edu", "AIML", "Professor & Head, AIML", "+91 9811223350", "Generative AI & Neural Networks", "Faculty@123"),
        ]

        for f_user, f_code, fname, femail, fdept, fdesig, fphone, fspec, fpass in faculty_data:
            hashed_pass = generate_password_hash(fpass)
            cursor.execute("""
            INSERT OR REPLACE INTO users (user_id, password_hash, role, name, email, department)
            VALUES (?, ?, ?, ?, ?, ?)
            """, (f_user, hashed_pass, "faculty", fname, femail, fdept))

            cursor.execute("""
            INSERT OR REPLACE INTO users (user_id, password_hash, role, name, email, department)
            VALUES (?, ?, ?, ?, ?, ?)
            """, (f_code, hashed_pass, "faculty", fname, femail, fdept))

            cursor.execute("""
            INSERT OR REPLACE INTO faculty (faculty_id, user_id, name, email, department, designation, phone, specialization)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (f_user, f_user, fname, femail, fdept, fdesig, fphone, fspec))

        # -------------------------------------------------------------
        # SEED 4b: HOD (HEAD OF DEPARTMENT) ACCOUNTS
        # -------------------------------------------------------------
        hod_data = [
            ("hod_cse", "Hod@123", "Dr. Sunita Rao (HOD CSE)", "hod.cse@campusiq.edu", "CSE"),
            ("hod_aiml", "Hod@123", "Dr. Priya Krishnaswamy (HOD AIML)", "hod.aiml@campusiq.edu", "AIML"),
            ("hod_ece", "Hod@123", "Dr. Amit Verma (HOD ECE)", "hod.ece@campusiq.edu", "ECE"),
            ("hod_it", "Hod@123", "Dr. Meenakshi Sundaram (HOD IT)", "hod.it@campusiq.edu", "IT"),
            ("hod_aids", "Hod@123", "Prof. Neha Gupta (HOD AI&DS)", "hod.aids@campusiq.edu", "AI&DS"),
            ("hod_me", "Hod@123", "Dr. K. S. Pillai (HOD ME)", "hod.me@campusiq.edu", "ME"),
        ]
        for h_user, h_pass, h_name, h_email, h_dept in hod_data:
            cursor.execute("SELECT COUNT(*) as count FROM users WHERE user_id = ?", (h_user,))
            if cursor.fetchone()["count"] == 0:
                h_pass_hash = generate_password_hash(h_pass)
                cursor.execute("""
                INSERT INTO users (user_id, password_hash, role, name, email, department)
                VALUES (?, ?, 'hod', ?, ?, ?)
                """, (h_user, h_pass_hash, h_name, h_email, h_dept))

        mentor_map = {
            "Dr. Sunita Rao": "faculty001",
            "Dr. Meenakshi Sundaram": "faculty002",
            "Prof. Neha Gupta": "faculty003",
            "Dr. Amit Verma": "faculty004",
            "Dr. K. S. Pillai": "faculty005",
            "Dr. Priya Krishnaswamy": "faculty006",
        }

        # -------------------------------------------------------------
        # SEED 5: EXACTLY 10 DUMMY STUDENTS FROM CSV
        # 2 Low-Risk, 4 Medium-Risk, 4 High-Risk
        # All students can log in with User ID and Student@123
        # -------------------------------------------------------------
        if CSV_PATH.exists():
            with open(CSV_PATH, mode="r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                index = 1
                for row in reader:
                    s_code = row["student_id"] # e.g. CIQ-2026-001
                    s_user = f"student{index:03d}" # e.g. student001 .. student010
                    s_pass = "Student@123"

                    hashed_spass = generate_password_hash(s_pass)
                    mentor = row.get("mentor", "Dr. Sunita Rao")
                    fac_id = mentor_map.get(mentor, "faculty001")

                    metrics = analytics_engine.compute_student_metrics(row)

                    # Primary login user (e.g. student001)
                    cursor.execute("""
                    INSERT OR REPLACE INTO users (user_id, password_hash, role, name, email, department)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """, (s_user, hashed_spass, "student", row["name"], row["email"], row["department"]))

                    # Alias login user (e.g. CIQ-2026-001)
                    cursor.execute("""
                    INSERT OR REPLACE INTO users (user_id, password_hash, role, name, email, department)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """, (s_code, hashed_spass, "student", row["name"], row["email"], row["department"]))

                    # Seed students table: student_id is s_code (CIQ-2026-001) and user_id is s_user (student001)
                    cursor.execute("""
                    INSERT OR REPLACE INTO students (
                        student_id, user_id, name, email, gender, department, department_name,
                        semester, section, faculty_id, mentor_name, cgpa, academic_marks_pct,
                        attendance_pct, backlogs, lms_weekly_hours, lms_engagement_score,
                        assignment_completion_pct, extracurricular_score, placement_aptitude_score,
                        technical_skills_score, student_feedback_score, phone, success_score, risk_level, segment
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        s_code, s_user, row["name"], row["email"], row.get("gender", "Female"),
                        row["department"], row.get("department_name", row["department"]),
                        int(row["semester"]), row.get("section", "A"),
                        fac_id, mentor, float(row["cgpa"]), float(row["academic_marks_pct"]),
                        float(row["attendance_pct"]), int(row["backlogs"]),
                        float(row["lms_weekly_hours"]), float(row["lms_engagement_score"]),
                        float(row["assignment_completion_pct"]), float(row["extracurricular_score"]),
                        float(row["placement_aptitude_score"]), float(row["technical_skills_score"]),
                        float(row["student_feedback_score"]), row.get("phone", "+91 9800000000"),
                        metrics["success_score"], metrics["risk_level"], metrics["segment"]
                    ))

                    index += 1

        # -------------------------------------------------------------
        # SEED 6: SAMPLE INTERVENTIONS WITH DIVERSE STATUSES
        # ('Pending', 'In Progress', 'Completed')
        # -------------------------------------------------------------
        initial_interventions = [
            ("student007", "faculty002", "Dr. Meenakshi Sundaram", "Statutory Attendance Advisory Meeting", "Immediate", "Student briefed on 61.5% attendance deficit. Scheduled supplementary coaching for 2 backlog subjects.", "In Progress"),
            ("student008", "faculty001", "Dr. Sunita Rao", "Remedial Peer Tutoring Assignment", "Immediate", "Assigned 8th sem senior peer tutor for clearing 3 backlogs. Weekly check-in on Fridays.", "Pending"),
            ("student009", "faculty004", "Dr. Amit Verma", "Student Wellness & Exam Stress Counseling", "High", "Critical attendance (58.0%) review and mental health check-in. Study timetable re-architected.", "In Progress"),
            ("student003", "faculty001", "Dr. Sunita Rao", "KPMG Technical Coding & Aptitude Mock Bootcamp", "Moderate", "Enrolled in placement aptitude training program. Student has strong 8.4 CGPA but needs DSA polish.", "Completed")
        ]
        for s_id, f_id, f_name, a_type, prio, notes, status in initial_interventions:
            cursor.execute("""
            INSERT INTO interventions (student_id, faculty_id, faculty_name, action_type, priority, notes, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (s_id, f_id, f_name, a_type, prio, notes, status))

        # -------------------------------------------------------------
        # SEED 7: NOTIFICATIONS
        # -------------------------------------------------------------
        notifications = [
            ("admin001", "Institutional Risk Radar Alert", "4 students identified in High Risk bracket across Semester 4 & 6 cohorts.", "alert"),
            ("admin001", "NAAC & NIRF Accreditation Audit Ready", "Departmental metrics calibrated for all 5 engineering faculties.", "info"),
            ("admin001", "KPMG Campus Placement Diagnostic", "40.0% of cohort currently meet Tier-1 KPMG aptitude & technical threshold.", "success"),
            ("faculty001", "Attendance Watchlist Alert", "Kabir Mehta (student008) in your CSE cohort below 70% statutory attendance.", "warning"),
            ("faculty002", "Intervention In-Progress", "Attendance catch-up meeting underway for Divya Rao (student007).", "info"),
            ("student001", "Honor Peer Mentorship Nomination", "Nominated for Department Peer Tutor Program based on 92.3 success score.", "success"),
            ("student007", "Statutory Attendance Advisory", "Attendance is 61.5%. Meeting scheduled with Dr. Meenakshi Sundaram.", "alert"),
            ("student002", "Campus Placement Mock Test", "Diagnostic score recorded: 88/100. Excellent progress!", "info")
        ]
        for u_id, title, msg, n_type in notifications:
            cursor.execute("""
            INSERT INTO notifications (user_id, title, message, type)
            VALUES (?, ?, ?, ?)
            """, (u_id, title, msg, n_type))

        conn.commit()
        print("[CampusIQ DB] Initialization complete! Seeded 10-student calibrated cohort: 2 Low, 4 Medium, 4 High.")

    # -------------------------------------------------------------
    # SEED 8: ACADEMIC RECORDS (Multi-Semester & Mid-Exam Telemetry)
    # -------------------------------------------------------------
    cursor.execute("SELECT COUNT(*) as count FROM academic_records")
    has_academic = cursor.fetchone()["count"] > 0
    if not has_academic or force:
        from database.academic_curriculum import generate_records_for_student
        cursor.execute("SELECT * FROM students")
        all_students = [dict(r) for r in cursor.fetchall()]
        for stu in all_students:
            recs = generate_records_for_student(stu)
            for r in recs:
                cursor.execute("""
                INSERT INTO academic_records (
                    student_id, year, semester, semester_label, academic_year,
                    course_code, course_name, credits, mid1_marks, mid1_max,
                    mid2_marks, mid2_max, internal_marks, internal_max,
                    external_marks, external_max, total_marks, total_max,
                    grade, status, classes_conducted, classes_attended, attendance_pct, sgpa
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    r["student_id"], r["year"], r["semester"], r["semester_label"], r["academic_year"],
                    r["course_code"], r["course_name"], r["credits"], r["mid1_marks"], r["mid1_max"],
                    r["mid2_marks"], r["mid2_max"], r["internal_marks"], r["internal_max"],
                    r["external_marks"], r["external_max"], r["total_marks"], r["total_max"],
                    r["grade"], r["status"], r["classes_conducted"], r["classes_attended"], r["attendance_pct"], r["sgpa"]
                ))
        conn.commit()
        print(f"[CampusIQ DB] Seeded multi-semester academic records for {len(all_students)} students.")

    # -------------------------------------------------------------
    # SEED 9: SEMESTER FEE RECORDS
    # -------------------------------------------------------------
    cursor.execute("SELECT COUNT(*) as count FROM student_fees")
    has_fees = cursor.fetchone()["count"] > 0
    if not has_fees or force:
        sem_acad_years = {
            1: "2022-2023", 2: "2022-2023",
            3: "2023-2024", 4: "2023-2024",
            5: "2024-2025", 6: "2024-2025",
            7: "2025-2026", 8: "2025-2026"
        }
        sem_due_dates = {
            1: "2022-08-30", 2: "2023-01-20",
            3: "2023-08-30", 4: "2024-01-20",
            5: "2024-08-30", 6: "2025-01-20",
            7: "2025-08-30", 8: "2026-01-20"
        }
        cursor.execute("SELECT * FROM students")
        students_list = [dict(r) for r in cursor.fetchall()]

        for s in students_list:
            sid = s["student_id"]
            # Student CIQ-2026-010 (Arjun Verma) is intentionally left without fee records
            # to verify empty-state handling: "No fee details are available for your account yet."
            if sid == "CIQ-2026-010":
                continue

            cur_sem = int(s["semester"])
            for sem in range(1, cur_sem + 1):
                y = (sem + 1) // 2
                s_part = 1 if (sem % 2 != 0) else 2
                s_label = f"{y}-{s_part}"
                acad_yr = sem_acad_years.get(sem, "2024-2025")
                base_fee = 65000.0

                if sem < cur_sem:
                    # Completed prior semesters: fully paid except for Kabir Mehta (has partial in Sem 4)
                    if sid == "CIQ-2026-008" and sem == 4:
                        paid = 45000.0
                        d_date = sem_due_dates.get(sem, "2024-01-20")
                    else:
                        paid = base_fee
                        d_date = sem_due_dates.get(sem, "2023-08-30")
                else:
                    # Current ongoing semester variations:
                    if sid == "CIQ-2026-001":
                        paid = base_fee      # Fully Paid
                        d_date = "2026-01-20"
                    elif sid == "CIQ-2026-002":
                        paid = 40000.0       # Partially Paid (Due: ₹25,000, deadline upcoming)
                        d_date = "2026-11-30"
                    elif sid == "CIQ-2026-003":
                        paid = 0.0           # Due (Due: ₹65,000, deadline upcoming)
                        d_date = "2026-11-15"
                    elif sid == "CIQ-2026-004":
                        paid = 65000.0       # Paid, missing due date to test "Not available" fallback
                        d_date = None
                    elif sid == "CIQ-2026-008":
                        paid = 20000.0       # Overdue (Due: ₹45,000, deadline past: 2026-09-15)
                        d_date = "2026-09-15"
                    else:
                        paid = base_fee
                        d_date = sem_due_dates.get(sem, "2026-01-20")

                cursor.execute("""
                INSERT INTO student_fees (
                    student_id, academic_year, year, semester, semester_label, total_fee, amount_paid, due_date
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (sid, acad_yr, y, sem, s_label, base_fee, paid, d_date))

        conn.commit()
        print(f"[CampusIQ DB] Seeded semester fee records for students.")

    # -------------------------------------------------------------
    # SEED 10: ENSURE AIML COURSE & 10 DUMMY STUDENTS PER COURSE
    # -------------------------------------------------------------
    ensure_aiml_and_dummy_students(conn=conn)

    conn.close()


DEMO_STUDENTS_POOL = {
    "AIML": [
        {"name": "Arvind Swaminathan", "gender": "Male", "sem": 6, "sec": "A", "cgpa": 8.85, "marks": 86.0, "att": 89.5, "backlogs": 0, "hours": 14.0, "lms": 88.0, "assign": 92.0, "extra": 80.0, "apt": 85.0, "tech": 90.0, "feedback": 4.5},
        {"name": "Deepthi Subramanian", "gender": "Female", "sem": 6, "sec": "A", "cgpa": 8.40, "marks": 82.5, "att": 86.0, "backlogs": 0, "hours": 12.5, "lms": 82.0, "assign": 88.0, "extra": 75.0, "apt": 80.0, "tech": 85.0, "feedback": 4.3},
        {"name": "Vishal Narayanan", "gender": "Male", "sem": 4, "sec": "A", "cgpa": 7.95, "marks": 78.0, "att": 82.0, "backlogs": 0, "hours": 11.0, "lms": 76.0, "assign": 84.0, "extra": 70.0, "apt": 75.0, "tech": 80.0, "feedback": 4.1},
        {"name": "Shruti Prabhakar", "gender": "Female", "sem": 4, "sec": "B", "cgpa": 7.60, "marks": 74.0, "att": 79.0, "backlogs": 0, "hours": 9.5, "lms": 72.0, "assign": 78.0, "extra": 68.0, "apt": 72.0, "tech": 76.0, "feedback": 3.9},
        {"name": "Akash Venkataraman", "gender": "Male", "sem": 6, "sec": "B", "cgpa": 7.20, "marks": 70.5, "att": 76.5, "backlogs": 1, "hours": 8.5, "lms": 68.0, "assign": 74.0, "extra": 65.0, "apt": 68.0, "tech": 72.0, "feedback": 3.7},
        {"name": "Keerthi Raghavan", "gender": "Female", "sem": 4, "sec": "A", "cgpa": 6.90, "marks": 67.0, "att": 75.0, "backlogs": 1, "hours": 8.0, "lms": 64.0, "assign": 70.0, "extra": 60.0, "apt": 65.0, "tech": 68.0, "feedback": 3.5},
        {"name": "Suresh Madhavan", "gender": "Male", "sem": 6, "sec": "A", "cgpa": 6.45, "marks": 62.5, "att": 71.0, "backlogs": 1, "hours": 7.0, "lms": 58.0, "assign": 65.0, "extra": 55.0, "apt": 60.0, "tech": 64.0, "feedback": 3.3},
        {"name": "Sandhya Ramaswamy", "gender": "Female", "sem": 6, "sec": "B", "cgpa": 6.10, "marks": 59.0, "att": 68.0, "backlogs": 2, "hours": 6.0, "lms": 52.0, "assign": 60.0, "extra": 50.0, "apt": 55.0, "tech": 58.0, "feedback": 3.0},
        {"name": "Nitin Krishnamurthy", "gender": "Male", "sem": 4, "sec": "B", "cgpa": 5.75, "marks": 55.0, "att": 63.5, "backlogs": 2, "hours": 5.0, "lms": 46.0, "assign": 52.0, "extra": 45.0, "apt": 50.0, "tech": 52.0, "feedback": 2.8},
        {"name": "Pavithra Sundar", "gender": "Female", "sem": 6, "sec": "A", "cgpa": 5.30, "marks": 51.0, "att": 59.0, "backlogs": 3, "hours": 4.5, "lms": 42.0, "assign": 48.0, "extra": 40.0, "apt": 45.0, "tech": 48.0, "feedback": 2.6},
    ],
    "CSE": [
        {"name": "Kavya Nair", "gender": "Female", "sem": 6, "sec": "A", "cgpa": 8.90, "marks": 87.0, "att": 91.0, "backlogs": 0, "hours": 15.0, "lms": 89.0, "assign": 94.0, "extra": 82.0, "apt": 88.0, "tech": 92.0, "feedback": 4.6},
        {"name": "Manoj Sundaram", "gender": "Male", "sem": 6, "sec": "B", "cgpa": 8.25, "marks": 80.0, "att": 85.0, "backlogs": 0, "hours": 12.0, "lms": 80.0, "assign": 86.0, "extra": 74.0, "apt": 78.0, "tech": 84.0, "feedback": 4.2},
        {"name": "Ishita Sen", "gender": "Female", "sem": 4, "sec": "A", "cgpa": 7.80, "marks": 76.0, "att": 81.0, "backlogs": 0, "hours": 10.5, "lms": 74.0, "assign": 82.0, "extra": 70.0, "apt": 74.0, "tech": 78.0, "feedback": 4.0},
        {"name": "Pranav Bhat", "gender": "Male", "sem": 6, "sec": "A", "cgpa": 7.35, "marks": 71.0, "att": 77.0, "backlogs": 1, "hours": 9.0, "lms": 69.0, "assign": 75.0, "extra": 66.0, "apt": 69.0, "tech": 73.0, "feedback": 3.8},
        {"name": "Tanya Agarwal", "gender": "Female", "sem": 4, "sec": "B", "cgpa": 6.85, "marks": 66.0, "att": 74.5, "backlogs": 1, "hours": 7.5, "lms": 63.0, "assign": 69.0, "extra": 58.0, "apt": 64.0, "tech": 66.0, "feedback": 3.4},
        {"name": "Karthik Rajan", "gender": "Male", "sem": 6, "sec": "B", "cgpa": 6.25, "marks": 60.0, "att": 69.0, "backlogs": 2, "hours": 6.5, "lms": 55.0, "assign": 62.0, "extra": 52.0, "apt": 58.0, "tech": 60.0, "feedback": 3.1},
        {"name": "Meera Nambiar", "gender": "Female", "sem": 4, "sec": "A", "cgpa": 5.45, "marks": 53.0, "att": 61.0, "backlogs": 3, "hours": 4.8, "lms": 44.0, "assign": 50.0, "extra": 42.0, "apt": 48.0, "tech": 50.0, "feedback": 2.7},
    ],
    "IT": [
        {"name": "Siddharth Joshi", "gender": "Male", "sem": 6, "sec": "A", "cgpa": 8.70, "marks": 85.0, "att": 88.0, "backlogs": 0, "hours": 13.5, "lms": 86.0, "assign": 91.0, "extra": 78.0, "apt": 84.0, "tech": 88.0, "feedback": 4.4},
        {"name": "Anika Deshmukh", "gender": "Female", "sem": 6, "sec": "B", "cgpa": 8.10, "marks": 79.0, "att": 83.0, "backlogs": 0, "hours": 11.5, "lms": 78.0, "assign": 84.0, "extra": 72.0, "apt": 76.0, "tech": 82.0, "feedback": 4.1},
        {"name": "Varun Pillai", "gender": "Male", "sem": 4, "sec": "A", "cgpa": 7.70, "marks": 75.0, "att": 80.0, "backlogs": 0, "hours": 10.0, "lms": 73.0, "assign": 80.0, "extra": 68.0, "apt": 71.0, "tech": 76.0, "feedback": 3.9},
        {"name": "Rhea Mukherjee", "gender": "Female", "sem": 6, "sec": "A", "cgpa": 7.15, "marks": 69.5, "att": 76.0, "backlogs": 1, "hours": 8.5, "lms": 67.0, "assign": 73.0, "extra": 64.0, "apt": 67.0, "tech": 70.0, "feedback": 3.6},
        {"name": "Gautam Iyer", "gender": "Male", "sem": 4, "sec": "B", "cgpa": 6.70, "marks": 64.0, "att": 73.0, "backlogs": 1, "hours": 7.0, "lms": 61.0, "assign": 67.0, "extra": 56.0, "apt": 62.0, "tech": 64.0, "feedback": 3.3},
        {"name": "Shreya Kulkarni", "gender": "Female", "sem": 6, "sec": "B", "cgpa": 6.05, "marks": 58.0, "att": 67.0, "backlogs": 2, "hours": 5.8, "lms": 50.0, "assign": 58.0, "extra": 48.0, "apt": 54.0, "tech": 56.0, "feedback": 2.9},
        {"name": "Nikhil Varma", "gender": "Male", "sem": 4, "sec": "A", "cgpa": 5.40, "marks": 52.0, "att": 60.0, "backlogs": 3, "hours": 4.5, "lms": 43.0, "assign": 49.0, "extra": 41.0, "apt": 46.0, "tech": 49.0, "feedback": 2.6},
    ],
    "AI&DS": [
        {"name": "Devika Menon", "gender": "Female", "sem": 6, "sec": "A", "cgpa": 8.80, "marks": 86.0, "att": 89.0, "backlogs": 0, "hours": 14.0, "lms": 87.0, "assign": 92.0, "extra": 80.0, "apt": 86.0, "tech": 90.0, "feedback": 4.5},
        {"name": "Abhishek Chawla", "gender": "Male", "sem": 6, "sec": "A", "cgpa": 8.30, "marks": 81.0, "att": 84.5, "backlogs": 0, "hours": 12.0, "lms": 80.0, "assign": 86.0, "extra": 74.0, "apt": 79.0, "tech": 84.0, "feedback": 4.2},
        {"name": "Priyanka Roy", "gender": "Female", "sem": 4, "sec": "A", "cgpa": 7.85, "marks": 77.0, "att": 81.5, "backlogs": 0, "hours": 10.5, "lms": 75.0, "assign": 82.0, "extra": 70.0, "apt": 75.0, "tech": 79.0, "feedback": 4.0},
        {"name": "Harish Venkatesh", "gender": "Male", "sem": 4, "sec": "B", "cgpa": 7.45, "marks": 72.5, "att": 78.0, "backlogs": 0, "hours": 9.5, "lms": 71.0, "assign": 77.0, "extra": 67.0, "apt": 71.0, "tech": 75.0, "feedback": 3.8},
        {"name": "Simran Kaur", "gender": "Female", "sem": 6, "sec": "B", "cgpa": 7.05, "marks": 68.5, "att": 76.0, "backlogs": 1, "hours": 8.5, "lms": 66.0, "assign": 72.0, "extra": 63.0, "apt": 66.0, "tech": 70.0, "feedback": 3.6},
        {"name": "Aditya Bhattacharya", "gender": "Male", "sem": 4, "sec": "A", "cgpa": 6.65, "marks": 64.0, "att": 73.5, "backlogs": 1, "hours": 7.2, "lms": 60.0, "assign": 66.0, "extra": 57.0, "apt": 61.0, "tech": 65.0, "feedback": 3.3},
        {"name": "Nandini Swaminathan", "gender": "Female", "sem": 6, "sec": "A", "cgpa": 6.15, "marks": 59.0, "att": 69.0, "backlogs": 2, "hours": 6.2, "lms": 53.0, "assign": 60.0, "extra": 51.0, "apt": 56.0, "tech": 59.0, "feedback": 3.0},
        {"name": "Tarun Namboodiri", "gender": "Male", "sem": 6, "sec": "B", "cgpa": 5.65, "marks": 54.0, "att": 63.0, "backlogs": 2, "hours": 5.2, "lms": 47.0, "assign": 53.0, "extra": 45.0, "apt": 50.0, "tech": 53.0, "feedback": 2.8},
        {"name": "Lavanya Srinivasan", "gender": "Female", "sem": 4, "sec": "B", "cgpa": 5.25, "marks": 50.0, "att": 58.5, "backlogs": 3, "hours": 4.2, "lms": 41.0, "assign": 47.0, "extra": 39.0, "apt": 44.0, "tech": 47.0, "feedback": 2.5},
    ],
    "ECE": [
        {"name": "Rajeshwari Hegde", "gender": "Female", "sem": 6, "sec": "A", "cgpa": 8.75, "marks": 85.0, "att": 88.5, "backlogs": 0, "hours": 13.5, "lms": 85.0, "assign": 90.0, "extra": 78.0, "apt": 83.0, "tech": 87.0, "feedback": 4.4},
        {"name": "Sanjay Nambiar", "gender": "Male", "sem": 6, "sec": "B", "cgpa": 8.15, "marks": 79.5, "att": 84.0, "backlogs": 0, "hours": 11.8, "lms": 79.0, "assign": 85.0, "extra": 73.0, "apt": 77.0, "tech": 81.0, "feedback": 4.1},
        {"name": "Komal Saxena", "gender": "Female", "sem": 4, "sec": "A", "cgpa": 7.75, "marks": 75.5, "att": 81.0, "backlogs": 0, "hours": 10.2, "lms": 74.0, "assign": 81.0, "extra": 69.0, "apt": 73.0, "tech": 77.0, "feedback": 3.9},
        {"name": "Vivek Anand", "gender": "Male", "sem": 4, "sec": "B", "cgpa": 7.30, "marks": 71.0, "att": 77.0, "backlogs": 1, "hours": 8.8, "lms": 68.0, "assign": 74.0, "extra": 65.0, "apt": 68.0, "tech": 72.0, "feedback": 3.7},
        {"name": "Swati Mahajan", "gender": "Female", "sem": 6, "sec": "A", "cgpa": 6.80, "marks": 65.5, "att": 74.0, "backlogs": 1, "hours": 7.5, "lms": 62.0, "assign": 68.0, "extra": 58.0, "apt": 63.0, "tech": 66.0, "feedback": 3.4},
        {"name": "Deepak Ranganathan", "gender": "Male", "sem": 6, "sec": "B", "cgpa": 6.30, "marks": 61.0, "att": 70.0, "backlogs": 2, "hours": 6.4, "lms": 55.0, "assign": 61.0, "extra": 52.0, "apt": 58.0, "tech": 61.0, "feedback": 3.1},
        {"name": "Pallavi Joshi", "gender": "Female", "sem": 4, "sec": "A", "cgpa": 5.80, "marks": 56.0, "att": 64.0, "backlogs": 2, "hours": 5.3, "lms": 48.0, "assign": 54.0, "extra": 46.0, "apt": 51.0, "tech": 53.0, "feedback": 2.8},
        {"name": "Rahul Chandran", "gender": "Male", "sem": 4, "sec": "B", "cgpa": 5.35, "marks": 51.5, "att": 59.5, "backlogs": 3, "hours": 4.4, "lms": 42.0, "assign": 48.0, "extra": 40.0, "apt": 45.0, "tech": 48.0, "feedback": 2.6},
    ],
    "ME": [
        {"name": "Kiran Patil", "gender": "Male", "sem": 6, "sec": "A", "cgpa": 8.65, "marks": 84.0, "att": 87.5, "backlogs": 0, "hours": 13.0, "lms": 84.0, "assign": 89.0, "extra": 77.0, "apt": 82.0, "tech": 86.0, "feedback": 4.3},
        {"name": "Vandana Rao", "gender": "Female", "sem": 6, "sec": "A", "cgpa": 8.05, "marks": 78.5, "att": 83.0, "backlogs": 0, "hours": 11.2, "lms": 77.0, "assign": 83.0, "extra": 71.0, "apt": 76.0, "tech": 80.0, "feedback": 4.1},
        {"name": "Suraj Sridhar", "gender": "Male", "sem": 4, "sec": "A", "cgpa": 7.65, "marks": 74.5, "att": 80.0, "backlogs": 0, "hours": 9.8, "lms": 72.0, "assign": 79.0, "extra": 67.0, "apt": 71.0, "tech": 75.0, "feedback": 3.8},
        {"name": "Naveen Karunakaran", "gender": "Male", "sem": 4, "sec": "B", "cgpa": 7.25, "marks": 70.0, "att": 76.5, "backlogs": 1, "hours": 8.5, "lms": 67.0, "assign": 73.0, "extra": 63.0, "apt": 67.0, "tech": 71.0, "feedback": 3.6},
        {"name": "Akshata Shenoy", "gender": "Female", "sem": 6, "sec": "B", "cgpa": 6.75, "marks": 65.0, "att": 73.5, "backlogs": 1, "hours": 7.2, "lms": 61.0, "assign": 67.0, "extra": 57.0, "apt": 62.0, "tech": 65.0, "feedback": 3.3},
        {"name": "Girish Kulkarni", "gender": "Male", "sem": 4, "sec": "A", "cgpa": 6.20, "marks": 60.0, "att": 68.5, "backlogs": 2, "hours": 6.2, "lms": 54.0, "assign": 60.0, "extra": 50.0, "apt": 56.0, "tech": 59.0, "feedback": 3.0},
        {"name": "Rashmi Nair", "gender": "Female", "sem": 6, "sec": "B", "cgpa": 5.85, "marks": 56.5, "att": 65.0, "backlogs": 2, "hours": 5.5, "lms": 49.0, "assign": 55.0, "extra": 46.0, "apt": 52.0, "tech": 54.0, "feedback": 2.9},
        {"name": "Dinesh Mohan", "gender": "Male", "sem": 4, "sec": "B", "cgpa": 5.40, "marks": 52.0, "att": 60.0, "backlogs": 3, "hours": 4.6, "lms": 43.0, "assign": 49.0, "extra": 41.0, "apt": 46.0, "tech": 49.0, "feedback": 2.6},
        {"name": "Bhavna Shetty", "gender": "Female", "sem": 6, "sec": "A", "cgpa": 5.10, "marks": 48.0, "att": 56.0, "backlogs": 3, "hours": 4.0, "lms": 38.0, "assign": 45.0, "extra": 37.0, "apt": 42.0, "tech": 45.0, "feedback": 2.4},
    ],
}

DEPT_METADATA = {
    "CSE": {"name": "Computer Science & Engineering", "mentor": "Dr. Sunita Rao", "fac_id": "faculty001"},
    "IT": {"name": "Information Technology", "mentor": "Dr. Meenakshi Sundaram", "fac_id": "faculty002"},
    "AI&DS": {"name": "Artificial Intelligence & Data Science", "mentor": "Prof. Neha Gupta", "fac_id": "faculty003"},
    "ECE": {"name": "Electronics & Communication Engineering", "mentor": "Dr. Amit Verma", "fac_id": "faculty004"},
    "ME": {"name": "Mechanical Engineering", "mentor": "Dr. K. S. Pillai", "fac_id": "faculty005"},
    "AIML": {"name": "Artificial Intelligence and Machine Learning", "mentor": "Dr. Priya Krishnaswamy", "fac_id": "faculty006"},
}

def ensure_aiml_and_dummy_students(conn=None):
    """
    Idempotently:
    1. Ensures AIML department, AIML courses, and AIML faculty exist.
    2. Ensures every supported course/department has 10 designated dummy/demo student records.
    3. Preserves all official demo students and real students.
    4. Safe and idempotent across repeated invocations.
    """
    owns_conn = False
    if conn is None:
        conn = get_db()
        owns_conn = True

    cursor = conn.cursor()

    try:
        # 1. Ensure AIML in departments
        cursor.execute("SELECT code FROM departments WHERE code = 'AIML'")
        if not cursor.fetchone():
            cursor.execute("""
            INSERT INTO departments (code, name, hod_name, student_count, faculty_count)
            VALUES (?, ?, ?, ?, ?)
            """, ("AIML", "Artificial Intelligence and Machine Learning", "Dr. Priya Krishnaswamy", 0, 1))

        # 2. Ensure AIML faculty (faculty006)
        cursor.execute("SELECT faculty_id FROM faculty WHERE faculty_id = 'faculty006'")
        if not cursor.fetchone():
            cursor.execute("""
            INSERT INTO faculty (faculty_id, user_id, name, email, department, designation, phone, specialization)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, ("faculty006", "faculty006", "Dr. Priya Krishnaswamy", "priya.k@campusiq.edu", "AIML", "Professor & Head, AIML", "+91 9811223350", "Generative AI & Neural Networks"))

        # 3. Ensure AIML courses
        aiml_courses = [
            ("AIML401", "Artificial Intelligence and Machine Learning", "AIML", 4, 4, "Dr. Priya Krishnaswamy", 88.5),
            ("AIML402", "Deep Learning & Neural Architectures", "AIML", 6, 4, "Dr. Priya Krishnaswamy", 86.0)
        ]
        for c_code, c_name, dept, sem, cred, fac, prate in aiml_courses:
            cursor.execute("SELECT course_code FROM courses WHERE course_code = ?", (c_code,))
            if not cursor.fetchone():
                cursor.execute("""
                INSERT INTO courses (course_code, course_name, department, semester, credits, faculty_name, pass_rate)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (c_code, c_name, dept, sem, cred, fac, prate))

        # 4. Check dummy student count per department and top up to 10
        OFFICIAL_DEMO_IDS = {f"CIQ-2026-{i:03d}" for i in range(1, 11)}
        from database.academic_curriculum import generate_records_for_student

        for dept_code, pool in DEMO_STUDENTS_POOL.items():
            meta = DEPT_METADATA[dept_code]
            cursor.execute("SELECT student_id FROM students WHERE department = ?", (dept_code,))
            existing_sids = [r[0] for r in cursor.fetchall()]
            
            # Count only official demo and generated dummy records (exclude real students)
            existing_dummy_sids = [sid for sid in existing_sids if sid in OFFICIAL_DEMO_IDS or sid.startswith("CIQ-DEMO-")]
            existing_dummy_count = len(existing_dummy_sids)
            needed = max(0, 10 - existing_dummy_count)

            if needed > 0:
                added_count = 0
                dept_tag = dept_code.replace("&", "")
                for idx, cand in enumerate(pool, start=1):
                    if added_count >= needed:
                        break
                    cand_id = f"CIQ-DEMO-{dept_tag}-{idx:02d}"
                    if cand_id in existing_sids:
                        continue

                    email = f"{cand['name'].lower().replace(' ', '.')}@demo.campusiq.edu"
                    s_data = {
                        "cgpa": cand["cgpa"],
                        "academic_marks_pct": cand["marks"],
                        "attendance_pct": cand["att"],
                        "backlogs": cand["backlogs"],
                        "lms_weekly_hours": cand["hours"],
                        "lms_engagement_score": cand["lms"],
                        "assignment_completion_pct": cand["assign"],
                        "extracurricular_score": cand["extra"],
                        "placement_aptitude_score": cand["apt"],
                        "technical_skills_score": cand["tech"],
                        "student_feedback_score": cand["feedback"]
                    }
                    metrics = analytics_engine.compute_student_metrics(s_data)

                    cursor.execute("""
                    INSERT INTO students (
                        student_id, user_id, name, email, gender, department, department_name,
                        semester, section, faculty_id, mentor_name, cgpa, academic_marks_pct,
                        attendance_pct, backlogs, lms_weekly_hours, lms_engagement_score,
                        assignment_completion_pct, extracurricular_score, placement_aptitude_score,
                        technical_skills_score, student_feedback_score, phone, success_score, risk_level, segment
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        cand_id, cand_id, cand["name"], email, cand["gender"],
                        dept_code, meta["name"],
                        cand["sem"], cand["sec"],
                        meta["fac_id"], meta["mentor"],
                        cand["cgpa"], cand["marks"],
                        cand["att"], cand["backlogs"],
                        cand["hours"], cand["lms"],
                        cand["assign"], cand["extra"],
                        cand["apt"], cand["tech"],
                        cand["feedback"], "+91 9800000000",
                        metrics["success_score"], metrics["risk_level"], metrics["segment"]
                    ))

                    # Seed academic records for dummy student
                    stu_row = {
                        "student_id": cand_id,
                        "department": dept_code,
                        "semester": cand["sem"],
                        "cgpa": cand["cgpa"],
                        "academic_marks_pct": cand["marks"],
                        "attendance_pct": cand["att"]
                    }
                    try:
                        recs = generate_records_for_student(stu_row)
                        for r in recs:
                            cursor.execute("""
                            INSERT INTO academic_records (
                                student_id, year, semester, semester_label, academic_year,
                                course_code, course_name, credits, mid1_marks, mid1_max,
                                mid2_marks, mid2_max, internal_marks, internal_max,
                                external_marks, external_max, total_marks, total_max,
                                grade, status, classes_conducted, classes_attended, attendance_pct, sgpa
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                            """, (
                                r["student_id"], r["year"], r["semester"], r["semester_label"], r["academic_year"],
                                r["course_code"], r["course_name"], r["credits"], r["mid1_marks"], r["mid1_max"],
                                r["mid2_marks"], r["mid2_max"], r["internal_marks"], r["internal_max"],
                                r["external_marks"], r["external_max"], r["total_marks"], r["total_max"],
                                r["grade"], r["status"], r["classes_conducted"], r["classes_attended"], r["attendance_pct"], r["sgpa"]
                            ))
                    except Exception:
                        pass

                    # Seed sample fee record for current semester
                    y = (cand["sem"] + 1) // 2
                    s_part = 1 if (cand["sem"] % 2 != 0) else 2
                    s_label = f"{y}-{s_part}"
                    cursor.execute("""
                    INSERT INTO student_fees (
                        student_id, academic_year, year, semester, semester_label, total_fee, amount_paid, due_date
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (cand_id, "2024-2025", y, cand["sem"], s_label, 65000.0, 65000.0, "2025-01-20"))

                    added_count += 1

        # 5. Update department student and faculty counts
        cursor.execute("""
        UPDATE departments
        SET student_count = (SELECT COUNT(*) FROM students WHERE students.department = departments.code),
            faculty_count = (SELECT COUNT(*) FROM faculty WHERE faculty.department = departments.code)
        """)

        # 6. Auto-sync: Ensure every faculty and student has an authentication record in users table
        cursor.execute("SELECT * FROM faculty")
        f_pass_hash = generate_password_hash("Faculty@123")
        for f in cursor.fetchall():
            f_uid = f["user_id"] or f["faculty_id"]
            cursor.execute("SELECT COUNT(*) as count FROM users WHERE user_id = ?", (f_uid,))
            if cursor.fetchone()["count"] == 0:
                cursor.execute("""
                INSERT INTO users (user_id, password_hash, role, name, email, department)
                VALUES (?, ?, 'faculty', ?, ?, ?)
                """, (f_uid, f_pass_hash, f["name"], f["email"], f["department"]))

        cursor.execute("SELECT * FROM students")
        s_pass_hash = generate_password_hash("Student@123")
        for s in cursor.fetchall():
            s_uid = s["student_id"]
            cursor.execute("SELECT COUNT(*) as count FROM users WHERE user_id = ?", (s_uid,))
            if cursor.fetchone()["count"] == 0:
                cursor.execute("""
                INSERT INTO users (user_id, password_hash, role, name, email, department)
                VALUES (?, ?, 'student', ?, ?, ?)
                """, (s_uid, s_pass_hash, s["name"], s["email"], s["department"]))

        conn.commit()
    finally:
        if owns_conn:
            conn.close()

if __name__ == "__main__":
    init_db(force=True)
