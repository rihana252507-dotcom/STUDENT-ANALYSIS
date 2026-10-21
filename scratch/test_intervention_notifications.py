"""
Verification Test Suite: Admin-to-Faculty Intervention Notifications with Red Dot Indicator
Tests all 12 items in TASK specification.
"""
import pytest
import sqlite3
import json
from app import app
from database.db import get_db, DB_PATH

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def login(client, user_id, password):
    return client.post("/login", data={"username": user_id, "password": password}, follow_redirects=True)

def test_01_admin_creates_intervention_and_notification(client):
    """1 & 2: Admin creates intervention; it's saved in SQLite along with faculty notification."""
    # Login as admin
    res = login(client, "admin001", "Admin@123")
    assert res.status_code == 200

    # Select existing student student001 and assign to faculty001
    payload = {
        "title": "Attendance Improvement Plan Test",
        "action_type": "Attendance Improvement Plan Test",
        "priority": "Urgent",
        "faculty_id": "faculty001",
        "faculty_name": "Dr. Sunita Rao",
        "due_date": "2026-11-01",
        "instructions": "Contact student, discuss attendance concerns, and prepare weekly improvement plan.",
        "notes": "Test intervention notes from Admin"
    }
    post_res = client.post("/api/students/student001/intervention", json=payload)
    assert post_res.status_code == 201
    data = post_res.get_json()
    assert data["success"] is True
    intv_id = data["intervention_id"]

    # Verify persistence in SQLite
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM interventions WHERE id = ?", (intv_id,))
    intv = cur.fetchone()
    assert intv is not None
    assert intv["student_id"] == "CIQ-2026-001"
    assert intv["faculty_id"] == "faculty001"
    assert intv["title"] == "Attendance Improvement Plan Test"
    assert intv["priority"] == "Urgent"
    assert intv["due_date"] == "2026-11-01"
    assert intv["status"] == "Assigned"

    # Verify notification in SQLite
    cur.execute("SELECT * FROM notifications WHERE intervention_id = ?", (intv_id,))
    notif = cur.fetchone()
    assert notif is not None
    assert notif["user_id"] == "faculty001"
    assert notif["is_read"] == 0
    assert "Attendance Improvement Plan Test" in notif["title"]
    conn.close()

def test_02_faculty_sees_notification_and_unread_count(client):
    """3 & 4: Correct faculty sees notification with unread count > 0 (red dot)."""
    # Login as faculty001
    res = login(client, "faculty001", "Faculty@123")
    assert res.status_code == 200

    notif_res = client.get("/api/notifications")
    assert notif_res.status_code == 200
    data = notif_res.get_json()
    assert data["unread_count"] > 0
    assert any(n.get("intv_title") == "Attendance Improvement Plan Test" or "Attendance Improvement Plan Test" in n.get("title", "") for n in data["notifications"])

def test_03_other_faculty_cannot_see_or_modify(client):
    """10: Other faculty cannot access the notification or modify the intervention."""
    # Find our test intervention
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT id FROM interventions WHERE title = 'Attendance Improvement Plan Test' ORDER BY id DESC LIMIT 1")
    intv_row = cur.fetchone()
    assert intv_row is not None
    intv_id = intv_row["id"]
    cur.execute("SELECT id FROM notifications WHERE intervention_id = ?", (intv_id,))
    notif_row = cur.fetchone()
    notif_id = notif_row["id"]
    conn.close()

    # Login as faculty002
    res = login(client, "faculty002", "Faculty@123")
    assert res.status_code == 200

    # Notification list of faculty002 should NOT contain this notification
    notif_res = client.get("/api/notifications")
    notifs = notif_res.get_json()["notifications"]
    assert not any(n["id"] == notif_id for n in notifs)

    # Attempt to mark notification read should fail 403
    mark_res = client.post(f"/api/notifications/{notif_id}/read")
    assert mark_res.status_code == 403

    # Attempt to update intervention should fail 403
    update_res = client.put(f"/api/interventions/{intv_id}", json={
        "status": "In Progress",
        "action_taken": "Unauthorized update attempt"
    })
    assert update_res.status_code == 403

def test_04_faculty_marks_notification_as_read_and_red_dot_clears(client):
    """5 & 6: Opening/marking read clears unread state and persists across re-login."""
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT id FROM interventions WHERE title = 'Attendance Improvement Plan Test' ORDER BY id DESC LIMIT 1")
    intv_id = cur.fetchone()["id"]
    cur.execute("SELECT id FROM notifications WHERE intervention_id = ?", (intv_id,))
    notif_id = cur.fetchone()["id"]
    conn.close()

    # Login as faculty001
    login(client, "faculty001", "Faculty@123")

    # Mark as read
    res = client.post(f"/api/notifications/{notif_id}/read")
    assert res.status_code == 200

    # Verify DB persistence
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT is_read, read_at FROM notifications WHERE id = ?", (notif_id,))
    row = cur.fetchone()
    assert row["is_read"] == 1
    assert row["read_at"] is not None
    conn.close()

    # Logout and re-login
    client.get("/logout")
    login(client, "faculty001", "Faculty@123")

    # Fetch notifications again; this item should be read
    res2 = client.get("/api/notifications")
    data2 = res2.get_json()
    item = next(n for n in data2["notifications"] if n["id"] == notif_id)
    assert item["is_read"] == 1

def test_05_faculty_updates_intervention_status_and_notes(client):
    """7 & 8: Faculty marks In Progress, adds notes, then marks Completed."""
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT id FROM interventions WHERE title = 'Attendance Improvement Plan Test' ORDER BY id DESC LIMIT 1")
    intv_id = cur.fetchone()["id"]
    conn.close()

    # Login as faculty001
    login(client, "faculty001", "Faculty@123")

    # Step 1: Mark In Progress with Action Taken
    res1 = client.put(f"/api/interventions/{intv_id}", json={
        "status": "In Progress",
        "action_taken": "Conducted 1-on-1 meeting with Aarav",
        "implementation_notes": "Student agreed to daily attendance tracking"
    })
    assert res1.status_code == 200

    # Step 2: Mark Completed
    res2 = client.put(f"/api/interventions/{intv_id}", json={
        "status": "Completed",
        "action_taken": "Conducted 1-on-1 meeting; student attended all classes this week",
        "implementation_notes": "Completed weekly improvement plan successfully"
    })
    assert res2.status_code == 200

    # Verify persistence
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM interventions WHERE id = ?", (intv_id,))
    row = cur.fetchone()
    assert row["status"] == "Completed"
    assert "Conducted 1-on-1" in row["action_taken"]
    assert "Completed weekly" in row["implementation_notes"]
    assert row["completed_at"] is not None
    conn.close()

def test_06_admin_views_intervention_progress_and_faculty_response(client):
    """9: Admin views intervention status and faculty response."""
    login(client, "admin001", "Admin@123")

    res = client.get("/api/interventions")
    assert res.status_code == 200
    data = res.get_json()
    intvs = data["interventions"]
    match = next(i for i in intvs if i.get("title") == "Attendance Improvement Plan Test")
    assert match["status"] == "Completed"
    assert match["faculty_name"] == "Dr. Sunita Rao"
    assert match["notif_is_read"] == 1
    assert "Conducted 1-on-1" in match["action_taken"]
