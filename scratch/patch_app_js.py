import os

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
js_path = os.path.join(base_dir, "static", "js", "app.js")

with open(js_path, "r", encoding="utf-8") as f:
    js_content = f.read()

norm_js = js_content.replace("\r\n", "\n")

# 1. Update renderRiskAlertsTable with High -> Medium -> Low sorting and backlog subjects in driver text
old_risk_table = """function renderRiskAlertsTable(students) {
  const tbody = document.getElementById("riskAlertsTableBody");
  if (!tbody) return;

  // Show all advisees meeting any academic risk conditions
  const atRisk = (students || []).filter(s => {
    const risk = (s.risk_level || "").toLowerCase();
    const backlogs = parseInt(s.backlogs) || 0;
    const att = parseFloat(s.attendance_pct) || 0;
    const score = parseFloat(s.success_score) || 0;
    const marks = parseFloat(s.academic_marks_pct) || 0;
    const cgpa = parseFloat(s.cgpa) || 0;
    return risk === "high" || risk === "medium" || backlogs > 0 || (att > 0 && att < 75) || (score > 0 && score < 70) || (marks > 0 && marks < 50) || (cgpa > 0 && cgpa < 6.0);
  });

  if (atRisk.length === 0) {
    tbody.innerHTML = `<tr><td colspan="5" style="text-align:center; padding:24px; color:#C4B5FD;">No at-risk advisees identified for your caseload.</td></tr>`;
    return;
  }

  tbody.innerHTML = atRisk.map(s => {
    const riskLower = (s.risk_level || "").toLowerCase();
    const riskClass = riskLower === "high" ? "badge-high" : "badge-medium";
    const riskDisplay = s.risk_level ? `${s.risk_level} Risk` : "At Risk";

    let drivers = [];
    const backlogs = parseInt(s.backlogs) || 0;
    const att = parseFloat(s.attendance_pct) || 0;
    const cgpa = parseFloat(s.cgpa) || 0;
    const marks = parseFloat(s.academic_marks_pct) || 0;

    if (att > 0 && att < 75 && backlogs > 0) {
      drivers.push(`Attendance (${att}%) & ${backlogs} Backlog${backlogs > 1 ? 's' : ''}`);
    } else {
      if (backlogs > 0) drivers.push(`${backlogs} Active Backlog${backlogs > 1 ? 's' : ''}`);
      if (att > 0 && att < 75) drivers.push(`Attendance Shortage (${att}%)`);
    }"""

new_risk_table = """function renderRiskAlertsTable(students) {
  const tbody = document.getElementById("riskAlertsTableBody");
  if (!tbody) return;

  // Show all advisees meeting any academic risk conditions
  const atRisk = (students || []).filter(s => {
    const risk = (s.risk_level || "").toLowerCase();
    const backlogs = parseInt(s.backlogs) || 0;
    const att = parseFloat(s.attendance_pct) || 0;
    const score = parseFloat(s.success_score) || 0;
    const marks = parseFloat(s.academic_marks_pct) || 0;
    const cgpa = parseFloat(s.cgpa) || 0;
    return risk === "high" || risk === "medium" || backlogs > 0 || (att > 0 && att < 75) || (score > 0 && score < 70) || (marks > 0 && marks < 50) || (cgpa > 0 && cgpa < 6.0);
  });

  // Sort High -> Medium -> Low risk order; within same tier, lowest success score first
  const riskPriority = { 'high': 0, 'medium': 1, 'low': 2 };
  atRisk.sort((a, b) => {
    const ra = riskPriority[(a.risk_level || '').toLowerCase()] ?? 2;
    const rb = riskPriority[(b.risk_level || '').toLowerCase()] ?? 2;
    if (ra !== rb) return ra - rb;
    return (parseFloat(a.success_score) || 0) - (parseFloat(b.success_score) || 0);
  });

  if (atRisk.length === 0) {
    tbody.innerHTML = `<tr><td colspan="5" style="text-align:center; padding:24px; color:#5B6B82;">No at-risk advisees identified for your caseload.</td></tr>`;
    return;
  }

  tbody.innerHTML = atRisk.map(s => {
    const riskLower = (s.risk_level || "").toLowerCase();
    const riskClass = riskLower === "high" ? "badge-high" : "badge-medium";
    const riskDisplay = s.risk_level ? `${s.risk_level} Risk` : "At Risk";

    let drivers = [];
    const backlogs = parseInt(s.backlogs) || 0;
    const att = parseFloat(s.attendance_pct) || 0;
    const cgpa = parseFloat(s.cgpa) || 0;
    const marks = parseFloat(s.academic_marks_pct) || 0;

    const bSubj = s.backlog_details && s.backlog_details.length > 0
      ? s.backlog_details.map(b => b.display).join(", ")
      : (s.backlog_subjects || "");

    if (att > 0 && att < 75 && backlogs > 0) {
      const subjNote = bSubj ? ` (${bSubj})` : '';
      drivers.push(`Attendance (${att}%) & ${backlogs} Backlog${backlogs > 1 ? 's' : ''}${subjNote}`);
    } else {
      if (backlogs > 0) {
        const subjNote = bSubj ? `: ${bSubj}` : '';
        drivers.push(`${backlogs} Active Backlog${backlogs > 1 ? 's' : ''}${subjNote}`);
      }
      if (att > 0 && att < 75) drivers.push(`Attendance Shortage (${att}%)`);
    }"""

