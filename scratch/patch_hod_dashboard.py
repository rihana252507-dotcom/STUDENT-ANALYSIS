import os

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
app_path = os.path.join(base_dir, "app.py")
tpl_path = os.path.join(base_dir, "templates", "hod_dashboard.html")

# ==========================================
# 1. PATCH app.py
# ==========================================
with open(app_path, "r", encoding="utf-8") as f:
    app_text = f.read()

norm_app = app_text.replace("\r\n", "\n")

# A. Update log_intervention role check and HOD handling
old_log_intv = """@app.route("/api/students/<student_id>/intervention", methods=["POST"])
@login_required
@role_required("admin", "faculty")
def log_intervention(student_id):"""

new_log_intv = """@app.route("/api/students/<student_id>/intervention", methods=["POST"])
@login_required
@role_required("admin", "faculty", "hod")
def log_intervention(student_id):"""

assert old_log_intv in norm_app, "old_log_intv not found in app.py"
norm_app = norm_app.replace(old_log_intv, new_log_intv, 1)

old_log_intv_body = """    # 1. Verify student exists
    cursor.execute("SELECT * FROM students WHERE student_id = ? COLLATE NOCASE OR user_id = ? COLLATE NOCASE", (student_id, student_id))
    student = cursor.fetchone()
    if not student:
        conn.close()
        return jsonify({"error": "Not Found", "message": "Student not found"}), 404

    # 2. Determine and verify assigned faculty
    target_faculty_id = data.get("faculty_id") or data.get("assigned_faculty")
    faculty_row = None

    if target_faculty_id:
        cursor.execute("SELECT * FROM faculty WHERE faculty_id = ? COLLATE NOCASE OR user_id = ? COLLATE NOCASE", (target_faculty_id, target_faculty_id))
        faculty_row = cursor.fetchone()

    if not faculty_row and data.get("faculty_name"):
        cursor.execute("SELECT * FROM faculty WHERE name = ? COLLATE NOCASE", (data.get("faculty_name").strip(),))
        faculty_row = cursor.fetchone()

    # Fallback to student's assigned faculty mentor
    if not faculty_row and student["faculty_id"]:
        cursor.execute("SELECT * FROM faculty WHERE faculty_id = ? COLLATE NOCASE OR user_id = ? COLLATE NOCASE", (student["faculty_id"], student["faculty_id"]))
        faculty_row = cursor.fetchone()

    if faculty_row:
        faculty_id = faculty_row["user_id"]
        faculty_name = faculty_row["name"]
    else:
        if current_role == "faculty":
            faculty_id = current_user_id
            faculty_name = session.get("name", "Faculty Mentor")
        else:
            conn.close()
            return jsonify({"error": "Bad Request", "message": "A valid faculty member must be selected."}), 400

    # 3. Transactional insert of intervention and faculty notification
    try:
        cursor.execute("BEGIN TRANSACTION")
        cursor.execute(\"\"\"
        INSERT INTO interventions (
            student_id, faculty_id, faculty_name, action_type, title,
            priority, instructions, notes, due_date, status
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        \"\"\", (
            student["student_id"], faculty_id, faculty_name, action_type, title,
            priority, instructions, notes, due_date, "Assigned" if current_role == "admin" else "In Progress"
        ))"""

new_log_intv_body = """    # 1. Verify student exists
    cursor.execute("SELECT * FROM students WHERE student_id = ? COLLATE NOCASE OR user_id = ? COLLATE NOCASE", (student_id, student_id))
    student = cursor.fetchone()
    if not student:
        conn.close()
        return jsonify({"error": "Not Found", "message": "Student not found"}), 404

    # Enforce department restriction for HOD
    if current_role == "hod":
        dept = (session.get("department") or "").upper()
        if (student["department"] or "").upper() != dept:
            conn.close()
            return jsonify({"error": "Forbidden", "message": "Cannot log intervention for student from another department"}), 403

    # 2. Determine and verify assigned faculty
    target_faculty_id = data.get("faculty_id") or data.get("assigned_faculty")
    faculty_row = None

    if target_faculty_id:
        cursor.execute("SELECT * FROM faculty WHERE faculty_id = ? COLLATE NOCASE OR user_id = ? COLLATE NOCASE", (target_faculty_id, target_faculty_id))
        faculty_row = cursor.fetchone()

    if not faculty_row and data.get("faculty_name"):
        cursor.execute("SELECT * FROM faculty WHERE name = ? COLLATE NOCASE", (data.get("faculty_name").strip(),))
        faculty_row = cursor.fetchone()

    # Fallback to student's assigned faculty mentor
    if not faculty_row and student["faculty_id"]:
        cursor.execute("SELECT * FROM faculty WHERE faculty_id = ? COLLATE NOCASE OR user_id = ? COLLATE NOCASE", (student["faculty_id"], student["faculty_id"]))
        faculty_row = cursor.fetchone()

    if faculty_row:
        faculty_id = faculty_row["user_id"]
        faculty_name = faculty_row["name"]
    else:
        if current_role == "faculty":
            faculty_id = current_user_id
            faculty_name = session.get("name", "Faculty Mentor")
        elif current_role == "hod":
            faculty_id = current_user_id
            faculty_name = session.get("name", "Head of Department")
        else:
            conn.close()
            return jsonify({"error": "Bad Request", "message": "A valid faculty member must be selected."}), 400

    # 3. Transactional insert of intervention and faculty notification
    try:
        cursor.execute("BEGIN TRANSACTION")
        cursor.execute(\"\"\"
        INSERT INTO interventions (
            student_id, faculty_id, faculty_name, action_type, title,
            priority, instructions, notes, due_date, status
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        \"\"\", (
            student["student_id"], faculty_id, faculty_name, action_type, title,
            priority, instructions, notes, due_date, "Assigned" if current_role in ("admin", "hod") else "In Progress"
        ))"""

