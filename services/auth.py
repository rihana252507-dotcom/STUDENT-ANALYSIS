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
    Returns user dict on success, None on failure.
    """
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id.strip(),))
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
    session["user_id"] = user["user_id"]
    session["role"] = user["role"]
    session["name"] = user["name"]
    session["email"] = user["email"]
    session["department"] = user.get("department", "")

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
                elif user_role == "faculty":
                    return redirect(url_for("faculty_dashboard"))
                elif user_role == "student":
                    return redirect(url_for("student_dashboard"))
                return redirect(url_for("login"))

            return f(*args, **kwargs)
        return decorated_function
    return decorator
