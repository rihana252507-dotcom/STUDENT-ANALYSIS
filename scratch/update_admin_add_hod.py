# 1. Update app.py add_faculty
with open('app.py', 'r', encoding='utf-8') as f:
    app_code = f.read()

target_af = '''        # 3. Parameterized INSERT into users table for authentication
        cursor.execute("""
        INSERT INTO users (user_id, password_hash, role, name, email, department)
        VALUES (?, ?, 'faculty', ?, ?, ?)
        """, (faculty_id, hashed, name, email, dept))'''

repl_af = '''        # 3. Parameterized INSERT into users table for authentication (Faculty or HOD)
        user_role = (data.get("role") or "faculty").strip().lower()
        if user_role not in ("faculty", "hod"):
            user_role = "faculty"

        cursor.execute("""
        INSERT INTO users (user_id, password_hash, role, name, email, department)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (faculty_id, hashed, user_role, name, email, dept))

        if user_role == "hod":
            cursor.execute("UPDATE departments SET hod_name = ? WHERE code = ?", (name, dept))'''

if target_af in app_code:
    app_code = app_code.replace(target_af, repl_af, 1)
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(app_code)
    print("Updated add_faculty in app.py to support HOD role")

# 2. Update templates/admin_dashboard.html addFacultyModal
with open('templates/admin_dashboard.html', 'r', encoding='utf-8') as f:
    admin_html = f.read()

target_modal_af = '''          <div class="input-group-custom">
            <label>Designation</label>
            <input type="text" id="newFacDesig" placeholder="Associate Professor" required>
          </div>'''

repl_modal_af = '''          <div style="display:grid; grid-template-columns:1fr 1fr; gap:12px;">
            <div class="input-group-custom">
              <label>Designation</label>
              <input type="text" id="newFacDesig" placeholder="Associate Professor" required>
            </div>
            <div class="input-group-custom">
              <label>System Role</label>
              <select id="newFacRole" class="cyber-select" style="background:#FFFFFF; color:#172B4D; border:1px solid #DCE4EE; border-radius:8px; padding:10px;">
                <option value="faculty">Faculty Mentor</option>
                <option value="hod">Head of Department (HOD)</option>
              </select>
            </div>
          </div>'''

if target_modal_af in admin_html:
    admin_html = admin_html.replace(target_modal_af, repl_modal_af, 1)
    with open('templates/admin_dashboard.html', 'w', encoding='utf-8') as f:
        f.write(admin_html)
    print("Updated addFacultyModal in admin_dashboard.html")

# 3. Update static/js/app.js addFaculty payload
with open('static/js/app.js', 'r', encoding='utf-8') as f:
    js_code = f.read()

target_js_af = '''        department: document.getElementById("newFacDept").value,
        password: document.getElementById("newFacPassword")?.value.trim() || "Faculty@123",'''

repl_js_af = '''        department: document.getElementById("newFacDept").value,
        role: document.getElementById("newFacRole")?.value || "faculty",
        password: document.getElementById("newFacPassword")?.value.trim() || "Faculty@123",'''

if target_js_af in js_code:
    js_code = js_code.replace(target_js_af, repl_js_af, 1)
    with open('static/js/app.js', 'w', encoding='utf-8') as f:
        f.write(js_code)
    print("Updated addFacultyForm payload in app.js")
