/**
 * CampusIQ – AI-Powered Student Analytics and Success Platform
 * Frontend Interactive Controller (Chart.js, Telemetry, Modals, Action Hub, What-If Simulator)
 * KPMG in India Hackathon Challenge Prototype
 */

const STATE = {
  activeRisk: "ALL",
  activeDept: "ALL",
  activeSem: "ALL",
  searchQuery: "",
  sortBy: "department-asc",
  students: [],
  faculty: [],
  courses: [],
  interventions: [],
  selectedStudentId: null,
  charts: {}
};

// ==============================================================================
// 1. INITIALIZATION ON DOM READY
// ==============================================================================

document.addEventListener("DOMContentLoaded", async () => {
  setupNavigation();
  setupEventListeners();

  // If on Admin dashboard, load chart telemetry, department benchmarks, faculty, courses, interventions
  if (document.getElementById("riskDoughnutChart")) {
    await fetchCharts();
    await fetchDepartmentBenchmarks();
    await fetchFaculty();
    await fetchCourses();
    await fetchInterventions();
  }

  // If on Faculty dashboard, load faculty advisee caseload, interventions, and notifications
  if (document.getElementById("facultyAnalyticsIndicatorsRow") || document.getElementById("facultyOverviewTableBody")) {
    await fetchInterventions();
    await fetchNotifications();
  }

  // Load student directory / caseload
  if (document.getElementById("studentsTableBody") || document.getElementById("facultyAnalyticsIndicatorsRow") || document.getElementById("facultyOverviewTableBody") || document.getElementById("academicPerfTableBody") || document.getElementById("riskAlertsTableBody")) {
    await fetchStudents();
  }

  // If on Student dashboard, initialize radar chart and personal simulator
  if (document.getElementById("studentPillarRadarChart")) {
    initStudentRadar();
  }
  if (window.STUDENT_DATA || document.getElementById("personalRangeAttendance")) {
    initPersonalSimulator();
  }
});

// ==============================================================================
// 2. SIDEBAR NAVIGATION & SECTION SWITCHER (NO DEAD LINKS)
// ==============================================================================

function setupNavigation() {
  const navLinks = document.querySelectorAll(".sidebar-nav-link[data-section]");
  navLinks.forEach(link => {
    link.addEventListener("click", (e) => {
      e.preventDefault();
      const sectionId = link.getAttribute("data-section");
      if (sectionId) {
        switchSection(sectionId);
      }
    });
  });

  // Mobile sidebar toggle
  const btnToggleSidebar = document.getElementById("btnToggleSidebar");
  const sidebar = document.getElementById("appSidebar");
  if (btnToggleSidebar && sidebar) {
    btnToggleSidebar.addEventListener("click", () => {
      sidebar.classList.toggle("mobile-open");
    });
  }
}

window.switchSection = function(sectionId) {
  // Update sidebar active link
  let activeLabel = "";
  document.querySelectorAll(".sidebar-nav-link[data-section]").forEach(link => {
    if (link.getAttribute("data-section") === sectionId) {
      link.classList.add("active");
      const span = link.querySelector("span");
      if (span) activeLabel = span.textContent.trim();
    } else {
      link.classList.remove("active");
    }
  });

  // Update topbar breadcrumb current section text
  const breadcrumbEl = document.getElementById("topbarCurrentSection");
  if (breadcrumbEl && activeLabel) {
    breadcrumbEl.textContent = activeLabel;
  }

  // Hide all sections
  document.querySelectorAll(".dashboard-section").forEach(sec => {
    sec.classList.remove("active-section");
    sec.style.display = "none";
  });

  // Show target section
  const target = document.getElementById(sectionId);
  if (target) {
    target.classList.add("active-section");
    target.style.display = "block";
    target.scrollIntoView({ behavior: "smooth", block: "start" });
  }

  // Close mobile sidebar if open
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
};

// ==============================================================================
// 3. DATA FETCHING HANDLERS
// ==============================================================================

async function fetchStudents() {
  try {
    const params = new URLSearchParams();
    if (STATE.activeRisk !== "ALL") params.append("risk_level", STATE.activeRisk);
    if (STATE.activeDept !== "ALL") params.append("department", STATE.activeDept);
    if (STATE.activeSem !== "ALL") params.append("semester", STATE.activeSem);
    if (STATE.searchQuery) params.append("search", STATE.searchQuery);

    const [field, order] = STATE.sortBy.split("-");
    params.append("sort_by", field);
    params.append("order", order);

    const res = await fetch(`/api/students?${params.toString()}`);
    if (!res.ok) throw new Error("Failed to load students");
    const data = await res.json();

    STATE.students = data.students || [];
    renderStudentTable(STATE.students);
    renderFacultyOverview(STATE.students);
    renderRiskWatchlist(STATE.students);
    renderRiskAlertsTable(STATE.students);
    renderAcademicPerf(STATE.students);
    renderAttendanceTable(STATE.students);
    updateDynamicKpis(STATE.students, data.total_count);
    updateCohortSegments(STATE.students);
    populateSimulatorDropdown(STATE.students);
  } catch (err) {
    console.error("Error fetching students:", err);
  }
}

function updateDynamicKpis(students, totalCount) {
  const kpiTotal = document.getElementById("kpiTotalStudents");
  const kpiSuccess = document.getElementById("kpiAvgSuccess");
  const kpiHigh = document.getElementById("kpiHighRisk");
  const kpiHighPct = document.getElementById("kpiHighRiskPct");
  const kpiAttRate = document.getElementById("kpiAttendanceRate");
  const kpiAttAvg = document.getElementById("kpiAttendanceAvg");

  if (!students || students.length === 0) return;

  const total = students.length;
  const highRiskCount = students.filter(s => s.risk_level === "High").length;
  const avgSuccess = (students.reduce((acc, s) => acc + (s.success_score || 0), 0) / total).toFixed(1);
  const avgAttendance = (students.reduce((acc, s) => acc + (s.attendance_pct || 0), 0) / total).toFixed(1);
  const compliantCount = students.filter(s => s.attendance_pct >= 75.0).length;
  const compliantPct = ((compliantCount / total) * 100).toFixed(1);

  const SUCCESS_TARGET = 70;
  const ATT_THRESHOLD = 75;

  if (kpiTotal) kpiTotal.textContent = total;
  if (kpiSuccess) {
    const successVal = parseFloat(avgSuccess);
    const successColor = successVal < SUCCESS_TARGET ? '#DC2626' : '#172B4D';
    kpiSuccess.innerHTML = `<span style="color:${successColor}; font-weight:800;">${avgSuccess}</span><span class="kpi-sub">/100</span>`;
  }
  if (kpiHigh) kpiHigh.textContent = highRiskCount;
  if (kpiHighPct) kpiHighPct.textContent = `${((highRiskCount / total) * 100).toFixed(1)}%`;
  if (kpiAttRate) {
    const rateVal = parseFloat(compliantPct);
    const rateColor = rateVal < ATT_THRESHOLD ? '#DC2626' : '#172B4D';
    kpiAttRate.innerHTML = `<span style="color:${rateColor}; font-weight:700;">${compliantPct}%</span>`;
  }
  if (kpiAttAvg) {
    const attVal = parseFloat(avgAttendance);
    const attColor = attVal < ATT_THRESHOLD ? '#DC2626' : '#172B4D';
    kpiAttAvg.innerHTML = `Avg: <span style="color:${attColor}; font-weight:700;">${avgAttendance}%</span>`;
  }
}

function updateCohortSegments(students) {
  const segDebar = document.getElementById("segCountDebar");
  const segPlacement = document.getElementById("segCountPlacement");
  const segBacklogs = document.getElementById("segCountBacklogs");
  const segStars = document.getElementById("segCountStars");

  if (!students || students.length === 0) return;

  const lowAttCount = students.filter(s => s.attendance_pct < 75.0).length;
  const placementGapCount = students.filter(s => s.cgpa >= 7.5 && (s.placement_aptitude_score < 65 || s.technical_skills_score < 70)).length;
  const backlogCount = students.filter(s => s.backlogs > 0).length;
  const starCount = students.filter(s => (s.success_score || 0) >= 80).length;

  if (segDebar) segDebar.textContent = `${lowAttCount} Students`;
  if (segPlacement) segPlacement.textContent = `${placementGapCount} Students`;
  if (segBacklogs) segBacklogs.textContent = `${backlogCount} Students`;
  if (segStars) segStars.textContent = `${starCount} Students`;
}


