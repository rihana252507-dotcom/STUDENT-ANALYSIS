with open('templates/hod_dashboard.html', 'r', encoding='utf-8') as f:
    content = f.read()

target = '''            <div style="display:flex; gap:10px;">
              <span class="badge badge-low" style="font-size:0.78rem; padding:6px 14px;">Backend Verified Cohort</span>
            </div>'''

replacement = '''            <div style="display:flex; gap:10px; align-items:center; flex-wrap:wrap;">
              <span class="badge badge-low" style="font-size:0.78rem; padding:7px 14px;">Backend Verified Cohort</span>
              <button onclick="switchSection('section-reports')" style="background:#2F80ED; color:#FFFFFF; border:none; padding:7px 16px; border-radius:8px; font-size:0.8rem; font-weight:700; cursor:pointer; display:inline-flex; align-items:center; gap:6px; box-shadow:0 2px 8px rgba(47,128,237,0.35); transition:background 0.2s;" onmouseover="this.style.background='#1b68cc'" onmouseout="this.style.background='#2F80ED'">
                <i class="fa-solid fa-file-arrow-down"></i> Export Reports
              </button>
            </div>'''

if target in content:
    content = content.replace(target, replacement, 1)
    with open('templates/hod_dashboard.html', 'w', encoding='utf-8') as f:
        f.write(content)
    print("Added Export Reports button to Hero Banner")
else:
    print("WARNING: target not found")
