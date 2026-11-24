# -*- coding: utf-8 -*-
"""
Helper to prepare CASE PT2 questions for Practice Quiz Web App
"""
import sys, re
sys.path.append('C:/Users/thana/Desktop/PharmaCU_Workspace/Pharmacy Book/IDT/Oncology/PT 2')
import build_case_pt2_exam as b

LETTER_TO_INDEX = {'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5}
INDEX_TO_THAI = {1: 'ก', 2: 'ข', 3: 'ค', 4: 'ง', 5: 'จ'}

def get_subtopic(q_num, case_name):
    if q_num <= 5:
        return "CASE PT2: 1. Nasopharyngeal Carcinoma (NPC)"
    elif q_num <= 9:
        return "CASE PT2: 2. Relapsed APL (Acute Promyelocytic Leukemia)"
    elif q_num <= 13:
        return "CASE PT2: 3. NSCLC with Brain Metastases"
    elif q_num <= 18:
        return "CASE PT2: 4. Metastatic Colorectal Cancer (mCRC)"
    elif q_num <= 22:
        return "CASE PT2: 5. Relapsed Hodgkin Lymphoma in Obesity"
    elif q_num <= 25:
        return "CASE PT2: 6. Recurrent Renal Cell Carcinoma (RCC)"
    else:
        return "CASE PT2: 7. Comprehensive Case Synthesis"

def build_case_records(start_item_no=226):
    records = []
    for idx, q in enumerate(b.QUESTIONS):
        item_no = start_item_no + idx
        ans_num = LETTER_TO_INDEX.get(q['answer'], 1)
        ans_th = INDEX_TO_THAI.get(ans_num, 'ก')
        
        # Clean options: remove leading 'A. ', 'B. ' etc.
        cleaned_choices = []
        for opt in q['options']:
            c_text = re.sub(r'^[A-E]\.\s*', '', opt).strip()
            cleaned_choices.append(c_text)
            
        correct_choice_text = cleaned_choices[ans_num - 1]
        
        # Format explanation with PLE CC Segmented Template
        rationale_html = q['rationale'].strip().replace('\n\n', '<br><br>').replace('\n', '<br>')
        trap_html = q['trap'].strip().replace('\n\n', '<br><br>').replace('\n', '<br>')
        
        scenario_clean = q['scenario'].strip().replace('\n', '<br>')
        case_clean = q['case'].strip()
        
        explanation_parts = [
            f"✅ คำตอบที่ถูกต้อง: ข้อ {ans_th}. {correct_choice_text}",
            f"🎯 ทำไมข้อนี้ถึงถูก:<br>{rationale_html}",
            f"📌 จุดจำก่อนสอบ / กับดักข้อสอบ:<br>{trap_html}",
            f"📖 บริบทกรณีศึกษาจากอาจารย์ผู้สอน:<br><b>{case_clean}</b><br>{scenario_clean}"
        ]
        explanation = "<br><br>".join(explanation_parts)
        
        rec = {
            "id": f"14. Oncologic::{item_no + 2}",
            "itemNo": item_no,
            "category": "14. Oncologic",
            "topic": "Oncologic",
            "subtopic": get_subtopic(q['q_num'], q['case']),
            "track": "Clinic",
            "caseContext": case_clean,
            "caseStem": q['scenario'],
            "question": q['question'],
            "questionImage": "",
            "choices": cleaned_choices,
            "answer": ans_num,
            "explanation": explanation,
            "answerImage": "",
            "examType": "PT2 Oncology Case Exam",
            "examYear": "2567 / Final",
            "caseGroupId": f"PT2_CASE_{((q['q_num']-1)//5)+1}",
            "caseOrder": q['q_num'],
            "caseTotal": 26
        }
        records.append(rec)
    return records

if __name__ == '__main__':
    recs = build_case_records()
    print(f"Generated {len(recs)} case records.")
    print("Sample Q226:")
    print("ID:", recs[0]['id'])
    print("Subtopic:", recs[0]['subtopic'])
    print("Question:", recs[0]['question'])
    print("Answer:", recs[0]['answer'], f"({INDEX_TO_THAI[recs[0]['answer']]})")
    print("Choices count:", len(recs[0]['choices']))
    print("Explanation preview:\n", recs[0]['explanation'][:300])