window.showSegmentStudents = function(segmentType) {
  const students = STATE.students;
  if (!students || students.length === 0) {
    alert('Student data is still loading. Please wait a moment and try again.');
    return;
  }

  let filtered = [];
  let title = '', badge = '', badgeClass = '', subtitle = '';

  if (segmentType === 'debar') {
    filtered = students.filter(s => s.attendance_pct < 75.0);
    title = 'Low Attendance & Debarment Risk';
    badge = 'Debarment Alert';
    badgeClass = 'badge-high';
    subtitle = filtered.length + ' students with attendance < 75%. Urgent statutory counseling required.';
  } else if (segmentType === 'placement') {
    filtered = students.filter(s => s.cgpa >= 7.5 && (s.placement_aptitude_score < 65 || s.technical_skills_score < 70));
    title = 'Academically Strong but Placement-Unready';
    badge = 'Skills Gap';
    badgeClass = 'badge-medium';
    subtitle = filtered.length + ' student(s) with CGPA >= 7.5 but technical/aptitude score below threshold.';
  } else if (segmentType === 'backlogs') {
    filtered = students.filter(s => s.backlogs > 0);
    title = 'Academic Velocity & Backlog Risk';
    badge = 'Credit Delay';
    badgeClass = 'badge-high';
    subtitle = filtered.length + ' students with 1 or more active backlogs.';
  } else if (segmentType === 'stars') {
    filtered = students.filter(s => (s.success_score || 0) >= 80);
    title = 'High Potential Star Performers';
    badge = 'Exemplary';
    badgeClass = 'badge-low';
    subtitle = filtered.length + ' students with Composite Success Score >= 80.';
  }

  const container = document.getElementById('segmentStudentDrilldownContainer');
  const titleEl   = document.getElementById('drilldownTitle');
  const badgeEl   = document.getElementById('drilldownBadge');
  const subtitleEl = document.getElementById('drilldownSubtitle');
  const tbody     = document.getElementById('segmentStudentTableBody');

  if (!container || !tbody) { console.error('Drilldown elements not found'); return; }

  if (titleEl)    titleEl.textContent = title;
  if (badgeEl)  { badgeEl.textContent = badge; badgeEl.className = 'badge ' + badgeClass; }
  if (subtitleEl) subtitleEl.textContent = subtitle;

  if (filtered.length === 0) {
    tbody.innerHTML = '<tr><td colspan="9" style="text-align:center; padding:24px; color:#6B7280;">No students match this segment currently.</td></tr>';
  } else {
    tbody.innerHTML = filtered.map(function(s) {
      var riskClass = 'badge-' + (s.risk_badge || (s.risk_level || 'medium').toLowerCase());
      var attColor  = s.attendance_pct < 75 ? '#DC2626' : '#10B981';
      var cgpa      = parseFloat(s.cgpa || 0).toFixed(2);
      var score     = s.success_score != null ? s.success_score : '—';
      var scoreColor = (s.success_score != null && parseFloat(s.success_score) < 70) ? '#DC2626' : '#111827';
      var name      = (s.name || '').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
      return '<tr style="cursor:pointer;" onclick="inspectStudent(\'' + s.student_id + '\')">' +
        '<td><strong style="color:#111827;">' + name + '</strong>' +
          '<div class="student-id-code" style="font-size:0.72rem; color:#6B7280;">' + s.student_id + '</div></td>' +
        '<td><span class="badge badge-accent">' + (s.department || '—') + '</span></td>' +
        '<td>Sem ' + (s.semester || '—') + '</td>' +
        '<td><strong style="color:' + attColor + ';">' + s.attendance_pct + '%</strong></td>' +
        '<td><strong>' + cgpa + '</strong></td>' +
        (function(){
          var bCell = '<span style="color:' + (s.backlogs > 0 ? '#DC2626' : '#10B981') + '; font-weight:700;">' + s.backlogs + '</span>';
          if (s.backlogs > 0 && s.backlog_details && s.backlog_details.length > 0) {
            var subjList = s.backlog_details.map(function(b) { return (b.display || b.course_name || '').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;'); }).join(', ');
            bCell += '<div style="font-size:0.70rem; color:#DC2626; margin-top:2px; max-width:180px; word-break:break-word;">' + subjList + '</div>';
          } else if (s.backlogs > 0 && s.backlog_subjects) {
            var subjList2 = (Array.isArray(s.backlog_subjects) ? s.backlog_subjects : [s.backlog_subjects]).join(', ').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
            bCell += '<div style="font-size:0.70rem; color:#DC2626; margin-top:2px; max-width:180px; word-break:break-word;">' + subjList2 + '</div>';
          }
          return '<td>' + bCell + '</td>';
        }()) +
        '<td><span class="badge ' + riskClass + '">' + (s.risk_level || '—') + ' Risk</span></td>' +
        '<td><strong style="color:' + scoreColor + ';">' + score + '</strong>/100</td>' +
        '<td style="text-align:right;"><button class="btn-inspect" onclick="event.stopPropagation(); inspectStudent(\'' + s.student_id + '\')">Inspect &rarr;</button></td>' +
      '</tr>';
    }).join('');
  }

  container.style.display = 'block';
  container.scrollIntoView({ behavior: 'smooth', block: 'start' });
};

window.closeSegmentDrilldown = function() {
  var container = document.getElementById('segmentStudentDrilldownContainer');
  if (container) container.style.display = 'none';
};

async function fetchDepartmentBenchmarks() {
  const tbody = document.getElementById("adminDeptTableBody");
  if (!tbody) return;

  try {
    const res = await fetch("/api/admin/departments");
    if (!res.ok) return;
    const data = await res.json();

    tbody.innerHTML = (data.departments || []).map(d => {
      const auditBadge = d.high_risk_pct > 25
        ? `<span class="badge badge-high">Audit Flagged</span>`
        : (d.high_risk_pct > 15 ? `<span class="badge badge-medium">Review Needed</span>` : `<span class="badge badge-low">Accredited</span>`);

      return `
        <tr>
          <td><strong>${d.department}</strong><div class="student-id-code">${d.department_name}</div></td>
          <td><strong>${d.total_students}</strong></td>
          <td><span style="color:#F43F5E; font-weight:700;">${d.high_risk_count}</span> (${d.high_risk_pct}%)</td>
          <td>${d.medium_risk_count}</td>
          <td><span style="color:#10B981; font-weight:700;">${d.low_risk_count}</span></td>
          <td><strong>${d.avg_cgpa}</strong></td>
          <td><span style="color:${parseFloat(d.avg_attendance) < 75 ? '#DC2626' : '#172B4D'}; font-weight:${parseFloat(d.avg_attendance) < 75 ? '700' : '400'}">${d.avg_attendance}%</span></td>
          <td><strong style="color:${parseFloat(d.avg_success_score) < 70 ? '#DC2626' : '#172B4D'}">${d.avg_success_score}</strong>/100</td>
          <td>${d.placement_ready_rate}%</td>
          <td>${auditBadge}</td>
        </tr>
      `;
    }).join("");
  } catch (err) {
    console.error("Error loading department benchmarks:", err);
  }
}

async function fetchFaculty() {
  const tbody = document.getElementById("facultyTableBody");
  if (!tbody) return;

  try {
    const res = await fetch("/api/admin/faculty");
    if (!res.ok) return;
    const data = await res.json();
    STATE.faculty = data.faculty || [];

    tbody.innerHTML = STATE.faculty.map(f => `
      <tr>
        <td>
          <div style="display:flex; align-items:center; gap:10px;">
            <div class="student-avatar" style="background:var(--grad-pink-purple);">${f.name.substring(0, 2).toUpperCase()}</div>
            <div>
              <strong class="faculty-name" style="color:#000000; font-size:0.875rem;">${escapeHtml(f.name)}</strong>
              <div class="student-id-code">${escapeHtml(f.email)}</div>
            </div>
          </div>
        </td>
        <td><code>${f.faculty_id}</code></td>
        <td><span class="badge badge-accent">${f.department}</span></td>
        <td>${escapeHtml(f.designation)}</td>
        <td><span style="font-size:0.75rem; color:#374151; font-weight:500;">${escapeHtml(f.specialization || 'Engineering')}</span></td>
        <td><strong>${f.advisee_count || 20}</strong> Students</td>
        <td><span style="font-size:0.75rem; color:#4B5563;">${escapeHtml(f.phone || '+91 9800000000')}</span></td>
      </tr>
    `).join("");
  } catch (err) {
    console.error("Error fetching faculty directory:", err);
  }
}

async function fetchCourses() {
  const tbody = document.getElementById("coursesTableBody");
  if (!tbody) return;

  try {
    const res = await fetch("/api/admin/courses");
    if (!res.ok) return;
    const data = await res.json();
    STATE.courses = data.courses || [];

    tbody.innerHTML = STATE.courses.map(c => `
      <tr>
        <td><strong>${c.course_code}</strong></td>
        <td>${escapeHtml(c.course_name)}</td>
        <td><span class="badge badge-accent">${c.department}</span></td>
        <td>Sem ${c.semester}</td>
        <td><strong>${c.credits}</strong> Credits</td>
        <td>${escapeHtml(c.faculty_name)}</td>
        <td><span style="color:#10B981; font-weight:700;">${c.pass_rate}%</span></td>
      </tr>
    `).join("");
  } catch (err) {
    console.error("Error fetching courses catalog:", err);
  }
}

async function fetchInterventions() {
  const tbody = document.getElementById("interventionsTableBody");
  if (!tbody) return;

  try {
    const res = await fetch("/api/interventions");
    if (!res.ok) return;
    const data = await res.json();
    STATE.interventions = data.interventions || [];

    const isAdmin = !!document.getElementById("riskDoughnutChart");

    const rowsHtml = STATE.interventions.map(i => {
      const prio = i.priority || "High";
      const prioClass = (prio === "Immediate" || prio === "Urgent") ? "badge-high" : (prio === "High" ? "badge-medium" : "badge-low");
      const statusClass = i.status === "Completed" ? "badge-low" : (i.status === "In Progress" ? "badge-accent" : "badge-medium");
      const intvTitle = i.title || i.action_type || "Intervention";

      if (isAdmin) {
        // Admin View: shows Assigned Faculty, Intervention, Priority, Faculty Notification Read Status, Faculty Action & Notes, Status
        const notifBadge = i.notif_is_read
          ? `<span class="badge badge-low" title="Read at: ${escapeHtml(i.notif_read_at || 'Yes')}">Read</span>`
          : `<span class="badge badge-high">Unread</span>`;

        const notesContent = i.action_taken || i.implementation_notes
          ? `<div style="max-width:240px; font-size:0.75rem;"><strong style="color:#10B981;">Action:</strong> ${escapeHtml(i.action_taken || 'In progress')}<br><span style="color:#374151;">${escapeHtml(i.implementation_notes || '')}</span></div>`
          : `<span style="font-size:0.72rem; color:var(--text-muted); font-style:italic;">Awaiting faculty action</span>`;

        return `
          <tr>
            <td>#INT-${i.id}</td>
            <td>
              <strong style="color:#000000;">${escapeHtml(i.student_name || i.student_id)}</strong>
              <div class="student-id-code">${i.student_id} &bull; ${i.student_dept || ''}</div>
            </td>
            <td><strong style="color:var(--purple-deep);">${escapeHtml(i.faculty_name || 'Faculty Mentor')}</strong></td>
            <td><strong>${escapeHtml(intvTitle)}</strong></td>
            <td><span class="badge ${prioClass}">${prio}</span></td>
            <td>${notifBadge}</td>
            <td>${notesContent}</td>
            <td>
              <span class="badge ${statusClass}">${i.status || 'Assigned'}</span>
            </td>
          </tr>
        `;
      } else {
        // Faculty View: shows Advisee, Intervention, Priority, Instructions & Notes, Action Taken, Status, Action Button
        const instrText = i.instructions || i.notes || 'No specific instructions';
        const actionText = i.action_taken
          ? `<span style="color:#10B981; font-weight:600;">${escapeHtml(i.action_taken)}</span>`
          : `<span style="color:var(--text-muted); font-style:italic;">Pending action</span>`;

        return `
          <tr>
            <td>#INT-${i.id}</td>
            <td>
              <strong style="color:#000000;">${escapeHtml(i.student_name || i.student_id)}</strong>
              <div class="student-id-code">${i.student_id} &bull; ${i.student_dept || ''}</div>
            </td>
            <td><strong>${escapeHtml(intvTitle)}</strong></td>
            <td><span class="badge ${prioClass}">${prio}</span></td>
            <td><div style="max-width:260px; font-size:0.75rem; color:#1F2937; font-weight:500;">${escapeHtml(instrText)}</div></td>
            <td><div style="max-width:220px; font-size:0.75rem;">${actionText}</div></td>
            <td><span class="badge ${statusClass}">${i.status || 'Assigned'}</span></td>
            <td style="text-align:right;">
              <button class="btn-inspect" onclick="openFacultyUpdateModal(${i.id})">Update &rarr;</button>
            </td>
          </tr>
        `;
      }
    }).join("");

    tbody.innerHTML = rowsHtml;
  } catch (err) {
    console.error("Error fetching interventions:", err);
  }
}

window.openFacultyUpdateModal = function(id) {
  const intv = (STATE.interventions || []).find(i => i.id === id);
  if (!intv) return;

  const modal = document.getElementById("modalUpdateIntervention");
  if (!modal) return;

  document.getElementById("editIntvId").value = intv.id;
  document.getElementById("modalIntvDisplayTitle").textContent = `${intv.title || intv.action_type || 'Intervention'} (Student: ${intv.student_name || intv.student_id})`;
  document.getElementById("modalIntvDisplayInstructions").textContent = intv.instructions || intv.notes || 'No instructions specified.';
  document.getElementById("editIntvStatus").value = intv.status || "In Progress";
  document.getElementById("editIntvActionTaken").value = intv.action_taken || "";
  document.getElementById("editIntvNotes").value = intv.implementation_notes || "";

  modal.style.display = "flex";
  modal.setAttribute("aria-hidden", "false");
};

window.updateInterventionStatus = async function(id, newStatus) {
  try {
    const res = await fetch(`/api/interventions/${id}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ status: newStatus })
    });
    if (res.ok) {
      console.log(`Intervention #${id} status updated to ${newStatus}`);
      await fetchInterventions();
    }
  } catch (err) {
    console.error("Error updating intervention status:", err);
  }
};

async function fetchCharts() {
  try {
    const res = await fetch("/api/admin/charts");
    if (!res.ok) return;
    const data = await res.json();
    renderCharts(data);
  } catch (err) {
    console.error("Error loading chart data:", err);
  }
}

// ==============================================================================
// 4. CHART.JS VISUALIZATIONS
// ==============================================================================

function renderCharts(data) {
  if (!window.Chart) return;

  // 1. Risk Doughnut Chart
  const doughnutCanvas = document.getElementById("riskDoughnutChart");
  if (doughnutCanvas && data.risk_breakdown) {
    if (STATE.charts.risk) STATE.charts.risk.destroy();

    const rb = data.risk_breakdown;
    STATE.charts.risk = new Chart(doughnutCanvas, {
      type: "doughnut",
      data: {
        labels: rb.labels,
        datasets: [{
          data: rb.counts,
          backgroundColor: ["#DC2626", "#D97706", "#059669"],
          borderWidth: 2,
          borderColor: "#FFFFFF"
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false }
        },
        cutout: "70%"
      }
    });

    const legendWrap = document.getElementById("riskLegendSummary");
    if (legendWrap) {
      legendWrap.innerHTML = rb.labels.map((lbl, idx) => `
        <div class="legend-item" style="display:flex; align-items:center; gap:8px; font-size:0.8rem; color:#4B5563; margin:4px 0;">
          <span class="legend-color-box" style="width:12px; height:12px; border-radius:3px; background-color: ${rb.colors[idx]}"></span>
          <span>${lbl}: <strong>${rb.counts[idx]}</strong> (${rb.percentages[idx]}%)</span>
        </div>
      `).join("");
    }
  }

  // 2. Department Benchmark Bar Chart
  const deptBarCanvas = document.getElementById("departmentBarChart");
  if (deptBarCanvas && data.department_chart) {
    if (STATE.charts.dept) STATE.charts.dept.destroy();

    const dc = data.department_chart;
    STATE.charts.dept = new Chart(deptBarCanvas, {
      type: "bar",
      data: {
        labels: dc.labels,
        datasets: [
          {
            label: "Success Score (0-100)",
            data: dc.avg_success,
            backgroundColor: "#2F80ED",
            borderRadius: 6
          },
          {
            label: "Avg CGPA (x10)",
            data: dc.avg_cgpa.map(c => c * 10),
            backgroundColor: "#16A6A1",
            borderRadius: 6
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          y: { beginAtZero: true, max: 100, grid: { color: "rgba(229, 231, 235, 0.8)" }, ticks: { color: "#6B7280" } },
          x: { grid: { display: false }, ticks: { color: "#374151", font: { weight: "600" } } }
        },
        plugins: {
          legend: { position: "top", labels: { color: "#374151", boxWidth: 12, font: { size: 11, weight: "600" } } }
        }
      }
    });
  }

  // 3. Attendance vs CGPA Scatter Chart
  const scatterCanvas = document.getElementById("attendanceScatterChart");
  if (scatterCanvas && data.scatter_data) {
    if (STATE.charts.scatter) STATE.charts.scatter.destroy();

    const colorMap = { "High": "#DC2626", "Medium": "#D97706", "Low": "#059669" };

    STATE.charts.scatter = new Chart(scatterCanvas, {
      type: "scatter",
      data: {
        datasets: [{
          label: "Students",
          data: data.scatter_data,
          pointBackgroundColor: data.scatter_data.map(p => colorMap[p.risk] || "#2F80ED"),
          pointBorderColor: "#FFFFFF",
          pointBorderWidth: 1.5,
          pointRadius: 6,
          pointHoverRadius: 9
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          x: {
            title: { display: true, text: "Attendance (%)", color: "#374151", font: { size: 11, weight: "700" } },
            min: 50, max: 100, grid: { color: "rgba(229, 231, 235, 0.8)" }, ticks: { color: "#6B7280" }
          },
          y: {
            title: { display: true, text: "Cumulative GPA", color: "#374151", font: { size: 11, weight: "700" } },
            min: 4, max: 10, grid: { color: "rgba(229, 231, 235, 0.8)" }, ticks: { color: "#6B7280" }
          }
        },
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: {
              label: (ctx) => ` ${ctx.raw.name} (${ctx.raw.id}): CGPA ${ctx.raw.y}, Att: ${ctx.raw.x}%, Risk: ${ctx.raw.risk}`
            }
          }
        }
      }
    });
  }

  // 4. Systemic Risk Bottlenecks Bar Chart
  const systemicCanvas = document.getElementById("systemicRiskBarChart");
  if (systemicCanvas && data.systemic_risk_chart) {
    if (STATE.charts.systemic) STATE.charts.systemic.destroy();

    const sc = data.systemic_risk_chart;
    STATE.charts.systemic = new Chart(systemicCanvas, {
      type: "bar",
      data: {
        labels: sc.labels,
        datasets: [{
          label: "Students Affected",
          data: sc.counts,
          backgroundColor: ["#DC2626", "#2F80ED", "#D97706", "#F59E0B", "#123B66", "#16A6A1", "#0284C7"],
          borderRadius: 6
        }]
      },
      options: {
        indexAxis: "y",
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          x: { beginAtZero: true, grid: { color: "rgba(229, 231, 235, 0.8)" }, ticks: { color: "#6B7280", precision: 0 } },
          y: { grid: { display: false }, ticks: { color: "#374151", font: { size: 11, weight: "600" } } }
        },
        plugins: { legend: { display: false } }
      }
    });
  }
}

// Student Dashboard Radar Chart
function initStudentRadar() {
  const radarCanvas = document.getElementById("studentPillarRadarChart");
  if (!radarCanvas || !window.Chart || !window.STUDENT_METRICS) return;

  const p = window.STUDENT_METRICS.pillars || { academic: 80, attendance: 85, lms: 80, placement: 85, wellbeing: 85 };

  new Chart(radarCanvas, {
    type: "radar",
    data: {
      labels: [
        "Academic Marks (30%)",
        "Attendance (20%)",
        "LMS Learning (15%)",
        "Placement Skills (20%)",
        "Wellbeing (15%)"
      ],
      datasets: [{
        label: "My Evaluated Score",
        data: [p.academic, p.attendance, p.lms, p.placement, p.wellbeing],
        fill: true,
        backgroundColor: "rgba(47, 128, 237, 0.20)",
        borderColor: "#2F80ED",
        pointBackgroundColor: "#123B66",
        pointBorderColor: "#FFFFFF",
        pointHoverBackgroundColor: "#FFFFFF",
        pointHoverBorderColor: "#2F80ED"
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        r: {
          angleLines: { color: "rgba(229, 231, 235, 0.8)" },
          grid: { color: "rgba(229, 231, 235, 0.8)" },
          pointLabels: { color: "#374151", font: { size: 11, weight: "700" } },
          ticks: { backdropColor: "transparent", color: "#6B7280", stepSize: 20 },
          min: 0,
          max: 100
        }
      },
      plugins: {
        legend: { display: false }
      }
    }
  });
}

// ==============================================================================
// 5. STUDENT TABLE RENDERING
// ==============================================================================

function renderStudentTable(students) {
  const tbody = document.getElementById("studentsTableBody");
  if (!tbody) return;

  if (!students || students.length === 0) {
    tbody.innerHTML = `<tr><td colspan="9" style="text-align:center; padding:32px; color:#C4B5FD;">No students found matching current filter criteria.</td></tr>`;
    return;
  }

  tbody.innerHTML = students.map(s => {
    const initials = s.name.split(" ").map(n => n[0]).join("").substring(0, 2).toUpperCase();
    const riskBadgeClass = `badge-${s.risk_badge || s.risk_level.toLowerCase()}`;
    const attWarning = s.attendance_pct < 75 ? "color:#DC2626; font-weight:700;" : "";
    const attBadge = s.attendance_pct < 75 ? `<span class="badge badge-high" style="font-size:0.65rem; padding:1px 5px;">&lt; 75%</span>` : "";
    const studentBacklogSubjs = s.backlog_details && s.backlog_details.length > 0
      ? s.backlog_details.map(b => b.display).join(", ")
      : (s.backlog_subjects || "");
    const backlogHtml = s.backlogs > 0
      ? `<span class="badge badge-high" style="padding:2px 6px;">${s.backlogs} Backlog${s.backlogs > 1 ? 's' : ''}</span>` +
        (studentBacklogSubjs ? `<div style="font-size:0.72rem; color:#DC2626; font-weight:600; margin-top:3px; max-width:200px; word-break:break-word;">${escapeHtml(studentBacklogSubjs)}</div>` : "")
      : `<span class="badge badge-low" style="padding:2px 6px;">None</span>`;

    let scoreColor = "#10B981";
    if (s.success_score < 60) scoreColor = "#F43F5E";
    else if (s.success_score < 75) scoreColor = "#F59E0B";

    return `
      <tr>
        <td>
          <div class="student-cell">
            <div class="student-avatar">${initials}</div>
            <div>
              <span class="student-name">${escapeHtml(s.name)}</span>
              <span class="student-id-code">${s.student_id}</span>
            </div>
          </div>
        </td>
        <td>
          <strong>${s.department}</strong>
          <div class="student-id-code">Sem ${s.semester} &bull; Sec ${s.section}</div>
        </td>
        ${s.mentor_name ? `<td><span class="faculty-advisor-name" style="font-weight:500; color:#000000;">${escapeHtml(s.mentor_name)}</span></td>` : ''}
        <td><strong>${parseFloat(s.cgpa).toFixed(2)}</strong><div class="student-id-code">${s.academic_marks_pct}% marks</div></td>
        <td><div style="${attWarning}">${s.attendance_pct}% ${attBadge}</div></td>
        <td>${backlogHtml}</td>
        <td>
          <div class="progress-cell">
            <strong style="color:${parseFloat(s.success_score) < 70 ? '#DC2626' : '#172B4D'}; font-weight:800;">${s.success_score}</strong>
            <div class="table-progress-bar">
              <div class="table-progress-fill" style="width: ${s.success_score}%; background-color: ${scoreColor};"></div>
            </div>
          </div>
        </td>
        <td><span class="badge ${riskBadgeClass}">${s.risk_level} Risk</span></td>
        <td class="text-right">
          <div style="display:inline-flex; gap:6px;">
            <button class="btn-inspect" onclick="inspectStudent('${s.student_id}')" title="Explainable AI Deep-Dive">
              <span>Analyze</span>
              <svg viewBox="0 0 24 24" width="13" height="13" fill="none" stroke="currentColor" stroke-width="2"><path d="M5 12h14M12 5l7 7-7 7"></path></svg>
            </button>
            <button class="btn-sm-action" style="background:rgba(244,63,94,0.15); border-color:rgba(244,63,94,0.4); color:#FDA4AF;" onclick="deleteStudent('${s.student_id}')" title="Delete Student">
              &times;
            </button>
          </div>
        </td>
      </tr>
    `;
  }).join("");
}

function renderFacultyOverview(students) {
  renderFacultyAnalyticsIndicators(students);
}

function renderFacultyAnalyticsIndicators(students) {
  const container = document.getElementById("facultyAnalyticsIndicatorsRow");
  const emptyState = document.getElementById("facultyAnalyticsEmptyState");
  if (!container) return;

  // 1. Empty state handling
  if (!students || students.length === 0) {
    container.style.display = "none";
    if (emptyState) emptyState.style.display = "block";
    return;
  }

  container.style.display = "grid";
  if (emptyState) emptyState.style.display = "none";

  const total = students.length;

  // =========================================================================
  // Indicator 1: Student Attendance
  // =========================================================================
  const attValidStudents = students.filter(s => s.attendance_pct !== null && s.attendance_pct !== undefined && !isNaN(Number(s.attendance_pct)));
  const attGraphicWrap = document.getElementById("facultyAttGraphicContainer");
  const attUnavailable = document.getElementById("facultyAttUnavailable");
  const attVal = document.getElementById("facultyAttVal");
  const attStatusTag = document.getElementById("facultyAttStatusTag");
  const attCircle = document.getElementById("facultyAttCircleProgress");

  if (attValidStudents.length === 0) {
    if (attGraphicWrap) attGraphicWrap.style.display = "none";
    if (attUnavailable) attUnavailable.style.display = "block";
  } else {
    if (attGraphicWrap) attGraphicWrap.style.display = "flex";
    if (attUnavailable) attUnavailable.style.display = "none";

    const avgAtt = (attValidStudents.reduce((sum, s) => sum + Number(s.attendance_pct), 0) / attValidStudents.length).toFixed(1);
    if (attVal) attVal.textContent = `${avgAtt}%`;

    const isCompliant = Number(avgAtt) >= 75.0;
    if (attStatusTag) {
      attStatusTag.textContent = isCompliant ? "Compliant" : "Shortage (<75%)";
      attStatusTag.style.color = isCompliant ? "#10B981" : "#DC2626";
    }

    if (attCircle) {
      const circumference = 263.89; // 2 * pi * 42
      const clampedPct = Math.min(100, Math.max(0, Number(avgAtt)));
      const offset = (circumference - (circumference * (clampedPct / 100))).toFixed(2);
      attCircle.style.strokeDashoffset = offset;
      attCircle.style.stroke = isCompliant ? "#10B981" : "#DC2626";
    }
  }

  // =========================================================================
  // Indicator 2: Student Backlogs
  // =========================================================================
  const backlogValidStudents = students.filter(s => s.backlogs !== null && s.backlogs !== undefined && !isNaN(Number(s.backlogs)));
  const backlogGraphicWrap = document.getElementById("facultyBacklogGraphicContainer");
  const backlogUnavailable = document.getElementById("facultyBacklogUnavailable");
  const backlogTotalVal = document.getElementById("facultyBacklogTotalVal");
  const backlogCircle = document.getElementById("facultyBacklogCircleProgress");
  const backlogSummaryBadge = document.getElementById("facultyBacklogSummaryBadge");

  if (backlogValidStudents.length === 0) {
    if (backlogGraphicWrap) backlogGraphicWrap.style.display = "none";
    if (backlogUnavailable) backlogUnavailable.style.display = "block";
    if (backlogSummaryBadge) backlogSummaryBadge.style.display = "none";
  } else {
    if (backlogGraphicWrap) backlogGraphicWrap.style.display = "flex";
    if (backlogUnavailable) backlogUnavailable.style.display = "none";
    if (backlogSummaryBadge) backlogSummaryBadge.style.display = "inline-block";

    const totalActiveBacklogs = backlogValidStudents.reduce((sum, s) => sum + Number(s.backlogs), 0);
    const studentsWithBacklogs = backlogValidStudents.filter(s => Number(s.backlogs) > 0).length;
    const backlogStudentPct = ((studentsWithBacklogs / total) * 100).toFixed(1);

    if (backlogTotalVal) backlogTotalVal.textContent = totalActiveBacklogs;

    if (backlogSummaryBadge) {
      backlogSummaryBadge.textContent = `${studentsWithBacklogs} of ${total} students (${backlogStudentPct}%) with active arrears`;
      backlogSummaryBadge.className = studentsWithBacklogs > 0 ? "badge badge-high" : "badge badge-low";
    }

    if (backlogCircle) {
      const circumference = 263.89;
      // Circular progress represents the percentage of assigned students with active backlogs
      const clampedPct = Math.min(100, Math.max(0, Number(backlogStudentPct)));
      const offset = (circumference - (circumference * (clampedPct / 100))).toFixed(2);
      backlogCircle.style.strokeDashoffset = offset;
      backlogCircle.style.stroke = studentsWithBacklogs > 0 ? "#F43F5E" : "#10B981";
    }
  }

  // =========================================================================
  // Indicator 3: Student Academic Risk
  // =========================================================================
  const riskValidStudents = students.filter(s => s.risk_level && ["High", "Medium", "Moderate", "Low"].includes(String(s.risk_level)));
  const riskGraphicWrap = document.getElementById("facultyRiskGraphicContainer");
  const riskUnavailable = document.getElementById("facultyRiskUnavailable");
  const riskLegend = document.getElementById("facultyRiskLegend");
  const lowCountEl = document.getElementById("facultyRiskLowCount");
  const medCountEl = document.getElementById("facultyRiskMedCount");
  const highCountEl = document.getElementById("facultyRiskHighCount");

  if (riskValidStudents.length === 0) {
    if (riskGraphicWrap) riskGraphicWrap.style.display = "none";
    if (riskUnavailable) riskUnavailable.style.display = "block";
    if (riskLegend) riskLegend.style.display = "none";
  } else {
    if (riskGraphicWrap) riskGraphicWrap.style.display = "flex";
    if (riskUnavailable) riskUnavailable.style.display = "none";
    if (riskLegend) riskLegend.style.display = "flex";

    const lowCount = riskValidStudents.filter(s => s.risk_level === "Low").length;
    const medCount = riskValidStudents.filter(s => s.risk_level === "Medium" || s.risk_level === "Moderate").length;
    const highCount = riskValidStudents.filter(s => s.risk_level === "High").length;

    if (lowCountEl) lowCountEl.textContent = lowCount;
    if (medCountEl) medCountEl.textContent = medCount;
    if (highCountEl) highCountEl.textContent = highCount;

    // Render / update Chart.js donut chart
    const canvas = document.getElementById("facultyRiskDoughnutChart");
    if (canvas && typeof Chart !== "undefined") {
      if (STATE.charts && STATE.charts.facultyRisk) {
        STATE.charts.facultyRisk.destroy();
      }
      const ctx = canvas.getContext("2d");
      STATE.charts = STATE.charts || {};
      STATE.charts.facultyRisk = new Chart(ctx, {
        type: "doughnut",
        data: {
          labels: ["Low Risk", "Moderate Risk", "High Risk"],
          datasets: [{
            data: [lowCount, medCount, highCount],
            backgroundColor: ["#10B981", "#F59E0B", "#F43F5E"],
            borderWidth: 2,
            borderColor: "#FFFFFF"
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          cutout: "68%",
          plugins: {
            legend: { display: false },
            tooltip: {
              callbacks: {
                label: function(context) {
                  const count = context.raw || 0;
                  const pct = ((count / total) * 100).toFixed(0);
                  return ` ${context.label}: ${count} (${pct}%)`;
                }
              }
            }
          }
        }
      });
    }
  }
}

function renderRiskWatchlist(students) {
  const adminWatch = document.getElementById("riskWatchlistBody");
  const facWatch = document.getElementById("facultyRiskWatchlistBody");
  const atRisk = (students || []).filter(s => s.risk_level === "High" || s.attendance_pct < 75 || s.backlogs > 0);

  // Store globally for filtering in Admin view
  STATE.atRiskStudents = atRisk;

  // 1. Render Admin Risk Monitoring View: strictly Student Name and Student ID ONLY
  if (adminWatch) {
    renderAdminRiskList(atRisk);
  }

  // 2. Render Faculty Risk Watchlist: preserve previous 7-column layout
  if (facWatch) {
    const facRowsHtml = atRisk.map(s => {
      let driver = "Multi-factor deficit";
      if (s.attendance_pct < 75 && s.backlogs > 0) driver = `Attendance (${s.attendance_pct}%) & ${s.backlogs} Backlogs`;
      else if (s.attendance_pct < 75) driver = `Statutory Attendance Shortage (${s.attendance_pct}%)`;
      else if (s.backlogs > 0) driver = `Arrears (${s.backlogs} Active Backlogs)`;
      else if (s.cgpa < 6.0) driver = `Academic Marks & CGPA (${s.cgpa})`;

      return `
        <tr>
          <td>
            <strong style="color:#000000; font-weight:700;">${escapeHtml(s.name)}</strong>
            <div class="student-id-code">${s.student_id}</div>
          </td>
          <td><span class="badge badge-accent">${s.department}</span></td>
          <td><span style="color:#F43F5E; font-weight:700;">${s.attendance_pct}%</span></td>
          <td><span style="color:#F43F5E; font-weight:700;">${s.backlogs}</span></td>
          <td><strong style="color:${(parseFloat(s.success_score) < 70) ? '#DC2626' : '#000000'};">${s.success_score}</strong>/100</td>
          <td><span style="font-size:0.75rem; color:#DC2626; font-weight:600;">${driver}</span></td>
          <td style="text-align:right;">
            <button class="btn-inspect" onclick="inspectStudent('${s.student_id}')">Intervene &rarr;</button>
          </td>
        </tr>
      `;
    }).join("");
    facWatch.innerHTML = facRowsHtml;
  }
}

// Render clean Admin Risk Monitoring initial list: Student Name and Student ID ONLY
function renderAdminRiskList(studentsList) {
  const adminWatch = document.getElementById("riskWatchlistBody");
  const countBadge = document.getElementById("adminRiskCountBadge");
  if (!adminWatch) return;

  if (countBadge) {
    countBadge.textContent = `${studentsList.length} At-Risk Student${studentsList.length === 1 ? '' : 's'}`;
  }

  if (studentsList.length === 0) {
    adminWatch.innerHTML = `
      <tr>
        <td colspan="3" style="text-align:center; padding:36px; color:#6B7280; font-size:0.875rem;">
          No students currently match the risk-monitoring criteria
        </td>
      </tr>
    `;
    return;
  }

  adminWatch.innerHTML = studentsList.map(s => `
    <tr style="cursor:pointer;" onclick="openAdminRiskDetail('${s.student_id}')">
      <td style="padding:12px 16px;">
        <strong style="color:#111827; font-weight:700; font-size:0.9375rem; cursor:pointer;" onclick="event.stopPropagation(); openAdminRiskDetail('${s.student_id}')">
          ${escapeHtml(s.name)}
        </strong>
      </td>
      <td style="padding:12px 16px;">
        <span class="student-id-code" style="font-size:0.8125rem; font-weight:600; color:#123B66;">
          ${s.student_id}
        </span>
      </td>
      <td style="padding:12px 16px; text-align:right;">
        <button class="btn-inspect" onclick="event.stopPropagation(); openAdminRiskDetail('${s.student_id}')">
          View Risk Profile &rarr;
        </button>
      </td>
    </tr>
  `).join("");
}

// Search filter for Admin Risk Monitoring list
window.filterAdminRiskList = function() {
  const input = document.getElementById("adminRiskSearchInput");
  const query = (input ? input.value : "").trim().toLowerCase();
  const source = STATE.atRiskStudents || [];

  if (!query) {
    renderAdminRiskList(source);
    return;
  }

  const filtered = source.filter(s =>
    (s.name || "").toLowerCase().includes(query) ||
    (s.student_id || "").toLowerCase().includes(query)
  );

  renderAdminRiskList(filtered);
};

// Open detailed risk profile for a selected student
window.openAdminRiskDetail = async function(studentId) {
  const listView = document.getElementById("adminRiskListView");
  const detailView = document.getElementById("adminRiskDetailView");
  if (!detailView) return;

  STATE.currentRiskStudentId = studentId;

  try {
    const res = await fetch(`/api/students/${studentId}`);
    if (!res.ok) {
      alert(`Unable to load risk profile for student ${studentId}.`);
      return;
    }
    const s = await res.json();

    // ── 1. Gender Avatar Icon ──
    const avatarContainer = document.getElementById("riskDetailAvatarContainer");
    if (avatarContainer) {
      const g = (s.gender || "").toLowerCase();
      let gradStyle = "background:linear-gradient(135deg,#123B66,#2F80ED);"; // neutral default
      let genderIcon = "";
      if (g === "male") {
        gradStyle = "background:linear-gradient(135deg,#2563EB,#0EA5E9);";
        genderIcon = '<line x1="16" y1="4" x2="19" y2="2"/><polyline points="16 2 19 2 19 5"/>';
      } else if (g === "female") {
        gradStyle = "background:linear-gradient(135deg,#EC4899,#F43F5E);";
        genderIcon = '<line x1="12" y1="16" x2="12" y2="21"/><line x1="9.5" y1="19" x2="14.5" y2="19"/>';
      }
      avatarContainer.innerHTML = `
        <div class="student-avatar" style="${gradStyle} width:54px; height:54px; border-radius:50%; display:flex; align-items:center; justify-content:center; color:#FFFFFF; flex-shrink:0;">
          <svg viewBox="0 0 24 24" width="28" height="28" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="8" r="4"/>
            <path d="M4 20c0-4 3.58-6.5 8-6.5s8 2.5 8 6.5"/>
            ${genderIcon}
          </svg>
        </div>
      `;
    }

    // ── 2. Student Header Info ──
    const sem = s.semester || 1;
    const year = Math.ceil(sem / 2);
    setTxt("riskDetailName", s.name);
    setTxt("riskDetailID", s.student_id);
    setTxt("riskDetailDept", s.department_name || s.department || "Engineering");
    setTxt("riskDetailSemYear", `Semester ${sem} (Year ${year})`);
    setTxt("riskDetailSection", s.section || "A");
    setTxt("riskDetailMentor", s.mentor_name || "Assigned Faculty Advisor");

    const riskBadge = document.getElementById("riskDetailRiskBadge");
    if (riskBadge) {
      const rLevel = s.risk_level || "Medium";
      riskBadge.className = `badge badge-${s.risk_badge || rLevel.toLowerCase()}`;
      riskBadge.textContent = `${rLevel} Risk`;
    }

    const scoreBadge = document.getElementById("riskDetailScoreBadge");
    if (scoreBadge) {
      scoreBadge.textContent = `Success Score: ${s.success_score != null ? s.success_score : '—'}/100`;
    }

    // ── 3. Circular Attendance Indicator & Subject Breakdown ──
    const attCircle = document.getElementById("riskDetailAttCircle");
    const attPercent = document.getElementById("riskDetailAttPercent");
    const attLabel = document.getElementById("riskDetailAttLabel");
    const attStatusBadge = document.getElementById("riskDetailAttStatusBadge");
    const attExplanation = document.getElementById("riskDetailAttExplanation");
    const subjectAttBody = document.getElementById("riskDetailSubjectAttBody");

    const attPct = s.attendance_pct != null ? parseFloat(s.attendance_pct) : null;
    if (attPct != null) {
      const circumference = 301.59;
      const offset = circumference * (1 - Math.min(100, Math.max(0, attPct)) / 100);
      if (attCircle) {
        attCircle.style.strokeDashoffset = offset;
        attCircle.style.stroke = attPct < 75.0 ? "#DC2626" : "#10B981";
      }
      if (attPercent) attPercent.textContent = `${attPct}%`;
      if (attLabel) attLabel.textContent = `Attendance: ${attPct}%`;

      if (attPct < 75.0) {
        if (attStatusBadge) {
          attStatusBadge.className = "badge badge-high";
          attStatusBadge.textContent = "Below 75% Statutory Minimum";
        }
        if (attExplanation) {
          attExplanation.innerHTML = `<span style="color:#DC2626; font-weight:700;">Attendance Concern:</span> Current attendance of <strong>${attPct}%</strong> is below the statutory 75.0% UGC/Institutional mandate (shortfall of <strong>${(75.0 - attPct).toFixed(1)}%</strong>). The student is at critical risk of semester examination debarment unless immediate statutory counseling is initiated.`;
        }
      } else {
        if (attStatusBadge) {
          attStatusBadge.className = "badge badge-low";
          attStatusBadge.textContent = "Compliant";
        }
        if (attExplanation) {
          attExplanation.innerHTML = `<span style="color:#059669; font-weight:700;">Compliant:</span> Current attendance of <strong>${attPct}%</strong> meets the institutional statutory requirement (&ge; 75%).`;
        }
      }
    } else {
      if (attPercent) attPercent.textContent = "N/A";
      if (attLabel) attLabel.textContent = "Attendance data unavailable";
      if (attStatusBadge) {
        attStatusBadge.className = "badge badge-accent";
        attStatusBadge.textContent = "Unavailable";
      }
      if (attExplanation) {
        attExplanation.textContent = "Attendance data unavailable for this record.";
      }
    }

    // Subject-wise Attendance Table
    const records = s.academic_records || [];
    if (subjectAttBody) {
      if (records.length === 0) {
        subjectAttBody.innerHTML = `<tr><td colspan="4" style="text-align:center; padding:12px; color:#6B7280;">Subject-level attendance records unavailable</td></tr>`;
      } else {
        subjectAttBody.innerHTML = records.map(r => {
          const rAtt = r.attendance_pct != null ? parseFloat(r.attendance_pct) : null;
          const rColor = rAtt != null ? (rAtt < 75.0 ? "#DC2626" : "#10B981") : "#6B7280";
          return `
            <tr>
              <td><strong>${escapeHtml(r.course_code)}</strong> <span style="color:#4B5563;">${escapeHtml(r.course_name)}</span></td>
              <td>Sem ${r.semester}</td>
              <td>${r.classes_attended != null ? r.classes_attended : '—'} / ${r.classes_conducted != null ? r.classes_conducted : '—'}</td>
              <td style="text-align:right;"><strong style="color:${rColor};">${rAtt != null ? rAtt + '%' : '—'}</strong></td>
            </tr>
          `;
        }).join("");
      }
    }

    // ── 4. Backlog Analysis ──
    const backlogBadge = document.getElementById("riskDetailBacklogBadge");
    const backlogSummary = document.getElementById("riskDetailBacklogSummary");
    const backlogBody = document.getElementById("riskDetailBacklogBody");
    const backlogCount = parseInt(s.backlogs || 0, 10);

    if (backlogBadge) {
      backlogBadge.className = backlogCount > 0 ? "badge badge-high" : "badge badge-low";
      backlogBadge.textContent = backlogCount > 0 ? `${backlogCount} Active Backlog${backlogCount > 1 ? 's' : ''}` : "No active backlogs";
    }

    if (backlogCount === 0) {
      if (backlogSummary) {
        backlogSummary.innerHTML = `
          <div style="padding:12px 16px; background:rgba(16, 185, 129, 0.08); border:1px solid rgba(16, 185, 129, 0.25); border-radius:8px; color:#065F46; font-size:0.875rem;">
            <strong>No active backlogs.</strong> All enrolled course credits have been cleared successfully. Academic velocity is on schedule.
          </div>
        `;
      }
      if (backlogBody) {
        backlogBody.innerHTML = `<tr><td colspan="5" style="text-align:center; padding:16px; color:#059669;">No active backlogs recorded in student transcript.</td></tr>`;
      }
    } else {
      if (backlogSummary) {
        backlogSummary.innerHTML = `
          <div style="padding:12px 16px; background:rgba(239, 68, 68, 0.08); border:1px solid rgba(239, 68, 68, 0.25); border-radius:8px; color:#991B1B; font-size:0.8125rem; line-height:1.5;">
            <strong>Credit Progression Concern:</strong> Student has <strong>${backlogCount} active backlog${backlogCount > 1 ? 's' : ''}</strong>. Active backlogs impede academic velocity, delay credit accumulation, and may block advanced prerequisite course registrations. Departmental tutoring and supplementary examination scheduling are required.
          </div>
        `;
      }
      const backlogRecords = records.filter(r => (r.status || "").toLowerCase() === "backlog" || (r.grade || "").toUpperCase() === "F");
      if (backlogBody) {
        if (backlogRecords.length > 0) {
          backlogBody.innerHTML = backlogRecords.map(b => `
            <tr>
              <td>
                <strong style="color:#DC2626;">${escapeHtml(b.course_code)}</strong> &bull; ${escapeHtml(b.course_name)}
              </td>
              <td>Sem ${b.semester}</td>
              <td><span class="badge badge-high">${escapeHtml(b.grade || 'F')}</span></td>
              <td><span style="color:#DC2626; font-weight:700;">Backlog</span></td>
              <td style="text-align:right;">${b.internal_marks != null ? b.internal_marks : '—'} / ${b.external_marks != null ? b.external_marks : '—'}</td>
            </tr>
          `).join("");
        } else {
          backlogBody.innerHTML = `
            <tr>
              <td colspan="5" style="text-align:center; padding:14px; color:#6B7280;">
                Subject details unavailable in current records (${backlogCount} active backlog count registered in student profile).
              </td>
            </tr>
          `;
        }
      }
    }

    // ── 5. Why This Student Is Flagged (Explainable Risk Attribution) ──
    const whyFlaggedBody = document.getElementById("riskDetailWhyFlaggedBody");
    const factorsCount = document.getElementById("riskDetailFactorsCount");
    const riskFactorsList = [];

    // Factor 1: Attendance
    if (attPct != null && attPct < 75.0) {
      riskFactorsList.push({
        factor: "Statutory Attendance Shortage",
        evidence: `Attendance is ${attPct}% (${(75.0 - attPct).toFixed(1)}% below statutory 75.0% threshold)`,
        reason: "Falls below UGC/Institutional 75% minimum mandatory requirement. Student is subject to semester examination debarment.",
        action: "Issue formal statutory attendance advisory and schedule counselor meeting within 48 hours."
      });
    }

    // Factor 2: Backlogs
    if (backlogCount > 0) {
      const bSubjects = records.filter(r => (r.status || "").toLowerCase() === "backlog" || (r.grade || "").toUpperCase() === "F").map(r => r.course_code).join(", ");
      riskFactorsList.push({
        factor: "Active Course Backlogs & Arrears",
        evidence: `${backlogCount} active uncleared subject(s) ${bSubjects ? '(' + bSubjects + ')' : ''}`,
        reason: "Delays credit accumulation velocity and risks extension of normal graduation timeline.",
        action: "Assign departmental senior peer tutor and register student for supplementary examination cycle."
      });
    }

    // Factor 3: CGPA / Academic Performance
    const cgpaVal = parseFloat(s.cgpa || 0);
    if (cgpaVal < 6.5) {
      riskFactorsList.push({
        factor: "Cumulative GPA (CGPA) Deficit",
        evidence: `Current CGPA is ${cgpaVal.toFixed(2)} / 10.00 (${cgpaVal < 5.8 ? 'Below 5.8 High Risk Threshold' : 'Below 6.5 Placement Benchmark'})`,
        reason: "Restricts eligibility for campus placement drives and signals cumulative learning deficit across semesters.",
        action: "Develop subject-specific academic recovery plan prioritizing high-credit core subjects."
      });
    }

    // Factor 4: Internal/Mid Marks
    const lowInternalRecs = records.filter(r => (r.internal_marks != null && r.internal_marks < 20.0) || (r.mid1_marks != null && r.mid1_marks < 10.0));
    if (lowInternalRecs.length > 0) {
      const lowNames = lowInternalRecs.slice(0, 2).map(r => r.course_code).join(", ");
      riskFactorsList.push({
        factor: "Internal / Continuous Assessment Deficit",
        evidence: `Sub-par internal test scores in ${lowNames} (< 50% internal marks)`,
        reason: "Low continuous evaluation marks significantly lower overall semester grade and increase failure probability.",
        action: "Conduct mid-semester doubt-clearing clinics and practical lab revision."
      });
    }

    // Factor 5: LMS / Digital Engagement
    const lmsHours = parseFloat(s.lms_weekly_hours || 0);
    const assignPct = parseFloat(s.assignment_completion_pct || 0);
    if (lmsHours < 5.0 || assignPct < 68.0) {
      riskFactorsList.push({
        factor: "Subdued LMS & Learning Engagement",
        evidence: `${lmsHours} hrs/week LMS time; ${assignPct}% assignment completion rate`,
        reason: "Inconsistent study habits outside lectures indicate learning disengagement or difficulty with coursework.",
        action: "Establish weekly LMS engagement targets and follow up on pending assignment submissions."
      });
    }

    // Factor 6: Placement Gap
    const techScore = parseFloat(s.technical_skills_score || 0);
    const aptScore = parseFloat(s.placement_aptitude_score || 0);
    if ((techScore < 70.0 || aptScore < 65.0) && sem >= 4) {
      riskFactorsList.push({
        factor: "Technical & Aptitude Placement Gap",
        evidence: `Technical: ${techScore}/100, Aptitude: ${aptScore}/100`,
        reason: "Skills gap reduces employability and clearance rate in corporate technical screening rounds.",
        action: "Enroll student in coding mock bootcamps and logical reasoning preparatory tracks."
      });
    }

    if (factorsCount) {
      factorsCount.textContent = `${riskFactorsList.length} Active Driver${riskFactorsList.length === 1 ? '' : 's'}`;
    }

    if (whyFlaggedBody) {
      if (riskFactorsList.length === 0) {
        whyFlaggedBody.innerHTML = `<tr><td colspan="4" style="text-align:center; padding:18px; color:#059669;">No active high-risk factors identified from database records.</td></tr>`;
      } else {
        whyFlaggedBody.innerHTML = riskFactorsList.map(f => `
          <tr>
            <td><strong style="color:#DC2626;">${escapeHtml(f.factor)}</strong></td>
            <td><strong style="color:#111827;">${escapeHtml(f.evidence)}</strong></td>
            <td><span style="color:#4B5563;">${escapeHtml(f.reason)}</span></td>
            <td><span style="color:#123B66; font-weight:600;">${escapeHtml(f.action)}</span></td>
          </tr>
        `).join("");
      }
    }

    // ── 6. CGPA, Marks, and Academic History ──
    const cgpaBadge = document.getElementById("riskDetailCGPABadge");
    if (cgpaBadge) {
      cgpaBadge.textContent = `Current CGPA: ${cgpaVal.toFixed(2)} / 10.00`;
    }

    const sgpaContainer = document.getElementById("riskDetailSgpaContainer");
    if (sgpaContainer) {
      // Group records by semester and extract SGPA
      const semMap = {};
      records.forEach(r => {
        if (r.semester && r.sgpa != null) {
          semMap[r.semester] = r.sgpa;
        }
      });
      const sems = Object.keys(semMap).sort((a,b) => parseInt(a,10) - parseInt(b,10));
      if (sems.length === 0) {
        sgpaContainer.innerHTML = `<span style="font-size:0.8125rem; color:#6B7280;">Semester SGPA progression records unavailable</span>`;
      } else {
        sgpaContainer.innerHTML = sems.map(sm => {
          const sgpaVal = parseFloat(semMap[sm] || 0);
          const sgpaColor = sgpaVal >= 7.5 ? "#059669" : (sgpaVal >= 6.0 ? "#D97706" : "#DC2626");
          return `
            <div style="padding:8px 16px; border-radius:8px; background:rgba(255,255,255,0.9); border:1px solid rgba(209,213,219,0.8); box-shadow:0 1px 2px rgba(0,0,0,0.05);">
              <span style="font-size:0.72rem; color:#6B7280; text-transform:uppercase; font-weight:700; display:block;">Semester ${sm}</span>
              <strong style="font-size:1.05rem; color:${sgpaColor};">${sgpaVal.toFixed(2)} SGPA</strong>
            </div>
          `;
        }).join("");
      }
    }

    const marksBody = document.getElementById("riskDetailAcademicMarksBody");
    if (marksBody) {
      if (records.length === 0) {
        marksBody.innerHTML = `<tr><td colspan="10" style="text-align:center; padding:16px; color:#6B7280;">No course evaluation records stored for this student.</td></tr>`;
      } else {
        marksBody.innerHTML = records.map(r => {
          const isBacklog = (r.status || "").toLowerCase() === "backlog" || (r.grade || "").toUpperCase() === "F";
          return `
            <tr>
              <td>Sem ${r.semester}</td>
              <td><strong style="color:#111827;">${escapeHtml(r.course_code)}</strong> &bull; ${escapeHtml(r.course_name)}</td>
              <td>${r.credits != null ? r.credits : '—'}</td>
              <td>${r.mid1_marks != null ? r.mid1_marks : '—'}</td>
              <td>${r.mid2_marks != null ? r.mid2_marks : '—'}</td>
              <td>${r.internal_marks != null ? r.internal_marks : '—'}</td>
              <td>${r.external_marks != null ? r.external_marks : '—'}</td>
              <td><strong>${r.total_marks != null ? r.total_marks : '—'}</strong></td>
              <td><span class="badge ${isBacklog ? 'badge-high' : 'badge-accent'}">${r.grade || '—'}</span></td>
              <td><span style="color:${isBacklog ? '#DC2626' : '#10B981'}; font-weight:700;">${r.status || (isBacklog ? 'Backlog' : 'Passed')}</span></td>
            </tr>
          `;
        }).join("");
      }
    }

    // ── 7. Multi-Pillar Diagnostics ──
    const compositeScoreEl = document.getElementById("riskDetailCompositeScore");
    if (compositeScoreEl) {
      compositeScoreEl.textContent = `Composite: ${s.success_score != null ? s.success_score : '—'}/100`;
    }

    const pillarsBody = document.getElementById("riskDetailPillarsBody");
    if (pillarsBody && s.pillars) {
      const p = s.pillars;
      const pillarDefs = [
        { label: "Academic Mastery", val: p.academic, max: 100 },
        { label: "Attendance & Discipline", val: p.attendance, max: 100 },
        { label: "LMS & Learning Engagement", val: p.lms, max: 100 },
        { label: "Placement Readiness", val: p.placement, max: 100 },
        { label: "Holistic Wellbeing", val: p.wellbeing, max: 100 }
      ];

      pillarsBody.innerHTML = pillarDefs.map(pd => {
        const pVal = Math.round(pd.val || 0);
        const pColor = pVal >= 75 ? "#10B981" : (pVal >= 60 ? "#F59E0B" : "#EF4444");
        return `
          <div>
            <div style="display:flex; justify-content:space-between; font-size:0.8125rem; margin-bottom:4px;">
              <span style="color:#374151; font-weight:600;">${pd.label}</span>
              <strong style="color:${pColor};">${pVal}/100</strong>
            </div>
            <div style="width:100%; height:6px; background:#E5E7EB; border-radius:3px; overflow:hidden;">
              <div style="width:${Math.min(100, Math.max(0, pVal))}%; height:100%; background:${pColor}; border-radius:3px; transition:width 0.6s ease;"></div>
            </div>
          </div>
        `;
      }).join("");
    }

    // ── 8. Recommended Actions ──
    const recsBody = document.getElementById("riskDetailRecommendationsBody");
    if (recsBody) {
      const recs = s.recommended_interventions || [];
      if (recs.length === 0 && riskFactorsList.length === 0) {
        recsBody.innerHTML = `<div style="padding:12px; color:#059669; font-size:0.875rem;">No immediate remedial interventions required. Academic progress is satisfactory.</div>`;
      } else {
        const actionItems = recs.length > 0 ? recs : riskFactorsList.map(rf => ({
          category: rf.factor,
          urgency: "High",
          action: rf.action,
          timeline: "Within 7 business days",
          rationale: rf.reason
        }));

        recsBody.innerHTML = actionItems.map(item => `
          <div style="padding:10px 14px; background:rgba(255,255,255,0.9); border:1px solid rgba(229,231,235,0.8); border-radius:8px; box-shadow:0 1px 2px rgba(0,0,0,0.03);">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:4px;">
              <strong style="font-size:0.8125rem; color:#111827;">${escapeHtml(item.action || item.title || 'Recommended Advisory')}</strong>
              <span class="badge ${item.urgency === 'Immediate' ? 'badge-high' : 'badge-medium'}" style="font-size:0.7rem;">${item.urgency || 'High'}</span>
            </div>
            <p style="font-size:0.75rem; color:#4B5563; margin:0; line-height:1.4;">${escapeHtml(item.rationale || item.description || '')}</p>
            <div style="font-size:0.7rem; color:#123B66; font-weight:600; margin-top:4px;">Timeline: ${escapeHtml(item.timeline || 'Upcoming evaluation cycle')}</div>
          </div>
        `).join("");
      }
    }

    // ── 9. View Switch ──
    if (listView) listView.style.display = "none";
    detailView.style.display = "block";
    const riskSection = document.getElementById("section-risk-monitoring");
    if (riskSection) riskSection.scrollIntoView({ behavior: "smooth", block: "start" });

  } catch (err) {
    console.error("Error loading risk details:", err);
    alert("Error loading student risk profile. Please try again.");
  }
};

// Return to clean student list
window.closeAdminRiskDetail = function() {
  const listView = document.getElementById("adminRiskListView");
  const detailView = document.getElementById("adminRiskDetailView");
  if (detailView) detailView.style.display = "none";
  if (listView) listView.style.display = "block";
  const riskSection = document.getElementById("section-risk-monitoring");
  if (riskSection) riskSection.scrollIntoView({ behavior: "smooth", block: "start" });
};

// Direct trigger to open intervention assignment for this student
window.openInterventionForRiskStudent = function() {
  const sid = STATE.currentRiskStudentId;
  if (!sid) return;
  // Use existing inspectStudent modal or interventions section
  inspectStudent(sid);
};

// Faculty Risk Alerts Table (5-column schema matching #section-risk-alerts)
function renderRiskAlertsTable(students) {
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
    }
    if (cgpa > 0 && cgpa < 6.0) drivers.push(`Low CGPA (${cgpa})`);
    if (marks > 0 && marks < 50) drivers.push(`Low Marks (${marks}%)`);

    if (drivers.length === 0) {
      drivers.push(s.risk_level ? `${s.risk_level} Risk Trajectory` : "Academic Risk Factor");
    }

    const driverText = drivers.join(" &bull; ");

    return `<tr>
      <td>
        <strong style="color:#000000;">${escapeHtml(s.name)}</strong>
        <div class="student-id-code">${s.student_id} &bull; ${s.department}</div>
      </td>
      <td><span class="badge ${riskClass}">${riskDisplay}</span></td>
      <td><strong style="color:${(parseFloat(s.success_score) < 70) ? '#DC2626' : '#172B4D'};">${s.success_score || '--'}</strong>/100</td>
      <td><span style="font-size:0.75rem; color:#DC2626; font-weight:600;">${driverText}</span></td>
      <td style="text-align:right;"><button class="btn-inspect" onclick="inspectStudent('${s.student_id}')">Intervene &rarr;</button></td>
    </tr>`;
  }).join("");
}

// Faculty Academic Performance Table (6-column schema matching #section-academic-performance)
function renderAcademicPerf(students) {
  const tbody = document.getElementById("academicPerfTableBody");
  if (!tbody) return;

  if (!students || students.length === 0) {
    tbody.innerHTML = `<tr><td colspan="6" style="text-align:center; padding:24px; color:#C4B5FD;">No academic records available.</td></tr>`;
    return;
  }

  // Display all advisees with students having active backlogs sorted prominently to the top
  const sorted = [...students].sort((a, b) => {
    const aBacklogs = parseInt(a.backlogs) || 0;
    const bBacklogs = parseInt(b.backlogs) || 0;
    if (bBacklogs !== aBacklogs) return bBacklogs - aBacklogs;
    return (a.name || "").localeCompare(b.name || "");
  });

  tbody.innerHTML = sorted.map(s => {
    const backlogsCount = parseInt(s.backlogs) || 0;
    const acadBacklogSubjs = s.backlog_details && s.backlog_details.length > 0
      ? s.backlog_details.map(b => b.display).join("; ")
      : (s.backlog_subjects || (backlogsCount + ' active backlog(s)'));
    const backlogHtml = backlogsCount > 0
      ? `<span class="badge badge-high">${backlogsCount} Active</span>
         <div style="font-size:0.75rem; color:#DC2626; font-weight:600; margin-top:4px; max-width:240px; word-break:break-word;">
           ${escapeHtml(acadBacklogSubjs)}
         </div>`
      : `<span class="badge badge-low">None (0)</span>`;

    const riskLower = (s.risk_level || "").toLowerCase();
    const standingClass = riskLower === "high" ? "badge-high" : (riskLower === "medium" ? "badge-medium" : "badge-low");
    const standingText = s.risk_level ? `${s.risk_level} Risk` : (backlogsCount > 0 ? "Backlog Watch" : "Good Standing");
    const marks = parseFloat(s.academic_marks_pct) || 0;
    const cgpa = parseFloat(s.cgpa) || 0;
    const masteryScore = marks > 0 ? Math.round(marks * 0.3 + cgpa * 3.5) : "--";
    const year = s.academic_year || Math.ceil((parseInt(s.semester) || 1) / 2);

    return `<tr>
      <td>
        <strong style="color:#000000;">${escapeHtml(s.name)}</strong>
        <div class="student-id-code">${s.student_id} &bull; ${s.department} &bull; Year ${year}, Sem ${s.semester}</div>
      </td>
      <td><strong>${marks > 0 ? marks + "%" : "--"}</strong></td>
      <td><strong>${cgpa > 0 ? cgpa.toFixed(2) : "--"}</strong></td>
      <td>${backlogHtml}</td>
      <td>${masteryScore !== "--" ? masteryScore + "/100" : "--"}</td>
      <td><span class="badge ${standingClass}">${escapeHtml(standingText)}</span></td>
    </tr>`;
  }).join("");
}

// Faculty Attendance Table (5-column schema matching #section-attendance)
function renderAttendanceTable(students) {
  const tbody = document.getElementById("attendanceTableBody");
  if (!tbody) return;

  if (!students || students.length === 0) {
    tbody.innerHTML = `<tr><td colspan="5" style="text-align:center; padding:24px; color:#C4B5FD;">No attendance data available.</td></tr>`;
    return;
  }

  tbody.innerHTML = students.map(s => {
    const att = parseFloat(s.attendance_pct) || 0;
    const shortfall = att < 75 ? (75 - att).toFixed(1) : 0;
    const debarred = att < 75;
    const attColor = att < 75 ? "#DC2626" : (att < 85 ? "#F59E0B" : "#10B981");
    const debarStatus = debarred
      ? `<span class="badge badge-high">Debarment Risk</span>`
      : `<span class="badge badge-low">Compliant</span>`;

    return `<tr>
      <td><strong style="color:#000000;">${escapeHtml(s.name)}</strong><div class="student-id-code">${s.student_id} &bull; ${s.department}</div></td>
      <td><strong style="color:${attColor};">${att}%</strong></td>
      <td>${debarred ? `<span style="color:#DC2626; font-weight:700;">${shortfall}% below threshold</span>` : `<span style="color:#10B981;">Within limit</span>`}</td>
      <td>${debarStatus}</td>
      <td style="text-align:right;"><button class="btn-inspect" onclick="inspectStudent('${s.student_id}')">Intervene &rarr;</button></td>
    </tr>`;
  }).join("");
}

// ==============================================================================
// 6. STUDENT DEEP-DIVE MODAL & EXPLAINABLE AI
// ==============================================================================

window.inspectStudent = async function(studentId) {
  try {
    const res = await fetch(`/api/students/${studentId}`);
    if (!res.ok) throw new Error("Could not find student profile");
    const s = await res.json();
    STATE.selectedStudentId = s.student_id;

    // Header Identity
    const initials = s.name.split(" ").map(n => n[0]).join("").substring(0, 2).toUpperCase();
    const avatarEl = document.getElementById("modalStudentAvatar");
    if (avatarEl) {
      const gender = (s.gender || "").toLowerCase();
      let gradStyle = "background:linear-gradient(135deg,#123B66,#2F80ED);"; // neutral/default
      let genderIcon = "";
      if (gender === "male") {
        gradStyle = "background:linear-gradient(135deg,#2563EB,#0EA5E9);";
        genderIcon = '<line x1="16" y1="4" x2="19" y2="2"/><polyline points="16 2 19 2 19 5"/>';
      } else if (gender === "female") {
        gradStyle = "background:linear-gradient(135deg,#EC4899,#F43F5E);";
        genderIcon = '<line x1="12" y1="16" x2="12" y2="21"/><line x1="9.5" y1="19" x2="14.5" y2="19"/>';
      }
      avatarEl.style.cssText = (avatarEl.getAttribute("style") || "") + " " + gradStyle;
      avatarEl.innerHTML = `<svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="8" r="4"/><path d="M4 20c0-4 3.58-6.5 8-6.5s8 2.5 8 6.5"/>${genderIcon}</svg>`;
    }
    
    setTxt("modalStudentName", s.name);
    setTxt("modalStudentID", s.student_id);
    setTxt("modalStudentDept", `${s.department_name} • Sem ${s.semester} (Sec ${s.section}) • Advisor: ${s.mentor_name || 'Department Faculty'}`);
    setTxt("modalStudentEmail", `${s.email} • ${s.phone || '+91 9800000000'}`);

    const riskBadge = document.getElementById("modalRiskBadge");
    if (riskBadge) {
      riskBadge.className = `badge badge-${s.risk_badge || s.risk_level.toLowerCase()}`;
      riskBadge.textContent = `${s.risk_level} Risk`;
    }

    // Composite Success Score & Progress
    setTxt("modalSuccessScore", s.success_score);
    const mScoreEl = document.getElementById("modalSuccessScore");
    if (mScoreEl) mScoreEl.style.color = (parseFloat(s.success_score) < 70) ? "#DC2626" : "#FFFFFF";
    const progBar = document.getElementById("modalProgressBar");
    if (progBar) progBar.style.width = `${Math.min(100, Math.max(5, s.success_score))}%`;

    // 5 Pillars
    if (s.pillars) {
      setTxt("pillarAcademicVal", `${s.pillars.academic}/100`);
      setWidth("pillarAcademicBar", `${s.pillars.academic}%`);

      setTxt("pillarAttendanceVal", `${s.pillars.attendance}/100`);
      setWidth("pillarAttendanceBar", `${s.pillars.attendance}%`);

      setTxt("pillarLmsVal", `${s.pillars.lms}/100`);
      setWidth("pillarLmsBar", `${s.pillars.lms}%`);

      setTxt("pillarPlacementVal", `${s.pillars.placement}/100`);
      setWidth("pillarPlacementBar", `${s.pillars.placement}%`);

      setTxt("pillarWellbeingVal", `${s.pillars.wellbeing}/100`);
      setWidth("pillarWellbeingBar", `${s.pillars.wellbeing}%`);
    }

    // Raw Metrics
    setTxt("modalCgpa", parseFloat(s.cgpa).toFixed(2));
    setTxt("modalMarks", `${s.academic_marks_pct}%`);
    setTxt("modalAttendance", `${s.attendance_pct}%`);
    const mAttEl = document.getElementById("modalAttendance");
    if (mAttEl) mAttEl.style.color = (parseFloat(s.attendance_pct) < 75.0) ? "#DC2626" : "#FFFFFF";
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
    }
    setTxt("modalAssignmentRate", `${s.assignment_completion_pct}%`);
    setTxt("modalAptitude", `${s.placement_aptitude_score}/100`);
    setTxt("modalTech", `${s.technical_skills_score}/100`);

    // Explainable Risk Factors
    const riskWrap = document.getElementById("modalRiskFactorsContainer");
    if (riskWrap) {
      if (s.risk_factors && s.risk_factors.length > 0) {
        riskWrap.innerHTML = s.risk_factors.map(rf => `
          <div class="factor-card ${rf.severity}">
            <div class="factor-card-top">
              <span class="factor-title">${escapeHtml(rf.title)}</span>
              <span class="factor-impact">${rf.impact}</span>
            </div>
            <p class="factor-desc">${escapeHtml(rf.description)}</p>
          </div>
        `).join("");
      } else {
        riskWrap.innerHTML = `
          <div class="factor-card success">
            <div class="factor-card-top"><span class="factor-title">No Critical Academic Risks</span><span class="factor-impact">Safe</span></div>
            <p class="factor-desc">Student currently meets or exceeds all institutional thresholds.</p>
          </div>
        `;
      }
    }

    // Standout Strengths
    const strengthWrap = document.getElementById("modalStrengthsContainer");
    if (strengthWrap) {
      if (s.positive_factors && s.positive_factors.length > 0) {
        strengthWrap.innerHTML = s.positive_factors.map(pf => `
          <div class="factor-card success">
            <div class="factor-card-top">
              <span class="factor-title">${escapeHtml(pf.title)}</span>
              <span class="factor-impact">${pf.impact}</span>
            </div>
            <p class="factor-desc">${escapeHtml(pf.description)}</p>
          </div>
        `).join("");
      } else {
        strengthWrap.innerHTML = `
          <div class="factor-card warning">
            <div class="factor-card-top"><span class="factor-title">Growth Potential</span></div>
            <p class="factor-desc">Advised to engage in structured extracurriculars and coding labs.</p>
          </div>
        `;
      }
    }

    // Recommended Interventions
    const intvWrap = document.getElementById("modalInterventionsContainer");
    if (intvWrap) {
      if (s.recommended_interventions && s.recommended_interventions.length > 0) {
        intvWrap.innerHTML = s.recommended_interventions.map(intv => `
          <div class="intervention-card" style="background:rgba(18,59,102,0.7); border:1px solid rgba(47,128,237,0.2); border-radius:10px; padding:12px; margin-bottom:8px; display:flex; justify-content:space-between; align-items:center;">
            <div>
              <div style="font-weight:700; font-size:0.875rem; color:#FFFFFF;">${escapeHtml(intv.action)}</div>
              <div style="font-size:0.75rem; color:#D4E9FF;">${escapeHtml(intv.rationale)}</div>
              <div style="font-size:0.7rem; color:#5B6B82; margin-top:2px;">Category: ${escapeHtml(intv.category)} &bull; Target: ${escapeHtml(intv.timeline)}</div>
            </div>
            <span class="badge ${intv.urgency === 'Immediate' ? 'badge-high' : (intv.urgency === 'High' ? 'badge-medium' : 'badge-low')}">${intv.urgency}</span>
          </div>
        `).join("");
      }
    }

    // Populate Faculty Select dropdown for Admin
    const facSelect = document.getElementById("formFacultySelect");
    if (facSelect) {
      facSelect.innerHTML = `<option value="">-- Select Responsible Faculty --</option>` +
        (STATE.faculty || []).map(f => {
          const isMentor = (s.mentor_name && f.name && s.mentor_name.toLowerCase() === f.name.toLowerCase()) || (s.faculty_id === f.faculty_id || s.faculty_id === f.user_id);
          return `<option value="${f.user_id}" ${isMentor ? 'selected' : ''}>${escapeHtml(f.name)} (${f.department} - ${f.designation})</option>`;
        }).join("");
    }

    // History Timeline
    renderInterventionHistory(s.logged_interventions || []);

    // Display modal
    const modal = document.getElementById("studentDetailModal");
    if (modal) {
      modal.style.display = "flex";
      modal.setAttribute("aria-hidden", "false");
    }
  } catch (err) {
    console.error("Error inspecting student:", err);
    alert("Could not load student profile: " + err.message);
  }
};

