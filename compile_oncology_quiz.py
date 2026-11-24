# -*- coding: utf-8 -*-
"""
Compile PT2 Comprehensive Oncology Exam Question Bank into quiz-data-offline.js
Total 225 high-yield oncology questions.
"""
import os, sys, re, json, datetime

sys.stdout.reconfigure(encoding='utf-8')

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
MD_PATH = 'C:/Users/thana/Desktop/PharmaCU_Workspace/Pharmacy Book/IDT/Oncology/PT 2/PT2_ONCOLOGY_EXAM_QUESTION_BANK_COMPREHENSIVE.md'
OUTPUT_JS = os.path.join(CURRENT_DIR, 'quiz-data-offline.js')

SPREADSHEET_ID = '1EEkYzLVM7yxVyXG1H3AZJgGw9v91tGFRH3bhtmnPVVY'
GAS_SCRIPT_ID = '1nJwbleNGtDtRVfxEL8s8QlmG5bkCOog13L-B_U98sCXYrbTXa0Xe72tA'
GAS_WEBAPP_URL = f'https://script.google.com/macros/s/{GAS_SCRIPT_ID}/exec'

print("=" * 65)
print("  🚀 Compiling PT2 Oncology Exam Question Bank into Offline JS")
print(f"  Source MD   : {MD_PATH}")
print(f"  Target File : {OUTPUT_JS}")
print("=" * 65)

with open(MD_PATH, 'r', encoding='utf-8') as f:
    text = f.read()

lines = text.splitlines()
q_header_re = re.compile(r'^###\s+ข้อที่\s+(\d+)(?:\s*\(([^)]+)\))?', re.UNICODE)
mod_re = re.compile(r'^##\s+(Module\s+\d+:[^\n]+)', re.UNICODE)

current_module = 'Module 1: Breast Cancer (มะเร็งเต้านม)'
questions = []
current_q = None
q_text_buffer = []

for line in lines:
    m_mod = mod_re.match(line.strip())
    if m_mod:
        current_module = m_mod.group(1).strip()
        continue
    m_q = q_header_re.match(line.strip())
    if m_q:
        if current_q and q_text_buffer:
            current_q['body'] = '\n'.join(q_text_buffer)
            questions.append(current_q)
            q_text_buffer = []
        current_q = {'num': int(m_q.group(1)), 'module': current_module}
        continue
    if current_q is not None:
        q_text_buffer.append(line)

if current_q and q_text_buffer:
    current_q['body'] = '\n'.join(q_text_buffer)
    questions.append(current_q)

print(f"Parsed {len(questions)} raw questions from markdown.")

CATEGORY_NAME = '14. Oncologic'
records = []

