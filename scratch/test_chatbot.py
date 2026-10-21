"""
Test Suite for CampusIQ Study Assistant Chatbot
"""
import sys
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

from app import app
import json

def test_chatbot_suite():
    client = app.test_client()

    print("\n--- 1. Testing Authentication & Authorization ---")
    # Unauthenticated request
    res = client.post("/api/student/chat", json={"message": "hello"})
    assert res.status_code == 401, f"Expected 401 for unauth, got {res.status_code}"
    print("Unauthenticated check: OK (401)")

    # Admin role request
    login_res = client.post("/login", json={"user_id": "admin001", "password": "Admin@123"})
    assert login_res.status_code == 200
    res = client.post("/api/student/chat", json={"message": "hello"})
    assert res.status_code == 403, f"Expected 403 for admin, got {res.status_code}"
    print("Admin forbidden check: OK (403)")
    client.get("/logout")

    # Faculty role request
    login_res = client.post("/login", json={"user_id": "faculty001", "password": "Faculty@123"})
    assert login_res.status_code == 200
    res = client.post("/api/student/chat", json={"message": "hello"})
    assert res.status_code == 403, f"Expected 403 for faculty, got {res.status_code}"
    print("Faculty forbidden check: OK (403)")
    client.get("/logout")

    print("\n--- 2. Testing Validation (Empty & Long Messages) ---")
    # Student login (student001)
    login_res = client.post("/login", json={"user_id": "student001", "password": "Student@123"})
    assert login_res.status_code == 200
    print("Student001 login: OK")

    # Empty message
    res = client.post("/api/student/chat", json={"message": "   "})
    assert res.status_code == 400
    print("Empty message rejected: OK (400)")

    # Excessive length (>1000 chars)
    res = client.post("/api/student/chat", json={"message": "a" * 1005})
    assert res.status_code == 400
    print("Overlong message rejected: OK (400)")

    print("\n--- 3. Testing 5 Suggested Questions for student001 (Low Risk, Aarav Reddy) ---")
    questions = [
        "How can I improve my academic performance?",
        "How can I improve my attendance?",
        "Help me make a study plan.",
        "Explain my recommendations.",
        "How can I reduce my academic risk?"
    ]
    for q in questions:
        res = client.post("/api/student/chat", json={"message": q})
        assert res.status_code == 200
        reply = res.get_json().get("reply", "")
        assert len(reply) > 20, f"Reply too short for question '{q}'"
        print(f"Q: '{q}'\nA: {reply[:100]}...\n")

    print("\n--- 4. Testing Custom & Fallback Questions for student001 ---")
    custom_qs = [
        ("Hello", "greeting"),
        ("What is my success score?", "score"),
        ("How is my placement readiness?", "placement"),
        ("What about my LMS activity?", "lms"),
        ("Thank you!", "thanks"),
        ("Can you help me with stress?", "wellbeing"),
        ("Random gibberish xyz123qwerty", "fallback")
    ]
    for q, label in custom_qs:
        res = client.post("/api/student/chat", json={"message": q})
        assert res.status_code == 200
        reply = res.get_json().get("reply", "")
        assert len(reply) > 10
        print(f"[{label}] Q: '{q}' -> A: {reply[:80]}...")

    client.get("/logout")

    print("\n--- 5. Testing Personalization for student008 (High Risk, Kabir Mehta) ---")
    login_res = client.post("/login", json={"user_id": "student008", "password": "Student@123"})
    assert login_res.status_code == 200

    # Test attendance advice for high risk student with low attendance (68%)
    res = client.post("/api/student/chat", json={"message": "How can I improve my attendance?"})
    reply = res.get_json().get("reply", "")
    assert "below the mandatory 75% cutoff" in reply or "shortfall" in reply.lower() or "68" in reply
    print("Student008 Attendance warning in reply: OK")

    # Test backlog advice for student with 3 backlogs
    res = client.post("/api/student/chat", json={"message": "Tell me about my backlogs"})
    reply = res.get_json().get("reply", "")
    assert "3 active backlog" in reply
    print("Student008 Backlog alert in reply: OK")

    # Test risk advice for student008 (High Risk)
    res = client.post("/api/student/chat", json={"message": "How can I reduce my academic risk?"})
    reply = res.get_json().get("reply", "")
    assert "High" in reply
    print("Student008 High risk guidance: OK")

    client.get("/logout")

    print("\n--- 6. Verifying Dashboard Template Integrity ---")
    # Verify student dashboard contains chatbot markup
    client.post("/login", json={"user_id": "student001", "password": "Student@123"})
    res = client.get("/student")
    assert res.status_code == 200
    html = res.data.decode("utf-8")
    assert "CampusIQ Study Assistant" in html
    assert "ciqChatMessages" in html
    assert "ciqChatInput" in html
    assert "ciqChatSend" in html
    assert "chatbot.js" in html
    # Ensure Recommendations section contains chatbot and no old cards
    assert "section-personalized-recommendations" in html
    assert "Tailored Academic Roadmap" not in html
    assert "Welcome back," in html
    assert "Here is your student profile and academic information." in html
    print("Student dashboard contains only chatbot in Recommendations section: OK")

    # Verify admin and faculty dashboard load without chatbot or breaking changes
    client.get("/logout")
    client.post("/login", json={"user_id": "admin001", "password": "Admin@123"})
    res = client.get("/admin")
    assert res.status_code == 200
    admin_html = res.data.decode("utf-8")
    assert "CampusIQ Study Assistant" not in admin_html
    print("Admin dashboard unchanged: OK")

    client.get("/logout")
    client.post("/login", json={"user_id": "faculty001", "password": "Faculty@123"})
    res = client.get("/faculty")
    assert res.status_code == 200
    faculty_html = res.data.decode("utf-8")
    assert "CampusIQ Study Assistant" not in faculty_html
    print("Faculty dashboard unchanged: OK")

    print("\nALL CHATBOT TESTS PASSED SUCCESSFULLY! 🎉\n")

if __name__ == "__main__":
    test_chatbot_suite()