assert old_log_intv_body in norm_app, "old_log_intv_body not found in app.py"
norm_app = norm_app.replace(old_log_intv_body, new_log_intv_body, 1)

# B. Update update_intervention_status role check & HOD check
old_upd_intv = """@app.route("/api/interventions/<int:id>", methods=["PUT"])
@login_required
@role_required("admin", "faculty")
def update_intervention_status(id):
    \"\"\"Updates progress status, action taken, and implementation notes of an active intervention.\"\"\"
    data = request.get_json(silent=True) or {}
    new_status = data.get("status")
    action_taken = data.get("action_taken")
    implementation_notes = data.get("implementation_notes") or data.get("notes")

    current_role = session.get("role")
    current_user_id = session.get("user_id")

    conn = get_db()
    cursor = conn.cursor()

    # Check permission: Faculty can update only their own assigned interventions
    cursor.execute("SELECT * FROM interventions WHERE id = ?", (id,))
    intv = cursor.fetchone()
    if not intv:
        conn.close()
        return jsonify({"error": "Not Found", "message": "Intervention not found"}), 404

    if current_role == "faculty" and intv["faculty_id"] != current_user_id:
        conn.close()
        return jsonify({"error": "Forbidden", "message": "You can only update interventions assigned to you"}), 403"""

new_upd_intv = """@app.route("/api/interventions/<int:id>", methods=["PUT"])
@login_required
@role_required("admin", "faculty", "hod")
def update_intervention_status(id):
    \"\"\"Updates progress status, action taken, and implementation notes of an active intervention.\"\"\"
    data = request.get_json(silent=True) or {}
    new_status = data.get("status")
    action_taken = data.get("action_taken")
    implementation_notes = data.get("implementation_notes") or data.get("notes")

    current_role = session.get("role")
    current_user_id = session.get("user_id")

    conn = get_db()
    cursor = conn.cursor()

    # Check permission: Faculty can update only their own assigned interventions; HOD only own department
    cursor.execute("SELECT * FROM interventions WHERE id = ?", (id,))
    intv = cursor.fetchone()
    if not intv:
        conn.close()
        return jsonify({"error": "Not Found", "message": "Intervention not found"}), 404

    if current_role == "faculty" and intv["faculty_id"] != current_user_id:
        conn.close()
        return jsonify({"error": "Forbidden", "message": "You can only update interventions assigned to you"}), 403

    if current_role == "hod":
        cursor.execute("SELECT department FROM students WHERE student_id = ?", (intv["student_id"],))
        st_row = cursor.fetchone()
        dept = (session.get("department") or "").upper()
        if not st_row or (st_row["department"] or "").upper() != dept:
            conn.close()
            return jsonify({"error": "Forbidden", "message": "You can only update interventions for students in your department"}), 403"""

assert old_upd_intv in norm_app, "old_upd_intv not found in app.py"
norm_app = norm_app.replace(old_upd_intv, new_upd_intv, 1)

# C. Update hod_overview backlog details
old_hod_backlogs = """    # Query academic_records to attach backlog subjects
    cursor.execute(\"\"\"
        SELECT student_id, GROUP_CONCAT(course_name, ', ') AS backlog_subjects, COUNT(*) AS backlog_records_count
        FROM academic_records
        WHERE LOWER(status) NOT IN ('passed', 'pass', 'completed', 'clear')
        GROUP BY student_id
    \"\"\")
    backlogs_map = {r["student_id"]: {"subjects": r["backlog_subjects"], "count": r["backlog_records_count"]} for r in cursor.fetchall()}
    for s in students_list:
        sid = s.get("student_id")
        b_info = backlogs_map.get(sid, {})
        s["backlog_subjects"] = b_info.get("subjects") or ""
        if not s.get("backlogs") and b_info.get("count"):
            s["backlogs"] = b_info["count"]"""

