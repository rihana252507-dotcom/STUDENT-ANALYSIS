"""
CampusIQ — Apply all targeted UI fixes from the summary:
1. Risk Monitoring refresh in app.js (switchSection hook)
2. SQLite label in admin_dashboard.html (subtitle + badge)
3. SQLite alert text in app.js
4. Placement Analysis card text contrast
5. Reports card backgrounds + text
6. Settings section readability
7. Faculty save button labels in faculty_dashboard.html
"""
import sys

BASE = r"c:\Users\samee\hackzelerate\STUDENT-ANALYSIS"

def replace_in_file(path, old, new, description):
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    if old not in content:
        print(f"  [WARN] Not found: {description}")
        return False
    count = content.count(old)
    content = content.replace(old, new)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  [OK] {description} (replaced {count} occurrence(s))")
    return True


# ── 1. app.js — Risk Monitoring: refresh list view when section is activated ──
app_js = BASE + r"\static\js\app.js"

old_switch_end = """  // Close mobile sidebar if open
  const sidebar = document.getElementById("appSidebar");
  if (sidebar && sidebar.classList.contains("mobile-open")) {
    sidebar.classList.remove("mobile-open");
  }
};"""

new_switch_end = """  // Close mobile sidebar if open
  const sidebar = document.getElementById("appSidebar");
  if (sidebar && sidebar.classList.contains("mobile-open")) {
    sidebar.classList.remove("mobile-open");
  }

  // Risk Monitoring: re-render list whenever this section is activated
  if (sectionId === "section-risk-monitoring") {
    const listView = document.getElementById("adminRiskListView");
    const detailView = document.getElementById("adminRiskDetailView");
    if (detailView) detailView.style.display = "none";
    if (listView) listView.style.display = "block";
    if (STATE && STATE.atRiskStudents && STATE.atRiskStudents.length >= 0) {
      if (typeof renderAdminRiskList === "function") {
        renderAdminRiskList(STATE.atRiskStudents);
      }
    }
  }
};"""

replace_in_file(app_js, old_switch_end, new_switch_end,
                "app.js — Risk Monitoring refresh hook in switchSection")

# ── 2. app.js — SQLite alert text ──
replace_in_file(app_js,
    'alert("Intervention assigned successfully and saved to SQLite!");',
    'alert("Intervention assigned successfully and saved!");',
    "app.js — SQLite alert text")

# ── 3. admin_dashboard.html — SQLite subtitle + badge ──
admin_html = BASE + r"\templates\admin_dashboard.html"

replace_in_file(admin_html,
    "Active remediation protocols, counseling notes, and progress outcomes recorded in SQLite.",
    "Active remediation protocols, counseling notes, and progress outcomes recorded in the system.",
    "admin_dashboard.html — SQLite subtitle")

replace_in_file(admin_html,
    '<span class="badge badge-low">Live SQLite Feed</span>',
    '<span class="badge badge-low">Live Activity Feed</span>',
    "admin_dashboard.html — Live SQLite Feed badge")

# ── 4. admin_dashboard.html — Placement Analysis card sub-labels contrast ──
# Three spans with color:#D4E9FF inside white glass-kpi-card
for old_span, new_span, desc in [
    (
        '<span style="font-size:0.75rem; color:#D4E9FF;">6 Students meeting Tier-1 criteria</span>',
        '<span style="font-size:0.75rem; color:#5B6B82;">6 Students meeting Tier-1 criteria</span>',
        "Placement KPI 1 sub-label color"
    ),
    (
        '<span style="font-size:0.75rem; color:#D4E9FF;">Quantitative, Logical &amp; Verbal</span>',
        '<span style="font-size:0.75rem; color:#5B6B82;">Quantitative, Logical &amp; Verbal</span>',
        "Placement KPI 2 sub-label color"
    ),
    (
        '<span style="font-size:0.75rem; color:#D4E9FF;">Algorithms, Coding &amp; Architecture</span>',
        '<span style="font-size:0.75rem; color:#5B6B82;">Algorithms, Coding &amp; Architecture</span>',
        "Placement KPI 3 sub-label color"
    ),
]:
    replace_in_file(admin_html, old_span, new_span, f"admin_dashboard.html — {desc}")

