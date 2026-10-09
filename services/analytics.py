"""
CampusIQ – Analytics Service
Explainable Multi-Pillar Student Success, Risk Scoring & Segmentation Engine
KPMG in India Hackathon Challenge Prototype
"""

class StudentAnalyticsEngine:
    """
    Explainable Multi-Pillar Student Success and Risk Scoring Engine.
    Deterministic, auditable, and rule-based with extensible hooks for ML models.
    """

    WEIGHTS = {
        "academic": 0.30,
        "attendance": 0.20,
        "lms": 0.15,
        "placement": 0.20,
        "wellbeing": 0.15
    }

    def compute_student_metrics(self, s):
        """
        Calculates normalized pillar scores, composite success score, risk category,
        explainable factors, student segment, and recommended mentor interventions.
        """
        cgpa = float(s.get("cgpa", 0))
        marks = float(s.get("academic_marks_pct", 0))
        attendance = float(s.get("attendance_pct", 0))
        backlogs = int(s.get("backlogs", 0))
        lms_hours = float(s.get("lms_weekly_hours", 0))
        lms_score_raw = float(s.get("lms_engagement_score", 0))
        assignment_pct = float(s.get("assignment_completion_pct", 0))
        extra_score = float(s.get("extracurricular_score", 0))
        aptitude = float(s.get("placement_aptitude_score", 0))
        tech = float(s.get("technical_skills_score", 0))
        feedback = float(s.get("student_feedback_score", 0))

        # --- Pillar 1: Academic Mastery (0-100) ---
        cgpa_norm = min(100.0, max(0.0, (cgpa / 10.0) * 100.0))
        academic_base = (cgpa_norm * 0.6) + (marks * 0.4)
        backlog_penalty = backlogs * 12.0  # -12 pts per active backlog
        academic_pillar = max(10.0, min(100.0, academic_base - backlog_penalty))

        # --- Pillar 2: Attendance & Discipline (0-100) ---
        if attendance >= 75.0:
            attendance_pillar = min(100.0, attendance)
        else:
            shortfall = 75.0 - attendance
            attendance_pillar = max(0.0, attendance - (shortfall * 1.5))

        # --- Pillar 3: LMS & Learning Engagement (0-100) ---
        hours_norm = min(100.0, (lms_hours / 18.0) * 100.0)
        lms_pillar = (hours_norm * 0.3) + (lms_score_raw * 0.35) + (assignment_pct * 0.35)
        lms_pillar = max(10.0, min(100.0, lms_pillar))

        # --- Pillar 4: Placement Readiness (0-100) ---
        placement_pillar = (tech * 0.55) + (aptitude * 0.45)
        placement_pillar = max(10.0, min(100.0, placement_pillar))

        # --- Pillar 5: Holistic Wellbeing (0-100) ---
        feedback_norm = min(100.0, (feedback / 5.0) * 100.0)
        wellbeing_pillar = (feedback_norm * 0.55) + (extra_score * 0.45)
        wellbeing_pillar = max(10.0, min(100.0, wellbeing_pillar))

        # Composite Success Score (0-100)
        composite_score = round(
            (academic_pillar * self.WEIGHTS["academic"]) +
            (attendance_pillar * self.WEIGHTS["attendance"]) +
            (lms_pillar * self.WEIGHTS["lms"]) +
            (placement_pillar * self.WEIGHTS["placement"]) +
            (wellbeing_pillar * self.WEIGHTS["wellbeing"]),
            1
        )
        composite_score = max(5.0, min(99.5, composite_score))

        # Explainable Risk Classification Rules
        is_high_risk = (
            composite_score < 60.0 or
            attendance < 70.0 or
            backlogs >= 2 or
            (cgpa < 5.8 and backlogs >= 1)
        )

        is_medium_risk = (
            not is_high_risk and (
                composite_score < 74.0 or
                attendance < 78.0 or
                backlogs == 1 or
                assignment_pct < 68.0 or
                placement_pillar < 62.0
            )
        )

        if is_high_risk:
            risk_level = "High"
            risk_badge = "high"
        elif is_medium_risk:
            risk_level = "Medium"
            risk_badge = "medium"
        else:
            risk_level = "Low"
            risk_badge = "low"

        # Student Segmentation Classification
        if cgpa >= 7.5 and placement_pillar < 65.0:
            segment = "Academically Strong but Placement-Unready"
            segment_badge = "warning"
        elif attendance < 75.0:
            segment = "Low Attendance & Debarment Risk"
            segment_badge = "danger"
        elif backlogs >= 1 or cgpa < 6.0:
            segment = "Academic Velocity & Backlog Risk"
            segment_badge = "danger"
        elif composite_score >= 80.0 and backlogs == 0 and attendance >= 80.0:
            segment = "High Potential Star Performer"
            segment_badge = "success"
        else:
            segment = "Balanced Steady Performer"
            segment_badge = "primary"

        # Feature Impact Attribution (Explainable AI Factors)
        risk_factors = []
        positive_factors = []

        # Attendance factor
        if attendance < 75.0:
            impact_val = round((75.0 - attendance) * 0.9, 1)
            risk_factors.append({
                "category": "Regulatory Attendance",
                "severity": "danger" if attendance < 68.0 else "warning",
                "impact": f"-{impact_val} pts",
                "title": f"Attendance Shortfall ({attendance}%)",
                "description": "Falls below statutory 75% UGC/NAAC mandate. Exam debarment risk."
            })
        else:
            positive_factors.append({
                "category": "Attendance",
                "impact": "+8 pts",
                "title": f"Consistent Attendance ({attendance}%)",
                "description": "Meets university academic discipline and institutional compliance standards."
            })

        # Backlogs factor
        if backlogs > 0:
            risk_factors.append({
                "category": "Academic Velocity",
                "severity": "danger" if backlogs >= 2 else "warning",
                "impact": f"-{backlogs * 12} pts",
                "title": f"{backlogs} Active Backlog{'s' if backlogs > 1 else ''}",
                "description": "Clearing outstanding credits is urgent to preserve degree timeline."
            })

        # Academic marks / CGPA factor
        if cgpa < 6.5:
            risk_factors.append({
                "category": "Cumulative GPA",
                "severity": "danger" if cgpa < 5.8 else "warning",
                "impact": "-10 pts",
                "title": f"CGPA Below 6.5 Benchmark ({cgpa})",
                "description": "Restricts eligibility for Tier-1 campus placement recruitment drives."
            })
        elif cgpa >= 8.5:
            positive_factors.append({
                "category": "Academic Excellence",
                "impact": "+15 pts",
                "title": f"Top Tier CGPA ({cgpa})",
                "description": "Consistent first-class performance across internal evaluation cycles."
            })

        # LMS / Assignment engagement
        if assignment_pct < 65.0 or lms_hours < 5.0:
            risk_factors.append({
                "category": "Learning Management Engagement",
                "severity": "warning",
                "impact": "-6 pts",
                "title": f"Subdued LMS Activity ({lms_hours} hrs/wk, {assignment_pct}% submissions)",
                "description": "Indicates learning friction or low continuous self-directed revision."
            })
        elif lms_hours >= 14.0 and assignment_pct >= 90.0:
            positive_factors.append({
                "category": "Digital Engagement",
                "impact": "+10 pts",
                "title": f"Proactive Self-Study ({lms_hours} hrs/wk)",
                "description": "High continuous engagement with course materials and online lab assessments."
            })

        # Placement Readiness factor
        if placement_pillar < 60.0:
            risk_factors.append({
                "category": "Placement Readiness",
                "severity": "warning",
                "impact": "-8 pts",
                "title": f"Technical/Aptitude Deficit ({int(placement_pillar)}/100)",
                "description": "Requires targeted coding labs and logical reasoning bootcamp support."
            })
        elif placement_pillar >= 85.0:
            positive_factors.append({
                "category": "Placement Ready",
                "impact": "+12 pts",
                "title": f"Strong Technical Profile ({int(placement_pillar)}/100)",
                "description": "High competitive coding skills, project depth, and recruitment readiness."
            })

        # Wellbeing & Sentiment
        if feedback < 2.5:
            risk_factors.append({
                "category": "Student Wellbeing",
                "severity": "danger" if feedback < 2.0 else "warning",
                "impact": "-5 pts",
                "title": f"Low Wellness/Sentiment Index ({feedback}/5.0)",
                "description": "Elevated academic stress or personal challenges reported."
            })

        # Automated Faculty Intervention Recommendations
        interventions = []
        if attendance < 75.0:
            interventions.append({
                "id": "INT-ATT-01",
                "category": "Attendance Advisory",
                "urgency": "Immediate" if attendance < 68.0 else "High",
                "action": "Issue Statutory Attendance Warning & Schedule Dean Counseling",
                "timeline": "Within 48 hours",
                "rationale": f"Current attendance is {attendance}%, below UGC 75% minimum threshold."
            })
        if backlogs > 0:
            interventions.append({
                "id": "INT-ACAD-02",
                "category": "Remedial Academics",
                "urgency": "High",
                "action": f"Assign Department Peer Tutor for {backlogs} Outstanding Subject(s)",
                "timeline": "Next 7 days",
                "rationale": "Clear backlogs in upcoming supplementary examination cycle."
            })
        if placement_pillar < 65.0:
            interventions.append({
                "id": "INT-CAREER-03",
                "category": "Career Accelerator",
                "urgency": "Moderate",
                "action": "Enroll in KPMG Technical & Aptitude Mock Bootcamp",
                "timeline": "Next cohort (2 weeks)",
                "rationale": f"Placement score is {int(placement_pillar)}/100. Target benchmark is >= 75."
            })
        if assignment_pct < 70.0 or lms_hours < 6.0:
            interventions.append({
                "id": "INT-LMS-04",
                "category": "Academic Mentorship",
                "urgency": "Moderate",
                "action": "Mentor 1-on-1 Check-in for Assignment Catch-up & LMS Remediation",
                "timeline": "Within 10 days",
                "rationale": f"Assignment completion is {assignment_pct}%; resolve study roadblocks."
            })
        if feedback < 3.0:
            interventions.append({
                "id": "INT-WELL-05",
                "category": "Student Wellbeing",
                "urgency": "High",
                "action": "Refer to Campus Student Wellness Counselor for Stress Support",
                "timeline": "Within 3 days",
                "rationale": "Student wellbeing index signals academic fatigue or low motivation."
            })

        if not interventions:
            interventions.append({
                "id": "INT-HONOR-01",
                "category": "Peer Mentorship",
                "urgency": "Low",
                "action": "Nominate for Department Peer Mentor Program & Research Internship",
                "timeline": "Next semester",
                "rationale": "Exemplary academic and technical track record across all pillars."
            })

        pillars = {
            "academic": round(academic_pillar, 1),
            "attendance": round(attendance_pillar, 1),
            "lms": round(lms_pillar, 1),
            "placement": round(placement_pillar, 1),
            "wellbeing": round(wellbeing_pillar, 1)
        }

        return {
            "success_score": composite_score,
            "risk_level": risk_level,
            "risk_badge": risk_badge,
            "segment": segment,
            "segment_badge": segment_badge,
            "pillars": pillars,
            "risk_factors": risk_factors,
            "positive_factors": positive_factors,
            "recommended_interventions": interventions
        }

    def simulate_scenario(self, student, attendance_boost=0, clear_backlogs=0, lms_hours_boost=0, assignment_boost=0):
        """
        Calculates hypothetical projected metrics for What-If scenario simulations.
        """
        simulated = dict(student)
        simulated["attendance_pct"] = min(100.0, float(student["attendance_pct"]) + float(attendance_boost))
        simulated["backlogs"] = max(0, int(student["backlogs"]) - int(clear_backlogs))
        simulated["lms_weekly_hours"] = min(30.0, float(student["lms_weekly_hours"]) + float(lms_hours_boost))
        simulated["assignment_completion_pct"] = min(100.0, float(student["assignment_completion_pct"]) + float(assignment_boost))

        new_metrics = self.compute_student_metrics(simulated)
        diff = round(new_metrics["success_score"] - float(student.get("success_score", 0)), 1)

        return {
            "original": {
                "success_score": float(student.get("success_score", 0)),
                "risk_level": student.get("risk_level", "Medium")
            },
            "simulated": {
                "success_score": new_metrics["success_score"],
                "risk_level": new_metrics["risk_level"],
                "pillars": new_metrics["pillars"]
            },
            "score_delta": f"+{diff}" if diff >= 0 else str(diff),
            "risk_improved": (student.get("risk_level") != new_metrics["risk_level"])
        }

analytics_engine = StudentAnalyticsEngine()
