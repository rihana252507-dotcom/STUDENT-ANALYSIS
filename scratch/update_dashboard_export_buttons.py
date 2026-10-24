# Update admin_dashboard.html
with open('templates/admin_dashboard.html', 'r', encoding='utf-8') as f:
    admin_html = f.read()

# 1. Section 1 Overview buttons
target_adm_ov = '<button class="btn-action-secondary" onclick="exportCohortCSV()">Export CSV Report</button>'
repl_adm_ov = '<button class="btn-action-secondary" onclick="exportCohortCSV()">Export CSV</button>\n            <button class="btn-action-secondary" onclick="exportCohortExcel()" style="background:#16A6A1; color:#fff;">Export Excel</button>'
if target_adm_ov in admin_html:
    admin_html = admin_html.replace(target_adm_ov, repl_adm_ov, 1)
    print("Updated admin overview export buttons")

# 2. Section 3 Students header
target_adm_st = '<button class="btn-action-secondary" onclick="exportCohortCSV()">Export CSV</button>'
repl_adm_st = '<button class="btn-action-secondary" onclick="exportCohortCSV()">Export CSV</button>\n              <button class="btn-action-secondary" onclick="exportCohortExcel()" style="background:#16A6A1; color:#fff;">Export Excel</button>'
if target_adm_st in admin_html:
    admin_html = admin_html.replace(target_adm_st, repl_adm_st, 1)
    print("Updated admin student directory export buttons")

# 3. Section 11 Accreditation & Audit Report Export cards
target_adm_sec11 = '''            <div style="background:rgba(35,18,70,0.6); border:1px solid var(--border-glass); border-radius:14px; padding:20px;">
              <h4 style="color:#FFFFFF; font-size:1.1rem; margin-bottom:8px;">Full University Cohort Export</h4>
              <p style="font-size:0.8125rem; color:#D4E9FF; margin-bottom:16px;">Complete export of all 10 student records including CGPA, attendance, LMS hours, aptitude, and success scores.</p>
              <button class="btn-action-primary" onclick="exportCohortCSV()">Download Full CSV</button>
            </div>

            <div style="background:rgba(35,18,70,0.6); border:1px solid var(--border-glass); border-radius:14px; padding:20px;">
              <h4 style="color:#FFFFFF; font-size:1.1rem; margin-bottom:8px;">High-Risk Debarment Watchlist</h4>
              <p style="font-size:0.8125rem; color:#D4E9FF; margin-bottom:16px;">Filtered CSV of the 4 students identified in the High Risk category requiring dean-level intervention.</p>
              <button class="btn-action-secondary" onclick="exportRiskCSV('High')">Download High Risk CSV</button>
            </div>'''

repl_adm_sec11 = '''            <div style="background:rgba(18,59,102,0.6); border:1px solid #DCE4EE; border-radius:14px; padding:20px;">
              <h4 style="color:#FFFFFF; font-size:1.1rem; margin-bottom:8px;">Full University Cohort Export</h4>
              <p style="font-size:0.8125rem; color:#D4E9FF; margin-bottom:16px;">Complete export of student records including CGPA, attendance, LMS hours, aptitude, and success scores.</p>
              <div style="display:flex; gap:10px; flex-wrap:wrap;">
                <button class="btn-action-primary" onclick="exportCohortCSV()"><i class="fa-solid fa-file-csv"></i> Download Full CSV</button>
                <button class="btn-action-secondary" onclick="exportCohortExcel()" style="background:#16A6A1; color:#fff;"><i class="fa-solid fa-file-excel"></i> Download Excel (.xlsx)</button>
              </div>
            </div>

            <div style="background:rgba(18,59,102,0.6); border:1px solid #DCE4EE; border-radius:14px; padding:20px;">
              <h4 style="color:#FFFFFF; font-size:1.1rem; margin-bottom:8px;">High-Risk Debarment Watchlist</h4>
              <p style="font-size:0.8125rem; color:#D4E9FF; margin-bottom:16px;">Filtered records of students identified in the High Risk category requiring administrative intervention.</p>
              <div style="display:flex; gap:10px; flex-wrap:wrap;">
                <button class="btn-action-secondary" onclick="exportRiskCSV('High')"><i class="fa-solid fa-file-csv"></i> Download High Risk CSV</button>
                <button class="btn-action-primary" onclick="exportRiskExcel('High')" style="background:#16A6A1; color:#fff;"><i class="fa-solid fa-file-excel"></i> Download High Risk Excel</button>
              </div>
            </div>

            <div style="background:rgba(18,59,102,0.6); border:1px solid #DCE4EE; border-radius:14px; padding:20px;">
              <h4 style="color:#FFFFFF; font-size:1.1rem; margin-bottom:8px;">Interventions &amp; Advising Report</h4>
              <p style="font-size:0.8125rem; color:#D4E9FF; margin-bottom:16px;">Complete institution-wide log of student mentorship actions, counseling tasks, and follow-up resolutions.</p>
              <div style="display:flex; gap:10px; flex-wrap:wrap;">
                <a href="/api/interventions/export/csv" class="btn-action-primary" style="text-decoration:none; display:inline-flex; align-items:center; gap:6px;"><i class="fa-solid fa-file-csv"></i> Download Interventions CSV</a>
                <a href="/api/interventions/export/xlsx" class="btn-action-secondary" style="background:#16A6A1; color:#fff; text-decoration:none; display:inline-flex; align-items:center; gap:6px;"><i class="fa-solid fa-file-excel"></i> Download Interventions Excel</a>
              </div>
            </div>'''

