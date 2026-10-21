"""
Comprehensive verification test suite for Multilingual Student AI Chatbot.
Tests all 7 required scenarios:
1. Question in English -> English answer.
2. Question in Telugu -> Telugu answer.
3. Question in Hindi -> Hindi answer.
4. Mixed Telugu-English and Hindi-English questions.
5. English question with explicit Telugu preference request.
6. Personal attendance and CGPA accuracy using real authenticated student database records
   (Aarav Reddy / student001 vs. Kabir Mehta / student008).
7. Confirmation that existing dashboard, login, and features remain functional.
"""

import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import app
from database.db import get_db

def test_multilingual_student_chatbot():
    client = app.test_client()

    # -------------------------------------------------------------
    # Setup: Log in as student001 (Aarav Reddy: CSE, 94.0% Att, 8.85 CGPA, 0 Backlogs)
    # -------------------------------------------------------------
    client.get("/logout")
    login_res = client.post("/login", json={"user_id": "student001", "password": "Student@123"})
    assert login_res.status_code == 200, "Student001 login failed"

    # 1. Ask in English and receive English answer
    res_en = client.post("/api/student/chat", json={"message": "What is my attendance rate?"})
    assert res_en.status_code == 200
    data_en = res_en.get_json()
    assert data_en["language"] == "english"
    assert "94.0%" in data_en["reply"] or "94%" in data_en["reply"]
    assert "Aarav" in data_en["reply"]

    # 2. Ask in Telugu and receive Telugu answer
    res_te = client.post("/api/student/chat", json={"message": "నా అటెండెన్స్ ఎంత?"})
    assert res_te.status_code == 200
    data_te = res_te.get_json()
    assert data_te["language"] == "telugu"
    assert "94.0%" in data_te["reply"] or "94%" in data_te["reply"]
    assert "హాజరు" in data_te["reply"] or "నమస్కారం" in data_te["reply"]
    assert "Aarav" in data_te["reply"]

    # 3. Ask in Hindi and receive Hindi answer
    res_hi = client.post("/api/student/chat", json={"message": "मेरी उपस्थिति कितनी है?"})
    assert res_hi.status_code == 200
    data_hi = res_hi.get_json()
    assert data_hi["language"] == "hindi"
    assert "94.0%" in data_hi["reply"] or "94%" in data_hi["reply"]
    assert "उपस्थिति" in data_hi["reply"] or "नमस्ते" in data_hi["reply"]
    assert "Aarav" in data_hi["reply"]

    # 4. Ask mixed Telugu-English and Hindi-English questions
    # Mixed Teluglish
    res_teluglish = client.post("/api/student/chat", json={"message": "naa attendance ela undi?"})
    assert res_teluglish.status_code == 200
    data_teluglish = res_teluglish.get_json()
    assert data_teluglish["language"] in ["teluglish", "telugu"]
    assert "94" in data_teluglish["reply"]

    # Mixed Hinglish
    res_hinglish = client.post("/api/student/chat", json={"message": "mera cgpa kitna hai?"})
    assert res_hinglish.status_code == 200
    data_hinglish = res_hinglish.get_json()
    assert data_hinglish["language"] in ["hinglish", "hindi"]
    assert "9.1" in data_hinglish["reply"]

    # 5. Ask in English but explicitly request a Telugu answer
    res_exp_te = client.post("/api/student/chat", json={"message": "Explain my academic marks in Telugu."})
    assert res_exp_te.status_code == 200
    data_exp_te = res_exp_te.get_json()
    assert data_exp_te["language"] == "telugu"
    assert "CGPA" in data_exp_te["reply"] or "మార్కులు" in data_exp_te["reply"]
    assert "Aarav" in data_exp_te["reply"]

    # Follow-up test: Next message without explicit request inherits Telugu preference
    res_followup = client.post("/api/student/chat", json={"message": "timetable"})
    assert res_followup.status_code == 200
    assert res_followup.get_json()["language"] == "telugu"
    assert "టైమ్‌టేబుల్" in res_followup.get_json()["reply"] or "ఉదయం" in res_followup.get_json()["reply"]

    # Switch back to English explicitly
    res_switch_en = client.post("/api/student/chat", json={"message": "Please answer in English."})
    assert res_switch_en.status_code == 200
    assert res_switch_en.get_json()["language"] == "english"

    # -------------------------------------------------------------
    # 6. Verify with different student: Kabir Mehta (CIQ-2026-008)
    #    (High risk, 68% attendance, 3 backlogs: CS102, CS202, CS206)
    # -------------------------------------------------------------
    client.get("/logout")
    client.post("/login", json={"user_id": "student008", "password": "Student@123"})

    # Check Kabir's backlogs in English
    res_kabir_en = client.post("/api/student/chat", json={"message": "How many backlogs do I have?"})
    assert res_kabir_en.status_code == 200
    data_k_en = res_kabir_en.get_json()
    assert "3" in data_k_en["reply"]
    assert "Kabir" in data_k_en["reply"]

    # Check Kabir's attendance in Telugu (should flag warning about < 75%)
    res_kabir_te = client.post("/api/student/chat", json={"message": "నా అటెండెన్స్ ఎంత ఉంది?"})
    assert res_kabir_te.status_code == 200
    data_k_te = res_kabir_te.get_json()
    assert data_k_te["language"] in ["telugu", "teluglish"]
    assert "68" in data_k_te["reply"]
    assert "హెచ్చరిక" in data_k_te["reply"] or "తక్కువ" in data_k_te["reply"]

    # Check Kabir's backlogs in Hindi
    res_kabir_hi = client.post("/api/student/chat", json={"message": "मेरे बैकलॉग कितने हैं?"})
    assert res_kabir_hi.status_code == 200
    data_k_hi = res_kabir_hi.get_json()
    assert data_k_hi["language"] == "hindi"
    assert "3" in data_k_hi["reply"]
    assert "बैकलॉग" in data_k_hi["reply"]

    # -------------------------------------------------------------
    # 7. Confirm existing login and dashboard features still work
    # -------------------------------------------------------------
    # Student dashboard loads
    dash = client.get("/student")
    assert dash.status_code == 200
    assert "Kabir Mehta" in dash.data.decode("utf-8")

    # Fee details intact
    fees = client.get("/api/student/fee-details")
    assert fees.status_code == 200
    assert "records" in fees.get_json()

    # Skills intact
    skills = client.get("/api/student/skills")
    assert skills.status_code == 200

    # Academic records intact
    records = client.get("/api/student/academic-records")
    assert records.status_code == 200
    assert len(records.get_json()["records"]) > 0