function renderInterventionHistory(history) {
  const container = document.getElementById("modalInterventionHistory");
  if (!container) return;

  if (!history || history.length === 0) {
    container.innerHTML = `<p style="font-size:0.75rem; color:#5B6B82; font-style:italic;">No recorded counseling sessions yet for this student.</p>`;
    return;
  }

  container.innerHTML = history.map(item => `
    <div style="background:rgba(18,59,102,0.7); border:1px solid rgba(47,128,237,0.2); border-radius:8px; padding:10px 14px; margin-bottom:8px;">
      <div style="display:flex; justify-content:space-between; font-weight:700; font-size:0.78rem;">
        <span style="color:#FFFFFF;">${escapeHtml(item.title || item.action_type)} &bull; <strong style="color:#2F80ED;">${escapeHtml(item.faculty_name)}</strong></span>
        <span style="font-size:0.7rem; color:#5B6B82;">${item.created_at || 'Recently logged'}</span>
      </div>
      <p style="font-size:0.75rem; color:#D4E9FF; margin-top:4px;">${escapeHtml(item.instructions || item.notes)}</p>
      ${item.action_taken ? `<p style="font-size:0.72rem; color:#10B981; margin-top:2px;"><strong>Action Taken:</strong> ${escapeHtml(item.action_taken)}</p>` : ''}
    </div>
  `).join("");
}

