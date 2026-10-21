"""
CampusIQ – Multilingual Student AI Chatbot Service
Handles automatic language detection, conversational language preference tracking,
context-aware multilingual responses with verified database records,
and optional external LLM integration (OpenAI/compatible).
"""

import os
import re
import json

SYSTEM_INSTRUCTION = (
    "Answer the student's question in the language they used, unless they explicitly request another language. "
    "Understand multilingual and mixed-language messages. Preserve conversation context and give helpful, accurate answers. "
    "Use verified student records for personal academic questions. Never fabricate personal data or official college information."
)

SUPPORTED_LANGUAGES = {
    "english": "English",
    "telugu": "Telugu (తెలుగు)",
    "hindi": "Hindi (हिन्दी)",
    "tamil": "Tamil (தமிழ்)",
    "kannada": "Kannada (ಕನ್ನಡ)",
    "malayalam": "Malayalam (മലയാളം)",
    "urdu": "Urdu (اردو)",
    "bengali": "Bengali (বাংলা)",
    "marathi": "Marathi (मराठी)",
    "gujarati": "Gujarati (ગુજરાતી)",
    "punjabi": "Punjabi (ਪੰਜਾਬੀ)",
    "odia": "Odia (ଓଡ଼ିଆ)",
    "teluglish": "Telugu + English (Mixed)",
    "hinglish": "Hindi + English (Mixed)",
}

def detect_language_and_preference(text, current_preference=None):
    """
    Detects whether the message explicitly requests a language switch,
    or identifies the language from Unicode script or code-mixed Romanized text.
    Returns: (detected_language, is_explicit_preference_change)
    """
    t = text.lower().strip()

    # 1. Check for explicit language requests
    explicit_map = {
        "telugu": ["telugu", "తెలుగు"],
        "hindi": ["hindi", "हिन्दी", "हिंदी"],
        "english": ["english", "अंग्रेजी", "ఆంగ్లం"],
        "tamil": ["tamil", "தமிழ்"],
        "kannada": ["kannada", "ಕನ್ನಡ"],
        "malayalam": ["malayalam", "മലയാളം"],
        "urdu": ["urdu", "اردو"],
        "bengali": ["bengali", "bangla", "বাংলা"],
        "marathi": ["marathi", "मराठी"],
        "gujarati": ["gujarati", "ગુજરાતી"],
        "punjabi": ["punjabi", "ਪੰਜਾਬੀ"],
        "odia": ["odia", "oriyo", "ଓଡ଼ିଆ"],
    }

    for lang, triggers in explicit_map.items():
        for tr in triggers:
            pattern = (
                rf"(\b(in|into|explain|answer|reply|translate|use|with|speak)\b.*\b{tr}\b"
                rf"|\b{tr}\b.*\b(mein|me|lo|la|dalli|il|te|ma|samjhao|cheppandi|sollunga|heli|batao|language|bhasha)\b)"
            )
            if re.search(pattern, t):
                return lang, True

    # 2. Unicode native script detection
    if re.search(r"[\u0C00-\u0C7F]", text):
        return "telugu", False
    if re.search(r"[\u0900-\u097F]", text):
        # Distinguish Marathi if marathi-specific characters or context, else Hindi/Devanagari
        if any(w in t for w in ["आहे", "नाही", "माझे", "कसे", "सांगा"]):
            return "marathi", False
        return "hindi", False
    if re.search(r"[\u0B80-\u0BFF]", text):
        return "tamil", False
    if re.search(r"[\u0C80-\u0CFF]", text):
        return "kannada", False
    if re.search(r"[\u0D00-\u0D7F]", text):
        return "malayalam", False
    if re.search(r"[\u0980-\u09FF]", text):
        return "bengali", False
    if re.search(r"[\u0A80-\u0AFF]", text):
        return "gujarati", False
    if re.search(r"[\u0B00-\u0B7F]", text):
        return "odia", False
    if re.search(r"[\u0A00-\u0A7F]", text):
        return "punjabi", False
    if re.search(r"[\u0600-\u06FF]", text):
        return "urdu", False

    # 3. Transliterated / Romanized code-mixing detection
    teluglish_markers = [
        "ela", "naa", "naaku", "nenu", "cheppandi", "cheppu", "chudandi", "chaduvu",
        "undhi", "undi", "unnayi", "chala", "bagundi", "naku", "epudu", "enti",
        "em", "emito", "evaro", "evalu", "enni", "eppudu", "anni", "akkada",
        "ikkada", "ledu", "ledhu", "ayyindi", "vastundi", "vellandi", "raavali",
        "cheyandi", "cheyali", "cheskuni", "cheskovali", "ivvu", "iyyi", "ivvandi",
        "telugu", "avvali", "kadu", "kaadu", "okkasari", "cheppu", "theliyadu",
        "marchipomaku", "marchipoma", "peduta", "chuskundam", "manchi",
        "prepare", "avvali", "takkuva", "improve", "cheskovalante"
    ]
    hinglish_markers = [
        "kya", "kaise", "kaisa", "mera", "meri", "mere", "kitna", "kitni", "kitne",
        "batao", "samjhao", "padhai", "hai", "karo", "namaste", "mujhe", "bataiye",
        "kripya", "acha", "achha", "theek", "matlab", "seedha", "puri",
        "bana", "banao", "bata", "likho", "sikho", "seekho", "samjha", "deta",
        "chahiye", "chahie", "lagta", "lagti", "hota", "hoti", "karunga", "karungi",
        "karni", "karna", "karte", "nahi", "nahin", "nhi", "agar", "toh",
        "kyunki", "lekin", "mein", "bahut", "thoda", "zyada", "kam", "saari", "sab", "poori", "acchi",
        "bura", "achcha", "padhunga", "padhungi", "likhega", "likhna", "bhai",
        "yaar", "dost"
    ]

    words = set(re.findall(r"\b[a-z]+\b", t))
    if any(w in words for w in teluglish_markers):
        return "teluglish", False
    if any(w in words for w in hinglish_markers):
        return "hinglish", False
    if any(phrase in t for phrase in ["placement ki", "cgpa improve", "backlogs kaise", "theek hai"]):
        return "hinglish", False

    # 4. Respect current conversational preference if user previously asked to talk in another language
    if current_preference and current_preference in SUPPORTED_LANGUAGES:
        return current_preference, False

    return "english", False


