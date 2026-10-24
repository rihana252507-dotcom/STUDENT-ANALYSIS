with open('app.py', 'r', encoding='utf-8') as f:
    text = f.read()

target = """    # Enforce student permission
    if current_role == "student" and current_user_id.upper() != str(student_id).upper():
        return jsonify({"error": "Forbidden", "message": "Unauthorized simulation"}), 403"""

replacement = """    # Enforce student permission: allow matching by user_id or student_id
    if current_role == "student":
        allowed_ids = {str(current_user_id).upper(), str(session.get("student_id", "")).upper()}
        if str(student_id).upper() not in allowed_ids:
            return jsonify({"error": "Forbidden", "message": "Unauthorized simulation"}), 403"""

assert target in text, "target not found in app.py"
text = text.replace(target, replacement)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(text)

print("app.py permission check updated successfully!")