for idx, q in enumerate(questions):
    item_no = idx + 1
    body = q['body']

    # Stem
    stem = ''
    m_stem = re.search(r'\*\*โจทย์[^*]*\:\*\*\s*(.*?)(?=\n\s*(?:-\s*[A-E]\.|\*\*ตัวเลือก))', body, re.DOTALL)
    if m_stem:
        stem = m_stem.group(1).strip()
    else:
        m_c = re.search(r'\n\s*-\s*A\.', body)
        if m_c:
            stem = body[:m_c.start()].replace('**โจทย์:**', '').strip()
        else:
            stem = body[:200].strip()

    # Clean stem formatting
    stem = re.sub(r'^[*\s]+โจทย์[^*]*\:[*\s]*', '', stem)
    stem = stem.strip()

    # Choices A-E
    choices = []
    for c_letter in ['A', 'B', 'C', 'D', 'E']:
        m_opt = re.search(rf'-\s*{c_letter}\.\s*(.*?)(?=\n\s*-\s*[B-E]\.|\n\s*\*\*เฉลย|\n\n|\Z)', body, re.DOTALL)
        if m_opt:
            c_text = m_opt.group(1).strip()
            # Clean trailing asterisks
            c_text = re.sub(r'\*+$', '', c_text).strip()
            choices.append(c_text)
        else:
            choices.append('')

    # Answer
    ans_key = 1
    m_ans = re.search(r'\*\*เฉลย[^*]*\:\*\*\s*([A-E1-5])', body)
    if m_ans:
        letter = m_ans.group(1).upper()
        mapping = {'A':1, 'B':2, 'C':3, 'D':4, 'E':5, '1':1, '2':2, '3':3, '4':4, '5':5}
        ans_key = mapping.get(letter, 1)

    # Explanation
    exp = ''
    m_exp = re.search(r'\*\*คำอธิบาย[^*]*\:\*\*\s*(.*)', body, re.DOTALL)
    if m_exp:
        exp = m_exp.group(1).strip()
    else:
        m_exp2 = re.search(r'####\s+คำอธิบาย[^\n]*\n(.*)', body, re.DOTALL)
        if m_exp2:
            exp = m_exp2.group(1).strip()
    
    # Format explanation to HTML paragraphs/bullets
    exp_html = exp.replace('\n\n', '<br><br>').replace('\n- ', '<br>• ').replace('\n', '<br>')

    # Subtopic clean
    mod_clean = re.sub(r'Module\s+\d+\:\s*', '', q['module'])
    mod_clean = re.sub(r'—.*$', '', mod_clean)
    mod_clean = re.sub(r'\(ข้อ.*$', '', mod_clean).strip()
    if not mod_clean:
        mod_clean = 'Oncology'

    rec = {
        "id": f"{CATEGORY_NAME}::{item_no + 2}",
        "itemNo": item_no,
        "category": CATEGORY_NAME,
        "topic": "Oncologic",
        "subtopic": mod_clean,
        "track": "Clinic",
        "caseContext": "",
        "caseStem": "",
        "question": stem,
        "questionImage": "",
        "choices": choices,
        "answer": ans_key,
        "explanation": exp_html,
        "answerImage": "",
        "examType": "PT2 Oncology Exam",
        "examYear": "2567 / Final",
        "caseGroupId": "",
        "caseOrder": 0,
        "caseTotal": 0
    }
    records.append(rec)

now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

categories_meta = [
    {
        "name": CATEGORY_NAME,
        "count": len(records),
        "track": "Clinic"
    }
]

questions_by_cat = {
    CATEGORY_NAME: records
}

header_comment = f"""/**
 * 📝 PLE-CC Quiz Practice -- Auto-compiled Offline Database (Clean PT2 Oncology Edition)
 * Total Questions: {len(records)} across 1 Category ({CATEGORY_NAME})
 * Build Timestamp: {now_str} (UTC+7)
 * Build Source: PT2_ONCOLOGY_EXAM_QUESTION_BANK_COMPREHENSIVE.md
 * Google Sheet ID: {SPREADSHEET_ID}
 */

window.QUIZ_GOOGLE_SHEET_ID = "{SPREADSHEET_ID}";
window.QUIZ_GAS_SCRIPT_ID = "{GAS_SCRIPT_ID}";
window.QUIZ_GAS_WEBAPP_URL = "{GAS_WEBAPP_URL}";
window.QUIZ_BUILD_TIMESTAMP = "{now_str}";
window.QUIZ_BUILD_SOURCE = "PT2 Comprehensive Oncology Exam Bank";
window.QUIZ_TOTAL_QUESTIONS = {len(records)};

window.QUIZ_OFFLINE_CATEGORIES = {json.dumps(categories_meta, ensure_ascii=False, indent=2)};

window.QUIZ_OFFLINE_QUESTIONS = {json.dumps(questions_by_cat, ensure_ascii=False, indent=2)};

window.QUIZ_OFFLINE_DB = {json.dumps(records, ensure_ascii=False, indent=2)};
"""

with open(OUTPUT_JS, 'w', encoding='utf-8') as f:
    f.write(header_comment)

print(f"✅ Successfully wrote {len(records)} oncology questions to {OUTPUT_JS} ({os.path.getsize(OUTPUT_JS):,} bytes)")
