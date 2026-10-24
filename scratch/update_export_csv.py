with open('app.py', 'r', encoding='utf-8') as f:
    code = f.read()

target_csv = '''    if current_role == "student":
        return jsonify({"error": "Forbidden"}), 403

    conn = get_db()
    cursor = conn.cursor()

    if current_role == "faculty":
        cursor.execute("SELECT * FROM students WHERE faculty_id = ? OR department = ?", (current_user_id, current_dept))
    else:
        cursor.execute("SELECT * FROM students")'''

repl_csv = '''    if current_role == "student":
        return jsonify({"error": "Forbidden"}), 403

    conn = get_db()
    cursor = conn.cursor()

    if current_role == "hod":
        if not current_dept:
            conn.close()
            return jsonify({"error": "Forbidden", "message": "No department assigned"}), 403
        cursor.execute("SELECT * FROM students WHERE department = ? COLLATE NOCASE", (current_dept,))
    elif current_role == "faculty":
        cursor.execute("SELECT * FROM students WHERE faculty_id = ? OR department = ?", (current_user_id, current_dept))
    else:
        cursor.execute("SELECT * FROM students")'''

if target_csv in code:
    code = code.replace(target_csv, repl_csv, 1)
    
    # Also ensure HOD cannot override dept via query parameter
    target_dept_filter = '''    if dept != "ALL":
        students = [s for s in students if s["department"].upper() == dept.upper()]'''
        
    repl_dept_filter = '''    if current_role == "hod":
        dept = current_dept
    if dept != "ALL":
        students = [s for s in students if (s.get("department") or "").upper() == dept.upper()]'''
        
    code = code.replace(target_dept_filter, repl_dept_filter, 1)
    
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(code)
    print("Updated export_csv in app.py for strict HOD department filtering")
else:
    print("Target not found for export_csv")
