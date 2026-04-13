# ESL Agent Project Guidelines

## Role & Context
You are assisting with the development and operation of the Personalized ESL Agent. This is a local CLI-based workflow system that automates ESL lesson planning, transcription, and post-class emails.

## File Structures & Formats
- **Student Profiles (`students/*.md`)**: When updating or reading student profiles, you MUST STRICTLY maintain the following markdown sections:
  - `## 基本資訊` (Basic Info)
  - `## 進度摘要` (Progress Summary)
  - `## 📅 課程記錄` (Lesson History - ordered newest to oldest, logging what was taught, what the student did well `好`, and what needs practice `練習中`).
- **Email Generation**: Always refer to `templates/Master_EmailStyle_Guide.md` and the user's memory preferences (concise, natural, group related topics) when generating emails. Do not deviate from the requested tone.
- **Lesson Plans (`plans/*.md`)**: Output content should be clean and ready-to-paste.

## Available Workflows (Skills)
When the user asks to perform an ESL task, map their request to the appropriate skill:
- **Pre-class prep**: Use `/esl-prep` (full prep with PDF) or `/esl-plan` (just the plan).
- **Post-class processing**: Use `/auto-lesson` (full workflow), `/transcribe` (local audio-to-text), or `/lesson-summary` (drafting email from transcript).
*(Note: Canva integration `/esl-canva` is currently disabled and marked as coming soon).*

## Development & Script Guidelines
- Custom scripts are located inside `.claude/skills/*/scripts/`.
- Always use `python3` for executing scripts.
- Temporary output files (raw transcripts, email drafts) must be written to the `tmp/` directory, not the project root.
- Do not hallucinate lesson dates. Extract them from the video metadata, transcript headers, or current system date.