// Delete student
window.deleteStudent = async function(studentId) {
  if (!confirm(`Are you sure you want to remove student ${studentId} from the database?`)) return;

  try {
    const res = await fetch(`/api/students/${studentId}`, { method: "DELETE" });
    const data = await res.json();
    if (res.ok) {
      alert(data.message || "Student removed successfully.");
      await fetchStudents();
    } else {
      alert("Error: " + (data.message || "Failed to delete student."));
    }
  } catch (err) {
    console.error("Error deleting student:", err);
    alert("Server error occurred while deleting student.");
  }
};

// ==============================================================================
// 6B. FACULTY STUDENT SEARCH & PROFILE LOOKUP (Student Profiles Section)
// ==============================================================================

window.searchAndInspectStudent = async function() {
  const input = document.getElementById("profileSearchInput");
  const resultContainer = document.getElementById("quickProfileResult");
  if (!input || !resultContainer) return;

  const query = input.value.trim();
  if (!query) {
    resultContainer.innerHTML = `<p style="color:#C4B5FD; font-size:0.85rem; padding:12px;">Please enter a student name, ID, or roll number.</p>`;
    return;
  }

  resultContainer.innerHTML = `<p style="color:#5B6B82; font-size:0.82rem; padding:12px;">Searching...</p>`;

  try {
    const res = await fetch(`/api/students?search=${encodeURIComponent(query)}`);
    if (!res.ok) throw new Error("Search request failed");
    const data = await res.json();
    const students = data.students || [];

    if (students.length === 0) {
      resultContainer.innerHTML = `
        <div style="padding:20px; text-align:center; background:#FFF5F5; border:1px solid #FCA5A5; border-radius:12px;">
          <svg viewBox="0 0 24 24" width="32" height="32" fill="none" stroke="#F43F5E" stroke-width="2" style="margin-bottom:8px;"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>
          <p style="color:#DC2626; font-weight:700; font-size:0.9rem; margin:0;">No student found for "<strong>${escapeHtml(query)}</strong>"</p>
          <p style="color:#6B7280; font-size:0.78rem; margin-top:6px;">Try a different name, partial name, student ID, or roll number.</p>
        </div>`;
      return;
    }

    if (students.length === 1) {
      // Single exact match – open modal directly
      inspectStudent(students[0].student_id);
      resultContainer.innerHTML = `<p style="color:#10B981; font-size:0.82rem; padding:8px;">✓ Opening profile for <strong>${escapeHtml(students[0].name)}</strong>...</p>`;
      return;
    }

    // Multiple matches – show a result list
    resultContainer.innerHTML = `
      <div style="margin-bottom:10px;">
        <span style="font-size:0.8rem; color:#6B7280; font-weight:600;">${students.length} students found matching "<strong style='color:#2F80ED'>${escapeHtml(query)}</strong>" — click to view profile:</span>
      </div>
      <div style="display:flex; flex-direction:column; gap:8px; max-height:420px; overflow-y:auto;">
        ${students.map(s => {
          const riskColor = s.risk_level === "High" ? "#F43F5E" : (s.risk_level === "Medium" ? "#F59E0B" : "#10B981");
          const initials = s.name.split(" ").map(n => n[0]).join("").substring(0, 2).toUpperCase();
          const attWarning = parseFloat(s.attendance_pct) < 75 ? " ⚠️" : "";
          const backlogBadge = parseInt(s.backlogs) > 0
            ? `<span style="background:#FEE2E2; color:#DC2626; font-size:0.68rem; font-weight:700; padding:2px 6px; border-radius:4px;">${s.backlogs} Backlog${s.backlogs > 1 ? 's' : ''}</span>`
            : `<span style="background:#DCFCE7; color:#16A34A; font-size:0.68rem; font-weight:700; padding:2px 6px; border-radius:4px;">No Backlogs</span>`;
          return `
            <div onclick="inspectStudent('${s.student_id}')" style="display:flex; align-items:center; gap:14px; background:#FFFFFF; border:1px solid #DCE4EE; border-radius:12px; padding:12px 16px; cursor:pointer; transition:all 0.15s;" onmouseover="this.style.borderColor='#2F80ED'; this.style.boxShadow='0 2px 12px rgba(47,128,237,0.15)'" onmouseout="this.style.borderColor='#DCE4EE'; this.style.boxShadow='none'">
              <div style="width:38px; height:38px; border-radius:50%; background:linear-gradient(135deg,#123B66,#2F80ED); display:flex; align-items:center; justify-content:center; color:#FFFFFF; font-weight:800; font-size:0.85rem; flex-shrink:0;">${initials}</div>
              <div style="flex:1; min-width:0;">
                <div style="font-weight:700; color:#172B4D; font-size:0.88rem;">${escapeHtml(s.name)}</div>
                <div style="font-size:0.72rem; color:#6B7280; margin-top:2px;">${s.student_id} &bull; ${s.department} &bull; Sem ${s.semester}</div>
              </div>
              <div style="display:flex; flex-direction:column; align-items:flex-end; gap:4px; flex-shrink:0;">
                <span style="font-size:0.72rem; font-weight:700; color:#374151;">CGPA: <strong>${parseFloat(s.cgpa).toFixed(2)}</strong></span>
                <span style="font-size:0.72rem; color:${riskColor}; font-weight:700;">${s.attendance_pct}% att${attWarning}</span>
                ${backlogBadge}
              </div>
              <div style="color:#2F80ED; flex-shrink:0;">
                <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M5 12h14M12 5l7 7-7 7"></path></svg>
              </div>
            </div>`;
        }).join("")}
      </div>`;
  } catch (err) {
    console.error("Error searching students:", err);
    resultContainer.innerHTML = `<p style="color:#F43F5E; font-size:0.82rem; padding:12px;">Search failed. Please try again.</p>`;
  }
};

