# ESL Student Profile Creator (esl-student)

## Trigger
User commands `/esl-student <student_name>`
Example: `/esl-student Leon`

## Role
You help the teacher create a new student profile by asking a short series of questions, then generating a well-structured Markdown profile saved to `students/<name>.md`.

## Workflow

### 1. Check if profile already exists
Use the `Read` tool to check if `students/<student_name>.md` already exists.
- If it exists, warn the teacher and ask if they want to update it or cancel.
- If it doesn't exist, proceed to the interview.

### 2. Interview the teacher
Ask the following questions one at a time (or grouped logically). Accept answers in English or Chinese. When using AskUserQuestion, use the following standardized options (remember that AskUserQuestion only allows up to 4 options, and the last option should usually be 'Other' to allow free text input):

1. **What is the student's occupation?** (職業)
   - Tech / IT
   - Education
   - Student
   - Other
2. **What is their current level?** (Note: AskUserQuestion max 4 options, 'Other' is auto-added)
   - A1-A2 (Beginner)
   - A2-B1 (Pre-Intermediate)
   - B1-B2 (Intermediate)
   - C1+ (Advanced)
3. **What is their learning goal?** (學習目標)
   - Daily Conversation
   - Business English
   - Bilingual Teaching
   - Other
4. **What should the class focus on?** (上課重點)
   - Speaking & Listening
   - Reading & Writing
   - Grammar
   - Other
5. **Any personal background that's useful for lesson planning?** (個人背景 — e.g., job details, hobbies, lifestyle, schedule. This helps pick relevant topics.)
   - Add Details (Provide free text)
   - Skip
6. **Any known weaknesses?** (薄弱項 — e.g., tense switching, prepositions, phrasal verbs, pronunciation)
   - Grammar Issues (tenses, prepositions, etc.)
   - Vocabulary / Word Choice
   - Pronunciation
   - Other

### 3. Generate the profile
Create the profile using this exact format (matching `students/Hsuan.md`):

```markdown
# 📝 學生學習檔案 (Student Profile)

## 基本資訊
* **姓名:** [Name]
* **職業:** [Occupation]
* **當前程度:** [CEFR Level]
* **學習目標:** [Learning Goal]
* **上課重點:** [Class Focus]
* **個人背景:** [Personal Background]

---

## 📈 進度摘要
* **已掌握:** (to be filled after lessons)
* **持續練習中:** (to be filled after lessons)
* **薄弱項:** [Known Weaknesses from interview]
* **下節重點建議:** First lesson — assess actual level and establish baseline

---

## 📅 課程記錄

*(No lessons yet)*
```

### 4. Save the file
Write the profile to `students/<student_name>.md` using the `Write` tool.

### 5. Confirm
Tell the teacher:
> ✅ Student profile for **[Name]** created at `students/[Name].md`
> Ready to use with `/esl-prep [Name]` or `/esl-plan [Name]`.

## Notes
- Keep 進度摘要 (Progress Summary) mostly empty for new students — it gets filled in after lessons.
- The 薄弱項 (Weaknesses) should include anything the teacher already knows from placement tests, trial lessons, or initial impressions.
- 課程記錄 (Lesson History) starts empty — the `/lesson` skill fills this in after each class.
- **下節建議 rule:** In the 課程記錄 section, only the **most recent lesson** should have a `* **下節建議:**` line. All older lessons should NOT include it. When adding a new lesson entry, remove the `下節建議` line from the previously most recent lesson.
