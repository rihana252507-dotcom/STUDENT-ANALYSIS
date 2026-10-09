/**
 * CampusIQ – AI-Powered Student Analytics and Success Platform
 * Frontend Interactive Controller
 * KPMG in India Hackathon Challenge Prototype
 */

// ==============================================================================
// 1. GLOBAL STATE & CONFIGURATION
// ==============================================================================

const STATE = {
  apiBase: (window.location.port === "5000" || window.location.port === "") 
    ? "" 
    : "http://127.0.0.1:5000",
  currentRole: "faculty",        // 'faculty' | 'admin'
  department: "ALL",
  riskFilter: "ALL",
  semesterFilter: "ALL",
  searchQuery: "",
  sortBy: "risk_level-asc",
  allStudents: [],
  filteredStudents: [],
  charts: {},
  currentSelectedStudentId: null
};

// ==============================================================================
// 2. DOM ELEMENT REFERENCES
// ==============================================================================

const DOM = {
  // Status & Header
  apiStatusText: document.getElementById("apiStatusText"),
  btnFacultyView: document.getElementById("btnFacultyView"),
  btnAdminView: document.getElementById("btnAdminView"),
  globalDeptFilter: document.getElementById("globalDeptFilter"),
  btnOpenSimulator: document.getElementById("btnOpenSimulator"),
  btnExportCSV: document.getElementById("btnExportCSV"),
  
  // Context Banner
  contextRoleTag: document.getElementById("contextRoleTag"),
  contextTitle: document.getElementById("contextTitle"),
  contextSubtitle: document.getElementById("contextSubtitle"),
  
  // KPI Cards
  kpiTotalStudents: document.getElementById("kpiTotalStudents"),
  kpiAvgSuccess: document.getElementById("kpiAvgSuccess"),
  kpiAvgCgpaTag: document.getElementById("kpiAvgCgpaTag"),
  kpiHighRisk: document.getElementById("kpiHighRisk"),
  kpiHighRiskPct: document.getElementById("kpiHighRiskPct"),
  kpiAttendanceRate: document.getElementById("kpiAttendanceRate"),
  kpiAttendanceAvg: document.getElementById("kpiAttendanceAvg"),
  kpiPlacementRate: document.getElementById("kpiPlacementRate"),
  kpiPlacementCount: document.getElementById("kpiPlacementCount"),
  
  // Admin Section
  adminDeptBenchmarkSection: document.getElementById("adminDeptBenchmarkSection"),
  adminDeptTableBody: document.getElementById("adminDeptTableBody"),
  
  // Charts
  riskDoughnutCanvas: document.getElementById("riskDoughnutChart"),
  riskLegendSummary: document.getElementById("riskLegendSummary"),
  departmentBarCanvas: document.getElementById("departmentBarChart"),
  attendanceScatterCanvas: document.getElementById("attendanceScatterChart"),
  systemicRiskBarCanvas: document.getElementById("systemicRiskBarChart"),
  
  // Roster Controls
  studentSearchInput: document.getElementById("studentSearchInput"),
  btnClearSearch: document.getElementById("btnClearSearch"),
  rosterDeptFilter: document.getElementById("rosterDeptFilter"),
  rosterSemFilter: document.getElementById("rosterSemFilter"),
  rosterSortBy: document.getElementById("rosterSortBy"),
  pillFilters: document.querySelectorAll(".pill-filter"),
  countAll: document.getElementById("countAll"),
  countHigh: document.getElementById("countHigh"),
  countMed: document.getElementById("countMed"),
  countLow: document.getElementById("countLow"),
  displayedCount: document.getElementById("displayedCount"),
  totalCohortCount: document.getElementById("totalCohortCount"),
  
  // Table & Empty State
  studentsTableBody: document.getElementById("studentsTableBody"),
  rosterEmptyState: document.getElementById("rosterEmptyState"),
  btnResetFilters: document.getElementById("btnResetFilters"),
  
  // Student Detail Modal
  studentDetailModal: document.getElementById("studentDetailModal"),
  btnCloseModal: document.getElementById("btnCloseModal"),
  modalStudentAvatar: document.getElementById("modalStudentAvatar"),
  modalStudentName: document.getElementById("modalStudentName"),
  modalRiskBadge: document.getElementById("modalRiskBadge"),
  modalStudentID: document.getElementById("modalStudentID"),
  modalStudentDept: document.getElementById("modalStudentDept"),
  modalStudentEmail: document.getElementById("modalStudentEmail"),
  modalSuccessScore: document.getElementById("modalSuccessScore"),
  modalProgressBar: document.getElementById("modalProgressBar"),
  pillarAcademicBar: document.getElementById("pillarAcademicBar"),
  pillarAcademicVal: document.getElementById("pillarAcademicVal"),
  pillarAttendanceBar: document.getElementById("pillarAttendanceBar"),
  pillarAttendanceVal: document.getElementById("pillarAttendanceVal"),
  pillarLmsBar: document.getElementById("pillarLmsBar"),
  pillarLmsVal: document.getElementById("pillarLmsVal"),
  pillarPlacementBar: document.getElementById("pillarPlacementBar"),
  pillarPlacementVal: document.getElementById("pillarPlacementVal"),
  pillarWellbeingBar: document.getElementById("pillarWellbeingBar"),
  pillarWellbeingVal: document.getElementById("pillarWellbeingVal"),
  
  modalCgpa: document.getElementById("modalCgpa"),
  modalMarks: document.getElementById("modalMarks"),
  modalAttendance: document.getElementById("modalAttendance"),
  modalBacklogs: document.getElementById("modalBacklogs"),
  modalLmsHours: document.getElementById("modalLmsHours"),
  modalAssignmentRate: document.getElementById("modalAssignmentRate"),
  modalAptitude: document.getElementById("modalAptitude"),
  modalTech: document.getElementById("modalTech"),
  modalRiskFactorsContainer: document.getElementById("modalRiskFactorsContainer"),
  modalStrengthsContainer: document.getElementById("modalStrengthsContainer"),
  modalInterventionsContainer: document.getElementById("modalInterventionsContainer"),
  
  // Intervention Form & History
  interventionForm: document.getElementById("interventionForm"),
  formActionType: document.getElementById("formActionType"),
  formPriority: document.getElementById("formPriority"),
  formMentorName: document.getElementById("formMentorName"),
  formNotes: document.getElementById("formNotes"),
  formFeedbackMsg: document.getElementById("formFeedbackMsg"),
  modalInterventionHistory: document.getElementById("modalInterventionHistory"),
  
  // Simulator Modal
  simulatorModal: document.getElementById("simulatorModal"),
  btnCloseSimulator: document.getElementById("btnCloseSimulator"),
  simStudentSelect: document.getElementById("simStudentSelect"),
  rangeSimAttendance: document.getElementById("rangeSimAttendance"),
  valSimAttendance: document.getElementById("valSimAttendance"),
  rangeSimBacklogs: document.getElementById("rangeSimBacklogs"),
  valSimBacklogs: document.getElementById("valSimBacklogs"),
  rangeSimLms: document.getElementById("rangeSimLms"),
  valSimLms: document.getElementById("valSimLms"),
  rangeSimAssignment: document.getElementById("rangeSimAssignment"),
  valSimAssignment: document.getElementById("valSimAssignment"),
  btnRunSimulation: document.getElementById("btnRunSimulation"),
  simCurrentScore: document.getElementById("simCurrentScore"),
  simCurrentBadge: document.getElementById("simCurrentBadge"),
  simProjectedScore: document.getElementById("simProjectedScore"),
  simProjectedBadge: document.getElementById("simProjectedBadge"),
  simDeltaHighlight: document.getElementById("simDeltaHighlight"),
  simRecommendationText: document.getElementById("simRecommendationText")
};

