"""
CampusIQ – Database Module
SQLite Database Engine, Connection Manager, and Comprehensive Seed Generator
KPMG in India Hackathon Challenge Prototype (10-Student Calibrated Cohort)
"""

import sqlite3
import csv
from pathlib import Path
from werkzeug.security import generate_password_hash
from services.analytics import analytics_engine

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "database" / "campusiq.db"
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
        priority TEXT NOT NULL,
        notes TEXT NOT NULL,
        status TEXT DEFAULT 'In Progress',
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
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

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
            ("ME", "Mechanical Engineering", "Dr. K. S. Pillai", 1, 1)
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
            ("T&P201", "KPMG Campus Placement Mock Aptitude & Coding", "CSE", 8, 2, "Dr. Sunita Rao", 93.0)
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
            ("faculty005", "FAC-ME-01", "Dr. K. S. Pillai", "ks.pillai@campusiq.edu", "ME", "Professor & Head, ME", "+91 9811223349", "Robotics & Thermal Systems", "Faculty@123")
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

        mentor_map = {
            "Dr. Sunita Rao": "faculty001",
            "Dr. Meenakshi Sundaram": "faculty002",
            "Prof. Neha Gupta": "faculty003",
            "Dr. Amit Verma": "faculty004",
            "Dr. K. S. Pillai": "faculty005"
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

    conn.close()

if __name__ == "__main__":
    init_db(force=True)