def generate_multilingual_chat_reply(message, student_data, metrics, session_store):
    """
    Main entry point for generating multilingual student chat replies.
    Attempts external AI model if configured; otherwise uses verified multilingual rules.
    """
    current_pref = session_store.get("chat_lang_pref")
    lang, is_explicit = detect_language_and_preference(message, current_pref)

    # If the user explicitly requested a language, update preference in session
    if is_explicit:
        session_store["chat_lang_pref"] = lang

    # Maintain conversation history (last 8 messages)
    history = session_store.get("chat_history", [])

    # Try external LLM if configured
    llm_reply = _try_external_ai(message, student_data, metrics, history, lang)
    if llm_reply:
        history.append({"role": "user", "content": message})
        history.append({"role": "assistant", "content": llm_reply})
        session_store["chat_history"] = history[-8:]
        return {
            "reply": llm_reply,
            "language": lang,
            "ai_source": "configured_ai_model"
        }

    # Use built-in verified multilingual engine
    reply = _generate_local_multilingual_reply(message, student_data, metrics, lang, history)
    history.append({"role": "user", "content": message})
    history.append({"role": "assistant", "content": reply})
    session_store["chat_history"] = history[-8:]

    return {
        "reply": reply,
        "language": lang,
        "ai_source": "campusiq_multilingual_engine"
    }


def _try_external_ai(message, s, metrics, history, target_lang):
    """
    Attempts to call an external AI model (OpenAI API / compatible) if valid credentials exist.
    """
    api_key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not api_key or api_key.startswith("your_api") or len(api_key) < 20:
        return None

    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)

        student_context = (
            f"Verified Student Record:\n"
            f"- Name: {s.get('name')}\n"
            f"- Roll Number: {s.get('student_id')}\n"
            f"- Branch: {s.get('department')}\n"
            f"- Current Semester: {s.get('semester')}\n"
            f"- CGPA: {s.get('cgpa')}\n"
            f"- Attendance: {s.get('attendance_pct')}%\n"
            f"- Active Backlogs: {s.get('backlogs', 0)} ({s.get('backlog_subjects', 'None')})\n"
            f"- Success Score: {s.get('success_score')}/100\n"
            f"- Academic Risk Level: {s.get('risk_level')}\n"
            f"- Weekly LMS Hours: {s.get('lms_weekly_hours')} hrs/week\n"
            f"- Assignment Completion: {s.get('assignment_completion_pct')}%\n"
            f"- Placement Aptitude: {s.get('placement_aptitude_score')}/100\n"
            f"- Technical Skills: {s.get('technical_skills_score')}/100\n"
            f"- Faculty Mentor: {s.get('mentor_name')}\n"
        )

        messages = [
            {"role": "system", "content": f"{SYSTEM_INSTRUCTION}\n\n{student_context}\n\nTarget Response Language: {target_lang}."}
        ]
        # Include up to last 4 conversation turns for context
        for turn in history[-4:]:
            messages.append({"role": turn["role"], "content": turn["content"]})
        messages.append({"role": "user", "content": message})

        response = client.chat.completions.create(
            model=os.environ.get("OPENAI_MODEL", "gpt-4o-mini"),
            messages=messages,
            max_tokens=650,
            temperature=0.3
        )
        if response.choices and response.choices[0].message.content:
            return response.choices[0].message.content.strip()
    except Exception as e:
        # Graceful fallback to local multilingual engine if API fails or quota exceeded
        pass
    return None