// ==============================================================================
// 3. API INITIALIZATION & HEALTH CHECK
// ==============================================================================

async function initPlatform() {
  try {
    const healthRes = await fetch(`${STATE.apiBase}/api/health`);
    if (!healthRes.ok) throw new Error("API unreachable");
    const health = await healthRes.json();
    
    DOM.apiStatusText.textContent = `Backend Live: ${health.records_loaded} Students Monitored`;
    DOM.apiStatusText.parentElement.style.color = "#93C5FD";
  } catch (err) {
    console.warn("Could not reach local Flask backend:", err);
    DOM.apiStatusText.textContent = "Backend Disconnected - Start Flask Server";
    DOM.apiStatusText.parentElement.style.color = "#FCA5A5";
  }

  // Load core datasets
  await Promise.all([
    fetchOverview(),
    fetchCharts(),
    fetchStudents(),
    fetchDepartmentBenchmarks()
  ]);

  setupEventListeners();
}

// ==============================================================================
// 4. API FETCH HANDLERS
// ==============================================================================

async function fetchOverview() {
  try {
    const deptParam = STATE.department !== "ALL" ? `?department=${STATE.department}` : "";
    const res = await fetch(`${STATE.apiBase}/api/overview${deptParam}`);
    const data = await res.json();
    updateKPICards(data);
  } catch (err) {
    console.error("Error fetching overview:", err);
  }
}

function updateKPICards(data) {
  DOM.kpiTotalStudents.textContent = data.total_students || 0;
  DOM.kpiAvgSuccess.innerHTML = `${data.avg_success_score || 0}<span class="kpi-sub">/100</span>`;
  DOM.kpiAvgCgpaTag.textContent = `Avg CGPA: ${data.avg_cgpa || 0}`;
  
  DOM.kpiHighRisk.textContent = data.risk_counts ? data.risk_counts.high : 0;
  DOM.kpiHighRiskPct.textContent = `${data.risk_percentages ? data.risk_percentages.high : 0}% of cohort`;
  
  DOM.kpiAttendanceRate.textContent = `${data.attendance_compliance_rate || 0}%`;
  DOM.kpiAttendanceAvg.textContent = `Avg: ${data.avg_attendance || 0}%`;
  
  DOM.kpiPlacementRate.textContent = `${data.placement_ready_rate || 0}%`;
  DOM.kpiPlacementCount.textContent = `${data.placement_ready_count || 0} students`;

  // Update pill counts
  if (data.risk_counts) {
    DOM.countAll.textContent = data.total_students;
    DOM.countHigh.textContent = data.risk_counts.high;
    DOM.countMed.textContent = data.risk_counts.medium;
    DOM.countLow.textContent = data.risk_counts.low;
  }
}

