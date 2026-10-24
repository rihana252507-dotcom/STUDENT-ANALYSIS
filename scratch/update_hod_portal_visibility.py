import re

with open('templates/hod_dashboard.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update topbar profile chip to use standard classes and dark text
old_chip = """          <div class="topbar-profile-chip">
            <div class="topbar-avatar">{{ user.name[:2].upper() }}</div>
            <div style="display:flex; flex-direction:column; text-align:left;">
              <span class="topbar-user-name">{{ user.name }}</span>
              <span class="topbar-user-role">Head of Department ({{ dept_code }})</span>
            </div>
          </div>"""

new_chip = """          <div class="topbar-profile-chip">
            <div class="user-avatar-sm">{{ user.name[:2].upper() }}</div>
            <div class="topbar-user-text">
              <span class="user-name-text" style="color:#172B4D; font-weight:700; font-size:0.78rem;">{{ user.name }}</span>
              <span class="user-role-text" style="color:#5B6B82; font-size:0.68rem;">Head of Department ({{ dept_code }})</span>
            </div>
          </div>"""

# 2. Update section-overview to active-section with display:block
old_section = '<section id="section-overview" class="dashboard-section active">'
new_section = '<section id="section-overview" class="dashboard-section active-section active" style="display:block;">'

# 3. Update strong tag in hero-sub-desc
old_strong = '<strong>{{ dept_info.hod_name if dept_info else user.name }}</strong>'
new_strong = '<strong style="color:#FFFFFF;">{{ dept_info.hod_name if dept_info else user.name }}</strong>'

# 4. Update the entire script block
script_start = content.find('<script>')
assert script_start != -1

new_script = """<script>
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

        const rfCont = document.getElementById('modalRiskFactorsContainer');
        if (rfCont) {
          rfCont.innerHTML = (s.risk_factors || []).length > 0 
            ? s.risk_factors.map(rf => `<div style="background:#FEF2F2; border:1px solid #FCA5A5; color:#991B1B; padding:8px 12px; border-radius:6px; font-size:0.8rem; font-weight:600;"><i class="fas fa-exclamation-circle" style="margin-right:6px;"></i> ${escapeHtml(rf)}</div>`).join('')
            : '<div style="color:#5B6B82; font-size:0.8rem; font-style:italic;">No active negative risk triggers.</div>';
        }

        const stCont = document.getElementById('modalStrengthsContainer');
        if (stCont) {
          stCont.innerHTML = (s.strengths || []).length > 0
            ? s.strengths.map(st => `<div style="background:#ECFDF5; border:1px solid #6EE7B7; color:#065F46; padding:8px 12px; border-radius:6px; font-size:0.8rem; font-weight:600;"><i class="fas fa-check-circle" style="margin-right:6px;"></i> ${escapeHtml(st)}</div>`).join('')
            : '<div style="color:#5B6B82; font-size:0.8rem; font-style:italic;">Standard academic baseline.</div>';
        }

        if (modal) modal.style.display = 'flex';
      } catch (err) {
        console.error('Error fetching student detail:', err);
      }
    }

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
        const backlogText = backlogsCount > 0 
          ? `<span style="color:#DC2626; font-weight:700;">${backlogsCount} Backlog${backlogsCount > 1 ? 's' : ''}</span>`
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

    // Attach filter listeners
    ['filterStudentSearch', 'filterRiskLevel', 'filterAttendance', 'filterBacklogs'].forEach(id => {
      const el = document.getElementById(id);
      if (el) el.addEventListener('input', () => renderStudentsTable(HOD_DATA.students || []));
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
        if (parseInt(s.backlogs || 0) > 0) reasons.push(`${s.backlogs} Backlog(s)`);
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

# Apply replacements
assert old_chip in content, "old_chip not found"
content = content.replace(old_chip, new_chip)

assert old_section in content, "old_section not found"
content = content.replace(old_section, new_section)

if old_strong in content:
    content = content.replace(old_strong, new_strong)

content = content[:script_start] + new_script

with open('templates/hod_dashboard.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("SUCCESS: Updated templates/hod_dashboard.html successfully!")
