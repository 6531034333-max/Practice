# -*- coding: utf-8 -*-
"""
Upload PT2 Comprehensive Oncology Exam Question Bank to Quiz Google Sheet.
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
print("  🚀 Uploading PT2 Oncology Exam Bank to Google Sheet")
print(f"  Spreadsheet : {SPREADSHEET_ID}")
print(f"  Target Tab  : {TARGET_SHEET}")
print("=" * 65)

# 1. Parse questions from Markdown
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

# 2. Build rows A to S (19 columns) matching standard PLE CC format
rows = []
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

    # Explanation
    exp = ''
    m_exp = re.search(r'\*\*คำอธิบาย[^*]*\:\*\*\s*(.*)', body, re.DOTALL)
    if m_exp:
        exp = m_exp.group(1).strip()
    else:
        m_exp2 = re.search(r'####\s+คำอธิบาย[^\n]*\n(.*)', body, re.DOTALL)
        if m_exp2:
            exp = m_exp2.group(1).strip()

    # Subtopic
    mod_clean = re.sub(r'Module\s+\d+\:\s*', '', q['module'])
    mod_clean = re.sub(r'—.*$', '', mod_clean)
    mod_clean = re.sub(r'\(ข้อ.*$', '', mod_clean).strip()
    if not mod_clean:
        mod_clean = 'Oncology'

    # Build 19 columns:
    # A: ลำดับ, B: สถานการณ์เคส, C: คำถาม, D: รูปถาม, E: ช้อย1, F: ช้อย2, G: ช้อย3, H: ช้อย4, I: ช้อย5,
    # J: เฉลย 1-5, K: คำอธิบาย, L: รูปเฉลย, M: หัวข้อโรค, N: หัวข้อย่อย, O: Track, P: หมายเหตุ,
    # Q: ประเภทข้อสอบ, R: ปี/ชุด, S: Case ID
    row = [
        item_no,
        "", # Case Context
        stem,
        "", # Question Image
        choices[0] if len(choices) > 0 else "",
        choices[1] if len(choices) > 1 else "",
        choices[2] if len(choices) > 2 else "",
        choices[3] if len(choices) > 3 else "",
        choices[4] if len(choices) > 4 else "",
        ans_key,
        exp,
        "", # Answer Image
        "14. Oncologic",
        mod_clean,
        "Clinic",
        "PT2 Oncology Exam Question Bank",
        "MCQ",
        "2567 / Final",
        f"ONCO_Q{item_no}"
    ]
    rows.append(row)

# 3. Authenticate with Google Sheets API
creds = service_account.Credentials.from_service_account_file(
    CREDS_FILE, scopes=['https://www.googleapis.com/auth/spreadsheets']
)
service = build('sheets', 'v4', credentials=creds)

meta = service.spreadsheets().get(spreadsheetId=SPREADSHEET_ID).execute()
existing_sheets = {s['properties']['title']: s['properties']['sheetId'] for s in meta.get('sheets', [])}

# Ensure TARGET_SHEET exists
sheet_id = existing_sheets.get(TARGET_SHEET)
if sheet_id is None:
    if 'ชีต1' in existing_sheets:
        print(f"Renaming 'ชีต1' to '{TARGET_SHEET}'...")
        res = service.spreadsheets().batchUpdate(
            spreadsheetId=SPREADSHEET_ID,
            body={
                'requests': [{
                    'updateSheetProperties': {
                        'properties': {'sheetId': existing_sheets['ชีต1'], 'title': TARGET_SHEET},
                        'fields': 'title'
                    }
                }]
            }
        ).execute()
        sheet_id = existing_sheets['ชีต1']
    else:
        print(f"Creating new tab '{TARGET_SHEET}'...")
        res = service.spreadsheets().batchUpdate(
            spreadsheetId=SPREADSHEET_ID,
            body={
                'requests': [{
                    'addSheet': {'properties': {'title': TARGET_SHEET}}
                }]
            }
        ).execute()
        sheet_id = res['replies'][0]['addSheet']['properties']['sheetId']

# 4. Prepare Headers (Row 1 Banner, Row 2 Column Names)
banner_row = ['🏠 กลับสู่หน้าแรก (Go to Home Page)'] + [''] * 18
header_row = [
    'ลำดับ', 'สถานการณ์เคส / ข้อมูลผู้ป่วย', 'คำถาม', 'รูปถาม',
    'ตัวเลือก 1', 'ตัวเลือก 2', 'ตัวเลือก 3', 'ตัวเลือก 4', 'ตัวเลือก 5',
    'เฉลย (ตัวเลข 1-5)', 'คำอธิบายเฉลย', 'รูปเฉลย',
    'หัวข้อโรคสภาฯ', 'หัวข้อย่อย', 'Product / Clinic', 'หมายเหตุ',
    'ประเภทข้อสอบ', 'ปี / เลขชุด', 'Case ID (รหัสเคส)'
]

all_sheet_values = [banner_row, header_row] + rows

# 5. Clear and write values
print(f"Clearing old content in '{TARGET_SHEET}'...")
service.spreadsheets().values().clear(
    spreadsheetId=SPREADSHEET_ID,
    range=f"'{TARGET_SHEET}'!A1:S1000"
).execute()

print(f"Writing {len(all_sheet_values)} rows to '{TARGET_SHEET}'!A1...")
service.spreadsheets().values().update(
    spreadsheetId=SPREADSHEET_ID,
    range=f"'{TARGET_SHEET}'!A1:S{len(all_sheet_values)}",
    valueInputOption='RAW',
    body={'values': all_sheet_values}
).execute()

# 6. Apply formatting
print("Applying standard PLE CC styles and cell formats...")
style_reqs = [
    # Banner merge A1:S1
    {
        'mergeCells': {
            'range': {'sheetId': sheet_id, 'startRowIndex': 0, 'endRowIndex': 1, 'startColumnIndex': 0, 'endColumnIndex': 19},
            'mergeType': 'MERGE_ALL'
        }
    },
    # Banner style
    {
        'repeatCell': {
            'range': {'sheetId': sheet_id, 'startRowIndex': 0, 'endRowIndex': 1, 'startColumnIndex': 0, 'endColumnIndex': 19},
            'cell': {
                'userEnteredFormat': {
                    'backgroundColor': {'red': 0.89, 'green': 0.95, 'blue': 0.99},
                    'horizontalAlignment': 'CENTER',
                    'verticalAlignment': 'MIDDLE',
                    'textFormat': {'fontFamily': 'Bai Jamjuree', 'fontSize': 11, 'bold': True, 'foregroundColor': {'red': 0.05, 'green': 0.28, 'blue': 0.63}}
                }
            },
            'fields': 'userEnteredFormat(backgroundColor,horizontalAlignment,verticalAlignment,textFormat)'
        }
    },
    # Header Row 2 style
    {
        'repeatCell': {
            'range': {'sheetId': sheet_id, 'startRowIndex': 1, 'endRowIndex': 2, 'startColumnIndex': 0, 'endColumnIndex': 19},
            'cell': {
                'userEnteredFormat': {
                    'backgroundColor': {'red': 0.08, 'green': 0.40, 'blue': 0.75},
                    'horizontalAlignment': 'CENTER',
                    'verticalAlignment': 'MIDDLE',
                    'textFormat': {'fontFamily': 'Bai Jamjuree', 'fontSize': 10, 'bold': True, 'foregroundColor': {'red': 1.0, 'green': 1.0, 'blue': 1.0}}
                }
            },
            'fields': 'userEnteredFormat(backgroundColor,horizontalAlignment,verticalAlignment,textFormat)'
        }
    },
    # Data Rows: Wrap text, font Bai Jamjuree
    {
        'repeatCell': {
            'range': {'sheetId': sheet_id, 'startRowIndex': 2, 'endRowIndex': len(all_sheet_values), 'startColumnIndex': 0, 'endColumnIndex': 19},
            'cell': {
                'userEnteredFormat': {
                    'wrapStrategy': 'WRAP',
                    'verticalAlignment': 'TOP',
                    'textFormat': {'fontFamily': 'Bai Jamjuree', 'fontSize': 10}
                }
            },
            'fields': 'userEnteredFormat(wrapStrategy,verticalAlignment,textFormat)'
        }
    },
    # Center Col A (Index)
    {
        'repeatCell': {
            'range': {'sheetId': sheet_id, 'startRowIndex': 2, 'endRowIndex': len(all_sheet_values), 'startColumnIndex': 0, 'endColumnIndex': 1},
            'cell': {
                'userEnteredFormat': {
                    'horizontalAlignment': 'CENTER',
                    'textFormat': {'fontFamily': 'Bai Jamjuree', 'fontSize': 10, 'bold': True}
                }
            },
            'fields': 'userEnteredFormat(horizontalAlignment,textFormat)'
        }
    },
    # Center Col J (Answer Key)
    {
        'repeatCell': {
            'range': {'sheetId': sheet_id, 'startRowIndex': 2, 'endRowIndex': len(all_sheet_values), 'startColumnIndex': 9, 'endColumnIndex': 10},
            'cell': {
                'userEnteredFormat': {
                    'horizontalAlignment': 'CENTER',
                    'textFormat': {'fontFamily': 'Bai Jamjuree', 'fontSize': 11, 'bold': True, 'foregroundColor': {'red': 0.08, 'green': 0.5, 'blue': 0.24}}
                }
            },
            'fields': 'userEnteredFormat(horizontalAlignment,textFormat)'
        }
    }
]

service.spreadsheets().batchUpdate(spreadsheetId=SPREADSHEET_ID, body={'requests': style_reqs}).execute()
print(f"🎉 SUCCESS! {len(rows)} questions fully uploaded and styled in Google Sheet '{TARGET_SHEET}'!")