async function fetchStudents() {
  try {
    const params = new URLSearchParams();
    if (STATE.department !== "ALL") params.append("department", STATE.department);
    if (STATE.riskFilter !== "ALL") params.append("risk_level", STATE.riskFilter);
    if (STATE.semesterFilter !== "ALL") params.append("semester", STATE.semesterFilter);
    if (STATE.searchQuery) params.append("search", STATE.searchQuery);
    
    const [sortField, sortOrder] = STATE.sortBy.split("-");
    params.append("sort_by", sortField);
    params.append("order", sortOrder);

    const res = await fetch(`${STATE.apiBase}/api/students?${params.toString()}`);
    const data = await res.json();
    
    STATE.filteredStudents = data.students || [];
    renderStudentTable(STATE.filteredStudents);
    DOM.displayedCount.textContent = STATE.filteredStudents.length;
    DOM.totalCohortCount.textContent = data.total_dataset || 120;
    
    // Also update simulator select if not populated
    populateSimulatorStudentSelect(STATE.filteredStudents);
  } catch (err) {
    console.error("Error fetching students:", err);
  }
}

async function fetchDepartmentBenchmarks() {
  try {
    const res = await fetch(`${STATE.apiBase}/api/departments`);
    const data = await res.json();
    renderDepartmentBenchmarkTable(data.departments || []);
  } catch (err) {
    console.error("Error fetching department benchmarks:", err);
  }
}

async function fetchCharts() {
  try {
    const deptParam = STATE.department !== "ALL" ? `?department=${STATE.department}` : "";
    const res = await fetch(`${STATE.apiBase}/api/analytics/charts${deptParam}`);
    const data = await res.json();
    renderCharts(data);
  } catch (err) {
    console.error("Error fetching charts:", err);
  }
}

// ==============================================================================
// 5. CHART.JS VISUALIZATIONS
// ==============================================================================

function renderCharts(data) {
  if (!data || !window.Chart) return;

  // Chart 1: Risk Doughnut Chart
  if (data.risk_breakdown) {
    if (STATE.charts.riskDoughnut) STATE.charts.riskDoughnut.destroy();

    const rb = data.risk_breakdown;
    STATE.charts.riskDoughnut = new Chart(DOM.riskDoughnutCanvas, {
      type: "doughnut",
      data: {
        labels: rb.labels,
        datasets: [{
          data: rb.counts,
          backgroundColor: rb.colors,
          borderWidth: 2,
          borderColor: "#FFFFFF",
          hoverOffset: 6
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: {
              label: function(ctx) {
                const count = ctx.raw;
                const pct = rb.percentages[ctx.dataIndex];
                return ` ${ctx.label}: ${count} (${pct}%)`;
              }
            }
          }
        },
        cutout: "68%"
      }
    });

    // Populate legend
    DOM.riskLegendSummary.innerHTML = rb.labels.map((lbl, idx) => `
      <div class="legend-item">
        <span class="legend-color-box" style="background-color: ${rb.colors[idx]}"></span>
        <span>${lbl}: <strong>${rb.counts[idx]}</strong> (${rb.percentages[idx]}%)</span>
      </div>
    `).join("");
  }

  // Chart 2: Department Performance Benchmark
  if (data.department_chart) {
    if (STATE.charts.deptBar) STATE.charts.deptBar.destroy();

    const dc = data.department_chart;
    STATE.charts.deptBar = new Chart(DOM.departmentBarCanvas, {
      type: "bar",
      data: {
        labels: dc.labels,
        datasets: [
          {
            label: "Success Score (0-100)",
            data: dc.avg_success,
            backgroundColor: "#4F46E5",
            borderRadius: 6
          },
          {
            label: "Avg CGPA (Scaled x10)",
            data: dc.avg_cgpa.map(v => v * 10),
            backgroundColor: "#00338D",
            borderRadius: 6
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          y: {
            beginAtZero: true,
            max: 100,
            grid: { color: "#F1F5F9" },
            ticks: { font: { size: 11 } }
          },
          x: {
            grid: { display: false },
            ticks: { font: { size: 11, weight: "bold" } }
          }
        },
        plugins: {
          legend: {
            position: "top",
            labels: { boxWidth: 12, font: { size: 11 } }
          },
          tooltip: {
            callbacks: {
              afterLabel: function(ctx) {
                if (ctx.datasetIndex === 1) {
                  const actualCgpa = (ctx.raw / 10).toFixed(2);
                  return `Actual CGPA: ${actualCgpa} / 10.0`;
                }
              }
            }
          }
        }
      }
    });
  }

  // Chart 3: Attendance vs CGPA Scatter
  if (data.scatter_data) {
    if (STATE.charts.scatter) STATE.charts.scatter.destroy();

    const colorMap = {
      "High": "#EF4444",
      "Medium": "#F59E0B",
      "Low": "#10B981"
    };

    STATE.charts.scatter = new Chart(DOM.attendanceScatterCanvas, {
      type: "scatter",
      data: {
        datasets: [{
          label: "Students",
          data: data.scatter_data,
          pointBackgroundColor: data.scatter_data.map(p => colorMap[p.risk] || "#64748B"),
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
            title: { display: true, text: "Attendance Percentage (%)", font: { size: 11, weight: "600" } },
            min: 50,
            max: 100,
            grid: { color: "#F1F5F9" }
          },
          y: {
            title: { display: true, text: "Cumulative GPA (out of 10.0)", font: { size: 11, weight: "600" } },
            min: 4,
            max: 10,
            grid: { color: "#F1F5F9" }
          }
        },
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: {
              label: function(ctx) {
                const s = ctx.raw;
                return ` ${s.name} (${s.id}) [${s.dept}]: CGPA ${s.y}, Att: ${s.x}%, Risk: ${s.risk}`;
              }
            }
          }
        }
      }
    });
  }

  // Chart 4: Systemic Risk Bottlenecks
  if (data.systemic_risk_chart) {
    if (STATE.charts.systemic) STATE.charts.systemic.destroy();

    const sc = data.systemic_risk_chart;
    STATE.charts.systemic = new Chart(DOM.systemicRiskBarCanvas, {
      type: "bar",
      data: {
        labels: sc.labels,
        datasets: [{
          label: "Students Affected",
          data: sc.counts,
          backgroundColor: [
            "#DC2626",
            "#EF4444",
            "#F59E0B",
            "#FBBF24",
            "#6366F1",
            "#3B82F6",
            "#8B5CF6"
          ],
          borderRadius: 6
        }]
      },
      options: {
        indexAxis: "y",
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          x: {
            beginAtZero: true,
            grid: { color: "#F1F5F9" },
            ticks: { precision: 0 }
          },
          y: {
            grid: { display: false },
            ticks: { font: { size: 11 } }
          }
        },
        plugins: {
          legend: { display: false }
        }
      }
    });
  }
}

