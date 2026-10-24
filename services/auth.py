"""
CampusIQ – Authentication Service
Role-Based Access Control, Session Management, and Password Verification
KPMG in India Hackathon Challenge
"""

from functools import wraps
from flask import session, redirect, url_for, request, jsonify, flash
from werkzeug.security import check_password_hash, generate_password_hash
from database.db import get_db

def authenticate_user(user_id, password):
    """
    Validates user credentials against SQLite users table.
    Supports lookup by user_id, email, or linked student_id / faculty_id.
    Returns user dict on success, None on failure.
    """
    clean_id = (user_id or "").strip()
    if not clean_id or not password:
        return None

    conn = get_db()
    cursor = conn.cursor()

    # 1. Primary lookup in users table (case-insensitive)
    cursor.execute("""
        SELECT * FROM users 
        WHERE user_id = ? COLLATE NOCASE 
           OR email = ? COLLATE NOCASE
    """, (clean_id, clean_id))
    user = cursor.fetchone()

    # 2. If not found directly, check if clean_id is a student_id / roll number
    if not user:
        cursor.execute("""
            SELECT u.* FROM users u
            JOIN students s ON (s.user_id = u.user_id OR s.student_id = u.user_id)
            WHERE s.student_id = ? COLLATE NOCASE OR s.user_id = ? COLLATE NOCASE OR s.email = ? COLLATE NOCASE
        """, (clean_id, clean_id, clean_id))
        user = cursor.fetchone()

    # 3. If not found directly, check if clean_id is a faculty_id / code
    if not user:
        cursor.execute("""
            SELECT u.* FROM users u
            JOIN faculty f ON (f.user_id = u.user_id OR f.faculty_id = u.user_id)
            WHERE f.faculty_id = ? COLLATE NOCASE OR f.user_id = ? COLLATE NOCASE OR f.email = ? COLLATE NOCASE
        """, (clean_id, clean_id, clean_id))
        user = cursor.fetchone()

    conn.close()

    if not user:
        return None

    if check_password_hash(user["password_hash"], password):
        return {
            "id": user["id"],
            "user_id": user["user_id"],
            "role": user["role"],
            "name": user["name"],
            "email": user["email"],
            "department": user["department"]
        }
    return None

def login_user(user):
    """Stores user information securely in Flask session."""
    session.clear()
    session.permanent = True
    session["user_id"] = user["user_id"]
    session["role"] = user["role"]
    session["name"] = user["name"]
    session["email"] = user["email"]
    session["department"] = user.get("department", "")

    # Establish canonical student_id or faculty_id in session for reliable record queries
    conn = get_db()
    cursor = conn.cursor()
    if user["role"] == "student":
        cursor.execute("""
            SELECT student_id FROM students 
            WHERE student_id = ? COLLATE NOCASE OR user_id = ? COLLATE NOCASE OR email = ? COLLATE NOCASE
        """, (user["user_id"], user["user_id"], user.get("email", "")))
        s_row = cursor.fetchone()
        session["student_id"] = s_row["student_id"] if s_row else user["user_id"]
    elif user["role"] == "faculty":
        cursor.execute("""
            SELECT faculty_id FROM faculty 
            WHERE faculty_id = ? COLLATE NOCASE OR user_id = ? COLLATE NOCASE OR email = ? COLLATE NOCASE
        """, (user["user_id"], user["user_id"], user.get("email", "")))
        f_row = cursor.fetchone()
        session["faculty_id"] = f_row["faculty_id"] if f_row else user["user_id"]
    conn.close()

def logout_user():
    """Clears all session variables."""
    session.clear()

def get_current_user():
    """Returns currently authenticated user session dictionary or None."""
    if "user_id" in session:
        return {
            "user_id": session.get("user_id"),
            "role": session.get("role"),
            "name": session.get("name"),
            "email": session.get("email"),
            "department": session.get("department")
        }
    return None

def login_required(f):
    """Decorator ensuring that user is logged into an active session."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            if request.path.startswith("/api/"):
                return jsonify({"error": "Unauthorized", "message": "Authentication required"}), 401
            flash("Please sign in to access CampusIQ.", "warning")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function

def role_required(*allowed_roles):
    """Decorator enforcing strict role-based access permissions."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if "user_id" not in session:
                if request.path.startswith("/api/"):
                    return jsonify({"error": "Unauthorized", "message": "Authentication required"}), 401
                return redirect(url_for("login"))
            
            user_role = session.get("role")
            if user_role not in allowed_roles:
                if request.path.startswith("/api/"):
                    return jsonify({"error": "Forbidden", "message": "Insufficient role permissions"}), 403
                flash("You do not have authorization to access this view.", "danger")
                # Redirect user to their own dashboard
                if user_role == "admin":
                    return redirect(url_for("admin_dashboard"))
                elif user_role == "hod":
                    return redirect(url_for("hod_dashboard"))
                elif user_role == "faculty":
                    return redirect(url_for("faculty_dashboard"))
                elif user_role == "student":
                    return redirect(url_for("student_dashboard"))
                return redirect(url_for("login"))

            return f(*args, **kwargs)
        return decorated_function
    return decorator
