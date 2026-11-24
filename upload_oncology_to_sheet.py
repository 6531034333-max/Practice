# -*- coding: utf-8 -*-
"""
Upload PT2 Comprehensive Oncology Exam Question Bank to Quiz Google Sheet.
With PLE CC Multi-Section Explanation Template.
Spreadsheet ID: 1EEkYzLVM7yxVyXG1H3AZJgGw9v91tGFRH3bhtmnPVVY
Tab Name: 14. Oncologic
"""
import os, sys, re, json
from google.oauth2 import service_account
from googleapiclient.discovery import build

sys.stdout.reconfigure(encoding='utf-8')

CREDS_FILE = 'C:/Users/thana/Desktop/PLE-CC/gemini-sheets-editor-497118-060a7f15daf9.json'
SPREADSHEET_ID = '1EEkYzLVM7yxVyXG1H3AZJgGw9v91tGFRH3bhtmnPVVY'
TARGET_SHEET = '14. Oncologic'
MD_PATH = 'C:/Users/thana/Desktop/PharmaCU_Workspace/Pharmacy Book/IDT/Oncology/PT 2/PT2_ONCOLOGY_EXAM_QUESTION_BANK_COMPREHENSIVE.md'

print("=" * 65)
print("  🚀 Uploading PT2 Oncology Exam Bank (PLE CC Template) to Google Sheet")
print(f"  Spreadsheet : {SPREADSHEET_ID}")
print(f"  Target Tab  : {TARGET_SHEET}")
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

print(f"Parsed {len(questions)} questions from Markdown.")

LETTER_MAP = {'A': 'ก', 'B': 'ข', 'C': 'ค', 'D': 'ง', 'E': 'จ'}
INDEX_TO_THAI = {1: 'ก', 2: 'ข', 3: 'ค', 4: 'ง', 5: 'จ'}

def parse_explanation_sections(exp_raw, ans_num, ans_text, choices):
    if not exp_raw:
        ans_th = INDEX_TO_THAI.get(ans_num, 'ก')
        return f"✅ คำตอบที่ถูกต้อง: ข้อ {ans_th}. {ans_text}"

    why_correct = ""
    distractor_analysis = ""
    pearl = ""
    guideline = ""

    m_correct = re.search(r'-\s*\*\*เหตุผลข้อที่ถูก[^*]*\:\*\*\s*(.*?)(?=\n-\s*\*\*วิเคราะห์ตัวเลือก|\n-\s*\*\*ประเด็น|\Z)', exp_raw, re.DOTALL)
    if m_correct:
        why_correct = m_correct.group(1).strip()
    
    m_dist = re.search(r'-\s*\*\*วิเคราะห์ตัวเลือกที่ผิด[^*]*\:\*\*\s*(.*?)(?=\n-\s*\*\*ประเด็น|\nอ้างอิง|\Z)', exp_raw, re.DOTALL)
    if m_dist:
        distractor_analysis = m_dist.group(1).strip()
    
    m_pearl = re.search(r'-\s*\*\*ประเด็นทางเภสัชบำบัด[^*]*\:\*\*\s*(.*?)(?=\nอ้างอิง|\Z)', exp_raw, re.DOTALL)
    if m_pearl:
        pearl = m_pearl.group(1).strip()
    else:
        m_pearl2 = re.search(r'\*\*ประเด็น[^*]*\:\*\*\s*(.*?)(?=\nอ้างอิง|\Z)', exp_raw, re.DOTALL)
        if m_pearl2:
            pearl = m_pearl2.group(1).strip()
            
    m_ref = re.search(r'อ้างอิง\s*:\s*(.*)', exp_raw, re.DOTALL)
    if m_ref:
        guideline = m_ref.group(1).strip()

    why_correct_clean = why_correct.replace('\n  ', '\n').replace('\n- ', '\n• ').strip()

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
    dist_text = '\n'.join(dist_lines)

    pearl_clean = re.sub(r'^-\s*\*\*[^:]+:\*\*\s*', '', pearl).replace('\n  ', '\n').replace('\n- ', '\n• ').strip()
    guideline_clean = re.sub(r'^---\s*$', '', guideline).strip()

    ans_th = INDEX_TO_THAI.get(ans_num, 'ก')
    sections = [
        f"✅ คำตอบที่ถูกต้อง: ข้อ {ans_th}. {ans_text}"
    ]
    
    if why_correct_clean:
        sections.append(f"🎯 ทำไมข้อนี้ถึงถูก:\n{why_correct_clean}")
    
    if dist_text:
        sections.append(f"🔍 ข้ออื่นผิดเพราะอะไร:\n{dist_text}")
        
    if pearl_clean:
        sections.append(f"📌 จุดจำก่อนสอบ:\n{pearl_clean}")
        
    if guideline_clean:
        sections.append(f"📖 Guideline อ้างอิง:\n{guideline_clean}")

    return '\n\n'.join(sections)

