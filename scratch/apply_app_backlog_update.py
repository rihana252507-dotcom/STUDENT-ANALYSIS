with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. In get_students()
old_part1 = """    # Query academic_records to accurately attach backlog subjects and count
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

new_part1 = """    # Query academic_records to accurately attach backlog subjects and count
    cursor.execute(\"\"\"
        SELECT student_id, course_name, course_code, semester, academic_year, grade, status
        FROM academic_records
        WHERE LOWER(status) NOT IN ('passed', 'pass', 'completed', 'clear')
        ORDER BY semester ASC, course_name ASC
    \"\"\")
    backlogs_map = {}
    for r in cursor.fetchall():
        sid = r["student_id"]
        item = {
            "course_name": r["course_name"],
            "course_code": r["course_code"] or "",
            "semester": r["semester"],
            "academic_year": r["academic_year"] or "",
            "grade": r["grade"] or "F",
            "display": f"{r['course_name']} — {r['course_code']}" if r["course_code"] else r["course_name"]
        }
        backlogs_map.setdefault(sid, []).append(item)
    conn.close()

    students = []
    for r in rows:
        s = dict(r)
        b_items = backlogs_map.get(s["student_id"], [])
        rec_count = len(b_items)

        actual_backlogs = max(s.get("backlogs") or 0, rec_count)
        s["backlogs"] = actual_backlogs
        s["backlog_details"] = b_items
        if b_items:
            s["backlog_subjects"] = "; ".join([it["display"] for it in b_items])
        elif actual_backlogs > 0:
            s["backlog_subjects"] = ""
        else:
            s["backlog_subjects"] = ""
            s["backlogs"] = 0

        s["academic_year"] = (s.get("semester", 1) + 1) // 2
        students.append(s)"""

# 2. In get_student_detail()
old_part2 = """    student["logged_interventions"] = interventions
    student["academic_records"] = academic_records
    return jsonify(student)"""

new_part2 = """    student["logged_interventions"] = interventions
    student["academic_records"] = academic_records

    # Structured backlog details with subject names, codes, semester, academic year
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
    elif (student.get("backlogs") or 0) > 0:
        student["backlog_subjects"] = ""
    else:
        student["backlog_subjects"] = ""
        student["backlogs"] = 0

    return jsonify(student)"""

# Normalize CRLF/LF
content_norm = content.replace('\r\n', '\n')
old_part1_norm = old_part1.replace('\r\n', '\n')
new_part1_norm = new_part1.replace('\r\n', '\n')
old_part2_norm = old_part2.replace('\r\n', '\n')
new_part2_norm = new_part2.replace('\r\n', '\n')

assert old_part1_norm in content_norm, "old_part1 not found in app.py"
content_norm = content_norm.replace(old_part1_norm, new_part1_norm, 1)

assert old_part2_norm in content_norm, "old_part2 not found in app.py"
content_norm = content_norm.replace(old_part2_norm, new_part2_norm, 1)

# Write back preserving CRLF if original had it
if '\r\n' in content:
    content_final = content_norm.replace('\n', '\r\n')
else:
    content_final = content_norm

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content_final)

print("SUCCESS: app.py updated with backlog subject details!")