// ==============================================================================
// 6. STUDENT ROSTER TABLE RENDERING
// ==============================================================================

function renderStudentTable(students) {
  if (!students || students.length === 0) {
    DOM.studentsTableBody.innerHTML = "";
    DOM.rosterEmptyState.style.display = "block";
    return;
  }

  DOM.rosterEmptyState.style.display = "none";
  
  const rows = students.map(s => {
    // Initials for avatar
    const initials = s.name.split(" ").map(n => n[0]).join("").substring(0, 2).toUpperCase();
    
    // Risk Badge Class
    const riskBadgeClass = `badge-${s.risk_badge || s.risk_level.toLowerCase()}`;
    
    // Attendance warning styling
    const attWarning = s.attendance_pct < 75 ? "text-danger fw-bold" : "";
    const attBadge = s.attendance_pct < 75 
      ? `<span class="badge badge-high" style="font-size:0.65rem; padding:1px 5px;">&lt; 75%</span>` 
      : "";
      
    // Backlog badge
    const backlogHtml = s.backlogs > 0 
      ? `<span class="badge-backlog">${s.backlogs} Backlog${s.backlogs > 1 ? 's' : ''}</span>`
      : `<span class="badge-clear">None</span>`;

    // Progress bar color based on score
    let scoreColor = "#10B981";
    if (s.success_score < 60) scoreColor = "#EF4444";
    else if (s.success_score < 75) scoreColor = "#F59E0B";

    return `
      <tr data-student-id="${s.student_id}">
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
        <td>
          <span style="font-weight: 500;">${escapeHtml(s.mentor)}</span>
        </td>
        <td>
          <strong>${s.cgpa.toFixed(2)}</strong>
          <div class="student-id-code">${s.academic_marks_pct}% marks</div>
        </td>
        <td>
          <div class="${attWarning}">${s.attendance_pct}% ${attBadge}</div>
        </td>
        <td>
          ${backlogHtml}
        </td>
        <td>
          <div class="progress-cell">
            <strong>${s.success_score}</strong>
            <div class="table-progress-bar">
              <div class="table-progress-fill" style="width: ${s.success_score}%; background-color: ${scoreColor};"></div>
            </div>
          </div>
        </td>
        <td>
          <span class="badge ${riskBadgeClass}">${s.risk_level} Risk</span>
        </td>
        <td class="text-right">
          <button class="btn-inspect" onclick="inspectStudent('${s.student_id}')">
            <span>Analyze</span>
            <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2"><path d="M5 12h14M12 5l7 7-7 7"></path></svg>
          </button>
        </td>
      </tr>
    `;
  }).join("");

  DOM.studentsTableBody.innerHTML = rows;
}

// ==============================================================================
// 7. ADMIN DEPARTMENT BENCHMARK TABLE
// ==============================================================================