assert old_risk_table in norm_js, "old_risk_table target not found"
norm_js = norm_js.replace(old_risk_table, new_risk_table, 1)

# 2. Update modal inspectStudent with backlog subjects and breakdown
old_modal_backlogs = """    setTxt("modalAttendance", `${s.attendance_pct}%`);
    setTxt("modalBacklogs", s.backlogs);
    setTxt("modalLmsHours", `${s.lms_weekly_hours} hrs/wk`);"""

new_modal_backlogs = """    setTxt("modalAttendance", `${s.attendance_pct}%`);
    setTxt("modalBacklogs", s.backlogs);
    setTxt("modalLmsHours", `${s.lms_weekly_hours} hrs/wk`);

    // Render Backlog Subjects Breakdown Section if present
    const backlogSec = document.getElementById("modalBacklogsBreakdownSection");
    const backlogCont = document.getElementById("modalBacklogSubjectsContainer");
    const backlogBadge = document.getElementById("modalBacklogCountBadge");
    const bCount = parseInt(s.backlogs) || 0;

    if (backlogSec && backlogCont) {
      if (s.backlog_details && s.backlog_details.length > 0) {
        backlogSec.style.display = "block";
        if (backlogBadge) backlogBadge.textContent = `${s.backlog_details.length} Active Pending`;
        backlogCont.innerHTML = `
          <table style="width:100%; border-collapse:collapse; font-size:0.82rem; text-align:left;">
            <thead>
              <tr style="border-bottom:1px solid #DCE4EE; color:#5B6B82; font-size:0.75rem; text-transform:uppercase;">
                <th style="padding:6px 8px;">Subject / Course Name</th>
                <th style="padding:6px 8px;">Course Code</th>
                <th style="padding:6px 8px;">Semester</th>
                <th style="padding:6px 8px; text-align:right;">Status</th>
              </tr>
            </thead>
            <tbody>
              ${s.backlog_details.map(b => `
                <tr style="border-bottom:1px solid #F1F5F9; color:#172B4D;">
                  <td style="padding:6px 8px; font-weight:600;">${escapeHtml(b.course_name)}</td>
                  <td style="padding:6px 8px;"><code style="background:#F4F7FB; padding:2px 6px; border-radius:4px; font-size:0.75rem; color:#123B66; border:1px solid #DCE4EE;">${escapeHtml(b.course_code || '--')}</code></td>
                  <td style="padding:6px 8px; color:#5B6B82;">Sem ${b.semester || '--'}${b.academic_year ? ` &bull; ${escapeHtml(b.academic_year)}` : ''}</td>
                  <td style="padding:6px 8px; text-align:right;"><span class="badge badge-high" style="font-size:0.7rem; padding:2px 6px;">Backlog (${escapeHtml(b.grade || 'F')})</span></td>
                </tr>
              `).join('')}
            </tbody>
          </table>
        `;
      } else if (bCount > 0 && s.backlog_subjects) {
        backlogSec.style.display = "block";
        if (backlogBadge) backlogBadge.textContent = `${bCount} Active Pending`;
        backlogCont.innerHTML = `
          <div style="color:#DC2626; font-weight:600; font-size:0.85rem; padding:6px 4px;">
            ${escapeHtml(s.backlog_subjects)}
          </div>
        `;
      } else {
        backlogSec.style.display = "none";
        backlogCont.innerHTML = "";
      }
    }"""

