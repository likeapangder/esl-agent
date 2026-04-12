---
name: auto-lesson
description: Efficient 2-step lesson workflow. Transcribes video locally, then uses an agentic Writer to draft the email in a clean context window.
argument-hint: [video_file] [--to STUDENT_NAME] [--model WHISPER_MODEL]
disable-model-invocation: false
allowed-tools: Bash, Read, Write
---

# Auto Lesson Orchestrator (Optimized)

This skill orchestrates a clean, token-efficient post-class workflow. It handles the heavy lifting of transcription locally, then delegates the email writing to a specialized sub-agent to keep the main context clean.

## Usage

```bash
/auto-lesson <path_to_video.mp4> --to "Student Name"
```

## Prompt

You are an expert orchestrator for lesson workflows.

1.  **Step 1: Local Transcription**:
    *   Run the lesson summary script to generate a transcript:
        ```bash
        python3 .claude/skills/lesson-summary/scripts/lesson_summary.py "{{$1}}" --model {{model|default:"base"}}
        ```
    *   Find the path to the generated transcript file (it should be in `tmp/`).

2.  **Step 2: Agentic Email Generation**:
    *   Pass the transcript file directly to the `/lesson-email` writer agent:
        ```bash
        /lesson-email <transcript_file>
        ```
    *   **Note:** The `/lesson-email` skill runs in a forked context, so reading the transcript there won't clutter your current history.
    *   The `/lesson-email` skill will output the email text. Capture it and save it to a file (e.g., `tmp/{{$1|basename}}_email.txt`).

3.  **Step 3: Update Student Profile**:
    *   Find the student's profile Markdown file (`students/{{to|default:"Student"}}.md`).
    *   Read the generated email text and extract the key lesson points, strengths, and areas for improvement.
    *   Prepend a new entry to the `## 📅 課程記錄` section in the student's Markdown file. Ensure the entry matches the existing format (Date, Lesson Number, Focus, Progress, Suggestions, Homework).

4.  **Step 4: Delivery**:
    *   Extract the date from the transcript file (it should be on the first line like "DATE: 4/11"). Format it as MMDD (e.g., 0411).
    *   Open the generated email in Gmail using the extracted date:
        ```bash
        # Get the date string from the first line (e.g. "DATE: 4/11" -> "0411")
        LESSON_DATE=$(head -n 1 "tmp/{{$1|basename}}.txt" | grep -oE '[0-9]+/[0-9]+' | awk -F'/' '{printf "%02d%02d", $1, $2}')
        # Fallback to current date if not found
        if [ -z "$LESSON_DATE" ]; then LESSON_DATE=$(date +%m%d); fi
        
        python3 .claude/skills/send-email/scripts/send_email.py "tmp/{{$1|basename}}_email.txt" --subject "$LESSON_DATE AT Lesson with Peggy"
        ```

5.  **Report**: Confirm completion.