if target_adm_sec11 in admin_html:
    admin_html = admin_html.replace(target_adm_sec11, repl_adm_sec11, 1)
    print("Updated admin Section 11 report cards")

with open('templates/admin_dashboard.html', 'w', encoding='utf-8') as f:
    f.write(admin_html)

# Update faculty_dashboard.html
with open('templates/faculty_dashboard.html', 'r', encoding='utf-8') as f:
    fac_html = f.read()

target_fac_ov = '<button class="btn-action-secondary" onclick="exportCohortCSV()">Export Caseload CSV</button>'
repl_fac_ov = '<button class="btn-action-secondary" onclick="exportCohortCSV()">Export Caseload CSV</button>\n            <button class="btn-action-secondary" onclick="exportCohortExcel()" style="background:#16A6A1; color:#fff;">Export Caseload Excel</button>'
if target_fac_ov in fac_html:
    fac_html = fac_html.replace(target_fac_ov, repl_fac_ov, 1)
    print("Updated faculty overview export buttons")

target_fac_tbl = '<button class="btn-action-primary" onclick="exportCohortCSV()">Export Caseload</button>'
repl_fac_tbl = '<button class="btn-action-primary" onclick="exportCohortCSV()">Export Caseload CSV</button>\n            <button class="btn-action-secondary" onclick="exportCohortExcel()" style="background:#16A6A1; color:#fff;">Export Excel</button>'
if target_fac_tbl in fac_html:
    fac_html = fac_html.replace(target_fac_tbl, repl_fac_tbl, 1)
    print("Updated faculty table export buttons")

target_fac_rep = '<button class="btn-action-primary" onclick="exportCohortCSV()">Export Advisees CSV Report</button>'
repl_fac_rep = '''<div style="display:flex; gap:10px; flex-wrap:wrap;">
            <button class="btn-action-primary" onclick="exportCohortCSV()"><i class="fa-solid fa-file-csv"></i> Export Advisees CSV</button>
            <button class="btn-action-secondary" onclick="exportCohortExcel()" style="background:#16A6A1; color:#fff;"><i class="fa-solid fa-file-excel"></i> Export Advisees Excel (.xlsx)</button>
            <a href="/api/interventions/export/csv" class="btn-action-secondary" style="text-decoration:none; display:inline-flex; align-items:center; gap:6px;"><i class="fa-solid fa-file-csv"></i> Export Interventions CSV</a>
            <a href="/api/interventions/export/xlsx" class="btn-action-secondary" style="background:#123B66; color:#fff; text-decoration:none; display:inline-flex; align-items:center; gap:6px;"><i class="fa-solid fa-file-excel"></i> Export Interventions Excel</a>
          </div>'''
if target_fac_rep in fac_html:
    fac_html = fac_html.replace(target_fac_rep, repl_fac_rep, 1)
    print("Updated faculty report section")

with open('templates/faculty_dashboard.html', 'w', encoding='utf-8') as f:
    f.write(fac_html)

# Update student_dashboard.html
with open('templates/student_dashboard.html', 'r', encoding='utf-8') as f:
    stu_html = f.read()

target_stu_print = '''          <button class="btn-action-primary" onclick="window.print()" style="display:inline-flex; align-items:center; gap:8px;">
            <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2"><polyline points="6 9 6 2 18 2 18 9"></polyline><path d="M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2"></path><rect x="6" y="14" width="12" height="8"></rect></svg>
            Print Academic Transcript
          </button>'''

repl_stu_print = '''          <div style="display:flex; gap:8px; align-items:center; flex-wrap:wrap;">
            <a href="/api/student/transcript/export/csv" class="btn-action-secondary" style="display:inline-flex; align-items:center; gap:6px; text-decoration:none; font-size:0.8125rem;">
              <i class="fa-solid fa-file-csv"></i> Download CSV
            </a>
            <a href="/api/student/transcript/export/xlsx" class="btn-action-secondary" style="background:#16A6A1; color:#fff; display:inline-flex; align-items:center; gap:6px; text-decoration:none; font-size:0.8125rem;">
              <i class="fa-solid fa-file-excel"></i> Download Excel
            </a>
            <button class="btn-action-primary" onclick="window.print()" style="display:inline-flex; align-items:center; gap:8px;">
              <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2"><polyline points="6 9 6 2 18 2 18 9"></polyline><path d="M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2"></path><rect x="6" y="14" width="12" height="8"></rect></svg>
              Print Transcript
            </button>
          </div>'''

if target_stu_print in stu_html:
    stu_html = stu_html.replace(target_stu_print, repl_stu_print, 1)
    print("Updated student transcript export buttons")

with open('templates/student_dashboard.html', 'w', encoding='utf-8') as f:
    f.write(stu_html)

print("SUCCESS: All dashboard templates updated with unified CSV & Excel download options!")