assert old_modal_backlogs in norm_js, "old_modal_backlogs target not found"
norm_js = norm_js.replace(old_modal_backlogs, new_modal_backlogs, 1)

# 3. Update studentsTableBody in student directory to display backlog subject names
old_student_table_backlog = """    const backlogHtml = s.backlogs > 0
      ? `<span class="badge badge-high" style="padding:2px 6px;">${s.backlogs} Backlog${s.backlogs > 1 ? 's' : ''}</span>`
      : `<span class="badge badge-low" style="padding:2px 6px;">None</span>`;"""

new_student_table_backlog = """    const studentBacklogSubjs = s.backlog_details && s.backlog_details.length > 0
      ? s.backlog_details.map(b => b.display).join(", ")
      : (s.backlog_subjects || "");
    const backlogHtml = s.backlogs > 0
      ? `<span class="badge badge-high" style="padding:2px 6px;">${s.backlogs} Backlog${s.backlogs > 1 ? 's' : ''}</span>` +
        (studentBacklogSubjs ? `<div style="font-size:0.72rem; color:#DC2626; font-weight:600; margin-top:3px; max-width:200px; word-break:break-word;">${escapeHtml(studentBacklogSubjs)}</div>` : "")
      : `<span class="badge badge-low" style="padding:2px 6px;">None</span>`;"""

assert old_student_table_backlog in norm_js, "old_student_table_backlog target not found"
norm_js = norm_js.replace(old_student_table_backlog, new_student_table_backlog, 1)

# 4. Update renderAcademicPerf to use backlog_details display if available
old_acad_backlog = """    const backlogHtml = backlogsCount > 0
      ? `<span class="badge badge-high">${backlogsCount} Active</span>
         <div style="font-size:0.75rem; color:#DC2626; font-weight:600; margin-top:4px; max-width:240px; word-break:break-word;">
           ${s.backlog_subjects ? escapeHtml(s.backlog_subjects) : backlogsCount + ' active backlog(s)'}
         </div>`
      : `<span class="badge badge-low">None (0)</span>`;"""

new_acad_backlog = """    const acadBacklogSubjs = s.backlog_details && s.backlog_details.length > 0
      ? s.backlog_details.map(b => b.display).join("; ")
      : (s.backlog_subjects || (backlogsCount + ' active backlog(s)'));
    const backlogHtml = backlogsCount > 0
      ? `<span class="badge badge-high">${backlogsCount} Active</span>
         <div style="font-size:0.75rem; color:#DC2626; font-weight:600; margin-top:4px; max-width:240px; word-break:break-word;">
           ${escapeHtml(acadBacklogSubjs)}
         </div>`
      : `<span class="badge badge-low">None (0)</span>`;"""

assert old_acad_backlog in norm_js, "old_acad_backlog target not found"
norm_js = norm_js.replace(old_acad_backlog, new_acad_backlog, 1)

with open(js_path, "w", encoding="utf-8") as f:
    f.write(norm_js.replace("\n", "\r\n"))

print("Patched static/js/app.js successfully!")