// Bind Enter key on profileSearchInput
document.addEventListener("DOMContentLoaded", () => {
  const profileInput = document.getElementById("profileSearchInput");
  if (profileInput) {
    profileInput.addEventListener("keydown", (e) => {
      if (e.key === "Enter") {
        e.preventDefault();
        searchAndInspectStudent();
      }
    });
    // Live search as user types (debounced)
    let profileDebounce;
    profileInput.addEventListener("input", (e) => {
      clearTimeout(profileDebounce);
      const q = e.target.value.trim();
      if (q.length >= 2) {
        profileDebounce = setTimeout(() => searchAndInspectStudent(), 400);
      }
    });
  }

  // Also sync topbar search to student profiles section on faculty dashboard
  const topbarSearch = document.getElementById("topbarSearchInput");
  if (topbarSearch && document.getElementById("section-student-profiles")) {
    topbarSearch.addEventListener("keydown", (e) => {
      if (e.key === "Enter") {
        e.preventDefault();
        const profileInput2 = document.getElementById("profileSearchInput");
        if (profileInput2) {
          profileInput2.value = topbarSearch.value.trim();
          switchSection("section-student-profiles");
          searchAndInspectStudent();
        }
      }
    });
  }
});

// ==============================================================================
// 7. RECORD INTERVENTION ACTION (POST API)
// ==============================================================================

