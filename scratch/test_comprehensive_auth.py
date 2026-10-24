import pytest
from app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    app.config["SECRET_KEY"] = "test-secret"
    with app.test_client() as client:
        yield client


def test_unauthenticated_access_protection(client):
    """Unauthenticated requests must be blocked with redirect to /login or 401 for APIs."""
    pages = ["/admin", "/admin/dashboard", "/hod", "/hod/dashboard", "/faculty", "/faculty/dashboard", "/student", "/student/dashboard"]
    for p in pages:
        res = client.get(p)
        assert res.status_code == 302, f"Failed for {p}"
        assert "/login" in res.headers["Location"], f"Failed redirect for {p}"

    api_endpoints = ["/api/admin/overview", "/api/hod/overview", "/api/students", "/api/interventions"]
    for ep in api_endpoints:
        res = client.get(ep)
        assert res.status_code == 401, f"Failed for {ep}"


def test_invalid_login_credentials(client):
    """Invalid user credentials must stay on /login with flash message."""
    # Bad password
    res = client.post("/login", data={"username": "admin", "password": "WrongPassword!"})
    assert res.status_code == 200
    assert b"Invalid User ID or Password" in res.data

    # Unknown user
    res = client.post("/login", data={"username": "non_existent_user", "password": "AnyPassword"})
    assert res.status_code == 200
    assert b"Invalid User ID or Password" in res.data

    # Blank fields
    res = client.post("/login", data={"username": "", "password": ""})
    assert res.status_code == 200


def test_admin_full_lifecycle(client):
    """Admin logs in, accesses admin pages and APIs, gets redirected on unauthorized role portals, logs out."""
    login_res = client.post("/login", data={"username": "admin", "password": "Admin@123"}, follow_redirects=False)
    assert login_res.status_code == 302
    assert "/admin" in login_res.headers["Location"]

    # Access admin pages
    for p in ["/admin", "/admin/dashboard"]:
        res = client.get(p)
        assert res.status_code == 200
        assert b"CampusIQ" in res.data

    # Access admin overview API
    res = client.get("/api/admin/overview")
    assert res.status_code == 200

    # Cross-portal access (role_required redirects back to admin)
    for p in ["/faculty", "/student", "/hod"]:
        res = client.get(p, follow_redirects=False)
        assert res.status_code == 302
        assert "/admin" in res.headers["Location"]

    # Logout
    logout_res = client.get("/logout")
    assert logout_res.status_code == 302
    assert "/login" in logout_res.headers["Location"]

    # Confirm session terminated
    res = client.get("/admin")
    assert res.status_code == 302
    assert "/login" in res.headers["Location"]


def test_hod_full_lifecycle(client):
    """HOD logs in, accesses HOD pages and export APIs, gets redirected on admin/faculty/student portals, logs out."""
    login_res = client.post("/login", data={"username": "hod_cse", "password": "Hod@123"}, follow_redirects=False)
    assert login_res.status_code == 302
    assert "/hod" in login_res.headers["Location"]

    # Access HOD pages
    for p in ["/hod", "/hod/dashboard"]:
        res = client.get(p)
        assert res.status_code == 200
        assert b"CampusIQ" in res.data
        assert b"CSE" in res.data

    # Access HOD API
    res = client.get("/api/hod/overview")
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    assert data["department"]["code"] == "CSE"

    # Cross-portal access (redirects back to /hod)
    for p in ["/admin", "/faculty", "/student"]:
        res = client.get(p, follow_redirects=False)
        assert res.status_code == 302
        assert "/hod" in res.headers["Location"]

    # Cannot access admin-only API
    res = client.get("/api/admin/overview")
    assert res.status_code == 403

    # Logout
    client.get("/logout")
    res = client.get("/hod")
    assert res.status_code == 302
    assert "/login" in res.headers["Location"]


def test_faculty_full_lifecycle(client):
    """Faculty logs in, accesses faculty portal, gets redirected on other portals, logs out."""
    login_res = client.post("/login", data={"username": "faculty001", "password": "Faculty@123"}, follow_redirects=False)
    assert login_res.status_code == 302
    assert "/faculty" in login_res.headers["Location"]

    # Access faculty pages
    for p in ["/faculty", "/faculty/dashboard"]:
        res = client.get(p)
        assert res.status_code == 200
        assert b"CampusIQ" in res.data

    # Cross-portal access (redirects back to /faculty)
    for p in ["/admin", "/hod", "/student"]:
        res = client.get(p, follow_redirects=False)
        assert res.status_code == 302
        assert "/faculty" in res.headers["Location"]

    # Cannot access admin or hod API
    assert client.get("/api/admin/overview").status_code == 403
    assert client.get("/api/hod/overview").status_code == 403

    # Logout
    client.get("/logout")
    res = client.get("/faculty")
    assert res.status_code == 302
    assert "/login" in res.headers["Location"]


def test_student_full_lifecycle(client):
    """Student logs in, accesses student portal, gets redirected on other portals, logs out."""
    login_res = client.post("/login", data={"username": "student001", "password": "Student@123"}, follow_redirects=False)
    assert login_res.status_code == 302
    assert "/student" in login_res.headers["Location"]

    # Access student pages
    for p in ["/student", "/student/dashboard"]:
        res = client.get(p)
        assert res.status_code == 200
        assert b"CampusIQ" in res.data

    # Cross-portal access (redirects back to /student)
    for p in ["/admin", "/hod", "/faculty"]:
        res = client.get(p, follow_redirects=False)
        assert res.status_code == 302
        assert "/student" in res.headers["Location"]

    # Cannot access admin or hod API
    assert client.get("/api/admin/overview").status_code == 403
    assert client.get("/api/hod/overview").status_code == 403

    # Logout
    client.get("/logout")
    res = client.get("/student")
    assert res.status_code == 302
    assert "/login" in res.headers["Location"]
