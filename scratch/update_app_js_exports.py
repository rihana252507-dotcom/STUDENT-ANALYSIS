with open('static/js/app.js', 'r', encoding='utf-8') as f:
    text = f.read()

target = '''  window.exportCohortCSV = function() {
    window.location.href = `/api/export/csv?department=${STATE.activeDept}&risk_level=${STATE.activeRisk}`;
  };'''

replacement = '''  window.exportCohortCSV = function() {
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
  };'''

if target in text:
    text = text.replace(target, replacement, 1)
    with open('static/js/app.js', 'w', encoding='utf-8') as f:
        f.write(text)
    print("SUCCESS: static/js/app.js updated with Excel and Risk export functions!")
else:
    print("WARNING: target not found in static/js/app.js")
