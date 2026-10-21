JS_PATH = r"c:\Users\samee\hackzelerate\STUDENT-ANALYSIS\static\js\app.js"

with open(JS_PATH, "r", encoding="utf-8") as f:
    js = f.read()

# The existing renderRiskWatchlist function to replace
OLD_FUNC_START = "function renderRiskWatchlist(students) {"
old_pos = js.find(OLD_FUNC_START)
assert old_pos != -1, "Could not find OLD_FUNC_START in app.js"

# Find end of old renderRiskWatchlist
next_func_marker = "// Faculty Risk Alerts Table"
old_end = js.find(next_func_marker, old_pos)
assert old_end != -1, "Could not find next_func_marker in app.js"

NEW_JS = """function renderRiskWatchlist(students) {
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
          <td><strong>${s.success_score}</strong>/100</td>
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
        <span class="student-id-code" style="font-size:0.8125rem; font-weight:600; color:#5B21B6;">
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
      let gradStyle = "background:linear-gradient(135deg,#7C3AED,#EC4899);"; // neutral default
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
            <td><span style="color:#5B21B6; font-weight:600;">${escapeHtml(f.action)}</span></td>
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
            <div style="font-size:0.7rem; color:#5B21B6; font-weight:600; margin-top:4px;">Timeline: ${escapeHtml(item.timeline || 'Upcoming evaluation cycle')}</div>
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

// Faculty Risk Alerts Table"""

js = js[:old_pos] + NEW_JS + js[old_end + len(next_func_marker):]

with open(JS_PATH, "w", encoding="utf-8") as f:
    f.write(js)

print("static/js/app.js updated successfully!")
