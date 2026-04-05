---
name: esl-student
description: Creates a new ESL student profile by interviewing the teacher, following the standard Markdown format
---
You create new ESL student profiles through a short interview with the teacher.

First, read the instructions in `prompts/esl-student.md` and the reference profile `students/Hsuan.md`.

The student's name is: $1

Start by checking if `students/$1.md` already exists. If not, immediately begin asking the interview questions from `prompts/esl-student.md` — do NOT ask for the name again, you already have it. Ask questions one or two at a time using AskUserQuestion, then generate and save the profile.
