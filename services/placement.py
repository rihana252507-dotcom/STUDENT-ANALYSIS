"""
CampusIQ – Placement Readiness & Skill-Based Matching Service
Provides skill normalization, dynamic company role matching, academic eligibility checking,
and personalized skill recommendations for campus recruitment.
"""

import re
from typing import List, Dict, Any, Tuple

# Common skill alias dictionary for intelligent normalization
ALIAS_MAP = {
    "js": "javascript",
    "reactjs": "react",
    "react.js": "react",
    "dsa": "data structures and algorithms",
    "data structures": "data structures and algorithms",
    "data structure": "data structures and algorithms",
    "data structures and algorithms": "data structures and algorithms",
    "data structures & algorithms": "data structures and algorithms",
    "algorithms": "data structures and algorithms",
    "ml": "machine learning",
    "ai": "artificial intelligence",
    "py": "python",
    "c plus plus": "c++",
    "cpp": "c++",
    "c#": "c-sharp",
    "c sharp": "c-sharp",
    "aws cloud": "aws",
    "amazon web services": "aws",
    "cloud": "cloud computing",
    "node": "node.js",
    "nodejs": "node.js",
    "html5": "html",
    "css3": "css",
    "dbms": "sql",
    "relational databases": "sql",
    "database": "sql",
    "rdbms": "sql",
    "mysql": "mysql",
    "postgres": "postgresql",
    "postgresql": "postgresql"
}

# Verified company opportunities with sample recruitment profiles
# Real, verified official career URLs used for safe external navigation
COMPANY_OPPORTUNITIES: List[Dict[str, Any]] = [
    {
        "id": "tcs",
        "company_name": "Tata Consultancy Services",
        "short_name": "TCS",
        "badge_color": "linear-gradient(135deg, #003B75, #0066CC)",
        "job_role": "Systems Engineer / Ninja Developer",
        "role_description": "Entry-level software engineering, algorithmic design, enterprise application development, and client technology solutions.",
        "opportunity_type": "Sample Placement Opportunity",
        "required_skills": ["Python", "Java", "C++", "Data Structures and Algorithms"],
        "preferred_skills": ["SQL", "Cloud Computing", "Problem Solving"],
        "min_cgpa": 6.0,
        "max_backlogs": 0,
        "eligible_branches": ["CSE", "IT", "ECE", "EEE", "AIML", "Data Science", "All Engineering Branches"],
        "min_academic_year": 4,
        "academic_year_label": "Year 4 (Semester 7 & 8)",
        "deadline": "Campus Recruitment Drive (Illustrative)",
        "apply_url": "https://www.tcs.com/careers",
        "url_verified": True
    },
    {
        "id": "wipro",
        "company_name": "Wipro",
        "short_name": "Wipro",
        "badge_color": "linear-gradient(135deg, #1C3F94, #2A72D4)",
        "job_role": "Project Engineer (Elite Talent)",
        "role_description": "Full-stack application engineering, enterprise integration, automated testing, and technical support across client engagements.",
        "opportunity_type": "Sample Placement Opportunity",
        "required_skills": ["Java", "Python", "SQL"],
        "preferred_skills": ["HTML", "CSS", "JavaScript", "Communication"],
        "min_cgpa": 6.0,
        "max_backlogs": 0,
        "eligible_branches": ["CSE", "IT", "ECE", "EEE", "Mechanical", "Civil", "All Engineering Branches"],
        "min_academic_year": 4,
        "academic_year_label": "Year 4 (Semester 7 & 8)",
        "deadline": "Elite National Talent Hunt (Illustrative)",
        "apply_url": "https://careers.wipro.com",
        "url_verified": True
    },
    {
        "id": "infosys",
        "company_name": "Infosys",
        "short_name": "Infosys",
        "badge_color": "linear-gradient(135deg, #006B34, #00A854)",
        "job_role": "Systems Associate / Specialist Programmer",
        "role_description": "Core product engineering, backend data pipeline development, enterprise architectures, and cloud services implementation.",
        "opportunity_type": "Sample Placement Opportunity",
        "required_skills": ["Python", "Data Structures and Algorithms", "SQL"],
        "preferred_skills": ["React", "Machine Learning", "Cloud Computing"],
        "min_cgpa": 6.5,
        "max_backlogs": 0,
        "eligible_branches": ["CSE", "IT", "ECE", "AIML", "Data Science"],
        "min_academic_year": 4,
        "academic_year_label": "Year 4 (Semester 7 & 8)",
        "deadline": "InfyTQ / HackWithInfy (Illustrative)",
        "apply_url": "https://www.infosys.com/careers.html",
        "url_verified": True
    },
    {
        "id": "accenture",
        "company_name": "Accenture",
        "short_name": "Accenture",
        "badge_color": "linear-gradient(135deg, #A100FF, #6B00B6)",
        "job_role": "Associate Software Engineer (ASE)",
        "role_description": "Modern web development, responsive application interfaces, cloud application deployment, and continuous delivery pipelines.",
        "opportunity_type": "Sample Placement Opportunity",
        "required_skills": ["JavaScript", "HTML", "CSS", "SQL"],
        "preferred_skills": ["React", "AWS", "Problem Solving", "Cloud Computing"],
        "min_cgpa": 6.5,
        "max_backlogs": 1,
        "eligible_branches": ["CSE", "IT", "ECE", "EEE", "Mechanical", "Civil", "All Engineering Branches"],
        "min_academic_year": 4,
        "academic_year_label": "Year 4 (Semester 7 & 8)",
        "deadline": "On-Campus Hiring Drive (Illustrative)",
        "apply_url": "https://www.accenture.com/in-en/careers",
        "url_verified": True
    },
    {
        "id": "cognizant",
        "company_name": "Cognizant",
        "short_name": "Cognizant",
        "badge_color": "linear-gradient(135deg, #0033A0, #0066CC)",
        "job_role": "GenC Next / Programmer Analyst",
        "role_description": "High-performance software systems, database engineering, enterprise service APIs, and agile software development.",
        "opportunity_type": "Sample Placement Opportunity",
        "required_skills": ["Java", "C++", "SQL", "Data Structures and Algorithms"],
        "preferred_skills": ["Python", "MySQL", "AWS", "Communication"],
        "min_cgpa": 6.0,
        "max_backlogs": 1,
        "eligible_branches": ["CSE", "IT", "ECE", "EEE", "Mechanical", "All Engineering Branches"],
        "min_academic_year": 4,
        "academic_year_label": "Year 4 (Semester 7 & 8)",
        "deadline": "GenC Campus Hiring (Illustrative)",
        "apply_url": "https://careers.cognizant.com",
        "url_verified": True
    }
]