# ── 5. admin_dashboard.html — Reports cards: dark bg → light ──
for old_card, new_card, desc in [
    (
        '<div style="background:rgba(18,59,102,0.6); border:1px solid #DCE4EE; border-radius:14px; padding:20px;">\n              <h4 style="color:#FFFFFF; font-size:1.1rem; margin-bottom:8px;">Full University Cohort Export</h4>\n              <p style="font-size:0.8125rem; color:#D4E9FF; margin-bottom:16px;">Complete export of student records including CGPA, attendance, LMS hours, aptitude, and success scores.</p>',
        '<div style="background:#FFFFFF; border:1px solid #DCE4EE; border-radius:14px; padding:20px;">\n              <h4 style="color:#172B4D; font-size:1.1rem; margin-bottom:8px;">Full University Cohort Export</h4>\n              <p style="font-size:0.8125rem; color:#5B6B82; margin-bottom:16px;">Complete export of student records including CGPA, attendance, LMS hours, aptitude, and success scores.</p>',
        "Reports card 1 (Cohort Export)"
    ),
    (
        '<div style="background:rgba(18,59,102,0.6); border:1px solid #DCE4EE; border-radius:14px; padding:20px;">\n              <h4 style="color:#FFFFFF; font-size:1.1rem; margin-bottom:8px;">High-Risk Debarment Watchlist</h4>\n              <p style="font-size:0.8125rem; color:#D4E9FF; margin-bottom:16px;">Filtered records of students identified in the High Risk category requiring administrative intervention.</p>',
        '<div style="background:#FFFFFF; border:1px solid #DCE4EE; border-radius:14px; padding:20px;">\n              <h4 style="color:#172B4D; font-size:1.1rem; margin-bottom:8px;">High-Risk Debarment Watchlist</h4>\n              <p style="font-size:0.8125rem; color:#5B6B82; margin-bottom:16px;">Filtered records of students identified in the High Risk category requiring administrative intervention.</p>',
        "Reports card 2 (High-Risk Watchlist)"
    ),
    (
        '<div style="background:rgba(18,59,102,0.6); border:1px solid #DCE4EE; border-radius:14px; padding:20px;">\n              <h4 style="color:#FFFFFF; font-size:1.1rem; margin-bottom:8px;">Interventions &amp; Advising Report</h4>\n              <p style="font-size:0.8125rem; color:#D4E9FF; margin-bottom:16px;">Complete institution-wide log of student mentorship actions, counseling tasks, and follow-up resolutions.</p>',
        '<div style="background:#FFFFFF; border:1px solid #DCE4EE; border-radius:14px; padding:20px;">\n              <h4 style="color:#172B4D; font-size:1.1rem; margin-bottom:8px;">Interventions &amp; Advising Report</h4>\n              <p style="font-size:0.8125rem; color:#5B6B82; margin-bottom:16px;">Complete institution-wide log of student mentorship actions, counseling tasks, and follow-up resolutions.</p>',
        "Reports card 3 (Interventions)"
    ),
]:
    replace_in_file(admin_html, old_card, new_card, f"admin_dashboard.html — {desc}")

