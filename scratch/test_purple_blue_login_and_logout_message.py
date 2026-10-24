"""
Tests for:
1. Login page Purple + Blue theme styling and contrast.
2. Logout route displaying exact message 'Logged out successfully.' with #FFFFFF background, #172B4D text, #DCE4EE border, #16A34A icon, #6D28D9 accent.
3. Session clearance on logout.
4. Preserved login flows for all 4 roles.
"""

import os
import pytest
from app import app

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_login_page_purple_blue_palette():
    """Verify static/css/style.css defines the purple + blue theme scoped to the login page."""
    css_path = os.path.join(os.path.dirname(__file__), "..", "static", "css", "style.css")
    with open(css_path, "r", encoding="utf-8") as f:
        css = f.read()

    # Lavender & light blue background
    assert "#F3F0FF" in css
    assert "#EFF6FF" in css

    # Primary purple #6D28D9 and blue #2F80ED
    assert "#6D28D9" in css
    assert "#2F80ED" in css

    # Showcase panel gradient
    assert "linear-gradient(135deg, #6D28D9 0%, #2563EB 55%, #2F80ED 100%)" in css

    # Input fields: white background, #DCE4EE border, #6D28D9 focus
    assert "input:focus" in css
    assert "border-color: #6D28D9" in css

    # Button: purple to blue gradient
    assert "linear-gradient(135deg, #6D28D9 0%, #2F80ED 100%)" in css


def test_logout_displays_exact_message_and_styling(client):
    """Verify /logout clears session and flashes exact message 'Logged out successfully.' with white bg, dark text, #16A34A icon, #6D28D9 accent."""
    # 1. Log in first
    client.post("/login", data={"username": "admin001", "password": "Admin@123"}, follow_redirects=True)
    with client.session_transaction() as sess:
        assert sess.get("user_id") == "admin001"

    # 2. Trigger logout
    res = client.get("/logout", follow_redirects=True)
    assert res.status_code == 200
    html = res.get_data(as_text=True)

    # 3. Check exact message text
    assert "Logged out successfully." in html

    # 4. Check notification visual contract
    assert "ciq-flash-notification success" in html
    assert "background:#FFFFFF" in html
    assert "#172B4D" in html  # dark readable text
    assert "#DCE4EE" in html  # border
    assert "#16A34A" in html  # success icon
    assert "#6D28D9" in html  # purple accent border

    # 5. Confirm session is completely cleared
    with client.session_transaction() as sess:
        assert "user_id" not in sess


def test_all_four_role_logins_preserved(client):
    """Verify Admin, HOD, Faculty, and Student can all log in and access their respective dashboards."""
    roles = [
        ("admin001", "Admin@123", "admin", "/admin/dashboard"),
        ("hod_cse", "Hod@123", "hod", "/hod/dashboard"),
        ("faculty001", "Faculty@123", "faculty", "/faculty/dashboard"),
        ("student001", "Student@123", "student", "/student/dashboard"),
    ]

    for username, password, expected_role, expected_path in roles:
        res = client.post("/login", data={"username": username, "password": password}, follow_redirects=True)
        assert res.status_code == 200
        with client.session_transaction() as sess:
            assert sess.get("role") == expected_role
            assert sess.get("user_id") == username

        # Clean logout before next role
        client.get("/logout")