async function handleInterventionSubmit(e) {
  e.preventDefault();
  if (!STATE.selectedStudentId) return;

  const actionInput = document.getElementById("formActionType");
  const actionType = actionInput ? actionInput.value.trim() : "General Academic Counseling";
  const priorityEl = document.getElementById("formPriority");
  const priority = priorityEl ? priorityEl.value : "High";
  
  const facSelect = document.getElementById("formFacultySelect");
  const facultyId = facSelect ? facSelect.value : "";
  const facultyName = facSelect && facSelect.selectedIndex > 0 ? facSelect.options[facSelect.selectedIndex].text.split(" (")[0] : "";

  const dueDateEl = document.getElementById("formDueDate");
  const dueDate = dueDateEl ? dueDateEl.value : "";

  const instructionsEl = document.getElementById("formInstructions");
  const instructions = instructionsEl ? instructionsEl.value.trim() : "";

  const notesEl = document.getElementById("formNotes");
  const notes = (notesEl && notesEl.value.trim()) ? notesEl.value.trim() : (instructions || "Admin intervention assigned.");

  try {
    const res = await fetch(`/api/students/${STATE.selectedStudentId}/intervention`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        title: actionType,
        action_type: actionType,
        priority: priority,
        faculty_id: facultyId,
        faculty_name: facultyName,
        due_date: dueDate,
        instructions: instructions,
        notes: notes
      })
    });

    const data = await res.json();
    if (res.ok) {
      if (instructionsEl) instructionsEl.value = "";
      if (notesEl) notesEl.value = "";
      alert("Intervention assigned successfully and saved!");
      
      // Refresh timeline & interventions table
      const profileRes = await fetch(`/api/students/${STATE.selectedStudentId}`);
      const refreshed = await profileRes.json();
      renderInterventionHistory(refreshed.logged_interventions);
      await fetchInterventions();
    } else {
      alert("Error: " + (data.message || "Failed to record intervention"));
    }
  } catch (err) {
    console.error("Error saving intervention:", err);
    alert("Connection error while logging intervention.");
  }
}