def normalize_skill(skill: str) -> str:
    """Normalizes a skill string for case-insensitive and alias-aware comparison."""
    if not skill or not isinstance(skill, str):
        return ""
    s_mod = skill.lower().replace("&", " and ")
    cleaned = " ".join(s_mod.split()).strip(",.- ")
    return ALIAS_MAP.get(cleaned, cleaned)


def check_academic_eligibility(comp: Dict[str, Any], student_info: Dict[str, Any]) -> Tuple[str, str]:
    """
    Evaluates whether the student meets the academic criteria for a company opportunity.
    Checks: Academic Year, Minimum CGPA, Maximum Active Backlogs, and Branch/Department.
    Returns: (status, reason_string)
             status in ['Eligible', 'Not Eligible', 'Eligibility Pending']
    """
    if not student_info:
        return "Eligibility Pending", "Academic records not available for automated verification."

    # Derive academic year
    sem = student_info.get("semester")
    if sem is not None:
        try:
            acad_year = ((int(sem) - 1) // 2) + 1
        except (ValueError, TypeError):
            acad_year = student_info.get("academic_year", 4)
    else:
        acad_year = student_info.get("academic_year", 4)

    try:
        cgpa = float(student_info.get("cgpa", 0.0) or 0.0)
    except (ValueError, TypeError):
        cgpa = 0.0

    try:
        backlogs = int(student_info.get("backlogs", 0) or 0)
    except (ValueError, TypeError):
        backlogs = 0

    dept = str(student_info.get("department", "")).strip().upper()

    failed_reasons = []

    # 1. Academic Year Check
    min_year = comp.get("min_academic_year", 4)
    if acad_year < min_year:
        failed_reasons.append(f"Requires Year {min_year} standing (currently in Year {acad_year})")

    # 2. CGPA Check
    min_cgpa = comp.get("min_cgpa", 6.0)
    if cgpa < min_cgpa:
        failed_reasons.append(f"CGPA {cgpa:.2f} is below minimum cutoff of {min_cgpa}")

    # 3. Backlog Tolerance Check
    max_bl = comp.get("max_backlogs", 0)
    if backlogs > max_bl:
        bl_text = "zero backlogs allowed" if max_bl == 0 else f"maximum {max_bl} backlog allowed"
        failed_reasons.append(f"{backlogs} active backlog(s) exceed {bl_text}")

    # 4. Department Check
    eligible_depts = [b.upper() for b in comp.get("eligible_branches", [])]
    if "ALL" not in eligible_depts and "ALL ENGINEERING BRANCHES" not in eligible_depts:
        dept_matched = False
        for b in eligible_depts:
            if b in dept or dept in b:
                dept_matched = True
                break
        if not dept_matched:
            failed_reasons.append(f"Department {dept} not listed in eligible branches")

    if not failed_reasons:
        return "Eligible", "All verified academic requirements met (CGPA, backlogs, department, and academic year)."
    else:
        return "Not Eligible", "Criteria not met: " + " &bull; ".join(failed_reasons)


def match_companies_for_student(
    student_skills: List[str],
    student_info: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Computes dynamic company match percentages, matched/missing skills, academic eligibility,
    and personalized 'Skills to Improve' recommendations.
    """
    cleaned_entered = [s.strip() for s in student_skills if s and s.strip()]
    norm_entered = set(normalize_skill(s) for s in cleaned_entered)

    # If student entered no skills
    if not norm_entered:
        return {
            "has_entered_skills": False,
            "entered_skills": [],
            "companies": [],
            "skills_to_improve": [],
            "total_opportunities": len(COMPANY_OPPORTUNITIES),
            "message": "Please enter your technical and professional skills above and click 'Find Matching Companies' to see personalized opportunities."
        }

    company_results = []
    missing_by_top_companies: Dict[str, List[str]] = {}

    for comp in COMPANY_OPPORTUNITIES:
        req_skills = comp.get("required_skills", [])
        pref_skills = comp.get("preferred_skills", [])

        matched_req = []
        missing_req = []

        for r in req_skills:
            if normalize_skill(r) in norm_entered:
                matched_req.append(r)
            else:
                missing_req.append(r)

        matched_pref = []
        for p in pref_skills:
            if normalize_skill(p) in norm_entered:
                matched_pref.append(p)

        total_req = len(req_skills)
        if total_req > 0:
            match_pct = round((len(matched_req) / total_req) * 100)
        else:
            match_pct = 0

        elig_status, elig_reason = check_academic_eligibility(comp, student_info)

        company_results.append({
            "id": comp["id"],
            "company_name": comp["company_name"],
            "short_name": comp["short_name"],
            "badge_color": comp["badge_color"],
            "job_role": comp["job_role"],
            "role_description": comp["role_description"],
            "opportunity_type": comp["opportunity_type"],
            "required_skills": req_skills,
            "preferred_skills": pref_skills,
            "matched_required": matched_req,
            "missing_required": missing_req,
            "matched_preferred": matched_pref,
            "match_percentage": match_pct,
            "min_cgpa": comp["min_cgpa"],
            "max_backlogs": comp["max_backlogs"],
            "eligible_branches": comp["eligible_branches"],
            "min_academic_year": comp["min_academic_year"],
            "academic_year_label": comp["academic_year_label"],
            "deadline": comp["deadline"],
            "apply_url": comp["apply_url"],
            "url_verified": comp["url_verified"],
            "eligibility_status": elig_status,
            "eligibility_reason": elig_reason,
            "is_academically_eligible": (elig_status == "Eligible")
        })

    # Sort results: Highest match percentage first, then matched preferred count, then eligibility
    company_results.sort(
        key=lambda x: (x["match_percentage"], len(x["matched_preferred"]), x["is_academically_eligible"]),
        reverse=True
    )

    # Check if there is zero match across all companies
    max_match = max(c["match_percentage"] for c in company_results) if company_results else 0
    zero_match_state = (max_match == 0)

    # Build 'Skills to Improve' suggestions based on missing required skills of top roles
    # Wording: "Not listed in your skills yet: ..."
    skills_to_improve = []
    seen_skills = set()

    for comp in company_results:
        for missing in comp["missing_required"]:
            norm_m = normalize_skill(missing)
            if norm_m not in seen_skills and norm_m not in norm_entered:
                seen_skills.add(norm_m)
                skills_to_improve.append({
                    "skill": missing,
                    "target_company": comp["company_name"],
                    "role": comp["job_role"],
                    "impact": f"Adding this skill will improve your match score for {comp['company_name']} ({comp['job_role']})."
                })

    return {
        "has_entered_skills": True,
        "entered_skills": cleaned_entered,
        "companies": company_results,
        "skills_to_improve": skills_to_improve[:6],  # Top actionable suggestions
        "zero_match_state": zero_match_state,
        "total_opportunities": len(company_results),
        "message": "Direct skill matches found." if not zero_match_state else "No direct skill matches found for your currently entered skills. Try adding core technical skills like Python, Java, SQL, or Data Structures & Algorithms to broaden your results."
    }
