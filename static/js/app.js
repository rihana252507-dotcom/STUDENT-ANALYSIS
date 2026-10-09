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
  sortBy: "risk_level-asc",
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

  // If on Faculty dashboard, load faculty advisee caseload & interventions
  if (document.getElementById("facultyOverviewTableBody")) {
    await fetchInterventions();
  }

  // Load student directory / caseload
  if (document.getElementById("studentsTableBody") || document.getElementById("facultyOverviewTableBody")) {
    await fetchStudents();
  }

  // If on Student dashboard, initialize radar chart and personal simulator
  if (document.getElementById("studentPillarRadarChart")) {
    initStudentRadar();
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

  if (kpiTotal) kpiTotal.textContent = total;
  if (kpiSuccess) kpiSuccess.innerHTML = `${avgSuccess}<span class="kpi-sub">/100</span>`;
  if (kpiHigh) kpiHigh.textContent = highRiskCount;
  if (kpiHighPct) kpiHighPct.textContent = `${((highRiskCount / total) * 100).toFixed(1)}%`;
  if (kpiAttRate) kpiAttRate.textContent = `${compliantPct}%`;
  if (kpiAttAvg) kpiAttAvg.textContent = `Avg: ${avgAttendance}%`;
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
          <td>${d.avg_attendance}%</td>
          <td><strong>${d.avg_success_score}</strong>/100</td>
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
              <strong style="color:#FFFFFF; font-size:0.875rem;">${escapeHtml(f.name)}</strong>
              <div class="student-id-code">${escapeHtml(f.email)}</div>
            </div>
          </div>
        </td>
        <td><code>${f.faculty_id}</code></td>
        <td><span class="badge badge-accent">${f.department}</span></td>
        <td>${escapeHtml(f.designation)}</td>
        <td><span style="font-size:0.75rem; color:#DDD6FE;">${escapeHtml(f.specialization || 'Engineering')}</span></td>
        <td><strong>${f.advisee_count || 20}</strong> Students</td>
        <td><span style="font-size:0.75rem; color:#A78BFA;">${escapeHtml(f.phone || '+91 9800000000')}</span></td>
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
  const adminTbody = document.getElementById("interventionsTableBody");
  const facTbody = document.getElementById("facultyInterventionsTableBody");
  if (!adminTbody && !facTbody) return;

  try {
    const res = await fetch("/api/interventions");
    if (!res.ok) return;
    const data = await res.json();
    STATE.interventions = data.interventions || [];

    const rowsHtml = STATE.interventions.map(i => {
      const prioClass = i.priority === "Immediate" ? "badge-high" : (i.priority === "High" ? "badge-medium" : "badge-low");
      const statusClass = i.status === "Completed" ? "badge-low" : (i.status === "Resolved" ? "badge-low" : "badge-accent");

      return `
        <tr>
          <td>#INT-${i.id}</td>
          <td>
            <strong>${escapeHtml(i.student_name || i.student_id)}</strong>
            <div class="student-id-code">${i.student_id} &bull; ${i.student_dept || ''}</div>
          </td>
          <td>${escapeHtml(i.faculty_name)}</td>
          <td><strong>${escapeHtml(i.action_type)}</strong></td>
          <td><span class="badge ${prioClass}">${i.priority}</span></td>
          <td><div style="max-width:280px; font-size:0.75rem; color:#DDD6FE;">${escapeHtml(i.notes)}</div></td>
          <td>
            <select class="cyber-select" style="padding:4px 8px; font-size:0.75rem;" onchange="updateInterventionStatus(${i.id}, this.value)">
              <option value="In Progress" ${i.status === 'In Progress' ? 'selected' : ''}>In Progress</option>
              <option value="Resolved" ${i.status === 'Resolved' ? 'selected' : ''}>Resolved</option>
              <option value="Completed" ${i.status === 'Completed' ? 'selected' : ''}>Completed</option>
            </select>
          </td>
        </tr>
      `;
    }).join("");

    if (adminTbody) adminTbody.innerHTML = rowsHtml;
    if (facTbody) facTbody.innerHTML = rowsHtml;
  } catch (err) {
    console.error("Error fetching interventions:", err);
  }
}

