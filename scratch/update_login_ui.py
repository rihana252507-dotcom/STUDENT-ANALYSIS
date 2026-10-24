# Update static/css/style.css
with open('static/css/style.css', 'r', encoding='utf-8') as f:
    css = f.read()

css = css.replace(
    '  grid-template-columns: repeat(3, 1fr);',
    '  grid-template-columns: repeat(4, 1fr);',
    1
)

css = css.replace(
    '.demo-pills-row {\n  display: grid;\n  grid-template-columns: repeat(3, 1fr);',
    '.demo-pills-row {\n  display: grid;\n  grid-template-columns: repeat(auto-fit, minmax(130px, 1fr));',
    1
)

with open('static/css/style.css', 'w', encoding='utf-8') as f:
    f.write(css)
print("Updated static/css/style.css for 4 role tabs and demo pills")

# Update templates/login.html
with open('templates/login.html', 'r', encoding='utf-8') as f:
    login_html = f.read()

old_tabs = '''      <!-- 3 Role Options -->
      <div class="login-role-tabs" role="tablist">
        <button type="button" class="login-role-tab active" data-role="admin" onclick="selectLoginRole('admin')">Admin Login</button>
        <button type="button" class="login-role-tab" data-role="faculty" onclick="selectLoginRole('faculty')">Faculty Login</button>
        <button type="button" class="login-role-tab" data-role="student" onclick="selectLoginRole('student')">Student Login</button>
      </div>'''

new_tabs = '''      <!-- 4 Role Options -->
      <div class="login-role-tabs" role="tablist">
        <button type="button" class="login-role-tab active" data-role="admin" onclick="selectLoginRole('admin')">Admin</button>
        <button type="button" class="login-role-tab" data-role="hod" onclick="selectLoginRole('hod')">HOD</button>
        <button type="button" class="login-role-tab" data-role="faculty" onclick="selectLoginRole('faculty')">Faculty</button>
        <button type="button" class="login-role-tab" data-role="student" onclick="selectLoginRole('student')">Student</button>
      </div>'''

if old_tabs in login_html:
    login_html = login_html.replace(old_tabs, new_tabs, 1)

old_placeholder = '''      if (role === 'admin') u.placeholder = 'e.g. admin001';
      else if (role === 'faculty') u.placeholder = 'e.g. faculty001 or faculty002';
      else if (role === 'student') u.placeholder = 'e.g. student001 or student002';'''

new_placeholder = '''      if (role === 'admin') u.placeholder = 'e.g. admin001';
      else if (role === 'hod') u.placeholder = 'e.g. hod_cse or hod_aiml';
      else if (role === 'faculty') u.placeholder = 'e.g. faculty001 or faculty002';
      else if (role === 'student') u.placeholder = 'e.g. student001 or student002';'''

if old_placeholder in login_html:
    login_html = login_html.replace(old_placeholder, new_placeholder, 1)

old_demo_pill = '''          <div class="demo-pill-btn" onclick="fillDemo('faculty001', 'Faculty@123', 'faculty')" title="Sign in as Faculty Mentor (Dr. Sunita Rao)">
            <strong>Faculty Login</strong>
            <code>faculty001 / Faculty@123</code>
          </div>'''

new_demo_pill = '''          <div class="demo-pill-btn" onclick="fillDemo('hod_cse', 'Hod@123', 'hod')" title="Sign in as HOD CSE (Dr. Sunita Rao)">
            <strong>HOD Login (CSE)</strong>
            <code>hod_cse / Hod@123</code>
          </div>

          <div class="demo-pill-btn" onclick="fillDemo('faculty001', 'Faculty@123', 'faculty')" title="Sign in as Faculty Mentor (Dr. Sunita Rao)">
            <strong>Faculty Login</strong>
            <code>faculty001 / Faculty@123</code>
          </div>'''

if old_demo_pill in login_html:
    login_html = login_html.replace(old_demo_pill, new_demo_pill, 1)

with open('templates/login.html', 'w', encoding='utf-8') as f:
    f.write(login_html)
print("Updated templates/login.html")
