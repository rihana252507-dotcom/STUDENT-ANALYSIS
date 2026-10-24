import pytest
import sqlite3
from app import app
from services.analytics import analytics_engine

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_student_success_score_attendance_simulation(client):
    # 1. Log in as student001 (Aarav Reddy, CIQ-2026-001)
    login_res = client.post("/login", json={
        "user_id": "student001",
        "password": "Student@123"
    })
    assert login_res.status_code == 200, "Student login failed"

    # 2. Check original stored score and attendance in DB
    conn = sqlite3.connect("database/campusiq.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM students WHERE student_id = 'CIQ-2026-001'")
    db_student = dict(cursor.fetchone())
    conn.close()

    orig_attendance = db_student["attendance_pct"]
    orig_score = db_student["success_score"]
    assert orig_attendance == 94.0
    assert orig_score == 92.3

    # 3. Simulate with attendance boost = 0
    res0 = client.post("/api/simulate", json={
        "student_id": "CIQ-2026-001",
        "attendance_boost": 0,
        "clear_backlogs": 0,
        "lms_hours_boost": 0,
        "assignment_boost": 0
    })
    assert res0.status_code == 200
    data0 = res0.get_json()
    assert data0["simulated"]["success_score"] == orig_score
    assert data0["score_delta"] == "+0.0"

    # 4. Simulate with attendance boost = 5% (94 + 5 = 99%)
    res5 = client.post("/api/simulate", json={
        "student_id": "CIQ-2026-001",
        "attendance_boost": 5,
        "clear_backlogs": 0,
        "lms_hours_boost": 0,
        "assignment_boost": 0
    })
    assert res5.status_code == 200
    data5 = res5.get_json()
    assert data5["simulated"]["success_score"] == 93.3
    assert data5["score_delta"] == "+1.0"

    # 5. Simulate with attendance boost = 25% (capped at 100%)
    res25 = client.post("/api/simulate", json={
        "student_id": "CIQ-2026-001",
        "attendance_boost": 25,
        "clear_backlogs": 0,
        "lms_hours_boost": 0,
        "assignment_boost": 0
    })
    assert res25.status_code == 200
    data25 = res25.get_json()
    assert data25["simulated"]["success_score"] == 93.5
    assert data25["score_delta"] == "+1.2"

    # 6. Verify student records in DB were NOT modified by simulations
    conn = sqlite3.connect("database/campusiq.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM students WHERE student_id = 'CIQ-2026-001'")
    db_student_after = dict(cursor.fetchone())
    conn.close()

    assert db_student_after["attendance_pct"] == orig_attendance, "DB record attendance was altered!"
    assert db_student_after["success_score"] == orig_score, "DB record success_score was altered!"

def test_low_attendance_student_simulation(client):
    # Student student007 (Divya Rao, CIQ-2026-007, attendance 61.5%, High Risk, score 41.5)
    login_res = client.post("/login", json={
        "user_id": "student007",
        "password": "Student@123"
    })
    assert login_res.status_code == 200

    # Test boosts: +10% (from 61.5 to 71.5) and +15% (from 61.5 to 76.5, crossing 75% threshold)
    res10 = client.post("/api/simulate", json={
        "student_id": "CIQ-2026-007",
        "attendance_boost": 10
    })
    assert res10.status_code == 200
    data10 = res10.get_json()
    assert data10["simulated"]["success_score"] == 46.5
    assert data10["score_delta"] == "+5.0"

    res15 = client.post("/api/simulate", json={
        "student_id": "CIQ-2026-007",
        "attendance_boost": 15
    })
    assert res15.status_code == 200
    data15 = res15.get_json()
    assert data15["simulated"]["success_score"] == 48.6
    assert data15["score_delta"] == "+7.1"

def test_attendance_formula_weights():
    # Verify the mathematical multi-pillar formula deterministic weights
    engine = analytics_engine
    assert engine.WEIGHTS["academic"] == 0.30
    assert engine.WEIGHTS["attendance"] == 0.20
    assert engine.WEIGHTS["lms"] == 0.15
    assert engine.WEIGHTS["placement"] == 0.20
    assert engine.WEIGHTS["wellbeing"] == 0.15
    assert sum(engine.WEIGHTS.values()) == 1.0