window.updateInterventionStatus = async function(id, newStatus) {
  try {
    const res = await fetch(`/api/interventions/${id}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ status: newStatus })
    });
    if (res.ok) {
      console.log(`Intervention #${id} status updated to ${newStatus}`);
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
            backgroundColor: "#7C3AED",
            borderRadius: 6
          },
          {
            label: "Avg CGPA (x10)",
            data: dc.avg_cgpa.map(c => c * 10),
            backgroundColor: "#EC4899",
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
          pointBackgroundColor: data.scatter_data.map(p => colorMap[p.risk] || "#7C3AED"),
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
          backgroundColor: ["#DC2626", "#EC4899", "#D97706", "#F59E0B", "#7C3AED", "#8B5CF6", "#0284C7"],
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
        backgroundColor: "rgba(236, 72, 153, 0.25)",
        borderColor: "#EC4899",
        pointBackgroundColor: "#A855F7",
        pointBorderColor: "#FFFFFF",
        pointHoverBackgroundColor: "#FFFFFF",
        pointHoverBorderColor: "#EC4899"
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
    const attWarning = s.attendance_pct < 75 ? "color:#F43F5E; font-weight:700;" : "";
    const attBadge = s.attendance_pct < 75 ? `<span class="badge badge-high" style="font-size:0.65rem; padding:1px 5px;">&lt; 75%</span>` : "";
    const backlogHtml = s.backlogs > 0
      ? `<span class="badge badge-high" style="padding:2px 6px;">${s.backlogs} Backlog${s.backlogs > 1 ? 's' : ''}</span>`
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
        ${s.mentor_name ? `<td><span style="font-weight:500; color:#DDD6FE;">${escapeHtml(s.mentor_name)}</span></td>` : ''}
        <td><strong>${parseFloat(s.cgpa).toFixed(2)}</strong><div class="student-id-code">${s.academic_marks_pct}% marks</div></td>
        <td><div style="${attWarning}">${s.attendance_pct}% ${attBadge}</div></td>
        <td>${backlogHtml}</td>
        <td>
          <div class="progress-cell">
            <strong>${s.success_score}</strong>
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
  const tbody = document.getElementById("facultyOverviewTableBody");
  if (!tbody) return;

  tbody.innerHTML = (students.slice(0, 8) || []).map(s => {
    const initials = s.name.split(" ").map(n => n[0]).join("").substring(0, 2).toUpperCase();
    const riskBadgeClass = `badge-${s.risk_badge || s.risk_level.toLowerCase()}`;
    const attWarning = s.attendance_pct < 75 ? "color:#F43F5E; font-weight:700;" : "";

    return `
      <tr>
        <td>
          <div class="student-cell">
            <div class="student-avatar">${initials}</div>
            <div>
              <span class="student-name">${escapeHtml(s.name)}</span>
              <span class="student-id-code">${s.student_id} &bull; ${s.department}</span>
            </div>
          </div>
        </td>
        <td>Sem ${s.semester}</td>
        <td><strong>${parseFloat(s.cgpa).toFixed(2)}</strong></td>
        <td><span style="${attWarning}">${s.attendance_pct}%</span></td>
        <td>${s.backlogs > 0 ? `<span style="color:#F43F5E; font-weight:700;">${s.backlogs}</span>` : '0'}</td>
        <td><strong>${s.success_score}</strong>/100</td>
        <td><span class="badge ${riskBadgeClass}">${s.risk_level}</span></td>
        <td style="text-align:right;">
          <button class="btn-inspect" onclick="inspectStudent('${s.student_id}')">
            <span>Intervene</span>
          </button>
        </td>
      </tr>
    `;
  }).join("");
}

function renderRiskWatchlist(students) {
  const adminWatch = document.getElementById("riskWatchlistBody");
  const facWatch = document.getElementById("facultyRiskWatchlistBody");
  const atRisk = (students || []).filter(s => s.risk_level === "High" || s.attendance_pct < 75 || s.backlogs > 0);

  const rowsHtml = atRisk.map(s => {
    let driver = "Multi-factor deficit";
    if (s.attendance_pct < 75 && s.backlogs > 0) driver = `Attendance (${s.attendance_pct}%) & ${s.backlogs} Backlogs`;
    else if (s.attendance_pct < 75) driver = `Statutory Attendance Shortage (${s.attendance_pct}%)`;
    else if (s.backlogs > 0) driver = `Arrears (${s.backlogs} Active Backlogs)`;
    else if (s.cgpa < 6.0) driver = `Academic Marks & CGPA (${s.cgpa})`;

    return `
      <tr>
        <td>
          <strong style="color:#FFFFFF;">${escapeHtml(s.name)}</strong>
          <div class="student-id-code">${s.student_id}</div>
        </td>
        <td><span class="badge badge-accent">${s.department}</span></td>
        <td><span style="color:#F43F5E; font-weight:700;">${s.attendance_pct}%</span></td>
        <td><span style="color:#F43F5E; font-weight:700;">${s.backlogs}</span></td>
        <td><strong>${s.success_score}</strong>/100</td>
        <td><span style="font-size:0.75rem; color:#FCA5A5;">${driver}</span></td>
        <td style="text-align:right;">
          <button class="btn-inspect" onclick="inspectStudent('${s.student_id}')">Intervene &rarr;</button>
        </td>
      </tr>
    `;
  }).join("");

  if (adminWatch) adminWatch.innerHTML = rowsHtml;
  if (facWatch) facWatch.innerHTML = rowsHtml;
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
    if (avatarEl) avatarEl.textContent = initials;
    
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
    setTxt("modalBacklogs", s.backlogs);
    setTxt("modalLmsHours", `${s.lms_weekly_hours} hrs/wk`);
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
          <div class="intervention-card" style="background:rgba(30,15,60,0.7); border:1px solid rgba(196,181,253,0.2); border-radius:10px; padding:12px; margin-bottom:8px; display:flex; justify-content:space-between; align-items:center;">
            <div>
              <div style="font-weight:700; font-size:0.875rem; color:#FFFFFF;">${escapeHtml(intv.action)}</div>
              <div style="font-size:0.75rem; color:#DDD6FE;">${escapeHtml(intv.rationale)}</div>
              <div style="font-size:0.7rem; color:#A78BFA; margin-top:2px;">Category: ${escapeHtml(intv.category)} &bull; Target: ${escapeHtml(intv.timeline)}</div>
            </div>
            <span class="badge ${intv.urgency === 'Immediate' ? 'badge-high' : (intv.urgency === 'High' ? 'badge-medium' : 'badge-low')}">${intv.urgency}</span>
          </div>
        `).join("");
      }
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
    container.innerHTML = `<p style="font-size:0.75rem; color:#A78BFA; font-style:italic;">No recorded counseling sessions yet for this student.</p>`;
    return;
  }

  container.innerHTML = history.map(item => `
    <div style="background:rgba(30,15,60,0.7); border:1px solid rgba(196,181,253,0.2); border-radius:8px; padding:10px 14px; margin-bottom:8px;">
      <div style="display:flex; justify-content:space-between; font-weight:700; font-size:0.78rem;">
        <span style="color:#FFFFFF;">${escapeHtml(item.action_type)} &bull; <strong style="color:#EC4899;">${escapeHtml(item.faculty_name)}</strong></span>
        <span style="font-size:0.7rem; color:#A78BFA;">${item.created_at || 'Recently logged'}</span>
      </div>
      <p style="font-size:0.75rem; color:#DDD6FE; margin-top:4px;">${escapeHtml(item.notes)}</p>
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
// 7. RECORD INTERVENTION ACTION (POST API)
// ==============================================================================

async function handleInterventionSubmit(e) {
  e.preventDefault();
  if (!STATE.selectedStudentId) return;

  const actionType = document.getElementById("formActionType").value;
  const priority = document.getElementById("formPriority").value;
  const mentorName = document.getElementById("formMentorName") ? document.getElementById("formMentorName").value : "Faculty Advisor";
  const notes = document.getElementById("formNotes").value;

  try {
    const res = await fetch(`/api/students/${STATE.selectedStudentId}/intervention`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        action_type: actionType,
        priority: priority,
        faculty_name: mentorName,
        notes: notes
      })
    });

    const data = await res.json();
    if (res.ok) {
      document.getElementById("formNotes").value = "";
      alert("Counseling intervention recorded successfully in database!");
      
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
      setTxt("personalDeltaText", `(+${data.score_delta} pts)`);
      const badge = document.getElementById("personalProjectedBadge");
      if (badge) {
        badge.className = `badge badge-${data.simulated.risk_level.toLowerCase()}`;
        badge.textContent = `${data.simulated.risk_level} Risk`;
      }
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

  // Simulator Modal Open/Close
  const btnOpenSim = document.getElementById("btnOpenSimulator") || document.getElementById("btnOpenStudentSim");
  const simModal = document.getElementById("simulatorModal");
  const btnCloseSim = document.getElementById("btnCloseSimulator");
  if (btnOpenSim && simModal) {
    btnOpenSim.addEventListener("click", () => { simModal.style.display = "flex"; });
    if (btnCloseSim) btnCloseSim.addEventListener("click", () => { simModal.style.display = "none"; });
    simModal.addEventListener("click", (e) => { if (e.target === simModal) simModal.style.display = "none"; });
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

  // Global Escape Key to dismiss modals
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") {
      if (detailModal) detailModal.style.display = "none";
      if (simModal) simModal.style.display = "none";
      if (addStudentModal) addStudentModal.style.display = "none";
      if (addFacultyModal) addFacultyModal.style.display = "none";
      if (notifDropdown) notifDropdown.style.display = "none";
    }
  });
}

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