def _detect_intent(msg_lower, history):
    """Identifies the conversational intent from message and context."""
    m = msg_lower

    # 1. Risk level & reduction (check before general academic keywords)
    if any(k in m for k in [
        "risk", "reduce risk", "lower risk", "academic risk", "danger",
        "ప్రమాదం", "రిస్క్", "జోఖిమ్", "खतरा", "ரிஸ்க்", "ಅಪಾಯ", "റിസ്ക്", "خطرہ"
    ]):
        return "risk"

    # 2. Recommendations & Action Plans
    if any(k in m for k in [
        "recommendation", "recommendations", "suggestion", "suggestions", "advice", "action plan",
        "సిఫార్సులు", "సూచనలు", "सुझाव", "பரிந்துரைகள்", "ಸಲಹೆಗಳು", "നിർദ്ദേശങ്ങൾ", "تجاویز"
    ]):
        return "recommendations"

    # 3. Study plan / schedule / timetable
    if any(k in m for k in [
        "study plan", "study schedule", "timetable", "schedule", "routine", "how to study", "preparation",
        "టైమ్‌టేబుల్", "స్టడీ ప్లాన్", "చదువుకోవడం ఎలా", "टाइमटेबल", "पढ़ाई की योजना",
        "படிப்பு திட்டம்", "ವೇಳಾಪಟ್ಟಿ", "പഠന പദ്ധതി", "ٹائم ٹیبل"
    ]):
        return "study_plan"

    # 4. Attendance
    if any(k in m for k in [
        "attendance", "attendence", "absent", "presence", "హాజరు", "అటెండెన్స్",
        "उपस्थिति", "हाजिरी", "வருகை", "ಹಾಜರಾತಿ", "ഹാജർ", "حاضری", "উপস্থিতি", "હાજરી", "ਉਪਸਥਿਤੀ"
    ]):
        return "attendance"

    # 5. Backlogs
    if any(k in m for k in [
        "backlog", "backlogs", "arrear", "arrears", "supplementary", "failed subject",
        "బ్యాక్‌లాగ్", "బకాయిలు", "बैकलॉग", "अपूर्ण", "பாக்கி", "ಬ್ಯಾಕ್‌ಲಾಗ್", "ബാക്ക്‌ലോഗ്", "بیک لاگ"
    ]):
        return "backlogs"

    # 6. Placement & Career
    if any(k in m for k in [
        "placement", "career", "job", "interview", "aptitude", "technical skills", "companies",
        "ప్లేస్‌మెంట్", "ఉద్యోగం", "ఇంటర్వ్యూ", "नौकरी", "प्लेसमेंट", "வேலைவாய்ப்பு", "ಉದ್ಯೋಗ", "തൊഴിൽ", "ملازمت"
    ]):
        return "placement"

    # 7. LMS & Online activity
    if any(k in m for k in ["lms", "assignment", "weekly hours", "study hours", "coursework"]):
        return "lms"

    # 8. Wellbeing / Stress
    if any(k in m for k in ["stress", "wellbeing", "mental health", "anxious", "burnout", "tired", "overwhelm"]):
        return "wellbeing"

    # 9. Success score
    if any(k in m for k in [
        "score", "success score", "points", "స్కోరు", "సక్సెస్ స్కోర్", "स्कोर", "ஸ்கோர்", "ಸ್ಕೋರ್"
    ]):
        return "score"

    # 10. CGPA / Marks / Academic Performance
    if any(k in m for k in [
        "cgpa", "gpa", "marks", "grades", "percentage", "academic", "performance",
        "మార్కులు", "సిజిపిఎ", "గ్రేడ్లు", "अंक", "मार्क्स", "रिजल्ट", "மதிப்பெண்",
        "ಅಂಕಗಳು", "മാർക്കുകൾ", "نمبر", "নম্বর", "ગુણ", "ਅੰਕ"
    ]):
        return "academics"

    # 11. General educational / programming / subject topics
    if any(k in m for k in [
        "explain", "what is", "how does", "teach me", "tell me about", "define",
        "concept", "example", "code", "coding", "program", "programming",
        "algorithm", "data structure", "pointer", "array", "linked list", "tree",
        "graph", "sorting", "searching", "recursion", "oop", "class", "object",
        "function", "loop", "variable", "database", "sql", "python", "java", "c++",
        "machine learning", "ai", "neural", "calculus", "differential", "integral",
        "matrix", "eigenvalue", "probability", "statistics", "physics", "chemistry",
        "engineering", "circuit", "signal", "networking", "os", "operating system",
        "compiler", "linker", "memory", "heap", "stack", "queue",
        # Teluglish educational
        "explain cheyyi", "explain cheyandi", "simple ga", "easy ga", "anedi em",
        "ela work avutundi", "ela cheyali", "ela use cheyyali", "em cheyali",
        "naku artham", "naku teliyadu", "basics cheppu",
        # Hinglish educational
        "samjhao mujhe", "explain karo", "kya hota hai", "kaise kaam", "kaise karte",
        "kaise likhte", "simple mein", "easy mein", "example do", "batao kaise",
        "pointers kya", "arrays kya", "linked list kya", "sorting kaise"
    ]):
        return "general_educational"

    # 12. Greetings
    if any(k in m for k in [
        "hello", "hi", "hey", "good morning", "good evening",
        "నమస్కారం", "హలో", "नमस्ते", "नमस्कार", "வணக்கம்", "ನಮಸ್ಕಾರ", "നമസ്കാരം", "سلام", "নমস্কার", "ਸਤਿ ਸ੍ਰੀ ਅਕਾਲ"
    ]):
        return "greeting"

    # 12. Thanks
    if any(k in m for k in [
        "thank", "thanks", "ధన్యవాదాలు", "థాంక్స్", "धन्यवाद", "शुक्रिया", "நன்றி", "ಧನ್ಯವಾದಗಳು", "നന്ദി"
    ]):
        return "thanks"

    # Contextual follow-up check (e.g. "explain this in telugu")
    if history:
        last_turn = history[-1]["content"].lower()
        if "attendance" in last_turn:
            return "attendance"
        if "cgpa" in last_turn or "marks" in last_turn:
            return "academics"
        if "backlog" in last_turn:
            return "backlogs"
        if "risk" in last_turn:
            return "risk"
        if "study" in last_turn or "routine" in last_turn:
            return "study_plan"

    return "general"