new_hod_backlogs = """    # Query academic_records to attach backlog subjects and structured details
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

    for s in students_list:
        sid = s.get("student_id")
        b_items = backlogs_details_map.get(sid, [])
        s["backlog_details"] = b_items
        s["backlog_subjects"] = ", ".join(backlogs_subjects_map.get(sid, []))
        if b_items:
            s["backlogs"] = max(s.get("backlogs") or 0, len(b_items))"""

assert old_hod_backlogs in norm_app, "old_hod_backlogs not found in app.py"
norm_app = norm_app.replace(old_hod_backlogs, new_hod_backlogs, 1)

with open(app_path, "wb") as f:
    f.write(norm_app.replace("\n", "\r\n").encode("utf-8"))

print("Patched app.py successfully!")

# ==========================================
# 2. PATCH templates/hod_dashboard.html
# ==========================================
with open(tpl_path, "r", encoding="utf-8") as f:
    tpl_text = f.read()

norm_tpl = tpl_text.replace("\r\n", "\n")

# Find the truncated section around line 604
old_modal_tail = """            <!-- Strengths List -->
            <div style="margin-bottom:18px;">
              <h4 style="font-size:0.875rem; font-weight:700; color:#172B4D; margin-bottom:8px;">Student Strengths &amp; Competencies</h4>
              <div id="modalStrengthsContainer" style="display:flex; flex-di<script>"""

assert old_modal_tail in norm_tpl, "old_modal_tail not found in hod_dashboard.html"

# Extract everything up to old_modal_tail
prefix = norm_tpl.split(old_modal_tail)[0]

