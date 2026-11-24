# -*- coding: utf-8 -*-
"""
Compile PT2 Comprehensive Oncology Exam Question Bank into quiz-data-offline.js
With PLE CC Multi-Section Explanation Template:
- ✅ คำตอบที่ถูกต้อง
- 🎯 ทำไมข้อนี้ถึงถูก
- 🔍 ข้ออื่นผิดเพราะอะไร
- 📌 จุดจำก่อนสอบ
- 📖 Guideline อ้างอิง
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
print("  🚀 Compiling PT2 Oncology Exam Question Bank (PLE CC Template)")
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

LETTER_MAP = {'A': 'ก', 'B': 'ข', 'C': 'ค', 'D': 'ง', 'E': 'จ'}
INDEX_TO_LETTER = {1: 'A', 2: 'B', 3: 'C', 4: 'D', 5: 'E'}
INDEX_TO_THAI = {1: 'ก', 2: 'ข', 3: 'ค', 4: 'ง', 5: 'จ'}

def parse_explanation_sections(exp_raw, ans_num, ans_text, choices):
    if not exp_raw:
        ans_th = INDEX_TO_THAI.get(ans_num, 'ก')
        return f"✅ คำตอบที่ถูกต้อง: ข้อ {ans_th}. {ans_text}"

    why_correct = ""
    distractor_analysis = ""
    pearl = ""
    guideline = ""

    # 1. Why correct
    m_correct = re.search(r'-\s*\*\*เหตุผลข้อที่ถูก[^*]*\:\*\*\s*(.*?)(?=\n-\s*\*\*วิเคราะห์ตัวเลือก|\n-\s*\*\*ประเด็น|\Z)', exp_raw, re.DOTALL)
    if m_correct:
        why_correct = m_correct.group(1).strip()
    
    # 2. Distractor analysis
    m_dist = re.search(r'-\s*\*\*วิเคราะห์ตัวเลือกที่ผิด[^*]*\:\*\*\s*(.*?)(?=\n-\s*\*\*ประเด็น|\nอ้างอิง|\Z)', exp_raw, re.DOTALL)
    if m_dist:
        distractor_analysis = m_dist.group(1).strip()
    
    # 3. Clinical Pearl
    m_pearl = re.search(r'-\s*\*\*ประเด็นทางเภสัชบำบัด[^*]*\:\*\*\s*(.*?)(?=\nอ้างอิง|\Z)', exp_raw, re.DOTALL)
    if m_pearl:
        pearl = m_pearl.group(1).strip()
    else:
        m_pearl2 = re.search(r'\*\*ประเด็น[^*]*\:\*\*\s*(.*?)(?=\nอ้างอิง|\Z)', exp_raw, re.DOTALL)
        if m_pearl2:
            pearl = m_pearl2.group(1).strip()
            
    # 4. Guideline / Ref
    m_ref = re.search(r'อ้างอิง\s*:\s*(.*)', exp_raw, re.DOTALL)
    if m_ref:
        guideline = m_ref.group(1).strip()

    # Format why_correct: convert markdown sub-bullets
    why_correct_clean = why_correct.replace('\n  ', '\n').replace('\n- ', '\n• ').strip()
    why_correct_html = why_correct_clean.replace('\n\n', '<br><br>').replace('\n', '<br>')

    # Format distractor_analysis:
    dist_lines = []
    for line in distractor_analysis.splitlines():
        line_s = line.strip()
        if not line_s:
            continue
        line_s = re.sub(r'^-\s*\*\*ตัวเลือก\s*([A-E])\s*(?:ผิดเพราะ)?\s*:\*\*', r'• ข้อ \1.', line_s)
        for l_en, l_th in LETTER_MAP.items():
            if f'• ข้อ {l_en}.' in line_s:
                c_idx = ord(l_en) - ord('A')
                c_val = choices[c_idx] if choices and c_idx < len(choices) else ''
                if c_val:
                    c_short = c_val[:45] + ('...' if len(c_val) > 45 else '')
                    line_s = line_s.replace(f'• ข้อ {l_en}.', f'• ข้อ {l_th}. ({c_short}):')
                else:
                    line_s = line_s.replace(f'• ข้อ {l_en}.', f'• ข้อ {l_th}.')
                break
        dist_lines.append(line_s)
    dist_html = '<br>'.join(dist_lines)

    # Format pearl
    pearl_clean = re.sub(r'^-\s*\*\*[^:]+:\*\*\s*', '', pearl).replace('\n  ', '\n').replace('\n- ', '\n• ').strip()
    pearl_html = pearl_clean.replace('\n\n', '<br><br>').replace('\n', '<br>')

    # Format guideline
    guideline_clean = re.sub(r'^---\s*$', '', guideline).strip()
    guideline_html = guideline_clean.replace('\n', '<br>').strip()

    # Build final PLE CC segmented template
    ans_th = INDEX_TO_THAI.get(ans_num, 'ก')
    sections = [
        f"✅ คำตอบที่ถูกต้อง: ข้อ {ans_th}. {ans_text}"
    ]
    
    if why_correct_html:
        sections.append(f"🎯 ทำไมข้อนี้ถึงถูก:<br>{why_correct_html}")
    
    if dist_html:
        sections.append(f"🔍 ข้ออื่นผิดเพราะอะไร:<br>{dist_html}")
        
    if pearl_html:
        sections.append(f"📌 จุดจำก่อนสอบ:<br>{pearl_html}")
        
    if guideline_html:
        sections.append(f"📖 Guideline อ้างอิง:<br>{guideline_html}")

    return '<br><br>'.join(sections)


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

    stem = re.sub(r'^[*\s]+โจทย์[^*]*\:[*\s]*', '', stem).strip()

    # Choices A-E
    choices = []
    for c_letter in ['A', 'B', 'C', 'D', 'E']:
        m_opt = re.search(rf'-\s*{c_letter}\.\s*(.*?)(?=\n\s*-\s*[B-E]\.|\n\s*\*\*เฉลย|\n\n|\Z)', body, re.DOTALL)
        if m_opt:
            c_text = re.sub(r'\*+$', '', m_opt.group(1).strip()).strip()
            choices.append(c_text)
        else:
            choices.append('')

    # Answer
    ans_key = 1
    m_ans = re.search(r'\*\*เฉลย[^*]*\:\*\*\s*([A-E1-5])', body)
    if m_ans:
        mapping = {'A':1, 'B':2, 'C':3, 'D':4, 'E':5, '1':1, '2':2, '3':3, '4':4, '5':5}
        ans_key = mapping.get(m_ans.group(1).upper(), 1)

    correct_choice_text = choices[ans_key - 1] if ans_key - 1 < len(choices) else ''

    # Explanation with PLE CC segmented template
    exp_formatted = parse_explanation_sections(body, ans_key, correct_choice_text, choices)

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
        "explanation": exp_formatted,
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
 * 📝 PLE-CC Quiz Practice -- Auto-compiled Offline Database (PLE CC Multi-Section Template)
 * Total Questions: {len(records)} across 1 Category ({CATEGORY_NAME})
 * Build Timestamp: {now_str} (UTC+7)
 * Build Source: PT2_ONCOLOGY_EXAM_QUESTION_BANK_COMPREHENSIVE.md
 * Google Sheet ID: {SPREADSHEET_ID}
 */

window.QUIZ_GOOGLE_SHEET_ID = "{SPREADSHEET_ID}";
window.QUIZ_GAS_SCRIPT_ID = "{GAS_SCRIPT_ID}";
window.QUIZ_GAS_WEBAPP_URL = "{GAS_WEBAPP_URL}";
window.QUIZ_BUILD_TIMESTAMP = "{now_str}";
window.QUIZ_BUILD_SOURCE = "PT2 Comprehensive Oncology Exam Bank (PLE CC Template)";
window.QUIZ_TOTAL_QUESTIONS = {len(records)};

window.QUIZ_OFFLINE_CATEGORIES = {json.dumps(categories_meta, ensure_ascii=False, indent=2)};

window.QUIZ_OFFLINE_QUESTIONS = {json.dumps(questions_by_cat, ensure_ascii=False, indent=2)};

window.QUIZ_OFFLINE_DB = {json.dumps(records, ensure_ascii=False, indent=2)};
"""

with open(OUTPUT_JS, 'w', encoding='utf-8') as f:
    f.write(header_comment)

print(f"✅ Successfully compiled {len(records)} oncology questions with PLE CC explanation template to {OUTPUT_JS} ({os.path.getsize(OUTPUT_JS):,} bytes)")
