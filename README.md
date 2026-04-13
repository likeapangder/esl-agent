# Personalized ESL Agent

A robust, local CLI-based agent powered by Claude Code for orchestrating personalized ESL lesson planning, audio transcription, and post-class summary emails.

## 🚀 Features

- **Lesson Planning:** Automatically generates QA-checked, level-appropriate lesson plans based on student profiles and Ellii worksheet PDFs.
- **Canva Integration:** Directly generates Canva presentations from your lesson plans using MCP tools, complete with custom typography rules, and automatically files them into the student's Canva folder.
- **Local Video Transcription:** Runs local `faster-whisper` transcription on your Mac to convert raw lesson video recordings into text transcripts without expensive cloud API costs.
- **Agentic Email Drafting:** Uses a specialized sub-agent to draft highly personalized, bilingual post-class summary emails that capture nuanced linguistic corrections and student progress.
- **Automated Profile Management:** Dynamically creates new student profiles via a short interactive interview, and automatically updates existing profiles with course records after every class.

## 🛠️ Setup

1. Install dependencies for the local transcription tools:
```bash
brew install ffmpeg
pip install faster-whisper anthropic rich
```

2. Run Claude Code in the project directory:
```bash
claude
```

## 📚 Claude Code Skills (Workflows)

This project relies heavily on custom Claude Code Skills to handle complex, multi-step agentic workflows. Run these directly inside the Claude Code prompt.

### 📝 Pre-Class: Lesson Prep
- **`/esl-student <Name>`** - Interactive interview to create a new student profile markdown file.
- **`/esl-prep <Name> "/path/to/worksheet.pdf"`** - The ultimate prep orchestrator. Reads the student's profile (weaknesses, goals, level), analyzes the PDF worksheet, and generates a tailored lesson plan with exact slide content.
- **`/esl-plan <Name> "Topic"`** - Generates just the lesson plan and slide content markdown (no Canva integration).
- **`/esl-canva <Name> plans/<Name>_Lesson.md`** - Reads a saved lesson plan markdown file and uses the Canva MCP to generate a presentation, applying strict styling rules (Century Gothic, bold headers, white background) and filing it in the student's Canva folder.

### 🎬 Post-Class: Auto Lesson Summary
- **`/auto-lesson /path/to/recording.mp4`** - The complete post-class orchestrator.
  1. Extracts audio and transcribes the lesson locally.
  2. Passes the transcript to an agentic email writer to draft a highly accurate bilingual summary email.
  3. Updates the student's profile (`students/*.md`) with the new lesson record and progress notes.
  4. Automatically opens the generated draft in your local Gmail interface via Chrome with the correct date in the subject line.
- **`/transcribe /path/to/recording.mp4`** - Runs only the local media processor to output a raw `.txt` transcript.
- **`/lesson-summary tmp/transcript.txt`** - Runs only the email writer sub-agent on a raw transcript, referencing the `Master_EmailStyle_Guide.md` and user feedback memories for tone.

## 📂 Project Structure

```
esl-agent/
├── README.md                     # This file
├── students/                     # Student profile storage (Markdown files e.g., Ariel.md)
├── plans/                        # Saved generated lesson plans (Markdown files)
├── templates/                    
│   └── Master_EmailStyle_Guide.md# Strict rules for email generation tone and format
├── prompts/                      # Detailed system prompts guiding agent behavior
│   ├── esl-prep.md               
│   ├── esl-plan.md               
│   ├── esl-canva.md              
│   └── esl-student.md            
├── tmp/                          # Temporary storage for transcripts and email drafts
└── .claude/
    ├── memory/                   # File-based auto memory for user preferences (e.g., feedback_email_style.md)
    └── skills/                   # Claude Code Skill definitions and sub-agents
        ├── auto-lesson/          # Post-class orchestrator
        ├── esl-canva/            # Canva MCP presentation generator
        ├── esl-plan/             # Lesson plan generator
        ├── esl-prep/             # Pre-class orchestrator
        ├── esl-student/          # Profile creator
        ├── lesson-summary/       # Email drafting sub-agent
        ├── send-email/           # Gmail opening script handler
        └── transcribe/           # Local transcription runner
```

## 🧑‍🎓 Student Profile Schema

Each student profile (`students/{name}.md`) follows a strict markdown format:
- **基本資訊 (Basic Info):** Name, Occupation, CEFR Level, Goals, Focus, Personal Background.
- **進度摘要 (Progress Summary):** Mastered concepts, ongoing practice, known weaknesses, and suggestions for the *next* lesson.
- **課程記錄 (Lesson History):** A chronological log (newest to oldest) of past lessons, highlighting what was taught, what the student did well (`好`), and what needs practice (`練習中`).
