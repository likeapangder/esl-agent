# ESL Lesson Prep Orchestrator (esl-prep)

## Trigger
User commands `/esl-prep <student_name> <topic_or_materials_path>`
Example: `/esl-prep Hsuan '/path/to/Smartwatches — Ellii.pdf'`

## Role
You are the orchestrator for ESL lesson preparation. Your job is to gather all necessary information, then delegate to the specialized sub-skills in sequence.

## Workflow

### Step 0: Parse Arguments
The user's command is visible in the conversation. It follows the format:
`/esl-prep <student_name> <topic_or_materials_path>`

**Parsing rules:**
- The **student name** is the first word after `/esl-prep` (e.g., `May`, `Hsuan`, `Ariel`).
- The **topic or path** is everything after the student name — could be a quoted file path, a topic keyword, etc.
- Example: `/esl-prep May '/Users/.../Going to the Box Office — Ellii.pdf'` → student = `May`, materials = the file path.

**⚠️ CRITICAL:** The student name and materials are ALREADY in the user's message. Extract them directly from the command text. Do NOT ask the user to re-provide them.

### Step 1: Information Gathering
- **Student Profile:** Use the `Read` tool to open and read `students/<student_name>.md`. Pay strict attention to their Current Level, Learning Goals, Weaknesses (薄弱項), and Recent Progress.
- **Teaching Materials:** If the user provides a path to a PDF (Elli worksheet), use the `Read` tool to extract the content (especially page 1 for the vocabulary preview). If they provide screenshots, analyze them. If they just provide a topic, note that no Elli worksheet is available.

### Step 2: Generate Lesson Plan
Invoke `/esl-plan <student_name> <topic_or_materials_path>` to generate the full lesson plan with QA-checked Canva slide content. Output the exact slide content so the teacher can easily copy-paste it.

### Step 3: Save the Lesson Plan
Automatically use the `Write` tool to save the complete generated lesson plan and slide content as a Markdown file in the `/Users/linhsinpei/esl-agent/plans` directory. Name the file `[StudentName]_[Topic].md`.

## Output
The combined output from the sub-skill:
1. The QA-approved lesson plan (from `/esl-plan`) with copy-paste ready slide text
2. Confirmation that the plan has been saved to the `plans` directory