// ==============================================================================
// 8. WHAT-IF SCENARIO SIMULATOR (ADMIN / FACULTY & PERSONAL)
// ==============================================================================

function populateSimulatorDropdown(students) {
  const select = document.getElementById("simStudentSelect");
  if (!select) return;

  const candidates = students.filter(s => s.risk_level === "High" || s.risk_level === "Medium");
  const pool = candidates.length > 0 ? candidates : students;

  select.innerHTML = pool.map(s => `
    <option value="${s.student_id}">${s.name} (${s.student_id}) - ${s.risk_level} Risk (Score: ${s.success_score})</option>
  `).join("");

  if (pool.length > 0) {
    updateSimulatorBaseline(pool[0].student_id);
  }
}

function updateSimulatorBaseline(studentId) {
  const student = STATE.students.find(s => s.student_id === studentId);
  if (!student) return;

  setTxt("simCurrentScore", student.success_score);
  const currentBadge = document.getElementById("simCurrentBadge");
  if (currentBadge) {
    currentBadge.className = `badge badge-${student.risk_badge || student.risk_level.toLowerCase()}`;
    currentBadge.textContent = `${student.risk_level} Risk`;
  }

  runScenarioSimulation();
}

async function runScenarioSimulation() {
  const select = document.getElementById("simStudentSelect");
  if (!select || !select.value) return;

  const studentId = select.value;
  const attBoost = parseFloat(document.getElementById("rangeSimAttendance").value);
  const backBoost = parseInt(document.getElementById("rangeSimBacklogs").value);
  const lmsBoost = parseFloat(document.getElementById("rangeSimLms").value);
  const assignBoost = parseFloat(document.getElementById("rangeSimAssignment").value);

  try {
    const res = await fetch("/api/simulate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        student_id: studentId,
        attendance_boost: attBoost,
        clear_backlogs: backBoost,
        lms_hours_boost: lmsBoost,
        assignment_boost: assignBoost
      })
    });

    const data = await res.json();
    setTxt("simProjectedScore", data.simulated.success_score);
    const badge = document.getElementById("simProjectedBadge");
    if (badge) {
      badge.className = `badge badge-${data.simulated.risk_level.toLowerCase()}`;
      badge.textContent = `${data.simulated.risk_level} Risk`;
    }

    setTxt("simDeltaHighlight", `Success Score Delta: +${data.score_delta} pts`);
    setTxt("simRecommendationText", data.risk_improved
      ? `Simulated remediation successfully transitions student from ${data.original.risk_level} Risk to ${data.simulated.risk_level} Risk!`
      : `Score improves by +${data.score_delta} pts. Further attendance recovery needed to clear statutory warning threshold.`
    );
  } catch (err) {
    console.error("Simulation error:", err);
  }
}

// Personal What-If Simulator for Student Dashboard
function initPersonalSimulator() {
  const btnRun = document.getElementById("btnRunPersonalSim");
  const sData = window.STUDENT_DATA;
  if (!sData) return;

  const rangeAtt = document.getElementById("personalRangeAttendance");
  const rangeBack = document.getElementById("personalRangeBacklogs");
  const rangeLms = document.getElementById("personalRangeLms");
  const rangeAssign = document.getElementById("personalRangeAssignment");

  if (rangeAtt) {
    rangeAtt.addEventListener("input", (e) => {
      setTxt("personalValAttendance", `+${e.target.value}%`);
      calcPersonalSim();
    });
  }
  if (rangeBack) {
    rangeBack.addEventListener("input", (e) => {
      setTxt("personalValBacklogs", `${e.target.value} Cleared`);
      calcPersonalSim();
    });
  }
  if (rangeLms) {
    rangeLms.addEventListener("input", (e) => {
      setTxt("personalValLms", `+${e.target.value} hrs/wk`);
      calcPersonalSim();
    });
  }
  if (rangeAssign) {
    rangeAssign.addEventListener("input", (e) => {
      setTxt("personalValAssignment", `+${e.target.value}%`);
      calcPersonalSim();
    });
  }
  if (btnRun) {
    btnRun.addEventListener("click", calcPersonalSim);
  }

  calcPersonalSim();
}

async function calcPersonalSim() {
  const sData = window.STUDENT_DATA;
  if (!sData) return;

  const attBoost = parseFloat(document.getElementById("personalRangeAttendance")?.value || 0);
  const backBoost = parseInt(document.getElementById("personalRangeBacklogs")?.value || 0);
  const lmsBoost = parseFloat(document.getElementById("personalRangeLms")?.value || 0);
  const assignBoost = parseFloat(document.getElementById("personalRangeAssignment")?.value || 0);

  try {
    const res = await fetch("/api/simulate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        student_id: sData.student_id,
        attendance_boost: attBoost,
        clear_backlogs: backBoost,
        lms_hours_boost: lmsBoost,
        assignment_boost: assignBoost
      })
    });

    if (res.ok) {
      const data = await res.json();
      setTxt("personalProjectedScore", data.simulated.success_score);
      const formattedDelta = String(data.score_delta).startsWith('+') || String(data.score_delta).startsWith('-')
        ? `(${data.score_delta} pts)`
        : `(+${data.score_delta} pts)`;
      setTxt("personalDeltaText", formattedDelta);
      const badge = document.getElementById("personalProjectedBadge");
      if (badge) {
        badge.className = `badge badge-${data.simulated.risk_level.toLowerCase()}`;
        badge.textContent = `${data.simulated.risk_level} Risk`;
      }
    } else {
      setTxt("personalDeltaText", "(Calculation failed)");
    }
  } catch (err) {
    console.error("Error in personal simulator:", err);
  }
}

// ==============================================================================
// 9. EVENT LISTENERS & MODAL CONTROLS
// ==============================================================================

function setupEventListeners() {
  // Global Topbar Search Input
  const topbarSearch = document.getElementById("topbarSearchInput");
  if (topbarSearch) {
    let topbarDebounce;
    topbarSearch.addEventListener("input", (e) => {
      clearTimeout(topbarDebounce);
      topbarDebounce = setTimeout(() => {
        STATE.searchQuery = e.target.value.trim();
        // If searching and not already on student section, switch to it on admin dashboard
        if (document.getElementById("section-students") && !document.getElementById("section-students").classList.contains("active-section")) {
          switchSection("section-students");
        }
        fetchStudents();
      }, 250);
    });

    // Press '/' key to focus topbar search
    document.addEventListener("keydown", (e) => {
      if (e.key === "/" && document.activeElement !== topbarSearch && !["INPUT", "TEXTAREA", "SELECT"].includes(document.activeElement.tagName)) {
        e.preventDefault();
        topbarSearch.focus();
      }
    });
  }

  // Search input (Admin)
  const searchInput = document.getElementById("studentSearchInput");
  if (searchInput) {
    let debounce;
    searchInput.addEventListener("input", (e) => {
      clearTimeout(debounce);
      debounce = setTimeout(() => {
        STATE.searchQuery = e.target.value.trim();
        fetchStudents();
      }, 250);
    });
  }

  // Search input (Faculty)
  const facSearchInput = document.getElementById("facultySearchInput");
  if (facSearchInput) {
    let debounce;
    facSearchInput.addEventListener("input", (e) => {
      clearTimeout(debounce);
      debounce = setTimeout(() => {
        STATE.searchQuery = e.target.value.trim();
        fetchStudents();
      }, 250);
    });
  }

  // Risk Pills (Admin)
  document.querySelectorAll(".pill-filter").forEach(pill => {
    pill.addEventListener("click", () => {
      document.querySelectorAll(".pill-filter").forEach(p => p.classList.remove("active"));
      pill.classList.add("active");
      STATE.activeRisk = pill.getAttribute("data-risk");
      fetchStudents();
    });
  });

  // Risk Pills (Faculty)
  document.querySelectorAll(".pill-filter-item").forEach(pill => {
    pill.addEventListener("click", () => {
      document.querySelectorAll(".pill-filter-item").forEach(p => p.classList.remove("active"));
      pill.classList.add("active");
      STATE.activeRisk = pill.getAttribute("data-risk");
      fetchStudents();
    });
  });

  // Filters (Admin)
  const deptSelect = document.getElementById("rosterDeptFilter");
  if (deptSelect) {
    deptSelect.addEventListener("change", (e) => {
      STATE.activeDept = e.target.value;
      fetchStudents();
    });
  }

  const semSelect = document.getElementById("rosterSemFilter");
  if (semSelect) {
    semSelect.addEventListener("change", (e) => {
      STATE.activeSem = e.target.value;
      fetchStudents();
    });
  }

  const sortSelect = document.getElementById("rosterSortBy");
  if (sortSelect) {
    sortSelect.addEventListener("change", (e) => {
      STATE.sortBy = e.target.value;
      fetchStudents();
    });
  }

  // Close inspection modal
  const btnCloseModal = document.getElementById("btnCloseModal");
  const detailModal = document.getElementById("studentDetailModal");
  if (btnCloseModal && detailModal) {
    btnCloseModal.addEventListener("click", () => { detailModal.style.display = "none"; });
    detailModal.addEventListener("click", (e) => { if (e.target === detailModal) detailModal.style.display = "none"; });
  }

  // Simulator Modal Open/Close (Admin) & Topbar What-If Simulator (Student)
  const btnOpenSim = document.getElementById("btnOpenSimulator");
  const simModal = document.getElementById("simulatorModal");
  const btnCloseSim = document.getElementById("btnCloseSimulator");
  if (btnOpenSim && simModal) {
    btnOpenSim.addEventListener("click", () => { simModal.style.display = "flex"; });
    if (btnCloseSim) btnCloseSim.addEventListener("click", () => { simModal.style.display = "none"; });
    simModal.addEventListener("click", (e) => { if (e.target === simModal) simModal.style.display = "none"; });
  }

  const btnOpenStudentSim = document.getElementById("btnOpenStudentSim");
  if (btnOpenStudentSim) {
    btnOpenStudentSim.addEventListener("click", () => {
      if (typeof window.switchSection === "function") {
        window.switchSection("section-my-success-score");
      }
      const simPanel = document.getElementById("personalRangeAttendance");
      if (simPanel) {
        simPanel.scrollIntoView({ behavior: "smooth", block: "center" });
        simPanel.focus();
      }
    });
  }

  // Simulator slider listeners (Admin)
  const simSelect = document.getElementById("simStudentSelect");
  if (simSelect) {
    simSelect.addEventListener("change", (e) => { updateSimulatorBaseline(e.target.value); });
  }

  const rangeAtt = document.getElementById("rangeSimAttendance");
  if (rangeAtt) {
    rangeAtt.addEventListener("input", (e) => {
      setTxt("valSimAttendance", `+${e.target.value}%`);
    });
  }

  const rangeBack = document.getElementById("rangeSimBacklogs");
  if (rangeBack) {
    rangeBack.addEventListener("input", (e) => {
      setTxt("valSimBacklogs", `${e.target.value} Backlog${e.target.value != 1 ? 's' : ''}`);
    });
  }

  const rangeLms = document.getElementById("rangeSimLms");
  if (rangeLms) {
    rangeLms.addEventListener("input", (e) => {
      setTxt("valSimLms", `+${e.target.value} hrs/wk`);
    });
  }

  const rangeAssign = document.getElementById("rangeSimAssignment");
  if (rangeAssign) {
    rangeAssign.addEventListener("input", (e) => {
      setTxt("valSimAssignment", `+${e.target.value}%`);
    });
  }

  const btnRunSim = document.getElementById("btnRunSimulation");
  if (btnRunSim) {
    btnRunSim.addEventListener("click", runScenarioSimulation);
  }

  // Intervention Form Submit
  const intvForm = document.getElementById("interventionForm");
  if (intvForm) {
    intvForm.addEventListener("submit", handleInterventionSubmit);
  }

  // Notifications Popover Toggle
  const btnNotif = document.getElementById("btnToggleNotifications");
  const notifDropdown = document.getElementById("notificationsDropdown");
  if (btnNotif && notifDropdown) {
    btnNotif.addEventListener("click", (e) => {
      e.stopPropagation();
      notifDropdown.style.display = notifDropdown.style.display === "block" ? "none" : "block";
    });
  }

  // Profile Dropdown Menus (Admin, Faculty, Student)
  const profilePairs = [
    { btnId: "adminProfileChipBtn", menuId: "adminProfileDropdown" },
    { btnId: "facultyProfileChipBtn", menuId: "facultyProfileDropdown" },
    { btnId: "studentProfileChipBtn", menuId: "studentProfileDropdown" }
  ];

  profilePairs.forEach(({ btnId, menuId }) => {
    const chipBtn = document.getElementById(btnId);
    const menuEl = document.getElementById(menuId);
    if (chipBtn && menuEl) {
      chipBtn.addEventListener("click", (e) => {
        e.stopPropagation();
        const isOpen = menuEl.style.display === "block";
        // Close all other dropdowns first
        profilePairs.forEach(p => {
          const m = document.getElementById(p.menuId);
          if (m) m.style.display = "none";
        });
        if (notifDropdown) notifDropdown.style.display = "none";
        menuEl.style.display = isOpen ? "none" : "block";
      });
    }
  });

  // Global click outside to dismiss popovers
  document.addEventListener("click", () => {
    if (notifDropdown) notifDropdown.style.display = "none";
    profilePairs.forEach(p => {
      const m = document.getElementById(p.menuId);
      if (m) m.style.display = "none";
    });
  });

  // Add Student Modal & Form
  const btnOpenAddStudent = document.getElementById("btnOpenAddStudent");
  const addStudentModal = document.getElementById("addStudentModal");
  const btnCloseAddStudent = document.getElementById("btnCloseAddStudent");
  const addStudentForm = document.getElementById("addStudentForm");

  if (btnOpenAddStudent && addStudentModal) {
    btnOpenAddStudent.addEventListener("click", () => { addStudentModal.style.display = "flex"; });
    if (btnCloseAddStudent) btnCloseAddStudent.addEventListener("click", () => { addStudentModal.style.display = "none"; });
    addStudentModal.addEventListener("click", (e) => { if (e.target === addStudentModal) addStudentModal.style.display = "none"; });
  }

  if (addStudentForm) {
    addStudentForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const payload = {
        student_id: document.getElementById("newStudentId").value.trim(),
        name: document.getElementById("newStudentName").value.trim(),
        email: document.getElementById("newStudentEmail").value.trim(),
        department: document.getElementById("newStudentDept").value,
        password: document.getElementById("newStudentPassword")?.value.trim() || "Student@123",
        phone: document.getElementById("newStudentPhone")?.value.trim() || "+91 9800000000",
        semester: parseInt(document.getElementById("newStudentSem").value),
        cgpa: parseFloat(document.getElementById("newStudentCgpa").value),
        attendance_pct: parseFloat(document.getElementById("newStudentAtt").value),
        backlogs: parseInt(document.getElementById("newStudentBack").value),
        placement_aptitude_score: parseFloat(document.getElementById("newStudentApt").value),
        technical_skills_score: parseFloat(document.getElementById("newStudentTech").value)
      };

      try {
        const res = await fetch("/api/students", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload)
        });
        const data = await res.json();
        if (res.ok) {
          alert(`Student ${payload.name} created successfully! User ID: ${payload.student_id}`);
          addStudentModal.style.display = "none";
          addStudentForm.reset();
          await fetchStudents();
        } else {
          alert("Error: " + (data.message || "Failed to create student"));
        }
      } catch (err) {
        console.error("Error creating student:", err);
        alert("Failed to submit student form.");
      }
    });
  }

  // Add Faculty Modal & Form
  const btnOpenAddFaculty = document.getElementById("btnOpenAddFaculty");
  const addFacultyModal = document.getElementById("addFacultyModal");
  const btnCloseAddFaculty = document.getElementById("btnCloseAddFaculty");
  const addFacultyForm = document.getElementById("addFacultyForm");

  if (btnOpenAddFaculty && addFacultyModal) {
    btnOpenAddFaculty.addEventListener("click", () => { addFacultyModal.style.display = "flex"; });
    if (btnCloseAddFaculty) btnCloseAddFaculty.addEventListener("click", () => { addFacultyModal.style.display = "none"; });
    addFacultyModal.addEventListener("click", (e) => { if (e.target === addFacultyModal) addFacultyModal.style.display = "none"; });
  }

  if (addFacultyForm) {
    addFacultyForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const payload = {
        faculty_id: document.getElementById("newFacId").value.trim(),
        name: document.getElementById("newFacName").value.trim(),
        email: document.getElementById("newFacEmail").value.trim(),
        department: document.getElementById("newFacDept").value,
        role: document.getElementById("newFacRole")?.value || "faculty",
        password: document.getElementById("newFacPassword")?.value.trim() || "Faculty@123",
        phone: document.getElementById("newFacPhone")?.value.trim() || "+91 9811223344",
        designation: document.getElementById("newFacDesig").value.trim(),
        specialization: document.getElementById("newFacSpec").value.trim()
      };

      try {
        const res = await fetch("/api/faculty", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload)
        });
        const data = await res.json();
        if (res.ok) {
          alert(`Faculty member ${payload.name} registered successfully!`);
          addFacultyModal.style.display = "none";
          addFacultyForm.reset();
          await fetchFaculty();
        } else {
          alert("Error: " + (data.message || "Failed to create faculty member"));
        }
      } catch (err) {
        console.error("Error creating faculty:", err);
        alert("Failed to register faculty member.");
      }
    });
  }

  // CSV Export
  const btnExport = document.getElementById("btnExportCSV");
  if (btnExport) {
    btnExport.addEventListener("click", exportCohortCSV);
  }

  window.exportCohortCSV = function() {
    window.location.href = `/api/export/csv?department=${STATE.activeDept}&risk_level=${STATE.activeRisk}`;
  };

  window.exportCohortExcel = function() {
    window.location.href = `/api/export/xlsx?department=${STATE.activeDept}&risk_level=${STATE.activeRisk}`;
  };

  window.exportRiskCSV = function(riskLevel) {
    const risk = riskLevel || 'High';
    window.location.href = `/api/export/csv?department=${STATE.activeDept}&risk_level=${risk}`;
  };

  window.exportRiskExcel = function(riskLevel) {
    const risk = riskLevel || 'High';
    window.location.href = `/api/export/xlsx?department=${STATE.activeDept}&risk_level=${risk}`;
  };

  // Faculty Update Intervention Modal & Form
  const modalUpdateIntv = document.getElementById("modalUpdateIntervention");
  const btnCloseUpdateIntv = document.getElementById("btnCloseUpdateIntv");
  const btnCancelUpdateIntv = document.getElementById("btnCancelUpdateIntv");
  const formUpdateIntv = document.getElementById("formUpdateInterventionAction");

  if (modalUpdateIntv) {
    if (btnCloseUpdateIntv) btnCloseUpdateIntv.addEventListener("click", () => { modalUpdateIntv.style.display = "none"; });
    if (btnCancelUpdateIntv) btnCancelUpdateIntv.addEventListener("click", () => { modalUpdateIntv.style.display = "none"; });
    modalUpdateIntv.addEventListener("click", (e) => { if (e.target === modalUpdateIntv) modalUpdateIntv.style.display = "none"; });
  }

  if (formUpdateIntv) {
    formUpdateIntv.addEventListener("submit", async (e) => {
      e.preventDefault();
      const intvId = document.getElementById("editIntvId").value;
      const newStatus = document.getElementById("editIntvStatus").value;
      const actionTaken = document.getElementById("editIntvActionTaken").value.trim();
      const notes = document.getElementById("editIntvNotes").value.trim();

      try {
        const res = await fetch(`/api/interventions/${intvId}`, {
          method: "PUT",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            status: newStatus,
            action_taken: actionTaken,
            implementation_notes: notes
          })
        });

        const data = await res.json();
        if (res.ok) {
          alert(`Intervention updated successfully! Status: ${newStatus}`);
          if (modalUpdateIntv) modalUpdateIntv.style.display = "none";
          await fetchInterventions();
          await fetchNotifications();
        } else {
          alert("Error: " + (data.message || "Failed to update intervention."));
        }
      } catch (err) {
        console.error("Error updating intervention:", err);
        alert("Failed to submit intervention update.");
      }
    });
  }

  // Global Escape Key to dismiss modals
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") {
      if (detailModal) detailModal.style.display = "none";
      if (simModal) simModal.style.display = "none";
      if (addStudentModal) addStudentModal.style.display = "none";
      if (addFacultyModal) addFacultyModal.style.display = "none";
      if (notifDropdown) notifDropdown.style.display = "none";
      if (modalUpdateIntv) modalUpdateIntv.style.display = "none";
    }
  });
}