function renderDepartmentBenchmarkTable(departments) {
  if (!departments || departments.length === 0) return;

  const rows = departments.map(d => {
    const auditStatusBadge = d.high_risk_pct > 25 
      ? `<span class="badge badge-high">Audit Flagged</span>` 
      : (d.high_risk_pct > 15 ? `<span class="badge badge-medium">Review Needed</span>` : `<span class="badge badge-low">Accredited</span>`);

    return `
      <tr>
        <td>
          <strong>${d.department}</strong>
          <div class="student-id-code">${d.department_name}</div>
        </td>
        <td><strong>${d.total_students}</strong></td>
        <td><span class="danger-text fw-bold">${d.high_risk_count}</span> (${d.high_risk_pct}%)</td>
        <td>${d.medium_risk_count}</td>
        <td><span class="success-text fw-bold">${d.low_risk_count}</span></td>
        <td><strong>${d.avg_cgpa}</strong></td>
        <td>${d.avg_attendance}%</td>
        <td><strong>${d.avg_success_score}</strong>/100</td>
        <td>${d.placement_ready_rate}%</td>
        <td>${auditStatusBadge}</td>
      </tr>
    `;
  }).join("");

  DOM.adminDeptTableBody.innerHTML = rows;
}

// ==============================================================================
// 8. STUDENT DEEP-DIVE MODAL & EXPLAINABLE AI HUB
// ==============================================================================

window.inspectStudent = async function(studentId) {
  try {
    const res = await fetch(`${STATE.apiBase}/api/students/${studentId}`);
    if (!res.ok) throw new Error("Student not found");
    const s = await res.json();
    STATE.currentSelectedStudentId = s.student_id;

    // Header Info
    const initials = s.name.split(" ").map(n => n[0]).join("").substring(0, 2).toUpperCase();
    DOM.modalStudentAvatar.textContent = initials;
    DOM.modalStudentName.textContent = s.name;
    DOM.modalStudentID.textContent = s.student_id;
    DOM.modalStudentDept.textContent = `${s.department_name} • Sem ${s.semester} (Sec ${s.section}) • Mentor: ${s.mentor}`;
    DOM.modalStudentEmail.textContent = `${s.email} • ${s.phone}`;
    
    // Risk Badge
    DOM.modalRiskBadge.className = `badge badge-${s.risk_badge || s.risk_level.toLowerCase()}`;
    DOM.modalRiskBadge.textContent = `${s.risk_level} Risk`;

    // Composite Success Score
    DOM.modalSuccessScore.textContent = s.success_score;
    DOM.modalProgressBar.style.width = `${Math.min(100, Math.max(5, s.success_score))}%`;
    
    // 5 Pillars
    DOM.pillarAcademicVal.textContent = `${s.pillars.academic}/100`;
    DOM.pillarAcademicBar.style.width = `${s.pillars.academic}%`;

    DOM.pillarAttendanceVal.textContent = `${s.pillars.attendance}/100`;
    DOM.pillarAttendanceBar.style.width = `${s.pillars.attendance}%`;

    DOM.pillarLmsVal.textContent = `${s.pillars.lms}/100`;
    DOM.pillarLmsBar.style.width = `${s.pillars.lms}%`;

    DOM.pillarPlacementVal.textContent = `${s.pillars.placement}/100`;
    DOM.pillarPlacementBar.style.width = `${s.pillars.placement}%`;

    DOM.pillarWellbeingVal.textContent = `${s.pillars.wellbeing}/100`;
    DOM.pillarWellbeingBar.style.width = `${s.pillars.wellbeing}%`;

    // Raw Metrics Strip
    DOM.modalCgpa.textContent = s.cgpa.toFixed(2);
    DOM.modalMarks.textContent = `${s.academic_marks_pct}%`;
    DOM.modalAttendance.textContent = `${s.attendance_pct}%`;
    DOM.modalBacklogs.textContent = s.backlogs;
    DOM.modalLmsHours.textContent = `${s.lms_weekly_hours} hrs/wk`;
    DOM.modalAssignmentRate.textContent = `${s.assignment_completion_pct}%`;
    DOM.modalAptitude.textContent = `${s.placement_aptitude_score}/100`;
    DOM.modalTech.textContent = `${s.technical_skills_score}/100`;

    // Populate Explainable Risk Factors
    if (s.risk_factors && s.risk_factors.length > 0) {
      DOM.modalRiskFactorsContainer.innerHTML = s.risk_factors.map(rf => `
        <div class="factor-card ${rf.severity}">
          <div class="factor-card-top">
            <span class="factor-title">${escapeHtml(rf.title)}</span>
            <span class="factor-impact">${rf.impact}</span>
          </div>
          <p class="factor-desc">${escapeHtml(rf.description)}</p>
        </div>
      `).join("");
    } else {
      DOM.modalRiskFactorsContainer.innerHTML = `
        <div class="factor-card success">
          <div class="factor-card-top">
            <span class="factor-title">No Critical Academic Risks Detected</span>
            <span class="factor-impact">Safe</span>
          </div>
          <p class="factor-desc">Student currently meets or exceeds all academic thresholds.</p>
        </div>
      `;
    }

    // Populate Strengths & Growth Areas
    if (s.positive_factors && s.positive_factors.length > 0) {
      DOM.modalStrengthsContainer.innerHTML = s.positive_factors.map(pf => `
        <div class="factor-card success">
          <div class="factor-card-top">
            <span class="factor-title">${escapeHtml(pf.title)}</span>
            <span class="factor-impact">${pf.impact}</span>
          </div>
          <p class="factor-desc">${escapeHtml(pf.description)}</p>
        </div>
      `).join("");
    } else {
      DOM.modalStrengthsContainer.innerHTML = `
        <div class="factor-card warning">
          <div class="factor-card-top">
            <span class="factor-title">Growth Potential</span>
          </div>
          <p class="factor-desc">Needs focused structured mentorship across multiple competencies.</p>
        </div>
      `;
    }

    // Populate Recommended Interventions
    if (s.recommended_interventions && s.recommended_interventions.length > 0) {
      DOM.modalInterventionsContainer.innerHTML = s.recommended_interventions.map(intv => `
        <div class="intervention-card">
          <div class="intervention-details">
            <div class="intervention-action-title">${escapeHtml(intv.action)}</div>
            <div class="intervention-rationale">${escapeHtml(intv.rationale)}</div>
            <div class="intervention-meta">
              <span class="chip-dept">${escapeHtml(intv.category)}</span>
              <span>&bull; Target: <strong>${escapeHtml(intv.timeline)}</strong></span>
            </div>
          </div>
          <span class="urgency-badge ${intv.urgency}">${intv.urgency} Action</span>
        </div>
      `).join("");
    }

    // Populate Logged Interventions History
    renderInterventionHistory(s.logged_interventions || []);

    // Set default mentor name in form
    DOM.formMentorName.value = s.mentor;
    DOM.formNotes.value = "";
    DOM.formFeedbackMsg.style.display = "none";

    // Show modal
    DOM.studentDetailModal.style.display = "flex";
    DOM.studentDetailModal.setAttribute("aria-hidden", "false");
  } catch (err) {
    console.error("Error opening student detail:", err);
    alert("Could not load student profile. Please make sure the Flask backend is running.");
  }
};

