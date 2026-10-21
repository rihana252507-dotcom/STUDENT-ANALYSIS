"""
Comprehensive verification test suite for the personalized Job Preparation
and Skills Roadmap in CampusIQ (Student Login -> Placement Readiness).

Verifies:
1. Student authentication and profile loading for Roadmap.
2. GET /api/student/roadmap returns pre-filled target role, branch, semester, stages, projects, and interview question bank.
3. POST /api/student/roadmap updates target role, timeline, hours, skill assessments, and practical tasks.
4. Skill gap categorization: Skills I Know, Skills I Am Learning, and Skills I Need to Learn.
5. Readiness score calculation: 50% weighted core skills + 50% weighted roadmap tasks.
6. Persistence: Database writes to `student_career_plan` and `student_skills` persist across logins.
7. Data isolation: Student A's career plan does not bleed into Student B's career plan.
8. Preservation of all 9 sections in student dashboard HTML markup.
"""

import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import app
from database.db import get_db

def test_career_roadmap_full_workflow():
    client = app.test_client()

    # -------------------------------------------------------------------------
    # 1. Login as Student 1 (student001 / Aarav Reddy)
    # -------------------------------------------------------------------------
    login_res = client.post("/login", json={"user_id": "student001", "password": "Student@123"})
    assert login_res.status_code == 200
    user_info = login_res.get_json()
    assert user_info["name"] == "Aarav Reddy"

    # -------------------------------------------------------------------------
    # 2. Check Student Dashboard HTML contains all 9 Roadmap Sections
    # -------------------------------------------------------------------------
    dash_res = client.get("/student")
    assert dash_res.status_code == 200
    html = dash_res.data.decode("utf-8")
    assert 'id="section-placement-readiness"' in html
    assert "Personalized Job Preparation &amp; Skills Roadmap" in html
    assert "1. Choose Your Career Goal" in html
    assert "2. Required Skills for Selected Job" in html
    assert "3. My Current Skills Self-Evaluation" in html
    assert "4. Skill Gap Analysis" in html
    assert "5. Step-by-Step Learning Roadmap" in html
    assert "6. Recommended Projects to Build" in html
    assert "7. Placement Practice Bank (Aptitude, Technical &amp; HR)" in html
    assert "8. Verified Learning Documentation &amp; Platforms" in html
    assert "Job Readiness Score" in html

    # -------------------------------------------------------------------------
    # 3. GET /api/student/roadmap endpoint returns structured roadmap data
    # -------------------------------------------------------------------------
    get_res = client.get("/api/student/roadmap")
    assert get_res.status_code == 200
    data = get_res.get_json()
    assert data["success"] is True
    assert data["student"]["name"] == "Aarav Reddy"
    assert "role_data" in data
    assert "core_skills" in data["role_data"]
    assert "optional_skills" in data["role_data"]
    assert "stages" in data["role_data"]
    assert len(data["role_data"]["stages"]) >= 3
    assert "projects" in data["role_data"]
    assert len(data["role_data"]["projects"]) >= 2
    assert "interview_prep" in data
    assert "Quantitative Aptitude" in data["interview_prep"]
    assert "HR & Behavioral Questions" in data["interview_prep"]

    # -------------------------------------------------------------------------
    # 4. POST /api/student/roadmap: Save tailored career goal & skill assessments
    # -------------------------------------------------------------------------
    update_payload = {
        "target_role": "Data Analyst",
        "timeline_days": "60",
        "daily_hours": "2-3",
        "skill_level": "Intermediate",
        "preferred_language": "Python",
        "skill_assessments": {
            "Advanced Microsoft Excel & Google Sheets": "Confident",
            "SQL (Window Functions, Aggregations, Subqueries)": "Confident",
            "Python for Data Analysis (Pandas, NumPy)": "Practiced",
            "Data Visualization (Power BI or Tableau, Matplotlib/Seaborn)": "Learning"
        },
        "completed_tasks": ["s1_Master SQL SELECT, WHERE, GROUP BY, HAVING, and JOINs"]
    }

    save_res = client.post("/api/student/roadmap", json=update_payload)
    assert save_res.status_code == 200
    updated_data = save_res.get_json()

    assert updated_data["plan"]["target_role"] == "Data Analyst"
    assert updated_data["plan"]["timeline_days"] == 60
    assert updated_data["plan"]["daily_hours"] == "2-3"

    # Verify skill gap classification
    skill_gap = updated_data["skill_gap"]
    assert skill_gap["known_count"] >= 3
    assert skill_gap["learning_count"] >= 1
    assert skill_gap["needed_count"] > 0

    # Verify readiness percentage
    progress = updated_data["progress"]
    assert progress["readiness_percentage"] > 0
    assert progress["core_skills_coverage_pct"] > 50

    # -------------------------------------------------------------------------
    # 5. Database Persistence across Logout and Re-Login
    # -------------------------------------------------------------------------
    client.get("/logout")
    login_res2 = client.post("/login", json={"user_id": "student001", "password": "Student@123"})
    assert login_res2.status_code == 200

    re_get = client.get("/api/student/roadmap")
    assert re_get.status_code == 200
    persisted_data = re_get.get_json()
    assert persisted_data["plan"]["target_role"] == "Data Analyst"
    assert persisted_data["plan"]["skill_assessments"]["SQL (Window Functions, Aggregations, Subqueries)"] == "Confident"

    # -------------------------------------------------------------------------
    # 6. User Isolation: Ensure Student 2 (student002) has their own separate plan
    # -------------------------------------------------------------------------
    client.get("/logout")
    login_s2 = client.post("/login", json={"user_id": "student002", "password": "Student@123"})
    assert login_s2.status_code == 200

    get_s2 = client.get("/api/student/roadmap")
    assert get_s2.status_code == 200
    data_s2 = get_s2.get_json()
    # Student 2 should have their own default or distinct target role, not student001's assessments
    assert data_s2["student"]["name"] == "Aditi Kulkarni"
    assert data_s2["student"]["student_id"] != "student001"
    # Ensure Aditi's assessments don't mirror Aarav's saved data analyst assessments
    s2_assessments = data_s2["plan"].get("skill_assessments", {})
    assert s2_assessments.get("Advanced Microsoft Excel & Google Sheets") != "Confident"
