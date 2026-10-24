import re

with open('templates/hod_dashboard.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add sidebar nav item
sidebar_target = '''        <a class="sidebar-nav-link" data-section="section-interventions">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line></svg>
          <span>Interventions</span>
        </a>'''

sidebar_replacement = sidebar_target + '''

        <div class="sidebar-nav-category">Institutional Reports</div>
        <a class="sidebar-nav-link" data-section="section-reports">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="7 10 12 15 17 10"></polyline><line x1="12" y1="15" x2="12" y2="3"></line></svg>
          <span>Export Reports</span>
        </a>'''

if sidebar_target in content:
    content = content.replace(sidebar_target, sidebar_replacement, 1)
    print("Added sidebar report nav link")
else:
    print("WARNING: sidebar_target not found")

# 2. Add Section 6: Reports & Export Center before {% endif %}
reports_section_html = '''
      <!-- SECTION 6: REPORTS & EXPORT CENTER -->
      <section id="section-reports" class="dashboard-section" style="display:none;">
        <div class="glass-card-container" style="background:#FFFFFF; border:1px solid #DCE4EE; border-radius:14px; padding:24px; margin-bottom:24px;">
          <div class="glass-card-header" style="margin-bottom:22px; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:12px;">
            <div>
              <h2 class="glass-card-title" style="font-size:1.25rem; font-weight:800; color:#172B4D; display:flex; align-items:center; gap:10px;">
                <i class="fa-solid fa-file-arrow-down" style="color:#2F80ED;"></i>
                Department Data Export &amp; Institutional Reporting
              </h2>
              <span class="glass-card-subtitle" style="font-size:0.8125rem; color:#5B6B82;">
                Download complete, authenticated student, faculty, and summary analytics for <strong>{{ dept_info.name if dept_info else dept_code }} ({{ dept_code }})</strong>.
              </span>
            </div>
            <div style="display:flex; align-items:center; gap:8px;">
              <span style="font-size:0.75rem; font-weight:700; color:#123B66; background:#EBF4FF; padding:6px 12px; border-radius:6px; border:1px solid #BFDBFE;">
                <i class="fa-solid fa-shield-halved" style="color:#2F80ED; margin-right:4px;"></i> Role Scoped: {{ dept_code }} HOD
              </span>
            </div>
          </div>

          <!-- Reports Grid -->
          <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(320px, 1fr)); gap:20px; margin-bottom:24px;">
            
            <!-- Report Card 1: Student Cohort -->
            <div style="background:#F8FBFF; border:1px solid #DCE4EE; border-radius:12px; padding:20px; display:flex; flex-direction:column; justify-content:space-between; transition:box-shadow 0.2s;" onmouseover="this.style.boxShadow='0 6px 16px rgba(18,59,102,0.08)'" onmouseout="this.style.boxShadow='none'">
              <div>
                <div style="display:flex; align-items:center; gap:12px; margin-bottom:12px;">
                  <div style="width:42px; height:42px; border-radius:10px; background:#EBF4FF; display:flex; align-items:center; justify-content:center; color:#2F80ED; font-size:1.15rem;">
                    <i class="fa-solid fa-user-graduate"></i>
                  </div>
                  <div>
                    <h3 style="font-size:1rem; font-weight:800; color:#172B4D; margin:0;">Student Cohort Roster</h3>
                    <span style="font-size:0.72rem; color:#5B6B82; font-weight:600; text-transform:uppercase;">Academic &amp; Risk Analytics</span>
                  </div>
                </div>
                <p style="font-size:0.8125rem; color:#5B6B82; line-height:1.5; margin-bottom:16px;">
                  Complete roster of {{ dept_code }} students with attendance rates, CGPA, semester exam marks, active backlogs, predictive success scores, risk levels, and intervention tracking status.
                </p>
                <div style="font-size:0.75rem; color:#172B4D; background:#FFFFFF; border:1px solid #DCE4EE; border-radius:6px; padding:8px 10px; margin-bottom:16px;">
                  <span style="font-weight:700;">Includes:</span> ID, Name, Section, Advisor, Attendance, CGPA, Marks %, Backlogs, Success Score, Risk Category.
                </div>
              </div>
              <div style="display:flex; gap:10px; flex-wrap:wrap; margin-top:auto;">
                <a href="/api/hod/export/students/csv" class="btn-export-csv" style="flex:1; text-align:center; background:#2F80ED; color:#FFFFFF; padding:10px 14px; border-radius:8px; text-decoration:none; font-weight:700; font-size:0.8125rem; display:inline-flex; align-items:center; justify-content:center; gap:6px; box-shadow:0 2px 6px rgba(47,128,237,0.25);">
                  <i class="fa-solid fa-file-csv"></i> Download CSV
                </a>
                <a href="/api/hod/export/students/xlsx" class="btn-export-xlsx" style="flex:1; text-align:center; background:#16A6A1; color:#FFFFFF; padding:10px 14px; border-radius:8px; text-decoration:none; font-weight:700; font-size:0.8125rem; display:inline-flex; align-items:center; justify-content:center; gap:6px; box-shadow:0 2px 6px rgba(22,166,161,0.25);">
                  <i class="fa-solid fa-file-excel"></i> Download Excel
                </a>
              </div>
            </div>

            <!-- Report Card 2: Faculty Directory -->
            <div style="background:#F8FBFF; border:1px solid #DCE4EE; border-radius:12px; padding:20px; display:flex; flex-direction:column; justify-content:space-between; transition:box-shadow 0.2s;" onmouseover="this.style.boxShadow='0 6px 16px rgba(18,59,102,0.08)'" onmouseout="this.style.boxShadow='none'">
              <div>
                <div style="display:flex; align-items:center; gap:12px; margin-bottom:12px;">
                  <div style="width:42px; height:42px; border-radius:10px; background:#EBF4FF; display:flex; align-items:center; justify-content:center; color:#123B66; font-size:1.15rem;">
                    <i class="fa-solid fa-chalkboard-user"></i>
                  </div>
                  <div>
                    <h3 style="font-size:1rem; font-weight:800; color:#172B4D; margin:0;">Faculty Directory &amp; Load</h3>
                    <span style="font-size:0.72rem; color:#5B6B82; font-weight:600; text-transform:uppercase;">Mentorship &amp; Teaching Load</span>
                  </div>
                </div>
                <p style="font-size:0.8125rem; color:#5B6B82; line-height:1.5; margin-bottom:16px;">
                  Directory of all {{ dept_code }} faculty members including designation, institutional email, phone, areas of specialization, active course assignments, and advisee counts.
                </p>
                <div style="font-size:0.75rem; color:#172B4D; background:#FFFFFF; border:1px solid #DCE4EE; border-radius:6px; padding:8px 10px; margin-bottom:16px;">
                  <span style="font-weight:700;">Includes:</span> Faculty ID, Name, Designation, Email, Phone, Specialization, Courses, Advisees, System Notice.
                </div>
              </div>
              <div style="display:flex; gap:10px; flex-wrap:wrap; margin-top:auto;">
                <a href="/api/hod/export/faculty/csv" class="btn-export-csv" style="flex:1; text-align:center; background:#2F80ED; color:#FFFFFF; padding:10px 14px; border-radius:8px; text-decoration:none; font-weight:700; font-size:0.8125rem; display:inline-flex; align-items:center; justify-content:center; gap:6px; box-shadow:0 2px 6px rgba(47,128,237,0.25);">
                  <i class="fa-solid fa-file-csv"></i> Download CSV
                </a>
                <a href="/api/hod/export/faculty/xlsx" class="btn-export-xlsx" style="flex:1; text-align:center; background:#16A6A1; color:#FFFFFF; padding:10px 14px; border-radius:8px; text-decoration:none; font-weight:700; font-size:0.8125rem; display:inline-flex; align-items:center; justify-content:center; gap:6px; box-shadow:0 2px 6px rgba(22,166,161,0.25);">
                  <i class="fa-solid fa-file-excel"></i> Download Excel
                </a>
              </div>
            </div>

            <!-- Report Card 3: Department Summary -->
            <div style="background:#F8FBFF; border:1px solid #DCE4EE; border-radius:12px; padding:20px; display:flex; flex-direction:column; justify-content:space-between; transition:box-shadow 0.2s;" onmouseover="this.style.boxShadow='0 6px 16px rgba(18,59,102,0.08)'" onmouseout="this.style.boxShadow='none'">
              <div>
                <div style="display:flex; align-items:center; gap:12px; margin-bottom:12px;">
                  <div style="width:42px; height:42px; border-radius:10px; background:#EBF4FF; display:flex; align-items:center; justify-content:center; color:#16A6A1; font-size:1.15rem;">
                    <i class="fa-solid fa-chart-pie"></i>
                  </div>
                  <div>
                    <h3 style="font-size:1rem; font-weight:800; color:#172B4D; margin:0;">Executive Summary KPIs</h3>
                    <span style="font-size:0.72rem; color:#5B6B82; font-weight:600; text-transform:uppercase;">Institutional Department Metrics</span>
                  </div>
                </div>
                <p style="font-size:0.8125rem; color:#5B6B82; line-height:1.5; margin-bottom:16px;">
                  High-level institutional briefing sheet with key departmental aggregates: risk cohort counts, mean attendance, average CGPA, backlog totals, and mentorship status.
                </p>
                <div style="font-size:0.75rem; color:#172B4D; background:#FFFFFF; border:1px solid #DCE4EE; border-radius:6px; padding:8px 10px; margin-bottom:16px;">
                  <span style="font-weight:700;">Includes:</span> Enrolled Total, High/Med/Low Risk Counts, Avg Attendance, Avg CGPA, Backlogs, Interventions.
                </div>
              </div>
              <div style="display:flex; gap:10px; flex-wrap:wrap; margin-top:auto;">
                <a href="/api/hod/export/summary/csv" class="btn-export-csv" style="flex:1; text-align:center; background:#2F80ED; color:#FFFFFF; padding:10px 14px; border-radius:8px; text-decoration:none; font-weight:700; font-size:0.8125rem; display:inline-flex; align-items:center; justify-content:center; gap:6px; box-shadow:0 2px 6px rgba(47,128,237,0.25);">
                  <i class="fa-solid fa-file-csv"></i> Download CSV
                </a>
                <a href="/api/hod/export/summary/xlsx" class="btn-export-xlsx" style="flex:1; text-align:center; background:#16A6A1; color:#FFFFFF; padding:10px 14px; border-radius:8px; text-decoration:none; font-weight:700; font-size:0.8125rem; display:inline-flex; align-items:center; justify-content:center; gap:6px; box-shadow:0 2px 6px rgba(22,166,161,0.25);">
                  <i class="fa-solid fa-file-excel"></i> Download Excel
                </a>
              </div>
            </div>

          </div>

          <!-- Governance & Security Note -->
          <div style="background:#F4F7FB; border:1px solid #DCE4EE; border-radius:10px; padding:16px 20px; display:flex; align-items:flex-start; gap:12px;">
            <i class="fa-solid fa-circle-info" style="color:#2F80ED; margin-top:3px; font-size:1rem;"></i>
            <div style="font-size:0.8rem; color:#5B6B82; line-height:1.5;">
              <strong style="color:#172B4D;">Security &amp; Data Governance Standards:</strong>
              All report outputs are generated dynamically in memory and strictly constrained to your authenticated department assignment (<strong>{{ dept_code }}</strong>). Passwords, password hashes, and session authentication tokens are excluded from all exports. Text fields are sanitized against spreadsheet formula injection vulnerabilities.
            </div>
          </div>
        </div>
      </section>
'''

section_target = '      </section>\n\n      {% endif %}'
if section_target in content:
    content = content.replace(section_target, '      </section>\n' + reports_section_html + '\n      {% endif %}', 1)
    print("Added Section 6: Reports & Export Center")
else:
    print("WARNING: section_target not found")

# 3. Update switchSection labelMap in <script>
labelmap_target = "'section-interventions': 'Interventions'"
labelmap_replacement = "'section-interventions': 'Interventions',\n        'section-reports': 'Department Reports'"
if labelmap_target in content:
    content = content.replace(labelmap_target, labelmap_replacement, 1)
    print("Updated labelMap in script")
else:
    print("WARNING: labelmap_target not found")

with open('templates/hod_dashboard.html', 'w', encoding='utf-8') as f:
    f.write(content)
print("SUCCESS: templates/hod_dashboard.html updated!")