def _generate_local_multilingual_reply(message, s, metrics, lang, history):
    """
    Generates authentic, verified localized responses across all supported Indian languages and English.
    Strictly uses real database metrics without fabricating personal records.
    """
    name = s.get("name", "").split()[0]
    cgpa = float(s.get("cgpa", 0))
    att = float(s.get("attendance_pct", 0))
    backlogs = int(s.get("backlogs", 0))
    score = float(s.get("success_score", 0))
    risk = s.get("risk_level", "Medium")
    dept = s.get("department", "")
    sem = s.get("semester", "")
    mentor = s.get("mentor_name", "మీ ఫ్యాకల్టీ మెంటర్")
    backlog_subjects = s.get("backlog_subjects", "")
    aptitude = float(s.get("placement_aptitude_score", 0))
    tech = float(s.get("technical_skills_score", 0))

    intent = _detect_intent(message.lower(), history)

    # =========================================================================
    # 1. TELUGU (తెలుగు) & TELUGLISH
    # =========================================================================
    if lang in ["telugu", "teluglish"]:
        if intent == "attendance":
            if att >= 85:
                return (f"నమస్కారం {name} గారూ! మీ ప్రస్తుత హాజరు శాతం (Attendance) {att}%. "
                        f"ఇది విశ్వవిద్యాలయ కనీస అర్హత (75%) కంటే చాలా మెరుగ్గా ఉంది. ఈ స్థిరత్వాన్ని కొనసాగించండి!")
            elif att >= 75:
                return (f"{name} గారూ, మీ హాజరు శాతం ప్రస్తుతం {att}%. "
                        f"మీరు కనీస 75% అర్హత సాధించినప్పటికీ బఫర్ తక్కువగా ఉంది. భవిష్యత్ తరగతులను తప్పక హాజరుకాండి.")
            else:
                deficit = round(75.0 - att, 1)
                return (f"⚠️ హెచ్చరిక {name} గారూ: మీ హాజరు శాతం ప్రస్తుతం {att}%. "
                        f"పరీక్షల అనుమతికి అవసరమైన 75% కంటే {deficit}% తక్కువగా ఉన్నారు. "
                        f"వెంటనే మీ ఫ్యాకల్టీ మెంటర్ ({mentor})ని సంప్రదించి రికవరీ ప్రణాళిక రూపొందించుకోండి.")

        if intent == "academics":
            return (f"{name} గారూ, మీ అకడమిక్ ప్రొఫైల్ వివరాలు:\n"
                    f"• ప్రస్తుత CGPA: {cgpa}/10.0\n"
                    f"• అంతర్గత పరీక్ష మార్కులు: {s.get('academic_marks_pct', '--')}%\n"
                    f"• బ్రాంచ్: {dept} (సెమిస్టర్ {sem})\n"
                    f"{'• గమనిక: మీకు ' + str(backlogs) + ' యాక్టివ్ బ్యాక్‌లాగ్‌లు ఉన్నాయి.' if backlogs > 0 else '• అభినందనలు: మీకు ఎటువంటి యాక్టివ్ బ్యాక్‌లాగ్‌లు లేవు!'}\n"
                    f"మరిన్ని మార్కులు సాధించడానికి రోజూ కోర్ సబ్జెక్టులపై 1 గంట కేటాయించండి.")

        if intent == "backlogs":
            if backlogs == 0:
                return f"గొప్ప వార్త {name} గారూ! మీ రికార్డుల ప్రకారం మీకు ఎటువంటి యాక్టివ్ బ్యాక్‌లాగ్‌లు లేవు. ఆల్ ది బెస్ట్!"
            else:
                subj_str = f" ({backlog_subjects})" if backlog_subjects else ""
                return (f"{name} గారూ, మీకు ప్రస్తుతం {backlogs} యాక్టివ్ బ్యాక్‌లాగ్‌లు ఉన్నాయి{subj_str}.\n"
                        f"పరిష్కార సూచనలు:\n"
                        f"1. రోజూ 1.5 గంటలు కేవలం బ్యాక్‌లాగ్ సబ్జెక్ట్ రివిజన్ కోసం కేటాయించండి.\n"
                        f"2. గత 3 సంవత్సరాల పరీక్ష పేపర్లను ప్రాక్టీస్ చేయండి.\n"
                        f"3. తదుపరి సప్లిమెంటరీ పరీక్షల్లో వీటిని క్లియర్ చేస్తే మీ సక్సెస్ స్కోర్ గణనీయంగా పెరుగుతుంది.")

        if intent == "risk":
            return (f"{name} గారూ, మీ ప్రస్తుత అకడమిక్ రిస్క్ స్థాయి: {risk} Risk (సక్సెస్ స్కోర్: {score}/100).\n"
                    f"రిస్క్ తగ్గించుకోవడానికి ముఖ్యమైన సూచనలు:\n"
                    f"• హాజరును 80% పైగా ఉంచుకోండి.\n"
                    f"{'• మీ ' + str(backlogs) + ' బ్యాక్‌లాగ్‌లను క్లియర్ చేయండి.' if backlogs > 0 else '• అసైన్‌మెంట్లు సకాలంలో సమర్పించండి.'}\n"
                    f"• డాష్‌బోర్డ్‌లోని What-If సిమ్యులేటర్‌ని ఉపయోగించి మీ స్కోర్ పెరుగుదలను చూడవచ్చు.")

        if intent == "study_plan":
            return (f"{name} గారూ ({dept} సెమిస్టర్ {sem}) కొరకు రోజువారీ స్టడీ టైమ్‌టేబుల్:\n"
                    f"🌅 ఉదయం (1.5 గం): నిన్నటి పాఠాల రివిజన్ మరియు ఫార్ములాలు\n"
                    f"☀️ మధ్యాహ్నం (1 గం): కష్టమైన సబ్జెక్టు ప్రాబ్లమ్ సాల్వింగ్\n"
                    f"🌆 సాయంత్రం (1 గం): LMS అసైన్‌మెంట్లు మరియు ల్యాబ్ రికార్డులు\n"
                    f"🌙 రాత్రి (30 నిమి): మరుసటి రోజు టాపిక్స్ అవలోకనం")

        if intent == "placement":
            return (f"{name} గారూ, మీ క్యాంపస్ ప్లేస్‌మెంట్ సంసిద్ధత:\n"
                    f"• ఆప్టిట్యూడ్ స్కోర్: {aptitude}/100\n"
                    f"• టెక్నికల్ స్కిల్స్ స్కోర్: {tech}/100\n"
                    f"• CGPA: {cgpa} | బ్యాక్‌లాగ్‌లు: {backlogs}\n"
                    f"Tier-1 కంపెనీల కోసం రోజుకు 2 కోడింగ్ సమస్యలు (LeetCode) ప్రాక్టీస్ చేయండి.")

        if intent == "general_educational":
            topic = message.strip()
            return (f"నమస్కారం {name} గారూ! మీరు అడిగిన విషయం: '{topic}'\n"
                    f"ఈ విషయంపై CampusIQ's AI నేరుగా సమాధానం ఇవ్వగలిగేందుకు ఒక API key అవసరం. "
                    f"అయితే, మీరు ఈ topic ని పేర్కొనగలిగితే నేను study tips, key concepts, మరియు practice questions "
                    f"సూచించగలను. మీ {dept} course కోసం:\n"
                    f"• సంబంధిత textbook chapters చదవండి\n"
                    f"• Online platforms (GeeksforGeeks, NPTEL, Coursera) use చేయండి\n"
                    f"• Previous year questions practice చేయండి\n"
                    f"• మీ ఫ్యాకల్టీ మెంటర్ ({mentor})ని సంప్రదించండి")

        if intent == "greeting":
            return (f"నమస్కారం {name} గారూ! 👋 నేను మీ CampusIQ స్టడీ అసిస్టెంట్‌ని. "
                    f"మీ సక్సెస్ స్కోర్ {score}/100 ({risk} Risk). మీ హాజరు, మార్కులు, స్టడీ ప్లాన్ లేదా బ్యాక్‌లాగ్‌ల గురించి నన్ను అడగవచ్చు.")

        if intent == "thanks":
            return f"ధన్యవాదాలు {name} గారూ! 😊 క్రమం తప్పకుండా శ్రమించండి, విజయం మీదే!"

        return (f"నమస్కారం {name} గారూ! మీ ప్రశ్న నాకు అర్థమైంది. "
                f"మీరు మీ హాజరు (Attendance), CGPA, బ్యాక్‌లాగ్‌లు (Backlogs), స్టడీ ప్లాన్ (Study Timetable) లేదా రిస్క్ తగ్గించుకునే మార్గాల గురించి అడగవచ్చు.")

    # =========================================================================
    # 2. HINDI (हिन्दी) & HINGLISH
    # =========================================================================
    if lang in ["hindi", "hinglish"]:
        if intent == "attendance":
            if att >= 85:
                return (f"नमस्ते {name}! आपकी वर्तमान उपस्थिति (Attendance) {att}% है, "
                        f"जो न्यूनतम 75% आवश्यकता से काफी अच्छी है। इसी निरंतरता को बनाए रखें!")
            elif att >= 75:
                return (f"{name}, आपकी उपस्थिति वर्तमान में {att}% है। आप 75% की सीमा में हैं, "
                        f"लेकिन बफर बहुत कम है। कृपया आगे की कक्षाओं में अनुपस्थित न हों।")
            else:
                deficit = round(75.0 - att, 1)
                return (f"⚠️ चेतावनी {name}: आपकी उपस्थिति {att}% है, जो अनिवार्य 75% कटऑफ से {deficit}% कम है। "
                        f"परीक्षा से वंचित होने से बचने के लिए तुरंत अपने फैकल्टी मेंटर ({mentor}) से संपर्क करें।")

        if intent == "academics":
            return (f"{name}, आपका सत्यापित शैक्षणिक रिकॉर्ड:\n"
                    f"• वर्तमान CGPA: {cgpa}/10.0\n"
                    f"• आंतरिक परीक्षा अंक: {s.get('academic_marks_pct', '--')}%\n"
                    f"• विभाग: {dept} (सेमेस्टर {sem})\n"
                    f"{'• सक्रिय बैकलॉग: ' + str(backlogs) if backlogs > 0 else '• स्थिति: कोई सक्रिय बैकलॉग नहीं है (बहुत बढ़िया!)'}\n"
                    f"अपने सीजीपीए को बेहतर बनाने के लिए पिछले वर्षों के प्रश्न पत्रों का अभ्यास करें।")

        if intent == "backlogs":
            if backlogs == 0:
                return f"बहुत अच्छी खबर {name}! आपके पास कोई सक्रिय बैकलॉग नहीं है। अपनी पढ़ाई इसी तरह जारी रखें!"
            else:
                subj_str = f" ({backlog_subjects})" if backlog_subjects else ""
                return (f"{name}, आपके पास वर्तमान में {backlogs} सक्रिय बैकलॉग हैं{subj_str}।\n"
                        f"सुझाव:\n"
                        f"1. प्रतिदिन 1.5 घंटे विशेष रूप से बैकलॉग विषयों को दें।\n"
                        f"2. पिछले 3 वर्षों के पूरक परीक्षा प्रश्नपत्र हल करें।\n"
                        f"3. इन विषयों को क्लियर करने से आपका सक्सेस स्कोर लगभग 12 अंक बढ़ जाएगा।")

        if intent == "risk":
            return (f"{name}, आपका वर्तमान शैक्षणिक जोखिम स्तर: {risk} Risk (सक्सेस स्कोर: {score}/100)।\n"
                    f"जोखिम कम करने के उपाय:\n"
                    f"• कक्षा में उपस्थिति 80% से अधिक रखें।\n"
                    f"{'• अपने ' + str(backlogs) + ' बैकलॉग को अगली परीक्षा में क्लियर करें।' if backlogs > 0 else '• समय पर असाइनमेंट जमा करें।'}\n"
                    f"• विस्तृत सुधार देखने के लिए डैशबोर्ड पर What-If सिम्युलेटर का उपयोग करें।")

        if intent == "study_plan":
            return (f"{name} ({dept} सेमेस्टर {sem}) के लिए दैनिक अध्ययन योजना (Timetable):\n"
                    f"🌅 सुबह (1.5 घंटे): मुख्य सिद्धांतों और सूत्रों का पुनरीक्षण\n"
                    f"☀️ दोपहर (1 घंटा): कठिन विषयों के न्यूमेरिकल और कोडिंग प्रश्न\n"
                    f"🌆 शाम (1 घंटा): एलएमएस असाइनमेंट और लैब वर्क\n"
                    f"🌙 रात (30 मिनट): अगले दिन के विषयों का त्वरित अवलोकन")

        if intent == "placement":
            return (f"{name}, आपकी प्लेसमेंट तत्परता रिपोर्ट:\n"
                    f"• एप्टीट्यूड स्कोर: {aptitude}/100\n"
                    f"• तकनीकी कौशल स्कोर: {tech}/100\n"
                    f"• CGPA: {cgpa} | बैकलॉग: {backlogs}\n"
                    f"कैंपस प्लेसमेंट के लिए प्रतिदिन कम से कम 2 कोडिंग समस्याएं हल करें।")

        if intent == "general_educational":
            topic = message.strip()
            return (f"नमस्ते {name}! आपने पूछा: '{topic}'\n"
                    f"यह एक educational question है। CampusIQ का AI assistant आपको best study resources बताएगा:\n"
                    f"• अपनी {dept} की textbooks और class notes पढ़ें\n"
                    f"• GeeksforGeeks, NPTEL, और YouTube tutorials देखें\n"
                    f"• Previous year question papers practice करें\n"
                    f"• अपने faculty mentor ({mentor}) से personally guidance लें\n"
                    f"• एक OpenAI API key configure होने पर मैं direct explanation दे सकता हूँ!")

        if intent == "greeting":
            return (f"नमस्ते {name}! 👋 मैं आपका CampusIQ स्टडी असिस्टेंट हूँ। "
                    f"आपका सक्सेस स्कोर {score}/100 ({risk} Risk) है। आप मुझसे उपस्थिति, अंक, पढ़ाई की योजना या बैकलॉग के बारे में पूछ सकते हैं।")

        if intent == "thanks":
            return f"आपका स्वागत है {name}! 😊 मेहनत जारी रखें, सफलता जरूर मिलेगी!"

        return (f"नमस्ते {name}! मैं आपकी सहायता के लिए तैयार हूँ। "
                f"आप अपनी उपस्थिति, CGPA, बैकलॉग, स्टडी टाइमटेबल या प्लेसमेंट की तैयारी के बारे में कोई भी प्रश्न पूछ सकते हैं।")

    # =========================================================================
    # 3. TAMIL (தமிழ்)
    # =========================================================================
    if lang == "tamil":
        if intent == "attendance":
            return (f"வணக்கம் {name}! உங்கள் தற்போதைய வருகை சதவீதம் (Attendance) {att}%. "
                    f"{'இது கட்டாய 75% வரம்பை விட சிறந்தது.' if att >= 75 else f'இது 75% வரம்பை விட குறைவு! உடனே உங்கள் பேராசிரியரை ({mentor}) சந்திக்கவும்.'}")
        if intent == "academics":
            return f"வணக்கம் {name}! உங்கள் தற்போதைய CGPA: {cgpa}/10.0, துறை: {dept} (செமஸ்டர் {sem}). செயலில் உள்ள அரியர்கள்: {backlogs}."
        if intent == "backlogs":
            return f"வணக்கம் {name}! உங்களுக்கு {backlogs} அரியர்கள் உள்ளன. தினமும் 1.5 மணிநேரம் பழைய வினாத்தாள்களைப் பயிற்சி செய்யுங்கள்."
        return f"வணக்கம் {name}! நான் உங்கள் CampusIQ உதவியாளர். உங்கள் வருகை ({att}%), CGPA ({cgpa}), மற்றும் படிப்பு வழிகாட்டுதல் பற்றி கேட்கலாம்."

    # =========================================================================
    # 4. KANNADA (ಕನ್ನಡ)
    # =========================================================================
    if lang == "kannada":
        if intent == "attendance":
            return (f"ನಮಸ್ಕಾರ {name}! ನಿಮ್ಮ ಪ್ರಸ್ತುತ ಹಾಜರಾತಿ (Attendance) {att}%. "
                    f"{'ಇದು ಕಡ್ಡಾಯ 75% ಕ್ಕಿಂತ ಉತ್ತಮವಾಗಿದೆ.' if att >= 75 else f'ಇದು ಕನಿಷ್ಠ 75% ಕ್ಕಿಂತ ಕಡಿಮೆಯಿದೆ! ತಕ್ಷಣ ನಿಮ್ಮ ಮಾರ್ಗದರ್ಶಕರನ್ನು ({mentor}) ಭೇಟಿ ಮಾಡಿ.'}")
        if intent == "academics":
            return f"ನಮಸ್ಕಾರ {name}! ನಿಮ್ಮ CGPA: {cgpa}/10.0, ವಿಭಾಗ: {dept} (ಸೆಮಿಸ್ಟರ್ {sem}). ಸಕ್ರಿಯ ಬ್ಯಾಕ್‌ಲಾಗ್‌ಗಳು: {backlogs}."
        return f"ನಮಸ್ಕಾರ {name}! ನಾನು ನಿಮ್ಮ CampusIQ ಸ್ಟಡಿ ಅಸಿಸ್ಟೆಂಟ್. ನಿಮ್ಮ ಹಾಜರಾತಿ ({att}%), CGPA ({cgpa}) ಮತ್ತು ಅಧ್ಯಯನ ಯೋಜನೆ ಬಗ್ಗೆ ಕೇಳಬಹುದು."

    # =========================================================================
    # 5. MALAYALAM (മലയാളം)
    # =========================================================================
    if lang == "malayalam":
        if intent == "attendance":
            return (f"നമസ്കാരം {name}! നിങ്ങളുടെ ഹാജർ നില (Attendance) {att}% ആണ്. "
                    f"{'ഇത് ആവശ്യമായ 75% നേക്കാൾ കൂടുതലാണ്.' if att >= 75 else f'ഇത് 75% നേക്കാൾ കുറവാണ്! ഉടൻ നിങ്ങളുടെ ഫാക്കൽറ്റി മെന്ററെ ({mentor}) കാണുക.'}")
        return f"നമസ്കാരം {name}! ഞാൻ നിങ്ങളുടെ CampusIQ സഹായിയാണ്. നിങ്ങളുടെ ഹാജർ ({att}%), CGPA ({cgpa}), പഠന തന്ത്രങ്ങൾ എന്നിവയെക്കുറിച്ച് ചോദിക്കാം."

    # =========================================================================
    # 6. URDU (اردو)
    # =========================================================================
    if lang == "urdu":
        if intent == "attendance":
            return (f"آداب {name}! آپ کی موجودہ حاضری {att}% ہے۔ "
                    f"{'یہ لازمی 75 فیصد سے بہتر ہے۔' if att >= 75 else f'یہ لازمی 75 فیصد سے کم ہے۔ فوری طور پر اپنے سرپرست ({mentor}) سے رابطہ کریں۔'}")
        return f"آداب {name}! میں آپ کا CampusIQ تعلیمی معاون ہوں۔ آپ اپنی حاضری ({att}%)، CGPA ({cgpa}) اور بیک لاگز کے بارے میں پوچھ سکتے ہیں۔"

    # =========================================================================
    # 7. BENGALI (বাংলা)
    # =========================================================================
    if lang == "bengali":
        if intent == "attendance":
            return (f"নমস্কার {name}! আপনার বর্তমান উপস্থিতি (Attendance) {att}%। "
                    f"{'এটি প্রয়োজনীয় ৭৫% এর চেয়ে ভালো।' if att >= 75 else f'এটি ৭৫% এর চেয়ে কম! অবিলম্বে আপনার মেন্টরের ({mentor}) সাথে যোগাযোগ করুন।'}")
        return f"নমস্কার {name}! আমি আপনার CampusIQ স্টাডি অ্যাসিস্ট্যান্ট। আপনার উপস্থিতি ({att}%), CGPA ({cgpa}) এবং পরীক্ষার প্রস্তুতি সম্পর্কে জানতে পারেন।"

    # =========================================================================
    # 8. MARATHI (मराठी)
    # =========================================================================
    if lang == "marathi":
        if intent == "attendance":
            return (f"नमस्कार {name}! तुमची उपस्थिती (Attendance) {att}% आहे. "
                    f"{'ही अनिवार्य ७५% पेक्षा जास्त आहे.' if att >= 75 else f'ही ७५% पेक्षा कमी आहे! कृपया आपल्या मेंटॉरशी ({mentor}) त्वरित संपर्क साधा.'}")
        return f"नमस्कार {name}! मी तुमचा CampusIQ स्टडी असिस्टंट आहे. उपस्थिती ({att}%), CGPA ({cgpa}) आणि अभ्यासाच्या नियोजनाबद्दल विचारा."

    # =========================================================================
    # 9. GUJARATI (ગુજરાતી)
    # =========================================================================
    if lang == "gujarati":
        if intent == "attendance":
            return (f"નમસ્તે {name}! તમારી હાજરી (Attendance) {att}% છે. "
                    f"{'તે જરૂરી ૭૫% કરતાં વધુ છે.' if att >= 75 else f'તે ૭૫% કરતાં ઓછી છે! તરત જ તમારા માર્ગદર્શક ({mentor}) નો સંપર્ક કરો.'}")
        return f"નમસ્તે {name}! હું તમારો CampusIQ સ્ટડી આસિસ્ટન્ટ છું. તમારી હાજરી ({att}%), CGPA ({cgpa}) અને અભ્યાસ વિશે પૂછી શકો છો."

    # =========================================================================
    # 10. PUNJABI (ਪੰਜਾਬੀ)
    # =========================================================================
    if lang == "punjabi":
        if intent == "attendance":
            return (f"ਸਤਿ ਸ੍ਰੀ ਅਕਾਲ {name}! ਤੁਹਾਡੀ ਹਾਜ਼ਰੀ {att}% ਹੈ। "
                    f"{'ਇਹ ਲੋੜੀਂਦੀ 75% ਤੋਂ ਵੱਧ ਹੈ।' if att >= 75 else f'ਇਹ 75% ਤੋਂ ਘੱਟ ਹੈ! ਤੁਰੰਤ ਆਪਣੇ ਮੈਂਟਰ ({mentor}) ਨਾਲ ਸੰਪਰਕ ਕਰੋ।'}")
        return f"ਸਤਿ ਸ੍ਰੀ ਅਕਾਲ {name}! ਮੈਂ ਤੁਹਾਡਾ CampusIQ ਸਹਾਇਕ ਹਾਂ। ਤੁਸੀਂ ਆਪਣੀ ਹਾਜ਼ਰੀ ({att}%) ਅਤੇ CGPA ({cgpa}) ਬਾਰੇ ਪੁੱਛ ਸਕਦੇ ਹੋ।"

    # =========================================================================
    # 11. ODIA (ଓଡ଼ିଆ)
    # =========================================================================
    if lang == "odia":
        if intent == "attendance":
            return (f"ନମସ୍କାର {name}! ଆପଣଙ୍କ ଉପସ୍ଥିତି (Attendance) {att}% ଅଟେ। "
                    f"{'ଏହା ୭୫% ରୁ ଅଧିକ ଅଟେ।' if att >= 75 else f'ଏହା ୭୫% ରୁ କମ ଅଟେ! ତୁରନ୍ତ ଆପଣଙ୍କ ମେଣ୍ଟରଙ୍କୁ ({mentor}) ଦେଖା କରନ୍ତୁ।'}")
        return f"ନମସ୍କାର {name}! ମୁଁ ଆପଣଙ୍କ CampusIQ ଷ୍ଟଡି ଆସିଷ୍ଟାଣ୍ଟ। ଆପଣ ନିଜ ଉପସ୍ଥିତି ({att}%) ଏବଂ CGPA ({cgpa}) ବିଷୟରେ ପଚାରି ପାରିବେ।"

    # =========================================================================
    # 12. ENGLISH (DEFAULT / FALLBACK)
    # =========================================================================
    if intent == "attendance":
        if att >= 85:
            return (f"Great news, {name}! Your attendance is {att}%, well above the 75% statutory requirement. "
                    f"Keep up the consistency!")
        elif att >= 75:
            return (f"Your attendance is {att}%, {name} — you meet the minimum 75% threshold, but there isn't much buffer. "
                    f"Try not to miss any more classes.")
        else:
            deficit = round(75.0 - att, 1)
            return (f"⚠️ {name}, your attendance is {att}%, which is {deficit}% below the mandatory 75% cutoff. "
                    f"This puts you at risk of exam debarment. Meet your faculty advisor ({mentor}) immediately.")

    if intent == "academics":
        tips = [f"Your current CGPA is {cgpa}/10.0 in {dept} (Semester {sem}), {name}."]
        if cgpa >= 8.0:
            tips.append("You are in good academic standing! Keep up your steady study schedule.")
        else:
            tips.append("Focus on core subjects and solve previous exam question papers to boost your marks.")
        if backlogs > 0:
            tips.append(f"Important: You have {backlogs} active backlog(s). Focus on clearing these in the upcoming cycle.")
        return "\n".join(tips)

    if intent == "backlogs":
        if backlogs == 0:
            return f"Great news, {name}! You have no active backlogs. Keep up the strong academic performance!"
        else:
            subj_str = f" ({backlog_subjects})" if backlog_subjects else ""
            return (f"You currently have {backlogs} active backlog(s), {name}{subj_str}. "
                    f"Dedicate 1.5 hours daily specifically to backlog subjects and practice past 3-year question papers.")

    if intent == "risk":
        return (f"Your current risk level is {risk}, {name} (Success Score: {score}/100).\n"
                f"Key steps to reduce risk:\n"
                f"• Maintain attendance strictly above 80%.\n"
                f"{'• Clear your ' + str(backlogs) + ' backlogs in the next exam cycle.' if backlogs > 0 else '• Submit all pending LMS assignments on time.'}\n"
                f"• Use the What-If Simulator on your dashboard to see how each improvement boosts your score.")

    if intent == "study_plan":
        return (f"Here is a suggested daily study timetable for you, {name} ({dept} Sem {sem}):\n"
                f"• Morning (1.5 hrs): Core concept revision and formula recall\n"
                f"• Afternoon (1 hr): Problem-solving in weaker subjects\n"
                f"• Evening (1 hr): LMS assignments and lab preparation\n"
                f"• Night (30 min): Quick preview of tomorrow's lectures")

    if intent == "placement":
        return (f"Your placement readiness summary, {name}:\n"
                f"• Aptitude Score: {aptitude}/100\n"
                f"• Technical Skills: {tech}/100\n"
                f"• CGPA: {cgpa} | Active Backlogs: {backlogs}\n"
                f"Solve 2 coding problems daily on online platforms and practice logical aptitude.")

    if intent == "score":
        return f"Your current Student Success Score is {score}/100, {name}.\nRisk Level: {risk} Risk\nMaintain strong attendance and submit coursework on time to maximize your score."

    if intent == "recommendations":
        recs = [f"Personalized Action Plan for {name} ({dept}):"]
        if att < 75:
            recs.append("• Prioritize attending all remaining classes to clear the 75% attendance threshold.")
        if backlogs > 0:
            recs.append(f"• Prepare dedicated revision hours for clearing your {backlogs} active backlog(s).")
        recs.append("• Complete pending LMS assignments and practice mock technical assessments.")
        return "\n".join(recs)

    if intent == "lms":
        lms_h = s.get("lms_weekly_hours", 0)
        asgn = s.get("assignment_completion_pct", 0)
        return f"LMS Learning Telemetry for {name}:\n• Weekly Digital Hours: {lms_h} hrs/week\n• Assignment Submission Rate: {asgn}%\nStay active on the portal for consistent engagement."

    if intent == "wellbeing":
        return f"Wellbeing & Balance Tips for {name}:\n• Take regular study breaks using the Pomodoro technique.\n• Reach out to your faculty mentor ({mentor}) if you feel overwhelmed.\n• Maintain balanced sleep and recreation routines alongside exam prep."

    if intent == "general_educational":
        return f"Educational Guide for {name} ({dept}):\n• Review your course syllabus and core reference textbooks.\n• Explore standard learning resources on GeeksforGeeks, NPTEL, and documentation.\n• Practice past exam questions and consult your faculty mentor ({mentor}) for conceptual doubts."

    if intent == "greeting":
        return (f"Hello {name}! 👋 I'm your CampusIQ Study Assistant. "
                f"Your current success score is {score}/100 ({risk} Risk). "
                f"How can I help you today? You can ask in English, Telugu, Hindi, Tamil, Kannada, or any language you prefer!")

    if intent == "thanks":
        return f"You're welcome, {name}! 😊 I'm always here to help. Keep up the consistent effort!"

    return (f"I'm here to help, {name}! You can ask about your attendance, CGPA, active backlogs, "
            f"study timetable, or ways to reduce your academic risk — in English, Telugu (తెలుగు), "
            f"Hindi (हिन्दी), or any language of your choice.")