rows = []
for idx, q in enumerate(questions):
    item_no = idx + 1
    body = q['body']

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

    choices = []
    for c_letter in ['A', 'B', 'C', 'D', 'E']:
        m_opt = re.search(rf'-\s*{c_letter}\.\s*(.*?)(?=\n\s*-\s*[B-E]\.|\n\s*\*\*เฉลย|\n\n|\Z)', body, re.DOTALL)
        if m_opt:
            choices.append(re.sub(r'\*+$', '', m_opt.group(1).strip()).strip())
        else:
            choices.append('')

    ans_key = 1
    m_ans = re.search(r'\*\*เฉลย[^*]*\:\*\*\s*([A-E1-5])', body)
    if m_ans:
        mapping = {'A':1, 'B':2, 'C':3, 'D':4, 'E':5, '1':1, '2':2, '3':3, '4':4, '5':5}
        ans_key = mapping.get(m_ans.group(1).upper(), 1)

    correct_choice_text = choices[ans_key - 1] if ans_key - 1 < len(choices) else ''
    exp_formatted = parse_explanation_sections(body, ans_key, correct_choice_text, choices)

    mod_clean = re.sub(r'Module\s+\d+\:\s*', '', q['module'])
    mod_clean = re.sub(r'—.*$', '', mod_clean)
    mod_clean = re.sub(r'\(ข้อ.*$', '', mod_clean).strip()
    if not mod_clean:
        mod_clean = 'Oncology'

    row = [
        item_no,
        "",
        stem,
        "",
        choices[0] if len(choices) > 0 else "",
        choices[1] if len(choices) > 1 else "",
        choices[2] if len(choices) > 2 else "",
        choices[3] if len(choices) > 3 else "",
        choices[4] if len(choices) > 4 else "",
        ans_key,
        exp_formatted,
        "",
        "14. Oncologic",
        mod_clean,
        "Clinic",
        "PT2 Oncology Exam Question Bank",
        "MCQ",
        "2567 / Final",
        f"ONCO_Q{item_no}"
    ]
    rows.append(row)

creds = service_account.Credentials.from_service_account_file(
    CREDS_FILE, scopes=['https://www.googleapis.com/auth/spreadsheets']
)
service = build('sheets', 'v4', credentials=creds)

banner_row = ['🏠 กลับสู่หน้าแรก (Go to Home Page)'] + [''] * 18
header_row = [
    'ลำดับ', 'สถานการณ์เคส / ข้อมูลผู้ป่วย', 'คำถาม', 'รูปถาม',
    'ตัวเลือก 1', 'ตัวเลือก 2', 'ตัวเลือก 3', 'ตัวเลือก 4', 'ตัวเลือก 5',
    'เฉลย (ตัวเลข 1-5)', 'คำอธิบายเฉลย', 'รูปเฉลย',
    'หัวข้อโรคสภาฯ', 'หัวข้อย่อย', 'Product / Clinic', 'หมายเหตุ',
    'ประเภทข้อสอบ', 'ปี / เลขชุด', 'Case ID (รหัสเคส)'
]

all_sheet_values = [banner_row, header_row] + rows

print(f"Writing {len(all_sheet_values)} rows to '{TARGET_SHEET}'!A1...")
service.spreadsheets().values().update(
    spreadsheetId=SPREADSHEET_ID,
    range=f"'{TARGET_SHEET}'!A1:S{len(all_sheet_values)}",
    valueInputOption='RAW',
    body={'values': all_sheet_values}
).execute()

print(f"🎉 SUCCESS! {len(rows)} questions fully updated with PLE CC explanation templates in Google Sheet '{TARGET_SHEET}'!")