clean_modal_and_script = """            <!-- Active Backlog Subjects Breakdown -->
            <div id="modalBacklogsBreakdownSection" style="display:none; margin-bottom:18px;">
              <h4 style="font-size:0.875rem; font-weight:700; color:#DC2626; margin-bottom:8px; display:flex; align-items:center; gap:6px;">
                <i class="fas fa-triangle-exclamation"></i>
                <span>Active Backlog Subjects</span>
                <span id="modalBacklogCountBadge" class="badge badge-high" style="font-size:0.7rem; padding:2px 6px;"></span>
              </h4>
              <div id="modalBacklogSubjectsContainer" style="background:#FFFFFF; border:1px solid #DCE4EE; border-radius:8px; padding:10px; font-size:0.82rem;"></div>
            </div>

            <!-- Risk Factors List -->
            <div style="margin-bottom:18px;">
              <h4 style="font-size:0.875rem; font-weight:700; color:#172B4D; margin-bottom:8px;">Explainable Risk Factors</h4>
              <div id="modalRiskFactorsContainer" style="display:flex; flex-direction:column; gap:6px;"></div>
            </div>

            <!-- Strengths List -->
            <div style="margin-bottom:18px;">
              <h4 style="font-size:0.875rem; font-weight:700; color:#172B4D; margin-bottom:8px;">Student Strengths &amp; Competencies</h4>
              <div id="modalStrengthsContainer" style="display:flex; flex-direction:column; gap:6px;"></div>
            </div>

          </div>
        </div>
      </div>

    </main>
  </div>

  <script>
    // State management for HOD dashboard
    let HOD_DATA = {
      department: {},
      metrics: {},
      faculty: [],
      students: [],
      interventions: []
    };

    // Navigation section switching
    document.querySelectorAll('.sidebar-nav-link[data-section]').forEach(link => {
      link.addEventListener('click', (e) => {
        e.preventDefault();
        const sectionId = link.getAttribute('data-section');
        switchSection(sectionId);
      });
    });

    function switchSection(sectionId) {
      document.querySelectorAll('.dashboard-section').forEach(sec => {
        sec.classList.remove('active-section');
        sec.classList.remove('active');
        sec.style.display = 'none';
      });
      document.querySelectorAll('.sidebar-nav-link[data-section]').forEach(lnk => lnk.classList.remove('active'));

      const targetSec = document.getElementById(sectionId);
      if (targetSec) {
        targetSec.classList.add('active-section');
        targetSec.classList.add('active');
        targetSec.style.display = 'block';
      }

      const activeLink = document.querySelector(`.sidebar-nav-link[data-section="${sectionId}"]`);
      if (activeLink) activeLink.classList.add('active');

      const labelMap = {
        'section-overview': 'Department Overview',
        'section-faculty': 'Faculty Directory',
        'section-students': 'Student Cohort',
        'section-risk': 'Risk Monitoring',
        'section-interventions': 'Interventions',
        'section-reports': 'Department Reports'
      };
      const topbarLbl = document.getElementById('topbarCurrentSection');
      if (topbarLbl) topbarLbl.textContent = labelMap[sectionId] || 'Overview';
    }
    window.switchSection = switchSection;

    // Modal controls
    const modal = document.getElementById('studentDetailModal');
    const btnCloseModal = document.getElementById('btnCloseModal');
    if (btnCloseModal) {
      btnCloseModal.addEventListener('click', () => { if (modal) modal.style.display = 'none'; });
    }
    if (modal) {
      modal.addEventListener('click', (e) => { if (e.target === modal) modal.style.display = 'none'; });
    }

    async function inspectStudent(studentId) {
      try {
        const res = await fetch(`/api/students/${encodeURIComponent(studentId)}`);
        if (!res.ok) {
          alert('Unable to load student profile (unauthorized or missing record).');
          return;
        }
        const s = await res.json();
        
        const setElTxt = (id, val) => {
          const el = document.getElementById(id);
          if (el) el.textContent = val;
        };

        setElTxt('modalStudentAvatar', (s.name || '').substring(0, 2).toUpperCase());
        setElTxt('modalStudentName', s.name || s.student_id);
        setElTxt('modalStudentID', `${s.student_id} • ${s.department} • Sem ${s.semester || 'N/A'}`);
        setElTxt('modalAttendance', (s.attendance_pct || 0) + '%');
        setElTxt('modalCgpa', parseFloat(s.cgpa || 0).toFixed(2));
        setElTxt('modalBacklogs', s.backlogs || 0);
        setElTxt('modalSuccessScore', s.success_score || '--');

        // Backlog subjects breakdown
        const backlogSec = document.getElementById('modalBacklogsBreakdownSection');
        const backlogCont = document.getElementById('modalBacklogSubjectsContainer');
        const backlogBadge = document.getElementById('modalBacklogCountBadge');
        const bCount = parseInt(s.backlogs) || 0;

        if (backlogSec && backlogCont) {
          if (s.backlog_details && s.backlog_details.length > 0) {
            backlogSec.style.display = 'block';
            if (backlogBadge) backlogBadge.textContent = `${s.backlog_details.length} Pending`;
            backlogCont.innerHTML = `
              <table style="width:100%; border-collapse:collapse; font-size:0.82rem; text-align:left;">
                <thead>
                  <tr style="border-bottom:1px solid #DCE4EE; color:#5B6B82; font-size:0.72rem; text-transform:uppercase;">
                    <th style="padding:6px 8px;">Subject / Course</th>
                    <th style="padding:6px 8px;">Code</th>
                    <th style="padding:6px 8px;">Semester</th>
                    <th style="padding:6px 8px; text-align:right;">Grade</th>
                  </tr>
                </thead>
                <tbody>
                  ${s.backlog_details.map(b => `
                    <tr style="border-bottom:1px solid #F1F5F9; color:#172B4D;">
                      <td style="padding:6px 8px; font-weight:600;">${escapeHtml(b.course_name)}</td>
                      <td style="padding:6px 8px;"><code style="background:#F4F7FB; padding:2px 6px; border-radius:4px; font-size:0.75rem; color:#123B66; border:1px solid #DCE4EE;">${escapeHtml(b.course_code || '--')}</code></td>
                      <td style="padding:6px 8px; color:#5B6B82;">Sem ${b.semester || '--'}${b.academic_year ? ` &bull; ${escapeHtml(b.academic_year)}` : ''}</td>
                      <td style="padding:6px 8px; text-align:right;"><span class="badge badge-high" style="font-size:0.7rem; padding:2px 6px;">${escapeHtml(b.grade || 'F')}</span></td>
                    </tr>
                  `).join('')}
                </tbody>
              </table>
            `;
          } else if (bCount > 0 && s.backlog_subjects) {
            backlogSec.style.display = 'block';
            if (backlogBadge) backlogBadge.textContent = `${bCount} Pending`;
            backlogCont.innerHTML = `<div style="color:#DC2626; font-weight:600;">${escapeHtml(s.backlog_subjects)}</div>`;
          } else {
            backlogSec.style.display = 'none';
            backlogCont.innerHTML = '';
          }
        }

        // Explainable risk factors
        const rfCont = document.getElementById('modalRiskFactorsContainer');
        if (rfCont) {
          const rfs = s.risk_factors || [];
          if (rfs.length > 0) {
            rfCont.innerHTML = rfs.map(rf => {
              const title = typeof rf === 'object' ? (rf.title || rf.category || '') : rf;
              const desc = typeof rf === 'object' && rf.description ? rf.description : '';
              const impact = typeof rf === 'object' && rf.impact ? `<span style="font-size:0.7rem; background:#FEE2E2; color:#991B1B; padding:2px 6px; border-radius:4px; font-weight:700;">${escapeHtml(rf.impact)}</span>` : '';
              return `
                <div style="background:#FEF2F2; border:1px solid #FCA5A5; color:#991B1B; padding:8px 12px; border-radius:6px; font-size:0.8rem;">
                  <div style="display:flex; justify-content:space-between; align-items:center; font-weight:700;">
                    <span><i class="fas fa-exclamation-circle" style="margin-right:6px;"></i> ${escapeHtml(title)}</span>
                    ${impact}
                  </div>
                  ${desc ? `<p style="margin:4px 0 0 0; font-size:0.75rem; color:#7F1D1D; font-weight:normal;">${escapeHtml(desc)}</p>` : ''}
                </div>
              `;
            }).join('');
          } else {
            rfCont.innerHTML = '<div style="color:#5B6B82; font-size:0.8rem; font-style:italic;">No active negative risk triggers.</div>';
          }
        }

        // Strengths
        const stCont = document.getElementById('modalStrengthsContainer');
        if (stCont) {
          const sts = (s.positive_factors && s.positive_factors.length > 0) ? s.positive_factors : (s.strengths || []);
          if (sts.length > 0) {
            stCont.innerHTML = sts.map(st => {
              const title = typeof st === 'object' ? (st.title || st.category || '') : st;
              const desc = typeof st === 'object' && st.description ? st.description : '';
              return `
                <div style="background:#ECFDF5; border:1px solid #6EE7B7; color:#065F46; padding:8px 12px; border-radius:6px; font-size:0.8rem;">
                  <div style="font-weight:700;"><i class="fas fa-check-circle" style="margin-right:6px;"></i> ${escapeHtml(title)}</div>
                  ${desc ? `<p style="margin:4px 0 0 0; font-size:0.75rem; color:#064E3B; font-weight:normal;">${escapeHtml(desc)}</p>` : ''}
                </div>
              `;
            }).join('');
          } else {
            stCont.innerHTML = '<div style="color:#5B6B82; font-size:0.8rem; font-style:italic;">Standard academic baseline.</div>';
          }
        }

        if (modal) modal.style.display = 'flex';
      } catch (err) {
        console.error('Error fetching student detail:', err);
      }
    }
    window.inspectStudent = inspectStudent;

    function escapeHtml(str) {
      if (!str) return '';
      return String(str).replace(/[&<>"']/g, m => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[m]);
    }

    // Load Department Overview Data
    async function loadHodDashboard() {
      try {
        const res = await fetch('/api/hod/overview');
        if (!res.ok) {
          console.warn('HOD overview returned status:', res.status);
          const errData = await res.json().catch(() => ({}));
          const errMsg = errData.message || 'Unable to load department data.';
          document.querySelectorAll('#hodFacultyTableBody, #hodStudentsTableBody, #hodInterventionsTableBody').forEach(tbody => {
            tbody.innerHTML = `<tr><td colspan="9" style="text-align:center; padding:24px; color:#DC2626; font-weight:600;"><i class="fas fa-triangle-exclamation" style="margin-right:6px;"></i> ${escapeHtml(errMsg)}</td></tr>`;
          });
          return;
        }
        const data = await res.json();
        HOD_DATA = data;

        const m = data.metrics || {};
        const setTxt = (id, val) => {
          const el = document.getElementById(id);
          if (el) el.textContent = val;
        };

        setTxt('statTotalStudents', m.total_students || 0);
        setTxt('statTotalFaculty', m.total_faculty || 0);
        setTxt('statAtRiskStudents', m.at_risk_students || 0);
        setTxt('statRiskSub', `High: ${m.high_risk_count || 0} • Medium: ${m.med_risk_count || 0}`);
        setTxt('statAvgAttendance', (m.avg_attendance || 0) + '%');
        setTxt('statAvgCgpa', parseFloat(m.avg_cgpa || 0).toFixed(2));
        setTxt('statAvgMarks', `Avg Marks: ${m.avg_marks || 0}%`);
        setTxt('statActiveInterventions', m.active_interventions || 0);
        setTxt('statTotalInterventions', `Total logged: ${m.total_interventions || 0}`);

        setTxt('deptSuccessScore', m.avg_success_score || '--');
        setTxt('deptTotalBacklogs', m.total_backlogs || 0);

        // Risk breakdown counts & bars
        const totalS = m.total_students || 1;
        setTxt('riskCountHigh', `${m.high_risk_count || 0} (${Math.round((m.high_risk_count || 0) / totalS * 100)}%)`);
        setTxt('riskCountMed', `${m.med_risk_count || 0} (${Math.round((m.med_risk_count || 0) / totalS * 100)}%)`);
        setTxt('riskCountLow', `${m.low_risk_count || 0} (${Math.round((m.low_risk_count || 0) / totalS * 100)}%)`);

        const setWidth = (id, pct) => {
          const el = document.getElementById(id);
          if (el) el.style.width = pct;
        };
        setWidth('barHighRisk', `${Math.min(100, Math.round((m.high_risk_count || 0) / totalS * 100))}%`);
        setWidth('barMedRisk', `${Math.min(100, Math.round((m.med_risk_count || 0) / totalS * 100))}%`);
        setWidth('barLowRisk', `${Math.min(100, Math.round((m.low_risk_count || 0) / totalS * 100))}%`);

        // Render Faculty Table
        renderFacultyTable(data.faculty?.list || []);

        // Render Students Table
        renderStudentsTable(data.students || []);

        // Render Risk Section
        renderRiskSection(data.students || []);

        // Render Interventions Table
        renderInterventionsTable(data.interventions || []);

      } catch (err) {
        console.error('Failed to load HOD overview:', err);
      }
    }

    function renderFacultyTable(facultyList) {
      const tbody = document.getElementById('hodFacultyTableBody');
      if (!tbody) return;
      if (!facultyList || facultyList.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" style="text-align:center; padding:24px; color:#5B6B82; font-weight:600;">No faculty members found for this department.</td></tr>';
        return;
      }
      tbody.innerHTML = facultyList.map(f => `
        <tr style="border-bottom:1px solid #DCE4EE;">
          <td style="padding:12px 14px; font-weight:700; font-size:0.8125rem;"><span style="color:#123B66;">${escapeHtml(f.faculty_id)}</span></td>
          <td style="padding:12px 14px; font-weight:700; font-size:0.875rem;"><span style="color:#172B4D;">${escapeHtml(f.name)}</span></td>
          <td style="padding:12px 14px; font-size:0.8125rem;"><span style="color:#5B6B82;">${escapeHtml(f.designation || 'Faculty')}</span></td>
          <td style="padding:12px 14px; font-size:0.8125rem; font-weight:500;"><span style="color:#172B4D;">${escapeHtml(f.specialization || 'General')}</span></td>
          <td style="padding:12px 14px; font-size:0.8125rem;"><a href="mailto:${escapeHtml(f.email || '')}" style="color:#2F80ED; text-decoration:none; font-weight:600;">${escapeHtml(f.email || 'N/A')}</a></td>
          <td style="padding:12px 14px; font-size:0.8125rem;"><span style="color:#5B6B82;">${escapeHtml(f.phone || 'N/A')}</span></td>
        </tr>
      `).join('');
    }

    function renderStudentsTable(students) {
      const tbody = document.getElementById('hodStudentsTableBody');
      if (!tbody) return;

      const q = (document.getElementById('filterStudentSearch')?.value || '').toLowerCase();
      const r = document.getElementById('filterRiskLevel')?.value || 'ALL';
      const a = document.getElementById('filterAttendance')?.value || 'ALL';
      const b = document.getElementById('filterBacklogs')?.value || 'ALL';

      const filtered = students.filter(s => {
        if (q && !(s.name || '').toLowerCase().includes(q) && !(s.student_id || '').toLowerCase().includes(q)) return false;
        if (r !== 'ALL' && (s.risk_level || '').toLowerCase() !== r.toLowerCase()) return false;
        if (a === 'BELOW_75' && parseFloat(s.attendance_pct || 0) >= 75) return false;
        if (a === 'ABOVE_75' && parseFloat(s.attendance_pct || 0) < 75) return false;
        if (b === 'HAS_BACKLOGS' && parseInt(s.backlogs || 0) === 0) return false;
        if (b === 'NO_BACKLOGS' && parseInt(s.backlogs || 0) > 0) return false;
        return true;
      });

      if (filtered.length === 0) {
        tbody.innerHTML = '<tr><td colspan="9" style="text-align:center; padding:24px; color:#5B6B82; font-weight:600;">No matching students found.</td></tr>';
        return;
      }

      tbody.innerHTML = filtered.map(s => {
        const risk = (s.risk_level || 'Low').toLowerCase();
        const badgeClass = risk === 'high' ? 'badge-high' : (risk === 'medium' ? 'badge-medium' : 'badge-low');
        const attVal = parseFloat(s.attendance_pct || 0);
        const attColor = attVal < 75 ? '#DC2626' : '#172B4D';
        const backlogsCount = parseInt(s.backlogs || 0);
        const bSubj = s.backlog_details && s.backlog_details.length > 0
          ? s.backlog_details.map(bk => bk.display).join(', ')
          : (s.backlog_subjects || '');
        const backlogText = backlogsCount > 0 
          ? `<span style="color:#DC2626; font-weight:700;">${backlogsCount} Backlog${backlogsCount > 1 ? 's' : ''}</span>` +
            (bSubj ? `<div style="font-size:0.72rem; color:#DC2626; margin-top:2px; max-width:180px; word-break:break-word;">${escapeHtml(bSubj)}</div>` : '')
          : '<span style="color:#16A34A; font-weight:600;">Clear (0)</span>';

        return `
          <tr style="border-bottom:1px solid #DCE4EE;">
            <td style="padding:10px 12px; font-weight:700; font-size:0.8125rem;"><span style="color:#123B66;">${escapeHtml(s.student_id)}</span></td>
            <td style="padding:10px 12px; font-weight:700; font-size:0.875rem;"><span style="color:#172B4D;">${escapeHtml(s.name)}</span></td>
            <td style="padding:10px 12px; font-size:0.8125rem;"><span style="color:#5B6B82;">Sem ${s.semester || 'N/A'} ${s.section ? '(' + s.section + ')' : ''}</span></td>
            <td style="padding:10px 12px; font-weight:700; font-size:0.8125rem;"><span style="color:${attColor};">${attVal.toFixed(1)}%</span></td>
            <td style="padding:10px 12px; font-weight:700; font-size:0.8125rem;"><span style="color:#172B4D;">${parseFloat(s.cgpa || 0).toFixed(2)}</span></td>
            <td style="padding:10px 12px; font-size:0.8125rem;">${backlogText}</td>
            <td style="padding:10px 12px; font-weight:700; font-size:0.8125rem;"><span style="color:#2F80ED;">${s.success_score || '--'}</span></td>
            <td style="padding:10px 12px;"><span class="badge ${badgeClass}">${escapeHtml(s.risk_level || 'Low')}</span></td>
            <td style="padding:10px 12px; text-align:right;">
              <button onclick="inspectStudent('${escapeHtml(s.student_id)}')" class="btn-inspect" style="padding:4px 10px; font-size:0.75rem; background:#EBF4FF; color:#123B66; border:1px solid #DCE4EE; border-radius:6px; font-weight:700; cursor:pointer;">Inspect &rarr;</button>
            </td>
          </tr>
        `;
      }).join('');
    }

    // Attach filter listeners for both input and change events
    ['filterStudentSearch', 'filterRiskLevel', 'filterAttendance', 'filterBacklogs'].forEach(id => {
      const el = document.getElementById(id);
      if (el) {
        el.addEventListener('input', () => renderStudentsTable(HOD_DATA.students || []));
        el.addEventListener('change', () => renderStudentsTable(HOD_DATA.students || []));
      }
    });

    function renderRiskSection(students) {
      const highList = students.filter(s => (s.risk_level || '').toLowerCase() === 'high');
      const medList = students.filter(s => (s.risk_level || '').toLowerCase() === 'medium');
      const lowList = students.filter(s => (s.risk_level || '').toLowerCase() === 'low');

      const setTxt = (id, val) => {
        const el = document.getElementById(id);
        if (el) el.textContent = val;
      };

      setTxt('cardHighRiskCount', `${highList.length} Students`);
      setTxt('cardMedRiskCount', `${medList.length} Students`);
      setTxt('cardLowRiskCount', `${lowList.length} Students`);

      const renderStudentRiskCard = (s, color) => {
        const reasons = [];
        if (parseFloat(s.attendance_pct || 0) < 75) reasons.push(`Attendance: ${parseFloat(s.attendance_pct).toFixed(1)}%`);
        if (parseInt(s.backlogs || 0) > 0) {
          const bSubj = s.backlog_details && s.backlog_details.length > 0
            ? s.backlog_details.map(bk => bk.display).join(', ')
            : (s.backlog_subjects || '');
          reasons.push(`${s.backlogs} Backlog(s)${bSubj ? ': ' + bSubj : ''}`);
        }
        if (parseFloat(s.cgpa || 0) < 7.0) reasons.push(`CGPA: ${parseFloat(s.cgpa).toFixed(2)}`);
        const reasonStr = reasons.length > 0 ? reasons.join(' • ') : 'Academic monitoring review';

        return `
          <div style="background:#FFFFFF; border:1px solid #DCE4EE; border-radius:8px; padding:10px 12px; display:flex; justify-content:space-between; align-items:center;">
            <div>
              <div style="font-weight:700; color:#172B4D; font-size:0.8125rem;">${escapeHtml(s.name)} <span style="font-weight:500; color:#5B6B82; font-size:0.75rem;">(${s.student_id})</span></div>
              <div style="font-size:0.72rem; color:${color}; margin-top:2px; font-weight:600;">${reasonStr}</div>
            </div>
            <button onclick="inspectStudent('${escapeHtml(s.student_id)}')" style="padding:3px 8px; font-size:0.72rem; background:#F4F7FB; border:1px solid #DCE4EE; border-radius:4px; font-weight:700; cursor:pointer; color:#123B66;">View</button>
          </div>
        `;
      };

      const highEl = document.getElementById('highRiskStudentsList');
      if (highEl) {
        highEl.innerHTML = highList.length > 0 
          ? highList.map(s => renderStudentRiskCard(s, '#DC2626')).join('')
          : '<div style="color:#5B6B82; font-size:0.75rem; font-style:italic;">No students currently classified as High Risk.</div>';
      }

      const medEl = document.getElementById('medRiskStudentsList');
      if (medEl) {
        medEl.innerHTML = medList.length > 0
          ? medList.map(s => renderStudentRiskCard(s, '#D97706')).join('')
          : '<div style="color:#5B6B82; font-size:0.75rem; font-style:italic;">No students currently classified as Medium Risk.</div>';
      }

      const lowEl = document.getElementById('lowRiskStudentsList');
      if (lowEl) {
        lowEl.innerHTML = lowList.length > 0
          ? lowList.slice(0, 5).map(s => renderStudentRiskCard(s, '#16A34A')).join('') + (lowList.length > 5 ? `<div style="font-size:0.72rem; color:#5B6B82; text-align:center; padding:4px;">+ ${lowList.length - 5} more students in good standing</div>` : '')
          : '<div style="color:#5B6B82; font-size:0.75rem; font-style:italic;">No records.</div>';
      }
    }

    function renderInterventionsTable(intvs) {
      const tbody = document.getElementById('hodInterventionsTableBody');
      if (!tbody) return;
      if (!intvs || intvs.length === 0) {
        tbody.innerHTML = '<tr><td colspan="7" style="text-align:center; padding:24px; color:#5B6B82; font-weight:600;">No interventions recorded for this department yet.</td></tr>';
        return;
      }

      tbody.innerHTML = intvs.map(i => {
        const prio = i.priority || 'High';
        const prioClass = (prio === 'Immediate' || prio === 'Urgent') ? 'badge-high' : (prio === 'High' ? 'badge-medium' : 'badge-low');
        const st = (i.status || 'Assigned');
        const statusClass = st === 'Completed' ? 'badge-low' : (st === 'In Progress' ? 'badge-accent' : 'badge-medium');
        const instr = i.instructions || i.notes || 'Routine academic advising';

        return `
          <tr style="border-bottom:1px solid #DCE4EE;">
            <td style="padding:10px 12px; font-weight:700; font-size:0.8125rem;"><span style="color:#123B66;">#INT-${i.id}</span></td>
            <td style="padding:10px 12px; font-weight:700; font-size:0.875rem;"><span style="color:#172B4D;">${escapeHtml(i.student_name || i.student_id)}</span> <span style="font-size:0.72rem; color:#5B6B82; display:block; font-weight:normal;">${escapeHtml(i.student_id)}</span></td>
            <td style="padding:10px 12px; font-size:0.8125rem; font-weight:600;"><span style="color:#123B66;">${escapeHtml(i.faculty_name || 'Faculty Mentor')}</span></td>
            <td style="padding:10px 12px; font-size:0.8125rem; font-weight:600;"><span style="color:#172B4D;">${escapeHtml(i.title || i.action_type || 'Intervention')}</span></td>
            <td style="padding:10px 12px;"><span class="badge ${prioClass}">${escapeHtml(prio)}</span></td>
            <td style="padding:10px 12px; font-size:0.75rem; max-width:260px;"><span style="color:#172B4D;">${escapeHtml(instr)}</span></td>
            <td style="padding:10px 12px;"><span class="badge ${statusClass}">${escapeHtml(st)}</span></td>
          </tr>
        `;
      }).join('');
    }

    // Auto-fetch on DOM ready or immediately if DOM already loaded
    function initHodDashboard() {
      switchSection('section-overview');
      loadHodDashboard();
    }

    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', initHodDashboard);
    } else {
      initHodDashboard();
    }
  </script>
</body>
</html>"""

new_tpl = prefix + clean_modal_and_script

with open(tpl_path, "wb") as f:
    f.write(new_tpl.replace("\n", "\r\n").encode("utf-8"))

print("Patched templates/hod_dashboard.html successfully!")
