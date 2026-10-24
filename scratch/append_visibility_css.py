with open('static/css/style.css', 'r', encoding='utf-8') as f:
    css = f.read()

visibility_css = '''

/* ==============================================================================
   CAMPUSIQ GLOBAL TEXT VISIBILITY & CONTRAST ENHANCEMENTS
   Portals: Login, Admin, Faculty, Student, and HOD
   Palette: Enterprise Blue (#2F80ED) + Navy (#123B66) + Teal (#16A6A1)
   ============================================================================== */

/* Modal Headers: Primary Navy background with high-contrast white text */
.glass-modal-header {
  background: #123B66 !important;
  color: #FFFFFF !important;
  border-top-left-radius: var(--radius-lg);
  border-top-right-radius: var(--radius-lg);
  padding: 16px 22px;
}

.glass-modal-header h2,
.glass-modal-header h3,
.glass-modal-header .glass-modal-title {
  color: #FFFFFF !important;
  font-weight: 800;
}

.glass-modal-header p,
.glass-modal-header span:not(.badge) {
  color: #D4E9FF !important;
}

.glass-modal-header .btn-close-modal-icon {
  background: rgba(255, 255, 255, 0.15) !important;
  color: #FFFFFF !important;
  border-radius: 50%;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.25rem;
  border: none;
  cursor: pointer;
  transition: var(--transition);
}

.glass-modal-header .btn-close-modal-icon:hover {
  background: rgba(255, 255, 255, 0.3) !important;
}

/* Modal Body readability */
.glass-modal-body {
  background: #FFFFFF;
  color: #172B4D;
}

.glass-modal-body label {
  color: #172B4D !important;
  font-weight: 700;
}

.glass-modal-body input,
.glass-modal-body select,
.glass-modal-body textarea {
  background: #F4F7FB !important;
  color: #172B4D !important;
  border: 1px solid #DCE4EE !important;
}

.glass-modal-body input:focus,
.glass-modal-body select:focus,
.glass-modal-body textarea:focus {
  border-color: #2F80ED !important;
  box-shadow: 0 0 0 3px rgba(47, 128, 237, 0.20) !important;
}

/* Modal 5 Pillars box: Deep Navy container with white/cyan readable values */
.glass-modal-body div[style*="rgba(35,18,70"],
.glass-modal-body div[style*="background:rgba(35, 18, 70"] {
  background: #123B66 !important;
  border: 1px solid #DCE4EE !important;
}

.glass-modal-body div[style*="rgba(35,18,70"] span,
.glass-modal-body div[style*="background:rgba(35, 18, 70"] span {
  color: #D4E9FF !important;
}

/* Global Select and Option Styling */
select.cyber-select,
.cyber-select {
  background-color: #FFFFFF !important;
  color: #172B4D !important;
  border: 1px solid #DCE4EE !important;
}

select.cyber-select option,
.cyber-select option {
  background-color: #FFFFFF !important;
  color: #172B4D !important;
}

/* Global Table Typography Contrast */
.cyber-table th {
  color: #5B6B82 !important;
  font-weight: 700 !important;
  background: #F9FAFB !important;
}

.cyber-table td {
  color: #172B4D !important;
}

.cyber-table tbody tr:hover {
  background: #F4F7FB !important;
}

/* Faculty Specialization & Advisor Text Contrast */
.faculty-specialization,
.faculty-specialization-text,
#facultyTableBody tr td .faculty-specialization,
#facultyTableBody tr td small,
#hodFacultyTableBody tr td {
  color: #172B4D !important;
  font-weight: 500;
}

/* Intervention Instruction & Notes High Contrast */
#modalIntvDisplayInstructions,
#modalIntvHeaderSub,
.intervention-notes-text {
  color: #D4E9FF !important;
}

/* Input Placeholders Contrast */
::placeholder {
  color: #9CA3AF !important;
  opacity: 1;
}

:-ms-input-placeholder {
  color: #9CA3AF !important;
}

::-ms-input-placeholder {
  color: #9CA3AF !important;
}
'''

if 'CAMPUSIQ GLOBAL TEXT VISIBILITY' not in css:
    css += visibility_css
    with open('static/css/style.css', 'w', encoding='utf-8') as f:
        f.write(css)
    print("Added global text visibility enhancements to static/css/style.css")
else:
    print("Already added")
