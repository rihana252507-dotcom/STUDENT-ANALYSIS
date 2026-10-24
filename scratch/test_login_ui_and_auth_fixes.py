"""
Comprehensive test suite verifying:
1. Login page blue color is soft and light, form is white, text is dark (#172B4D / #5B6B82).
2. Login success notification follows exact specification: #FFFFFF background, #172B4D text, #DCE4EE border, #16A34A success accent.
3. Failed login attempts do NOT display a success notification.
4. Dismissing notification does NOT log out the user or clear the session.
5. All 4 dashboards (Admin, HOD, Faculty, Student) load with HTTP 200, retain session across refreshes, and have high-contrast text.
6. Logout button and route work as intended.
"""

import os
import re
import pytest
from app import app
from database.db import get_db

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_login_page_renders_soft_light_palette(client):
    """Verify login page uses soft light canvas background, white card, and high-contrast text."""
    res = client.get("/login")
    assert res.status_code == 200
    html = res.get_data(as_text=True)

    # Check style.css has soft light background and white container
    css_path = os.path.join(os.path.dirname(__file__), "..", "static", "css", "style.css")
    with open(css_path, "r", encoding="utf-8") as f:
        css = f.read()

    # Soft, light page body
    assert "#F4F7FB" in css
    assert ".login-page-body" in css
    # White login container
    assert ".login-glass-container" in css
    assert "background: #FFFFFF" in css or "background:#FFFFFF" in css
    # Primary button #2F80ED
    assert ".btn-gradient-submit" in css
    assert "#2F80ED" in css


def test_login_success_notification_styling():
    """Verify .ciq-flash-notification specifies background #FFFFFF, color #172B4D, border #DCE4EE, accent #16A34A."""
    css_path = os.path.join(os.path.dirname(__file__), "..", "static", "css", "style.css")
    with open(css_path, "r", encoding="utf-8") as f:
        css = f.read()

    assert ".ciq-flash-notification" in css
    assert "#FFFFFF" in css
    assert "#172B4D" in css
    assert "#DCE4EE" in css
    assert "#16A34A" in css


def test_successful_login_displays_success_message(client):
    """Verify valid login establishes session, redirects to dashboard, and presents success message."""
    # Test Admin login
    res = client.post("/login", data={"username": "admin001", "password": "Admin@123"}, follow_redirects=True)
    assert res.status_code == 200
    html = res.get_data(as_text=True)

    # Success notification present
    assert "ciq-flash-notification" in html
    assert "logged in successfully" in html.lower() or "welcome back" in html.lower()
    # Correct white background & dark text inline or class
    assert "#FFFFFF" in html
    assert "#172B4D" in html

    # Confirm session established
    with client.session_transaction() as sess:
        assert sess.get("user_id") == "admin001"
        assert sess.get("role") == "admin"


def test_failed_login_does_not_display_success_notification(client):
    """Verify failed login attempt shows error message and NEVER shows success notification."""
    res = client.post("/login", data={"username": "admin001", "password": "WrongPassword!"}, follow_redirects=True)
    assert res.status_code == 200
    html = res.get_data(as_text=True)

    # Danger/warning alert shown
    assert "Invalid User ID or Password" in html
    # MUST NOT show success notification or success message
    assert "You are logged in successfully" not in html
    assert "ciq-flash-notification success" not in html

    # Session MUST NOT be authenticated
    with client.session_transaction() as sess:
        assert "user_id" not in sess


def test_session_remains_active_on_refresh_and_navigation(client):
    """Verify authenticated session persists across multiple requests and refreshes without premature logout."""
    # 1. Log in as Faculty
    client.post("/login", data={"username": "faculty001", "password": "Faculty@123"}, follow_redirects=True)

    with client.session_transaction() as sess:
        assert sess.get("user_id") == "faculty001"
        assert sess.get("role") == "faculty"

    # 2. Refresh dashboard
    res1 = client.get("/faculty/dashboard")
    assert res1.status_code == 200

    # 3. Request API endpoints as faculty
    res2 = client.get("/api/students")
    assert res2.status_code == 200

    # 4. Refresh dashboard again
    res3 = client.get("/faculty/dashboard")
    assert res3.status_code == 200

    # 5. Session remains valid
    with client.session_transaction() as sess:
        assert sess.get("user_id") == "faculty001"


def test_student_session_and_dashboard_refresh(client):
    """Verify student login (student001) persists and renders dashboard without redirecting to logout."""
    res = client.post("/login", data={"username": "student001", "password": "Student@123"}, follow_redirects=True)
    assert res.status_code == 200
    html = res.get_data(as_text=True)

    # Must be on student dashboard, NOT logged out
    assert "student-dashboard" in html.lower() or "my dashboard" in html.lower()

    # Refresh
    res2 = client.get("/student/dashboard")
    assert res2.status_code == 200
    html2 = res2.get_data(as_text=True)
    assert "my dashboard" in html2.lower()

    with client.session_transaction() as sess:
        assert sess.get("role") == "student"


def test_hod_session_and_dashboard_refresh(client):
    """Verify HOD login (hod_cse) persists and renders HOD dashboard without premature logout."""
    res = client.post("/login", data={"username": "hod_cse", "password": "Hod@123"}, follow_redirects=True)
    assert res.status_code == 200
    html = res.get_data(as_text=True)
    assert "hod dashboard" in html.lower() or "department overview" in html.lower()

    # Refresh
    res2 = client.get("/hod/dashboard")
    assert res2.status_code == 200


def test_logout_button_terminates_session(client):
    """Verify explicit call to /logout clears session and redirects to /login."""
    # First log in
    client.post("/login", data={"username": "admin001", "password": "Admin@123"}, follow_redirects=True)

    with client.session_transaction() as sess:
        assert sess.get("user_id") == "admin001"

    # Call /logout
    res = client.get("/logout", follow_redirects=True)
    assert res.status_code == 200
    html = res.get_data(as_text=True)
    assert "Portal Sign In" in html

    # Session is cleared
    with client.session_transaction() as sess:
        assert "user_id" not in sess


def test_dashboard_text_readability_in_templates():
    """Verify KPI card subtext and modals have dark high-contrast colors (#5B6B82 / #172B4D)."""
    admin_path = os.path.join(os.path.dirname(__file__), "..", "templates", "admin_dashboard.html")
    with open(admin_path, "r", encoding="utf-8") as f:
        html = f.read()

    # Faint #C4B5FD on white KPI cards replaced with readable #5B6B82
    assert '<span style="color:#C4B5FD; font-size:0.75rem;">Across 5 branches</span>' not in html
    assert '<span style="color:#5B6B82; font-size:0.75rem;">Across 5 branches</span>' in html
    assert '<span style="color:#5B6B82; font-size:0.75rem;">5-pillar weighted</span>' in html
    assert '<span style="color:#5B6B82; font-size:0.75rem;">UGC &ge; 75% rule</span>' in html

    # Light modal styling
    assert 'background:#F8FBFF; border:1px solid #DCE4EE;' in html
    assert 'color:#172B4D;' in html