// ==============================================================================
// NOTIFICATIONS CONTROLLER (PERSISTENT & RED UNREAD INDICATOR)
// ==============================================================================

async function fetchNotifications() {
  const topbarDot = document.getElementById("facultyTopbarNotifDot");
  const sidebarDot = document.getElementById("facultySidebarNotifDot");
  const notifList = document.getElementById("facultyNotificationsList");
  const notifFeed = document.getElementById("facultyNotificationsFeed");
  const countBadge = document.getElementById("facultyNotifCountBadge");

  try {
    const res = await fetch("/api/notifications");
    if (!res.ok) return;
    const data = await res.json();
    const notifications = data.notifications || [];
    const unreadCount = data.unread_count || 0;

    // Red unread dot indicator behavior
    const hasUnread = unreadCount > 0;
    if (topbarDot) topbarDot.style.display = hasUnread ? "block" : "none";
    if (sidebarDot) sidebarDot.style.display = hasUnread ? "inline-block" : "none";
    if (countBadge) {
      countBadge.textContent = hasUnread ? `${unreadCount} Unread Alert${unreadCount > 1 ? 's' : ''}` : "Live Feed";
      countBadge.style.color = hasUnread ? "#DC2626" : "var(--purple-electric)";
    }

    // Render dropdown list
    if (notifList) {
      if (notifications.length === 0) {
        notifList.innerHTML = `<div style="padding:14px; text-align:center; color:var(--text-muted); font-size:0.75rem;">No alerts or notifications recorded.</div>`;
      } else {
        notifList.innerHTML = notifications.map(n => {
          const isUnread = !n.is_read;
          const prio = n.intv_priority || "High";
          const prioColor = (prio === "Immediate" || prio === "Urgent") ? "#DC2626" : (prio === "High" ? "#D97706" : "#059669");

          return `
            <div class="notification-item" style="cursor:pointer; background:${isUnread ? 'rgba(239,68,68,0.06)' : 'transparent'}; border-left:${isUnread ? '3px solid #DC2626' : '3px solid transparent'};" onclick="openNotificationDetail(${n.id}, ${n.intervention_id || 'null'})">
              <div style="display:flex; justify-content:space-between; align-items:center;">
                <strong style="color:${isUnread ? '#000000' : 'var(--text-primary)'}; font-size:0.78rem;">
                  ${isUnread ? '<span style="display:inline-block; width:6px; height:6px; background:#DC2626; border-radius:50%; margin-right:5px;"></span>' : ''}
                  ${escapeHtml(n.title)}
                </strong>
                <span style="font-size:0.68rem; color:${prioColor}; font-weight:700;">${prio}</span>
              </div>
              <span style="color:var(--text-secondary); font-size:0.72rem; line-height:1.35; margin-top:2px;">${escapeHtml(n.message)}</span>
              <div style="display:flex; justify-content:space-between; font-size:0.68rem; color:var(--text-muted); margin-top:4px;">
                <span>${escapeHtml(n.created_at || '')}</span>
                <span style="font-weight:600; color:${isUnread ? '#DC2626' : '#059669'};">${isUnread ? 'Unread (Click to read)' : 'Read'}</span>
              </div>
            </div>
          `;
        }).join("");
      }
    }

    // Render full feed in section-notifications
    if (notifFeed) {
      if (notifications.length === 0) {
        notifFeed.innerHTML = `<div style="padding:20px; text-align:center; color:var(--text-muted); font-size:0.85rem;">No notifications recorded for your caseload.</div>`;
      } else {
        notifFeed.innerHTML = notifications.map(n => {
          const isUnread = !n.is_read;
          const prio = n.intv_priority || "High";
          const prioBadge = (prio === "Immediate" || prio === "Urgent") ? "badge-high" : (prio === "High" ? "badge-medium" : "badge-low");
          const statusBadge = n.intv_status === "Completed" ? "badge-low" : "badge-accent";

          return `
            <div style="background:#FFFFFF; border:1px solid ${isUnread ? '#FCA5A5' : 'var(--border-light)'}; border-left:4px solid ${isUnread ? '#DC2626' : 'var(--purple-deep)'}; border-radius:12px; padding:16px 20px; box-shadow:var(--shadow-xs);">
              <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:8px;">
                <div>
                  <div style="display:flex; align-items:center; gap:8px;">
                    ${isUnread ? '<span style="display:inline-block; width:8px; height:8px; background:#DC2626; border-radius:50%;"></span>' : ''}
                    <h3 style="color:#000000; font-size:0.95rem; font-weight:700; margin:0;">${escapeHtml(n.title)}</h3>
                    <span class="badge ${prioBadge}">${prio}</span>
                    <span class="badge ${statusBadge}">${n.intv_status || 'Assigned'}</span>
                  </div>
                  <div style="font-size:0.75rem; color:var(--text-muted); margin-top:4px;">
                    Assigned: ${escapeHtml(n.created_at || '')} ${n.intv_due_date ? `&bull; <strong style="color:#DC2626;">Due: ${escapeHtml(n.intv_due_date)}</strong>` : ''}
                  </div>
                </div>
                <div>
                  ${isUnread
                    ? `<button class="btn-inspect" onclick="markNotifAsRead(${n.id})">Mark as Read</button>`
                    : `<span style="font-size:0.72rem; color:#059669; font-weight:700;">✓ Read ${escapeHtml(n.read_at || '')}</span>`
                  }
                </div>
              </div>

              <div style="background:#FAF9FE; border:1px solid var(--border-light); border-radius:8px; padding:12px; margin:10px 0;">
                <div style="font-size:0.75rem; color:#4B5563; line-height:1.45;">${escapeHtml(n.message)}</div>
                ${n.intv_instructions ? `<div style="margin-top:6px; font-size:0.75rem; color:#1F2937;"><strong>Admin Instructions:</strong> ${escapeHtml(n.intv_instructions)}</div>` : ''}
              </div>

              ${n.intv_action_taken || n.intv_impl_notes ? `
                <div style="background:rgba(16,185,129,0.06); border:1px solid rgba(16,185,129,0.25); border-radius:8px; padding:10px 14px; margin-top:8px;">
                  <strong style="color:#059669; font-size:0.78rem;">Action Taken:</strong>
                  <span style="font-size:0.78rem; color:#374151;">${escapeHtml(n.intv_action_taken || 'In progress')}</span>
                  ${n.intv_impl_notes ? `<div style="font-size:0.74rem; color:#4B5563; margin-top:4px;">${escapeHtml(n.intv_impl_notes)}</div>` : ''}
                </div>
              ` : ''}

              ${n.intervention_id ? `
                <div style="margin-top:10px; display:flex; justify-content:flex-end;">
                  <button class="btn-action-primary" style="font-size:0.75rem; padding:6px 14px;" onclick="openFacultyUpdateModal(${n.intervention_id}); markNotifAsRead(${n.id});">
                    Update Intervention Action &rarr;
                  </button>
                </div>
              ` : ''}
            </div>
          `;
        }).join("");
      }
    }
  } catch (err) {
    console.error("Error fetching notifications:", err);
  }
}

window.openNotificationDetail = async function(notifId, intvId) {
  // Mark as read in SQLite
  await markNotifAsRead(notifId);

  // If linked to intervention, open update modal
  if (intvId) {
    await fetchInterventions();
    openFacultyUpdateModal(intvId);
  }
};

window.markNotifAsRead = async function(notifId) {
  try {
    const res = await fetch(`/api/notifications/${notifId}/read`, {
      method: "POST"
    });
    if (res.ok) {
      await fetchNotifications();
      await fetchInterventions();
    }
  } catch (err) {
    console.error("Error marking notification read:", err);
  }
};

// Helper utilities
function setTxt(id, val) {
  const el = document.getElementById(id);
  if (el) el.textContent = val;
}

function setWidth(id, val) {
  const el = document.getElementById(id);
  if (el) el.style.width = val;
}

function escapeHtml(str) {
  if (!str) return "";
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}
