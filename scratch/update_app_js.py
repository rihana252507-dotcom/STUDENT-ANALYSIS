with open('static/js/app.js', 'r', encoding='utf-8') as f:
    text = f.read()

target1 = """  // If on Student dashboard, initialize radar chart and personal simulator
  if (document.getElementById("studentPillarRadarChart")) {
    initStudentRadar();
    initPersonalSimulator();
  }"""

replacement1 = """  // If on Student dashboard, initialize radar chart and personal simulator
  if (document.getElementById("studentPillarRadarChart")) {
    initStudentRadar();
  }
  if (window.STUDENT_DATA || document.getElementById("personalRangeAttendance")) {
    initPersonalSimulator();
  }"""

target2 = """    if (res.ok) {
      const data = await res.json();
      setTxt("personalProjectedScore", data.simulated.success_score);
      setTxt("personalDeltaText", `(+${data.score_delta} pts)`);
      const badge = document.getElementById("personalProjectedBadge");
      if (badge) {
        badge.className = `badge badge-${data.simulated.risk_level.toLowerCase()}`;
        badge.textContent = `${data.simulated.risk_level} Risk`;
      }
    }"""

replacement2 = """    if (res.ok) {
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
    }"""

target3 = """  // Simulator Modal Open/Close
  const btnOpenSim = document.getElementById("btnOpenSimulator") || document.getElementById("btnOpenStudentSim");
  const simModal = document.getElementById("simulatorModal");
  const btnCloseSim = document.getElementById("btnCloseSimulator");
  if (btnOpenSim && simModal) {
    btnOpenSim.addEventListener("click", () => { simModal.style.display = "flex"; });
    if (btnCloseSim) btnCloseSim.addEventListener("click", () => { simModal.style.display = "none"; });
    simModal.addEventListener("click", (e) => { if (e.target === simModal) simModal.style.display = "none"; });
  }"""

replacement3 = """  // Simulator Modal Open/Close (Admin) & Topbar What-If Simulator (Student)
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
  }"""

assert target1 in text, "target1 not found"
assert target2 in text, "target2 not found"
assert target3 in text, "target3 not found"

text = text.replace(target1, replacement1)
text = text.replace(target2, replacement2)
text = text.replace(target3, replacement3)

with open('static/js/app.js', 'w', encoding='utf-8') as f:
    f.write(text)

print("Update completed successfully!")