# ── 6. admin_dashboard.html — Settings section: dark cards → light ──
settings_replacements = [
    (
        '<div style="background:rgba(30,15,60,0.6); padding:16px; border-radius:10px; border:1px solid var(--border-glass);">\n              <span style="font-size:0.75rem; color:#C4B5FD; font-weight:700;">1. ACADEMIC MASTERY</span>\n              <div style="font-size:1.6rem; font-weight:800; color:#2F80ED;">30%</div>\n              <span style="font-size:0.72rem; color:#D4E9FF;">CGPA &amp; internal marks (minus backlogs)</span>\n            </div>',
        '<div style="background:#F4F7FB; padding:16px; border-radius:10px; border:1px solid #DCE4EE;">\n              <span style="font-size:0.75rem; color:#5B6B82; font-weight:700;">1. ACADEMIC MASTERY</span>\n              <div style="font-size:1.6rem; font-weight:800; color:#2F80ED;">30%</div>\n              <span style="font-size:0.72rem; color:#5B6B82;">CGPA &amp; internal marks (minus backlogs)</span>\n            </div>',
        "Settings card 1 (Academic Mastery)"
    ),
    (
        '<div style="background:rgba(30,15,60,0.6); padding:16px; border-radius:10px; border:1px solid var(--border-glass);">\n              <span style="font-size:0.75rem; color:#C4B5FD; font-weight:700;">2. ATTENDANCE COMPLIANCE</span>\n              <div style="font-size:1.6rem; font-weight:800; color:#16A6A1;">20%</div>\n              <span style="font-size:0.72rem; color:#D4E9FF;">UGC &ge; 75% regulatory mandate</span>\n            </div>',
        '<div style="background:#F4F7FB; padding:16px; border-radius:10px; border:1px solid #DCE4EE;">\n              <span style="font-size:0.75rem; color:#5B6B82; font-weight:700;">2. ATTENDANCE COMPLIANCE</span>\n              <div style="font-size:1.6rem; font-weight:800; color:#16A6A1;">20%</div>\n              <span style="font-size:0.72rem; color:#5B6B82;">UGC &ge; 75% regulatory mandate</span>\n            </div>',
        "Settings card 2 (Attendance Compliance)"
    ),
    (
        '<div style="background:rgba(30,15,60,0.6); padding:16px; border-radius:10px; border:1px solid var(--border-glass);">\n              <span style="font-size:0.75rem; color:#C4B5FD; font-weight:700;">3. DIGITAL LMS ENGAGEMENT</span>\n              <div style="font-size:1.6rem; font-weight:800; color:#A855F7;">15%</div>\n              <span style="font-size:0.72rem; color:#D4E9FF;">Weekly LMS study hours &amp; assignments</span>\n            </div>',
        '<div style="background:#F4F7FB; padding:16px; border-radius:10px; border:1px solid #DCE4EE;">\n              <span style="font-size:0.75rem; color:#5B6B82; font-weight:700;">3. DIGITAL LMS ENGAGEMENT</span>\n              <div style="font-size:1.6rem; font-weight:800; color:#A855F7;">15%</div>\n              <span style="font-size:0.72rem; color:#5B6B82;">Weekly LMS study hours &amp; assignments</span>\n            </div>',
        "Settings card 3 (Digital LMS Engagement)"
    ),
    (
        '<div style="background:rgba(30,15,60,0.6); padding:16px; border-radius:10px; border:1px solid var(--border-glass);">\n              <span style="font-size:0.75rem; color:#C4B5FD; font-weight:700;">4. PLACEMENT READINESS</span>\n              <div style="font-size:1.6rem; font-weight:800; color:#06B6D4;">20%</div>\n              <span style="font-size:0.72rem; color:#D4E9FF;">Coding skills &amp; mock aptitude scores</span>\n            </div>',
        '<div style="background:#F4F7FB; padding:16px; border-radius:10px; border:1px solid #DCE4EE;">\n              <span style="font-size:0.75rem; color:#5B6B82; font-weight:700;">4. PLACEMENT READINESS</span>\n              <div style="font-size:1.6rem; font-weight:800; color:#06B6D4;">20%</div>\n              <span style="font-size:0.72rem; color:#5B6B82;">Coding skills &amp; mock aptitude scores</span>\n            </div>',
        "Settings card 4 (Placement Readiness)"
    ),
    (
        '<div style="background:rgba(30,15,60,0.6); padding:16px; border-radius:10px; border:1px solid var(--border-glass);">\n              <span style="font-size:0.75rem; color:#C4B5FD; font-weight:700;">5. HOLISTIC WELLBEING</span>\n              <div style="font-size:1.6rem; font-weight:800; color:#10B981;">15%</div>\n              <span style="font-size:0.72rem; color:#D4E9FF;">Extracurriculars &amp; wellness index</span>\n            </div>',
        '<div style="background:#F4F7FB; padding:16px; border-radius:10px; border:1px solid #DCE4EE;">\n              <span style="font-size:0.75rem; color:#5B6B82; font-weight:700;">5. HOLISTIC WELLBEING</span>\n              <div style="font-size:1.6rem; font-weight:800; color:#10B981;">15%</div>\n              <span style="font-size:0.72rem; color:#5B6B82;">Extracurriculars &amp; wellness index</span>\n            </div>',
        "Settings card 5 (Holistic Wellbeing)"
    ),
]
for old, new, desc in settings_replacements:
    replace_in_file(admin_html, old, new, f"admin_dashboard.html — {desc}")

# ── 7. faculty_dashboard.html — Save button labels ──
faculty_html = BASE + r"\templates\faculty_dashboard.html"

replace_in_file(faculty_html,
    '>Save to SQLite</button>',
    '>Save Intervention</button>',
    "faculty_dashboard.html — Save to SQLite → Save Intervention")

replace_in_file(faculty_html,
    '>Save Progress to SQLite</button>',
    '>Save Progress</button>',
    "faculty_dashboard.html — Save Progress to SQLite → Save Progress")

print("\nAll fixes applied.")
