import os

path = os.path.join(os.path.dirname(__file__), "..", "app.py")
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Update /api/students backlog query & fields
target1 = """    # Query academic_records to accurately attach backlog subjects and count
    cursor.execute(\"\"\"
        SELECT student_id, GROUP_CONCAT(course_name, ', ') AS backlog_subjects, COUNT(*) AS backlog_records_count
        FROM academic_records
        WHERE LOWER(status) NOT IN ('passed', 'pass', 'completed', 'clear')
        GROUP BY student_id
    \"\"\")
    backlogs_map = {
        r["student_id"]: {
            "subjects": r["backlog_subjects"],
            "count": r["backlog_records_count"]
        }
        for r in cursor.fetchall()
    }
    conn.close()

    students = []
    for r in rows:
        s = dict(r)
        b_info = backlogs_map.get(s["student_id"], {})
        rec_count = b_info.get("count", 0)
        raw_subjects = b_info.get("subjects") or ""
        
        actual_backlogs = max(s.get("backlogs") or 0, rec_count)
        s["backlogs"] = actual_backlogs
        if raw_subjects:
            s["backlog_subjects"] = raw_subjects
        elif actual_backlogs > 0:
            s["backlog_subjects"] = "1 Active Backlog" if actual_backlogs == 1 else f"{actual_backlogs} Active Backlogs"
        else:
            s["backlog_subjects"] = ""
            
        s["academic_year"] = (s.get("semester", 1) + 1) // 2
        students.append(s)"""

replacement1 = """    # Query academic_records to accurately attach backlog subjects, structured details, and count
    cursor.execute(\"\"\"
        SELECT student_id, course_name, course_code, semester, academic_year, grade, status
        FROM academic_records
        WHERE LOWER(status) NOT IN ('passed', 'pass', 'completed', 'clear')
        ORDER BY semester ASC, id ASC
    \"\"\")
    backlogs_details_map = {}
    backlogs_subjects_map = {}
    for r in cursor.fetchall():
        sid = r["student_id"]
        c_code = r["course_code"] or ""
        disp = f"{r['course_name']} — {c_code}" if c_code else r["course_name"]
        item = {
            "course_name": r["course_name"],
            "course_code": c_code,
            "semester": r["semester"],
            "academic_year": r["academic_year"] or "",
            "grade": r["grade"] or "F",
            "display": disp
        }
        backlogs_details_map.setdefault(sid, []).append(item)
        backlogs_subjects_map.setdefault(sid, []).append(r["course_name"])
    conn.close()

    students = []
    for r in rows:
        s = dict(r)
        b_items = backlogs_details_map.get(s["student_id"], [])
        rec_count = len(b_items)
        s["backlog_details"] = b_items

        actual_backlogs = max(s.get("backlogs") or 0, rec_count)
        s["backlogs"] = actual_backlogs
        if b_items:
            s["backlog_subjects"] = ", ".join(backlogs_subjects_map.get(s["student_id"], []))
        elif actual_backlogs > 0:
            s["backlog_subjects"] = "1 Active Backlog" if actual_backlogs == 1 else f"{actual_backlogs} Active Backlogs"
        else:
            s["backlog_subjects"] = ""
            
        s["academic_year"] = (s.get("semester", 1) + 1) // 2
        students.append(s)"""

# 2. Update /api/students/<student_id>
target2 = """    student["logged_interventions"] = interventions
    student["academic_records"] = academic_records
    return jsonify(student)"""

replacement2 = """    # Structured backlog details with subject names, codes, semester, academic year
    backlog_items = [
        {
            "course_name": r["course_name"],
            "course_code": r.get("course_code") or "",
            "semester": r.get("semester"),
            "academic_year": r.get("academic_year") or "",
            "grade": r.get("grade") or "F",
            "display": f"{r['course_name']} — {r['course_code']}" if r.get("course_code") else r["course_name"]
        }
        for r in academic_records
        if (r.get("status") or "").lower() not in ("passed", "pass", "completed", "clear")
    ]
    student["backlog_details"] = backlog_items
    if backlog_items:
        student["backlog_subjects"] = "; ".join([b["display"] for b in backlog_items])
        student["backlogs"] = max(student.get("backlogs") or 0, len(backlog_items))
    else:
        student["backlog_subjects"] = ""
        if not student.get("backlogs"):
            student["backlogs"] = 0

    student["logged_interventions"] = interventions
    student["academic_records"] = academic_records
    return jsonify(student)"""

# Normalise newlines for exact search and replacement
norm_content = content.replace("\r\n", "\n")
norm_target1 = target1.replace("\r\n", "\n")
norm_target2 = target2.replace("\r\n", "\n")

assert norm_target1 in norm_content, "target1 not found in app.py"
assert norm_target2 in norm_content, "target2 not found in app.py"

norm_content = norm_content.replace(norm_target1, replacement1.replace("\r\n", "\n"), 1)
norm_content = norm_content.replace(norm_target2, replacement2.replace("\r\n", "\n"), 1)

# Preserve original CRLF
new_content = norm_content.replace("\n", "\r\n")

with open(path, "w", encoding="utf-8") as f:
    f.write(new_content)

print("Successfully patched app.py with backlog details!")