function renderInterventionHistory(history) {
  if (!history || history.length === 0) {
    DOM.modalInterventionHistory.innerHTML = `
      <p style="font-size: 0.75rem; color: #94A3B8; font-style: italic;">No faculty actions logged yet for this academic period.</p>
    `;
    return;
  }

  DOM.modalInterventionHistory.innerHTML = history.map(item => `
    <div class="history-item">
      <div class="history-item-top">
        <span>${escapeHtml(item.action_type)} &bull; <strong style="color:#005EB8;">${escapeHtml(item.mentor_name)}</strong></span>
        <span class="history-item-time">${item.timestamp}</span>
      </div>
      <p style="color: #475569; margin-top: 4px;">${escapeHtml(item.notes)}</p>
    </div>
  `).join("");
}

// ==============================================================================
// 9. LOG FACULTY INTERVENTION (POST API)
// ==============================================================================

async function handleInterventionSubmit(e) {
  e.preventDefault();
  if (!STATE.currentSelectedStudentId) return;

  const payload = {
    action_type: DOM.formActionType.value,
    priority: DOM.formPriority.value,
    mentor_name: DOM.formMentorName.value,
    notes: DOM.formNotes.value
  };

  try {
    const res = await fetch(`${STATE.apiBase}/api/students/${STATE.currentSelectedStudentId}/intervention`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    const data = await res.json();
    if (res.ok) {
      DOM.formFeedbackMsg.textContent = "Intervention recorded successfully!";
      DOM.formFeedbackMsg.style.display = "inline";
      DOM.formNotes.value = "";

      // Re-fetch student detail to update history list live
      const detailRes = await fetch(`${STATE.apiBase}/api/students/${STATE.currentSelectedStudentId}`);
      const refreshed = await detailRes.json();
      renderInterventionHistory(refreshed.logged_interventions);

      setTimeout(() => {
        DOM.formFeedbackMsg.style.display = "none";
      }, 4000);
    } else {
      alert("Failed to record intervention: " + (data.error || "Unknown error"));
    }
  } catch (err) {
    console.error("Error logging intervention:", err);
    alert("Connection error logging intervention.");
  }
}

// ==============================================================================
// 10. WHAT-IF SCENARIO SIMULATOR
// ==============================================================================

function populateSimulatorStudentSelect(students) {
  // Populate simulator select with at-risk students for impactful demonstration
  const candidates = students.filter(s => s.risk_level === "High" || s.risk_level === "Medium");
  const pool = candidates.length > 0 ? candidates : students;

  DOM.simStudentSelect.innerHTML = pool.map(s => `
    <option value="${s.student_id}">${s.name} (${s.student_id}) - ${s.risk_level} Risk (Score: ${s.success_score})</option>
  `).join("");

  if (pool.length > 0) {
    updateSimulatorBaseline(pool[0].student_id);
  }
}

function updateSimulatorBaseline(studentId) {
  const student = STATE.filteredStudents.find(s => s.student_id === studentId);
  if (!student) return;

  DOM.simCurrentScore.textContent = student.success_score;
  DOM.simCurrentBadge.className = `badge badge-${student.risk_badge || student.risk_level.toLowerCase()}`;
  DOM.simCurrentBadge.textContent = `${student.risk_level} Risk`;

  // Run initial simulation
  runScenarioSimulation();
}

async function runScenarioSimulation() {
  const studentId = DOM.simStudentSelect.value;
  if (!studentId) return;

  const payload = {
    student_id: studentId,
    attendance_boost: parseFloat(DOM.rangeSimAttendance.value),
    clear_backlogs: parseInt(DOM.rangeSimBacklogs.value),
    lms_hours_boost: parseFloat(DOM.rangeSimLms.value),
    assignment_boost: parseFloat(DOM.rangeSimAssignment.value)
  };

  try {
    const res = await fetch(`${STATE.apiBase}/api/simulate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    const result = await res.json();

    DOM.simProjectedScore.textContent = result.simulated.success_score;
    DOM.simProjectedBadge.className = `badge badge-${result.simulated.risk_level.toLowerCase()}`;
    DOM.simProjectedBadge.textContent = `${result.simulated.risk_level} Risk`;

    DOM.simDeltaHighlight.textContent = `Success Score Delta: ${result.score_delta} pts`;

    if (result.risk_improved) {
      DOM.simRecommendationText.textContent = `Intervention projection successful: Student transitions from ${result.original.risk_level} Risk to ${result.simulated.risk_level} Risk!`;
    } else {
      DOM.simRecommendationText.textContent = `Score improved by ${result.score_delta} pts. Further attendance or backlog remediation required to clear warning thresholds.`;
    }
  } catch (err) {
    console.error("Simulation error:", err);
  }
}

// ==============================================================================
// 11. EXPORT TO CSV HANDLER
// ==============================================================================

function exportRosterToCSV() {
  const students = STATE.filteredStudents;
  if (!students || students.length === 0) {
    alert("No students to export.");
    return;
  }

  const headers = [
    "Student ID", "Name", "Email", "Department", "Semester", "Section", "Mentor",
    "CGPA", "Academic Marks %", "Attendance %", "Backlogs",
    "LMS Weekly Hours", "LMS Engagement", "Assignment Completion %",
    "Placement Aptitude", "Technical Skills", "Success Score", "Risk Level"
  ];

  const rows = students.map(s => [
    s.student_id,
    `"${s.name}"`,
    s.email,
    s.department,
    s.semester,
    s.section,
    `"${s.mentor}"`,
    s.cgpa,
    s.academic_marks_pct,
    s.attendance_pct,
    s.backlogs,
    s.lms_weekly_hours,
    s.lms_engagement_score,
    s.assignment_completion_pct,
    s.placement_aptitude_score,
    s.technical_skills_score,
    s.success_score,
    s.risk_level
  ]);

  const csvContent = "data:text/csv;charset=utf-8," + [headers.join(","), ...rows.map(r => r.join(","))].join("\n");
  const encodedUri = encodeURI(csvContent);
  const link = document.createElement("a");
  link.setAttribute("href", encodedUri);
  link.setAttribute("download", `CampusIQ_Student_Analytics_${new Date().toISOString().slice(0, 10)}.csv`);
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}

// ==============================================================================
// 12. EVENT LISTENERS & UI SWITCHERS
// ==============================================================================

function setupEventListeners() {
  // Role Switcher
  DOM.btnFacultyView.addEventListener("click", () => setRoleView("faculty"));
  DOM.btnAdminView.addEventListener("click", () => setRoleView("admin"));

  // Global Department Selector
  DOM.globalDeptFilter.addEventListener("change", (e) => {
    STATE.department = e.target.value;
    DOM.rosterDeptFilter.value = STATE.department;
    fetchOverview();
    fetchCharts();
    fetchStudents();
  });

  // Roster Department Filter
  DOM.rosterDeptFilter.addEventListener("change", (e) => {
    STATE.department = e.target.value;
    DOM.globalDeptFilter.value = STATE.department;
    fetchOverview();
    fetchCharts();
    fetchStudents();
  });

  // Semester Filter
  DOM.rosterSemFilter.addEventListener("change", (e) => {
    STATE.semesterFilter = e.target.value;
    fetchStudents();
  });

  // Sort By
  DOM.rosterSortBy.addEventListener("change", (e) => {
    STATE.sortBy = e.target.value;
    fetchStudents();
  });

  // Risk Filter Pills
  DOM.pillFilters.forEach(pill => {
    pill.addEventListener("click", () => {
      DOM.pillFilters.forEach(p => p.classList.remove("active"));
      pill.classList.add("active");
      STATE.riskFilter = pill.getAttribute("data-risk");
      fetchStudents();
    });
  });

  // Search Input with Debounce
  let searchTimeout;
  DOM.studentSearchInput.addEventListener("input", (e) => {
    const val = e.target.value.trim();
    DOM.btnClearSearch.style.display = val ? "block" : "none";
    clearTimeout(searchTimeout);
    searchTimeout = setTimeout(() => {
      STATE.searchQuery = val;
      fetchStudents();
    }, 250);
  });

  DOM.btnClearSearch.addEventListener("click", () => {
    DOM.studentSearchInput.value = "";
    DOM.btnClearSearch.style.display = "none";
    STATE.searchQuery = "";
    fetchStudents();
  });

  // Reset Filters button
  DOM.btnResetFilters.addEventListener("click", () => {
    STATE.searchQuery = "";
    STATE.department = "ALL";
    STATE.riskFilter = "ALL";
    STATE.semesterFilter = "ALL";
    STATE.sortBy = "risk_level-asc";

    DOM.studentSearchInput.value = "";
    DOM.btnClearSearch.style.display = "none";
    DOM.globalDeptFilter.value = "ALL";
    DOM.rosterDeptFilter.value = "ALL";
    DOM.rosterSemFilter.value = "ALL";
    DOM.rosterSortBy.value = "risk_level-asc";

    DOM.pillFilters.forEach(p => p.classList.remove("active"));
    document.querySelector(".pill-filter[data-risk='ALL']").classList.add("active");

    fetchOverview();
    fetchCharts();
    fetchStudents();
  });

  // Modal Closers
  DOM.btnCloseModal.addEventListener("click", () => {
    DOM.studentDetailModal.style.display = "none";
    DOM.studentDetailModal.setAttribute("aria-hidden", "true");
  });

  DOM.studentDetailModal.addEventListener("click", (e) => {
    if (e.target === DOM.studentDetailModal) {
      DOM.studentDetailModal.style.display = "none";
      DOM.studentDetailModal.setAttribute("aria-hidden", "true");
    }
  });

  // Simulator Modal Open/Close
  DOM.btnOpenSimulator.addEventListener("click", () => {
    DOM.simulatorModal.style.display = "flex";
    DOM.simulatorModal.setAttribute("aria-hidden", "false");
  });

  DOM.btnCloseSimulator.addEventListener("click", () => {
    DOM.simulatorModal.style.display = "none";
    DOM.simulatorModal.setAttribute("aria-hidden", "true");
  });

  DOM.simulatorModal.addEventListener("click", (e) => {
    if (e.target === DOM.simulatorModal) {
      DOM.simulatorModal.style.display = "none";
      DOM.simulatorModal.setAttribute("aria-hidden", "true");
    }
  });

  // Simulator Controls
  DOM.simStudentSelect.addEventListener("change", (e) => {
    updateSimulatorBaseline(e.target.value);
  });

  DOM.rangeSimAttendance.addEventListener("input", (e) => {
    DOM.valSimAttendance.textContent = `+${e.target.value}%`;
  });

  DOM.rangeSimBacklogs.addEventListener("input", (e) => {
    DOM.valSimBacklogs.textContent = `${e.target.value} Backlog${e.target.value != 1 ? 's' : ''}`;
  });

  DOM.rangeSimLms.addEventListener("input", (e) => {
    DOM.valSimLms.textContent = `+${e.target.value} hrs/wk`;
  });

  DOM.rangeSimAssignment.addEventListener("input", (e) => {
    DOM.valSimAssignment.textContent = `+${e.target.value}%`;
  });

  DOM.btnRunSimulation.addEventListener("click", runScenarioSimulation);

  // Intervention Form Submit
  DOM.interventionForm.addEventListener("submit", handleInterventionSubmit);

  // Export CSV
  DOM.btnExportCSV.addEventListener("click", exportRosterToCSV);

  // Close modals on Escape key
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") {
      DOM.studentDetailModal.style.display = "none";
      DOM.simulatorModal.style.display = "none";
    }
  });
}

function setRoleView(role) {
  STATE.currentRole = role;
  
  if (role === "admin") {
    DOM.btnAdminView.classList.add("active");
    DOM.btnAdminView.setAttribute("aria-selected", "true");
    DOM.btnFacultyView.classList.remove("active");
    DOM.btnFacultyView.setAttribute("aria-selected", "false");

    DOM.contextRoleTag.textContent = "Dean & Institutional Administrator View";
    DOM.contextTitle.textContent = "Institutional Student Success & Accreditation Intelligence";
    DOM.contextSubtitle.textContent = "Macro university-wide academic performance, NAAC/NIRF indicators, cross-department risk metrics, and systemic intervention tracking.";
    DOM.adminDeptBenchmarkSection.style.display = "block";
  } else {
    DOM.btnFacultyView.classList.add("active");
    DOM.btnFacultyView.setAttribute("aria-selected", "true");
    DOM.btnAdminView.classList.remove("active");
    DOM.btnAdminView.setAttribute("aria-selected", "false");

    DOM.contextRoleTag.textContent = "Faculty Advisory Mode";
    DOM.contextTitle.textContent = "Early Student Academic Risk & Success Radar";
    DOM.contextSubtitle.textContent = "Real-time monitoring across 120 enrolled students. Powered by explainable multi-pillar feature attribution with proactive intervention suggestions.";
    DOM.adminDeptBenchmarkSection.style.display = "none";
  }
}

// Utility: HTML escape for XSS protection
function escapeHtml(str) {
  if (!str) return "";
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

// Launch on DOM ready
document.addEventListener("DOMContentLoaded", initPlatform);
