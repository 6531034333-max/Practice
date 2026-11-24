# 🎓 PharmaCU Practice Hub (2-in-1 Web Application)

ระบบคลังข้อสอบและแฟลชการ์ดสำหรับเตรียมสอบใบประกอบวิชาชีพเภสัชกรรม (PLE-CC) รวมทั้ง 2 ระบบในเว็บเดียว รองรับการใช้งานแบบ Offline (PWA) และเชื่อมต่อ Google Sheets ส่วนตัว

🌐 **Live Website:** [https://6531034333-max.github.io/Practice/](https://6531034333-max.github.io/Practice/)

---

## 📌 โครงสร้างระบบ (System Structure)

1. **`index.html`** — หน้าหลัก Portal รวม 2 ระบบ (คลังข้อสอบ + แฟลชการ์ด) พร้อมแถบสลับระบบแบบ Real-time
2. **`quiz.html`** — ระบบทำข้อสอบจำลอง (PLE-CC Quiz Practice Engine) จับเวลา 30/60/100 ข้อ พร้อมเฉลยละเอียดและ Rationale
3. **`flashcard.html`** — ระบบแฟลชการ์ดทบทวนความจำ (PLE-CC Flashcards) รูปแบบ 3D Flip Card กรอง Subtopics รายวิชา
4. **`quiz-data-offline.js`** — ฐานข้อมูลข้อสอบออฟไลน์ (4,897 ข้อ ใน 32 หมวดวิชา)
5. **`flashcard-data-offline.js`** — ฐานข้อมูลแฟลชการ์ดออฟไลน์ (1,000+ ใบ ใน 28 หมวดวิชา)

---

## 🔗 การเชื่อมต่อ Google Sheets & Apps Script ส่วนตัว

| ระบบ | Google Sheet ID | Google Apps Script ID |
| :--- | :--- | :--- |
| **📝 คลังข้อสอบ (Quiz)** | `1EEkYzLVM7yxVyXG1H3AZJgGw9v91tGFRH3bhtmnPVVY` | `1nJwbleNGtDtRVfxEL8s8QlmG5bkCOog13L-B_U98sCXYrbTXa0Xe72tA` |
| **🗂️ แฟลชการ์ด (Flashcard)** | `1yY5Gnjv0vvtj0036V0bB5wa6kfalPHVFcjFZg1uDXEY` | `1QG2VNof-D8dv9gPSbVvGcZnY9RbEfPsRoewROAo3nFkhP8RehTf3Yfe0` |

---

## 🚀 สคริปต์คำสั่งด่วน (One-Click Batch Scripts)

- `Push_to_GitHub.bat` — Commit & Deploy โค้ดทั้งหมดขึ้น GitHub (`6531034333-max/Practice`)
- `Compile_Quiz.bat` — ดึงข้อมูลสดจาก Google Sheet ข้อสอบมาคอมไพล์เป็น `quiz-data-offline.js`
- `Compile_Flashcard.bat` — ดึงข้อมูลสดจาก Google Sheet แฟลชการ์ดมาคอมไพล์เป็น `flashcard-data-offline.js`
- `Push_Clasp_Quiz.bat` — อัปโหลดโค้ด Apps Script ข้อสอบ
- `Push_Clasp_Flashcard.bat` — อัปโหลดโค้ด Apps Script แฟลชการ์ด
